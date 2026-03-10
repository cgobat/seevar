#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: validate_fits.py
Version: 1.0.0
Objective: Validates generated synthetic FITS files for proper WCS and AAVSO headers, and checks image matrix integrity.
"""

import os
import glob
import numpy as np
from astropy.io import fits

def validate_directory(buffer_dir):
    if not os.path.isdir(buffer_dir):
        print(f"Error: Directory '{buffer_dir}' not found.")
        return

    fit_files = glob.glob(os.path.join(buffer_dir, "*.fit"))
    if not fit_files:
        print(f"No .fit files found in {buffer_dir}")
        return

    print(f"Found {len(fit_files)} FITS files for validation.\n")

    for fpath in fit_files:
        fname = os.path.basename(fpath)
        print(f"--- Validating: {fname} ---")
        
        try:
            with fits.open(fpath) as hdul:
                header = hdul[0].header
                data = hdul[0].data
                
                # 1. Check shape
                expected_shape = (1920, 1080)
                if data.shape == expected_shape:
                    print(f"  [PASS] Data Shape: {data.shape}")
                else:
                    print(f"  [FAIL] Data Shape: {data.shape} (Expected {expected_shape})")

                # 2. Check Data integrity (No NaNs, min/max bounds)
                has_nan = np.isnan(data).any()
                d_min, d_max = np.min(data), np.max(data)
                if not has_nan and 0 <= d_min and d_max <= 65535:
                    print(f"  [PASS] Data Integrity: Min={d_min}, Max={d_max}, No NaNs")
                else:
                    print(f"  [WARN] Data Integrity: Min={d_min}, Max={d_max}, Has NaNs={has_nan}")

                # 3. Check AAVSO Headers
                aavso_keys = {
                    'IMAGETYP': 'Light Frame',
                    'EXPTIME': 60.0,
                    'FILTER': 'CV',
                    'BAYERPAT': 'RGGB'
                }
                
                if 'OBJECT' in header:
                    print(f"  [PASS] Header 'OBJECT': {header['OBJECT']}")
                else:
                    print("  [FAIL] Header 'OBJECT': Missing")
                    
                for key, expected_val in aavso_keys.items():
                    if key in header and header[key] == expected_val:
                        print(f"  [PASS] Header '{key}': {header[key]}")
                    else:
                        val = header.get(key, 'Missing')
                        print(f"  [FAIL] Header '{key}': {val} (Expected {expected_val})")

                # 4. Check WCS Headers
                wcs_keys = ['CRVAL1', 'CRVAL2', 'CDELT1', 'CDELT2', 'CTYPE1', 'CTYPE2']
                missing_wcs = [k for k in wcs_keys if k not in header]
                if not missing_wcs:
                    print(f"  [PASS] WCS Headers: Present (CRVAL1={header['CRVAL1']}, CRVAL2={header['CRVAL2']})")
                else:
                    print(f"  [FAIL] WCS Headers: Missing {missing_wcs}")
                    
        except Exception as e:
            print(f"  [ERROR] Could not read {fname}: {e}")
        print("\n")

if __name__ == "__main__":
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'local_buffer')
    validate_directory(target_dir)
