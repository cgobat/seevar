#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/fits_inspector.py
Version: 1.0.0
Objective: Perform forensics on unknown FITS files to determine sensor size and residual headers.
"""

import glob
from pathlib import Path
try:
    from astropy.io import fits
except ImportError:
    print("❌ Astropy is missing. Please run: pip install astropy")
    exit(1)

BUFFER_DIR = Path("/mnt/usb_buffer/data/local_buffer")

def inspect_fits():
    print("\n🕵️ === FITS FORENSICS INITIATED ===")
    
    # Grab the first FITS file it can find
    files = glob.glob(str(BUFFER_DIR / "*.fit*"))
    
    if not files:
        print("❌ No FITS files found in the buffer.")
        return

    test_file = files[0]
    print(f"📄 Inspecting: {Path(test_file).name}")

    try:
        with fits.open(test_file) as hdul:
            print("\n📊 HDU (Header Data Unit) Info:")
            hdul.info()
            
            hdr = hdul[0].header
            data = hdul[0].data

            print("\n📏 Data Array Matrix:")
            if data is not None:
                # data.shape usually returns (Height, Width) or (Channels, Height, Width)
                print(f"   Shape: {data.shape}")
            else:
                print("   Data array is empty! This might be a corrupted file.")

            print("\n🏷️ Residual Header Keys (Top 10):")
            keys = list(hdr.keys())
            if len(keys) <= 1:
                print("   [CRITICAL] Header is completely stripped.")
            else:
                for k in keys[:10]:
                    print(f"   {k}: {hdr.get(k)}")

    except Exception as e:
        print(f"❌ Error reading FITS: {e}")

if __name__ == "__main__":
    inspect_fits()
