#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/ensemble_photometry.py
Version: 1.1.0
Objective: Ensemble photometry using verified AAVSO coordinates and magnitudes for Algol.
"""

import numpy as np
from pathlib import Path
try:
    from astropy.io import fits
    from astropy.wcs import WCS
    from astropy.coordinates import SkyCoord
    from photutils.aperture import CircularAperture, CircularAnnulus, aperture_photometry
except ImportError:
    print("❌ Missing dependencies. Run: pip install astropy photutils numpy")
    exit(1)

# Pointing to our historical test file
TEST_FILE = Path("/mnt/usb_buffer/data/local_buffer/algol.fits")

# Comparison Stars verified via AAVSO Fetcher (Labels converted to Mags)
COMPS = [
    {"label": "46", "ra": "03h11m17.38s", "dec": "+39d36m41.7s", "known_mag": 4.6},
    {"label": "79", "ra": "03h08m11.04s", "dec": "+41d35m07.3s", "known_mag": 7.9},
    {"label": "82", "ra": "03h11m24.95s", "dec": "+41d10m50.1s", "known_mag": 8.2}
]

def get_net_flux(data, wcs_obj, ra_str, dec_str, label):
    """Calculates background-subtracted flux for a specific coordinate."""
    try:
        coord = SkyCoord(ra_str, dec_str, frame='icrs')
        px, py = wcs_obj.world_to_pixel(coord)
        
        if not (0 <= px <= data.shape[1] and 0 <= py <= data.shape[0]):
            return None

        position = (px, py)
        aperture = CircularAperture(position, r=5.0)
        annulus = CircularAnnulus(position, r_in=10.0, r_out=15.0)
        
        phot_table = aperture_photometry(data, [aperture, annulus])
        
        annulus_mask = annulus.to_mask(method='center')
        bkg_data = annulus_mask.multiply(data)
        bkg_data_1d = bkg_data[annulus_mask.data > 0]
        bkg_median = np.median(bkg_data_1d) 
        
        net_flux = phot_table['aperture_sum_0'][0] - (bkg_median * aperture.area)
        return net_flux
    except:
        return None

def run_ensemble():
    print("\n🎻 === ENSEMBLE PHOTOMETRY ENGINE === 🎻")
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return

    with fits.open(TEST_FILE) as hdul:
        data = hdul[0].data
        w = WCS(hdul[0].header)
        
        # 1. Measure Target (Algol)
        algol_flux = get_net_flux(data, w, '03h08m10.1s', '+40d57m20.3s', "Algol")
        
        # 2. Measure Comparison Ensemble
        zero_points = []
        print(f"📡 Processing {len(COMPS)} comparison stars...")
        
        for c in COMPS:
            c_flux = get_net_flux(data, w, c['ra'], c['dec'], c['label'])
            if c_flux and c_flux > 0:
                # Formula: ZeroPoint = CatalogMag + 2.5 * log10(InstrumentalFlux)
                zp = c['known_mag'] + (2.5 * np.log10(c_flux))
                zero_points.append(zp)
                print(f"  ✅ Comp {c['label']}: Net Flux={c_flux:.2f} | ZP={zp:.4f}")

        if not zero_points:
            print("❌ Error: No comparison stars could be measured.")
            return

        # 3. Final Calculation
        avg_zp = np.mean(zero_points)
        std_zp = np.std(zero_points) # Error margin
        
        # Final Mag = -2.5 * log10(TargetFlux) + AverageZeroPoint
        final_mag = -2.5 * np.log10(algol_flux) + avg_zp

        print("-" * 45)
        print(f"📊 Ensemble Zero Point: {avg_zp:.4f} (±{std_zp:.4f})")
        print(f"✨ CALIBRATED MAGNITUDE (Algol): {final_mag:.4f}")
        print("-" * 45)

if __name__ == "__main__":
    run_ensemble()
