#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/aperture_photometry.py
Version: 1.0.0
Objective: Extract instrumental flux and magnitude using aperture photometry on precise WCS coordinates.
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

def extract_photometry():
    print("\n🌟 === APERTURE PHOTOMETRY EXTRACTION === 🌟")
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return

    try:
        with fits.open(TEST_FILE) as hdul:
            hdr = hdul[0].header
            data = hdul[0].data
            w = WCS(hdr)
            
            algol_coord = SkyCoord('03h08m10.1s', '+40d57m20.3s', frame='icrs')
            px, py = w.world_to_pixel(algol_coord)
            
            print(f"📍 Target Pixel: X={px:.2f}, Y={py:.2f}")

            # Define the Aperture (Radius=5 pixels for the star) 
            # and Annulus (Radius 10 to 15 pixels for the background sky)
            position = (px, py)
            aperture = CircularAperture(position, r=5.0)
            annulus = CircularAnnulus(position, r_in=10.0, r_out=15.0)
            
            # Perform photometry on both apertures
            phot_table = aperture_photometry(data, [aperture, annulus])
            
            # Calculate background sky per pixel
            annulus_mask = annulus.to_mask(method='center')
            bkg_data = annulus_mask.multiply(data)
            bkg_data_1d = bkg_data[annulus_mask.data > 0]
            
            # Use median for background to ignore nearby faint stars in the annulus
            bkg_median = np.median(bkg_data_1d) 
            
            # Total background to subtract = (background per pixel) * (area of star aperture)
            bkg_total = bkg_median * aperture.area
            
            # Calculate final flux and instrumental magnitude
            raw_flux = phot_table['aperture_sum_0'][0]
            net_flux = raw_flux - bkg_total
            
            if net_flux > 0:
                instrumental_mag = -2.5 * np.log10(net_flux)
                print(f"🧮 Background Sky (Median): {bkg_median:.4f} ADU")
                print(f"🔆 Raw Star Flux: {raw_flux:.4f} ADU")
                print(f"✨ Net Star Flux: {net_flux:.4f} ADU")
                print(f"📉 Instrumental Magnitude: {instrumental_mag:.4f}")
            else:
                print("⚠️ Net flux is negative. Star is not visible above the background noise.")

    except Exception as e:
        print(f"❌ Error during photometry: {e}")

if __name__ == "__main__":
    extract_photometry()
