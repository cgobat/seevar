#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/photometry_targeter.py
Version: 1.0.0
Objective: Use WCS headers to translate celestial RA/Dec into exact X/Y image pixels.
"""

from pathlib import Path
try:
    from astropy.io import fits
    from astropy.wcs import WCS
    from astropy.coordinates import SkyCoord
    import astropy.units as u
except ImportError:
    print("❌ Astropy is missing. Please run: pip install astropy")
    exit(1)

# Pointing directly to your Algol test file
TEST_FILE = Path("/mnt/usb_buffer/data/local_buffer/algol.fits")

def target_star():
    print("\n🎯 === PHOTOMETRY TARGETER === 🎯")
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return

    try:
        with fits.open(TEST_FILE) as hdul:
            hdr = hdul[0].header
            
            # 1. Extract the World Coordinate System (WCS) from the header
            print("🗺️ Reading WCS Astrometry grid from header...")
            w = WCS(hdr)
            
            # 2. Define our target coordinates (Algol: RA 03h08m10.1s, Dec +40d57m20.3s)
            # We convert this to decimal degrees for Astropy
            algol_coord = SkyCoord('03h08m10.1s', '+40d57m20.3s', frame='icrs')
            print(f"✨ Target (Algol): RA {algol_coord.ra.deg:.4f}°, DEC {algol_coord.dec.deg:.4f}°")
            
            # 3. Translate RA/Dec to Pixel X/Y
            px, py = w.world_to_pixel(algol_coord)
            
            print(f"📍 Calculated Pixel Location: X={px:.2f}, Y={py:.2f}")
            
            # Since the image is 1920x1080, if it worked, Algol should be right near the center (960, 540)
            if 0 <= px <= 1920 and 0 <= py <= 1080:
                print("✅ Target is successfully mapped within the image bounds!")
            else:
                print("⚠️ Target falls outside the image bounds.")

    except Exception as e:
        print(f"❌ Error processing FITS: {e}")

if __name__ == "__main__":
    target_star()
