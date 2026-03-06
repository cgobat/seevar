#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/differential_photometry.py
Version: 1.0.0
Objective: Perform differential aperture photometry using a target and a known comparison star.
"""

import numpy as np
from pathlib import Path
try:
    from astropy.io import fits
    from astropy.wcs import WCS
    from astropy.coordinates import SkyCoord
    from photutils.aperture import CircularAperture, CircularAnnulus, aperture_photometry
except ImportError:
    print("❌ Missing dependencies. Please run: pip install astropy photutils numpy")
    exit(1)

TEST_FILE = Path("/mnt/usb_buffer/data/local_buffer/algol.fits")

def measure_star(data, wcs_obj, ra_str, dec_str, name):
    """Measures net flux for a given coordinate."""
    coord = SkyCoord(ra_str, dec_str, frame='icrs')
    px, py = wcs_obj.world_to_pixel(coord)
    
    if not (0 <= px <= data.shape[1] and 0 <= py <= data.shape[0]):
        print(f"⚠️ {name} is outside the image bounds.")
        return None

    position = (px, py)
    aperture = CircularAperture(position, r=5.0)
    annulus = CircularAnnulus(position, r_in=10.0, r_out=15.0)
    
    phot_table = aperture_photometry(data, [aperture, annulus])
    
    ann_mask = annulus.to_mask(method='center')
    bkg_data = ann_mask.multiply(data)
    bkg_1d = bkg_data[ann_mask.data > 0]
    bkg_median = np.median(bkg_1d) 
    bkg_total = bkg_median * aperture.area
    
    raw_flux = phot_table['aperture_sum_0'][0]
    net_flux = raw_flux - bkg_total
    
    return net_flux

def calculate_differential():
    print("\n⚖️ === DIFFERENTIAL PHOTOMETRY ENGINE === ⚖️")
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return

    try:
        with fits.open(TEST_FILE) as hdul:
            hdr = hdul[0].header
            data = hdul[0].data
            w = WCS(hdr)
            
            # 1. Measure the Target (Algol)
            algol_flux = measure_star(data, w, '03h08m10.1s', '+40d57m20.3s', "Algol")
            
            # 2. Measure a "Dummy" Comp Star slightly offset from Algol
            # In a real run, this data comes from your comp_stars/ JSONs
            comp_flux = measure_star(data, w, '03h08m15.0s', '+40d59m00.0s', "Comp Star A")
            comp_known_mag = 3.50  # Let's pretend the AAVSO says this star is mag 3.50
            
            if algol_flux and comp_flux and algol_flux > 0 and comp_flux > 0:
                print(f"🔆 Algol Net Flux: {algol_flux:.4f} ADU")
                print(f"⭐ Comp Star Net Flux: {comp_flux:.4f} ADU (Ref Mag: {comp_known_mag})")
                
                # The Differential Photometry Equation: M_target = M_comp - 2.5 * log10(F_target / F_comp)
                mag_diff = -2.5 * np.log10(algol_flux / comp_flux)
                calculated_mag = comp_known_mag + mag_diff
                
                print(f"📉 Calculated Magnitude Difference: {mag_diff:.4f}")
                print(f"✅ Final Apparent Magnitude of Algol: {calculated_mag:.4f}")
            else:
                print("⚠️ Could not extract valid flux for both stars.")

    except Exception as e:
        print(f"❌ Error during differential photometry: {e}")

if __name__ == "__main__":
    calculate_differential()
