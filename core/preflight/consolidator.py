#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/consolidator.py
Version: 1.2.0
Objective: Unified funnel with "Solar Veto" to scrub targets in conjunction and apply horizon masks.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from astropy.coordinates import SkyCoord, AltAz
from astropy.time import Time
import astropy.units as u

# Align with FILE_MANIFEST.md structure
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from core.preflight.gps import gps_location
from core.preflight.horizon import is_obstructed

# Data Paths
CATALOG_FILE = PROJECT_ROOT / "catalogs" / "federation_catalog.json"
OUTPUT_PLAN = PROJECT_ROOT / "data" / "tonights_plan.json"

def run_consolidated_funnel():
    print(f"--- 🌌 CONSOLIDATED FUNNEL [SOLAR VETO ACTIVE] ---")
    
    if not CATALOG_FILE.exists():
        print(f"❌ Error: {CATALOG_FILE} not found. Run librarian/purify first.")
        return

    with open(CATALOG_FILE, 'r') as f:
        catalog_data = json.load(f)
        targets = catalog_data.get("targets", [])

    # Step 1: Solar Veto & Basic Readiness
    # Removes anything flagged as too close to the sun
    filtered = [t for t in targets if not t.get('solar_conjunction', False)]
    print(f"[1] Post-Solar Veto: {len(filtered)} targets remain.")

    # Step 2: Astronomical Math Block
    loc = gps_location.get_earth_location()
    now = Time(datetime.utcnow())
    altaz_frame = AltAz(obstime=now, location=loc)
    
    tonight = []
    for t in filtered:
        # Convert degrees to Astropy SkyCoord
        coord = SkyCoord(ra=t['ra']*u.deg, dec=t['dec']*u.deg, frame='icrs')
        altaz = coord.transform_to(altaz_frame)
        alt, az = altaz.alt.degree, altaz.az.degree

        # Step 3: Horizon Veto
        # Check against physical obstructions (trees, buildings)
        # We use a 15-degree hard floor for scientific quality
        if alt > 15:
            if not is_obstructed(az, alt):
                t['current_alt'] = round(alt, 2)
                t['current_az'] = round(az, 2)
                tonight.append(t)

    print(f"[2] Post-Horizon Veto: {len(tonight)} targets accessible.")

    # Step 4: Export the Nightly Plan
    with open(OUTPUT_PLAN, 'w') as f:
        json.dump({"generated": str(now), "plan": tonight}, f, indent=4)
    
    print(f"✅ Tonights plan secured: {OUTPUT_PLAN}")

if __name__ == "__main__":
    run_consolidated_funnel()
