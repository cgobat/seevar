#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/exposure_planner.py
Version: 1.2.0
Objective: Estimate optimal exposure time and frame count for a target given
           its magnitude range, sky conditions, field rotation and SNR goal.
           Three-way exposure cap: SNR, saturation, field rotation.
           Chunking strategy: safe single-frame exposure × n_frames to reach
           total integration time needed for faint-state detection.
           Feeds orchestrator exp_ms and n_frames.

Peer review contributions (March 2026):
  - mag_bright / mag_faint range — variable star magnitude swing
  - Chunking: fast safe frames for bright state, stacked for faint state
  - Scintillation noise term (Young's approximation) for small apertures
  - Field rotation cap per az/alt/lat (field_rotation.py)
"""

import math
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# IMX585 / S30-Pro sensor constants
# ---------------------------------------------------------------------------
GAIN_E_ADU        = 1.0
READ_NOISE_E      = 1.6
DARK_CURRENT_E_S  = 0.005
FULL_WELL_E       = 50000
SATURATION_ADU    = 60000
PIXEL_SCALE       = 3.75       # arcsec/pixel
APERTURE_MM       = 30.0
FOCAL_LENGTH_MM   = 150.0
FOCAL_RATIO       = FOCAL_LENGTH_MM / APERTURE_MM
APERTURE_M        = APERTURE_MM / 1000.0
COLLECTING_AREA   = math.pi * (APERTURE_M / 2.0) ** 2
ALTITUDE_M        = 0.0        # observer altitude metres — updated from config

SYSTEM_THROUGHPUT = 0.80 * 0.50 * 0.90   # QE * Bayer G * optics ~ 0.36
V0_FLUX           = 3.64e10 * 88.0        # photons/s/m² for V=0

BORTLE_SKY_E_S = {
    1: 0.002, 2: 0.003, 3: 0.005, 4: 0.010, 5: 0.020,
    6: 0.050, 7: 0.120, 8: 0.300, 9: 0.700,
}
DEFAULT_BORTLE   = 7
MIN_EXP_SEC      = 1.0
MAX_EXP_SEC      = 300.0
MAX_FRAME_SEC    = 20.0    # field rotation practical ceiling
TARGET_SNR       = 50.0
MIN_SNR          = 10.0
MAX_TOTAL_SEC    = 300.0   # max 5 minutes total per target

TYPICAL_FWHM_PIX    = 4.0
APERTURE_RADIUS_PIX = 1.7 * TYPICAL_FWHM_PIX
N_PIX_APERTURE      = math.pi * APERTURE_RADIUS_PIX ** 2


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------
@dataclass
class ExposurePlan:
    target_mag:         float   # faint-state magnitude used for SNR calc
    mag_bright:         float   # bright-state magnitude (saturation guard)
    exp_sec:            float   # single frame exposure in seconds
    exp_ms:             int     # single frame exposure in milliseconds
    n_frames:           int     # frames to stack for faint-state SNR
    total_sec:          float   # total integration time
    expected_snr:       float   # SNR per frame at faint state
    source_electrons_s: float
    sky_electrons_s:    float
    n_pix:              float
    saturates:          bool
    saturation_sec:     float
    scintillation_mag:  float   # scintillation noise floor in mmag
    bortle:             int
    note:               str


# ---------------------------------------------------------------------------
# CCD equation
# ---------------------------------------------------------------------------
def _source_rate(v_mag: float) -> float:
    return V0_FLUX * COLLECTING_AREA * SYSTEM_THROUGHPUT * 10.0**(-v_mag / 2.5)


def _snr(source_e_s, sky_e_pix_s, n_pix, t) -> float:
    signal   = source_e_s * t
    noise_sq = signal + n_pix * (sky_e_pix_s * t + DARK_CURRENT_E_S * t
                                  + READ_NOISE_E**2)
    return signal / math.sqrt(noise_sq) if noise_sq > 0 else 0.0


def _solve_exposure(source_e_s, sky_e_pix_s, n_pix, target_snr) -> float:
    S, N = source_e_s, n_pix
    B    = sky_e_pix_s + DARK_CURRENT_E_S
    R2   = READ_NOISE_E**2
    Q    = target_snr**2
    a    = S**2
    b    = -Q * (S + N * B)
    c    = -Q * N * R2
    disc = b**2 - 4*a*c
    if disc < 0:
        return MAX_EXP_SEC
    return max(MIN_EXP_SEC, (-b + math.sqrt(disc)) / (2*a))


def _saturation_time(source_e_s) -> float:
    peak_e_s = source_e_s * 0.10
    return FULL_WELL_E / peak_e_s if peak_e_s > 0 else MAX_EXP_SEC


# ---------------------------------------------------------------------------
# Scintillation noise (Young's approximation)
# Dominant noise source for bright stars with small apertures
# ---------------------------------------------------------------------------
def _scintillation_mmag(alt_deg: float, exp_sec: float,
                         aperture_mm: float = APERTURE_MM,
                         altitude_m: float = ALTITUDE_M) -> float:
    """
    Young's approximation for scintillation noise in mmag.
    sigma_scint = 0.09 * D^(-2/3) * X^1.75 * exp(-h/8000) / sqrt(2*t)
    D = aperture in cm, X = airmass, h = altitude in metres, t = exposure in s
    """
    if alt_deg <= 0:
        return 999.0
    airmass = 1.0 / math.sin(math.radians(alt_deg))
    D_cm    = aperture_mm / 10.0
    sigma   = (0.09 * D_cm**(-2/3) * airmass**1.75
               * math.exp(-altitude_m / 8000.0)
               / math.sqrt(2.0 * max(exp_sec, 0.1)))
    # Convert fractional intensity to mmag: sigma_mag = 2.5*log10(1+sigma) * 1000
    return round(2.5 * math.log10(1.0 + sigma) * 1000.0, 2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def plan_exposure(
    target_mag:      float,
    mag_bright:      Optional[float] = None,
    sky_bortle:      int   = DEFAULT_BORTLE,
    target_snr:      float = TARGET_SNR,
    fwhm_pix:        Optional[float] = None,
    az_deg:          Optional[float] = None,
    alt_deg:         Optional[float] = None,
    lat_deg:         Optional[float] = None,
    pixscale_arcsec: float = PIXEL_SCALE,
) -> ExposurePlan:
    """
    Calculate optimal exposure and frame count for a variable star.

    Args:
        target_mag:  Faint-state magnitude (worst case for SNR)
        mag_bright:  Bright-state magnitude (worst case for saturation)
                     Defaults to target_mag if not provided (non-variable)
        sky_bortle:  Bortle sky darkness class (1-9)
        target_snr:  Desired signal-to-noise ratio
        fwhm_pix:    Measured PSF FWHM in pixels (uses default if None)
        az_deg:      Target azimuth for field rotation cap
        alt_deg:     Target altitude for field rotation cap + scintillation
        lat_deg:     Observer latitude for field rotation cap
        pixscale_arcsec: Sensor pixel scale
    """
    if mag_bright is None:
        mag_bright = target_mag

    sky_e_s      = BORTLE_SKY_E_S.get(sky_bortle, BORTLE_SKY_E_S[DEFAULT_BORTLE])

    # Use faint state for SNR calculation
    source_faint = _source_rate(target_mag)
    # Use bright state for saturation calculation
    source_bright = _source_rate(mag_bright)

    n_pix = math.pi * (1.7 * fwhm_pix)**2 if fwhm_pix else N_PIX_APERTURE

    # --- Single frame exposure ---
    # Cap 1: SNR-optimal for faint state
    t_snr = _solve_exposure(source_faint, sky_e_s, n_pix, target_snr)

    # Cap 2: Saturation of bright state
    t_sat      = _saturation_time(source_bright)
    saturates  = t_sat < t_snr
    t_frame    = min(t_snr, t_sat * 0.5 if saturates else t_snr)

    # Cap 3: Field rotation
    rotation_note = ""
    if az_deg is not None and alt_deg is not None and lat_deg is not None:
        from core.flight.field_rotation import max_exposure_s as _rot_max
        rot = _rot_max(az_deg, alt_deg, lat_deg, pixscale_arcsec)
        if rot.max_exp_s < t_frame:
            t_frame = max(MIN_EXP_SEC, rot.max_exp_s)
            rotation_note = f" | ROT {rot.max_exp_s:.0f}s"

    # Practical ceiling (field rotation / firmware)
    t_frame = min(max(t_frame, MIN_EXP_SEC), MAX_FRAME_SEC)

    # --- Chunking: how many frames to reach required total integration ---
    # Total integration needed for faint state SNR
    # Bortle penalty: each step above 4 adds 15% integration time
    bortle_penalty = 1.0 + max(0, (sky_bortle - 4) * 0.15)

    # Base: 60s total for mag 12 at SNR 50
    mag_diff_faint  = target_mag - 12.0
    required_total  = 60.0 * (2.512 ** mag_diff_faint) * bortle_penalty
    required_total  = min(required_total, MAX_TOTAL_SEC)

    n_frames = max(1, math.ceil(required_total / t_frame))
    total_s  = round(t_frame * n_frames, 1)

    # SNR per frame
    achieved_snr = _snr(source_faint, sky_e_s, n_pix, t_frame)

    # Scintillation noise floor
    scint_mmag = _scintillation_mmag(
        alt_deg if alt_deg else 45.0, t_frame
    )

    # Build note
    if saturates:
        note = (f"BRIGHT STATE SATURATES at {t_sat:.1f}s — "
                f"frame {t_frame:.1f}s × {n_frames} = {total_s:.0f}s total"
                f"{rotation_note}")
    elif achieved_snr < MIN_SNR:
        note = (f"FAINT — best SNR {achieved_snr:.1f} at {t_frame:.1f}s × "
                f"{n_frames} frames = {total_s:.0f}s{rotation_note}")
    else:
        note = (f"{t_frame:.1f}s × {n_frames} = {total_s:.0f}s | "
                f"SNR {achieved_snr:.0f} | scint {scint_mmag:.1f}mmag"
                f"{rotation_note}")

    return ExposurePlan(
        target_mag=target_mag,
        mag_bright=mag_bright,
        exp_sec=round(t_frame, 1),
        exp_ms=int(t_frame * 1000),
        n_frames=n_frames,
        total_sec=total_s,
        expected_snr=round(achieved_snr, 1),
        source_electrons_s=round(source_faint, 3),
        sky_electrons_s=round(sky_e_s, 6),
        n_pix=round(n_pix, 1),
        saturates=saturates,
        saturation_sec=round(t_sat, 1),
        scintillation_mag=scint_mmag,
        bortle=sky_bortle,
        note=note,
    )


def plan_exposure_table(mags, sky_bortle=DEFAULT_BORTLE,
                        target_snr=TARGET_SNR):
    return [plan_exposure(m, sky_bortle=sky_bortle,
                          target_snr=target_snr) for m in mags]


if __name__ == "__main__":
    print("SeeVar Exposure Planner v1.2.0 — Haarlem, Bortle 8, S30-Pro")
    print("=" * 75)
    print(f"{'Target':20} {'Bright':>7} {'Faint':>6} {'Frame':>7} "
          f"{'N':>5} {'Total':>7} {'SNR':>6} {'Scint':>8}")
    print("-" * 75)

    test_targets = [
        ("Constant V=10",    10.0, 10.0),
        ("Mira (6-13)",       6.0, 13.0),
        ("T CrB (2-10 NR)",   2.0, 10.0),
        ("SS Cyg (8-12 UG)",  8.0, 12.0),
        ("Faint CV (14-16)",  14.0, 16.0),
        ("RCrB (6-15)",       6.0, 15.0),
    ]

    for name, bright, faint in test_targets:
        p = plan_exposure(faint, mag_bright=bright, sky_bortle=8,
                          az_deg=180, alt_deg=45, lat_deg=52.38)
        print(f"{name:20} {bright:>7.1f} {faint:>6.1f} "
              f"{p.exp_sec:>6.1f}s {p.n_frames:>5d} "
              f"{p.total_sec:>6.0f}s {p.expected_snr:>6.1f} "
              f"{p.scintillation_mag:>7.1f}mm")
    print()
    print("Note: T CrB — recurrent nova, check saturation at maximum!")
