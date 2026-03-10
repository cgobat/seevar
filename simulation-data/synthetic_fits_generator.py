#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: synthetic_fits_generator.py
Version: 1.0.0
Objective: Generates a synthetic, scientifically accurate RAW FITS file for a requested target using Gaia DR3 catalog data.
"""

import os
import sys
import json
import argparse
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.vizier import Vizier

# --- Core Configurations ---
FOV_RA_DEG = 1.28
FOV_DEC_DEG = 0.72
IMG_WIDTH = 1080   # X-axis (Seestar Portrait)
IMG_HEIGHT = 1920  # Y-axis (Seestar Portrait)
NOISE_FLOOR = 500
NOISE_STD = 15     # Standard deviation for read noise simulation
CDELT_VAL = 0.00067

def generate_synthetic_fits(target_name, plan_file):
    # 1. Load target data from the daily roster
    if not os.path.exists(plan_file):
        print(f"Error: Roster file '{plan_file}' not found.")
        sys.exit(1)

    with open(plan_file, 'r') as f:
        plan = json.load(f)
    
    target_data = next((t for t in plan.get('targets', []) if t['name'] == target_name), None)
    if not target_data:
        print(f"Error: Target '{target_name}' not found in {plan_file}.")
        sys.exit(1)
        
    ra_deg = target_data['ra']
    dec_deg = target_data['dec']
    print(f"Target found: {target_name} at RA: {ra_deg}, DEC: {dec_deg}")

    # 2. Query VizieR (Gaia DR3) for background stars
    print("Querying Gaia DR3 via VizieR. This may take a moment...")
    v = Vizier(columns=['RA_ICRS', 'DE_ICRS', 'Gmag'])
    v.ROW_LIMIT = -1  # Unlimited rows within the FOV
    
    coord = SkyCoord(ra=ra_deg, dec=dec_deg, unit=(u.deg, u.deg), frame='icrs')
    result = v.query_region(
        coord, 
        width=FOV_RA_DEG * u.deg, 
        height=FOV_DEC_DEG * u.deg, 
        catalog="I/355/gaiadr3"
    )
    
    if len(result) == 0:
        print("Error: No stars found in catalog for this region.")
        sys.exit(1)
        
    stars = result[0]
    print(f"Found {len(stars)} stars in the FOV.")

    # 3. Create the Canvas with noise floor
    canvas = np.random.normal(NOISE_FLOOR, NOISE_STD, (IMG_HEIGHT, IMG_WIDTH))
    
    # 4. Generate WCS Projection
    w = WCS(naxis=2)
    w.wcs.crpix = [IMG_WIDTH / 2, IMG_HEIGHT / 2]
    w.wcs.cdelt = np.array([-CDELT_VAL, CDELT_VAL]) # RA decreases to the right
    w.wcs.crval = [ra_deg, dec_deg]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

    # 5. Project Catalog to Pixels & Render Optics
    print("Projecting WCS and rendering optical PSFs...")
    star_coords = SkyCoord(ra=stars['RA_ICRS'], dec=stars['DE_ICRS'], unit=(u.deg, u.deg))
    x_pix, y_pix = w.world_to_pixel(star_coords)
    mags = stars['Gmag']
    
    for x, y, mag in zip(x_pix, y_pix, mags):
        if np.isnan(mag) or np.isnan(x) or np.isnan(y):
            continue
            
        x_idx, y_idx = int(round(x)), int(round(y))
        
        # Only render if the center of the star is within the bounds
        if 0 <= x_idx < IMG_WIDTH and 0 <= y_idx < IMG_HEIGHT:
            # Flux Scaling: Magnitude to ADU mapping
            # Tuned so mag 5 ~ 50,000 ADU, avoiding hard saturation.
            flux_amplitude = 10 ** ((15 - mag) / 2.5) * 150 
            
            # Draw a 2D Gaussian point spread function (5x5 matrix bounding box)
            for i in range(-2, 3):
                for j in range(-2, 3):
                    xi, yj = x_idx + i, y_idx + j
                    if 0 <= xi < IMG_WIDTH and 0 <= yj < IMG_HEIGHT:
                        dist_sq = i**2 + j**2
                        val = flux_amplitude * np.exp(-dist_sq / 1.5)
                        canvas[yj, xi] += val

    # Enforce 16-bit limits
    canvas = np.clip(canvas, 0, 65535).astype(np.uint16)

    # 6. Build Headers and Save output
    hdu = fits.PrimaryHDU(canvas)
    header = hdu.header
    
    # Inject standard and mandatory AAVSO headers
    header.update(w.to_header())
    header['OBJECT'] = target_name
    header['IMAGETYP'] = 'Light Frame'
    header['EXPTIME'] = 60.0
    header['FILTER'] = 'CV'
    header['BAYERPAT'] = 'RGGB'
    
    # Setup directories
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'local_buffer')
    os.makedirs(out_dir, exist_ok=True)
    
    safe_name = target_name.replace(" ", "_")
    out_path = os.path.join(out_dir, f"{safe_name}_001.fit")
    
    hdu.writeto(out_path, overwrite=True)
    print(f"Synthetic capture complete. Saved to: {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deterministic Synthetic Sky Generator for Seestar pipeline.")
    parser.add_argument("--target", required=True, help="Target name exact match as listed in the JSON roster.")
    parser.add_argument("--plan", default="tonights_plan.json", help="Path to the JSON flight roster.")
    args = parser.parse_args()
    
    generate_synthetic_fits(args.target, args.plan)
