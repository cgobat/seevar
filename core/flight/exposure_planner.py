#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/exposure_planner.py
Version: 1.1.0
Objective: Estimate optimal exposure time for a target given magnitude, sky conditions,
           desired SNR and field rotation limit. Three-way cap: SNR, saturation,
           field rotation. Shortest wins. Feeds orchestrator exp_ms.
"""

import math
from dataclasses import dataclass
from typing import Optional

from core.flight.field_rotation import max_exposure_s as _field_rotation_max

# ---------------------------------------------------------------------------
# IMX585 / S30-Pro sensor constants
# ---------------------------------------------------------------------------
GAIN_E_ADU       = 1.0
READ_NOISE_E     = 1.6
DARK_CURRENT_E_S = 0.005
FULL_WELL_E      = 50000
SATURATION_ADU   = 60000
PIXEL_SCALE      = 3.75
APERTURE_MM      = 30.0
FOCAL_LENGTH_MM  = 150.0
FOCAL_RATIO      = FOCAL_LENGTH_MM / APERTURE_MM
APERTURE_M       = APERTURE_MM / 1000.0
COLLECTING_AREA  = math.pi * (APERTURE_M / 2.0) ** 2

SYSTEM_THROUGHPUT = 0.80 * 0.50 * 0.90    # QE * Bayer G * optics ~ 0.36

V0_FLUX_PHOTONS_S_M2 = 3.64e10 * 88.0     # photons/s/m² for V=0, Johnson V band

# Sky background per pixel per second, by Bortle class
BORTLE_SKY_E_S = {
    1: 0.002, 2: 0.003, 3: 0.005, 4: 0.010, 5: 0.020,
    6: 0.050, 7: 0.120, 8: 0.300, 9: 0.700,
}
DEFAULT_BORTLE = 7

MIN_EXP_SEC  = 5.0
MAX_EXP_SEC  = 300.0
TARGET_SNR   = 50.0
MIN_SNR      = 10.0

TYPICAL_FWHM_PIX    = 4.0
APERTURE_RADIUS_PIX = 1.7 * TYPICAL_FWHM_PIX
N_PIX_APERTURE      = math.pi * APERTURE_RADIUS_PIX ** 2


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------
@dataclass
class ExposurePlan:
    target_mag: float
    exp_sec: float
    exp_ms: int
    expected_snr: float
    source_electrons_s: float
    sky_electrons_s: float
    n_pix: float
    saturates: bool
    saturation_sec: float
    bortle: int
    note: str


# ---------------------------------------------------------------------------
# Core CCD equation
# ---------------------------------------------------------------------------
def _source_rate(v_mag: float) -> float:
    photons_s = V0_FLUX_PHOTONS_S_M2 * COLLECTING_AREA * SYSTEM_THROUGHPUT
    return photons_s * 10.0 ** (-v_mag / 2.5)


def _snr(source_e_s: float, sky_e_pix_s: float, n_pix: float, t: float) -> float:
    signal = source_e_s * t
    noise_sq = signal + n_pix * (sky_e_pix_s * t + DARK_CURRENT_E_S * t + READ_NOISE_E ** 2)
    if noise_sq <= 0:
        return 0.0
    return signal / math.sqrt(noise_sq)


def _solve_for_exposure(source_e_s: float, sky_e_pix_s: float, n_pix: float, target_snr: float) -> float:
    S, N, B, R2, Q = source_e_s, n_pix, sky_e_pix_s + DARK_CURRENT_E_S, READ_NOISE_E ** 2, target_snr ** 2
    a = S ** 2
    b = -Q * (S + N * B)
    c = -Q * N * R2

    discriminant = b ** 2 - 4.0 * a * c
    if discriminant < 0: return MAX_EXP_SEC
    t = (-b + math.sqrt(discriminant)) / (2.0 * a)
    return max(MIN_EXP_SEC, t)


def _saturation_time(source_e_s: float) -> float:
    peak_fraction = 0.10
    peak_e_s = source_e_s * peak_fraction
    if peak_e_s <= 0: return MAX_EXP_SEC
    return FULL_WELL_E / peak_e_s


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def plan_exposure(
    target_mag: float,
    sky_bortle: int = DEFAULT_BORTLE,
    target_snr: float = TARGET_SNR,
    fwhm_pix: Optional[float] = None,
    az_deg: Optional[float] = None,
    alt_deg: Optional[float] = None,
    lat_deg: Optional[float] = None,
    pixscale_arcsec: float = PIXEL_SCALE,
) -> ExposurePlan:
    sky_e_s    = BORTLE_SKY_E_S.get(sky_bortle, BORTLE_SKY_E_S[DEFAULT_BORTLE])
    source_e_s = _source_rate(target_mag)
    n_pix = math.pi * (1.7 * fwhm_pix) ** 2 if fwhm_pix is not None else N_PIX_APERTURE

    t_recommended = _solve_for_exposure(source_e_s, sky_e_s, n_pix, target_snr)
    t_sat         = _saturation_time(source_e_s)

    saturates = t_sat < t_recommended
    if saturates: t_recommended = max(MIN_EXP_SEC, t_sat * 0.5)

    # Field rotation cap — alt-az smear limit
    rotation_note = ""
    if az_deg is not None and alt_deg is not None and lat_deg is not None:
        rot = _field_rotation_max(az_deg, alt_deg, lat_deg, pixscale_arcsec)
        if rot.max_exp_s < t_recommended:
            t_recommended = max(MIN_EXP_SEC, rot.max_exp_s)
            rotation_note = f" | ROTATION CAP {rot.max_exp_s:.1f}s ({rot.note[:40]})"

    t_recommended = min(max(t_recommended, MIN_EXP_SEC), MAX_EXP_SEC)
    achieved_snr  = _snr(source_e_s, sky_e_s, n_pix, t_recommended)

    if saturates:
        note = f"SATURATES at {t_sat:.1f}s — capped at {t_recommended:.1f}s. SNR={achieved_snr:.0f}. Consider ND filter."
    elif achieved_snr < MIN_SNR:
        note = f"Target too faint for SNR>{MIN_SNR:.0f} within {MAX_EXP_SEC:.0f}s. Best SNR={achieved_snr:.1f} at {t_recommended:.0f}s."
    else:
        note = f"Recommended: {t_recommended:.1f}s for SNR={achieved_snr:.0f} (Bortle {sky_bortle}, mag {target_mag:.1f}){rotation_note}"

    return ExposurePlan(
        target_mag=target_mag, exp_sec=round(t_recommended, 1), exp_ms=int(t_recommended * 1000),
        expected_snr=round(achieved_snr, 1), source_electrons_s=round(source_e_s, 3), sky_electrons_s=round(sky_e_s, 6),
        n_pix=round(n_pix, 1), saturates=saturates, saturation_sec=round(t_sat, 1), bortle=sky_bortle, note=note,
    )

def plan_exposure_table(mags: list, sky_bortle: int = DEFAULT_BORTLE, target_snr: float = TARGET_SNR) -> list:
    return [plan_exposure(m, sky_bortle, target_snr) for m in mags]

if __name__ == "__main__":
    for mag in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:
        p = plan_exposure(mag, sky_bortle=DEFAULT_BORTLE, target_snr=TARGET_SNR)
        print(f"{p.target_mag:>5.1f}  {p.exp_sec:>7.1f}  {p.expected_snr:>6.1f}  {p.note[:40]}")
