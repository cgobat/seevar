#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/nightly_planner.py
Version: 2.2.0
Objective: Executes the 6-step filtering funnel with real-time Alt/Az visibility verification.
"""

import json, sys
from pathlib import Path
from datetime import datetime
from astropy.coordinates import SkyCoord, AltAz
from astropy.time import Time
import astropy.units as u

# Project Setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Internal Logic Imports
from core.preflight.gps import gps_location
from core.preflight.horizon import is_obstructed

# Path Configuration
DATA_DIR = PROJECT_ROOT / "data"
CATALOG_DIR = PROJECT_ROOT / "catalogs"
RAW_HARVEST = CATALOG_DIR / "campaign_targets.json"
OUTPUT_PLAN = DATA_DIR / "tonights_plan.json"

def run_funnel():
    print(f"--- 🌌 INITIATING NIGHTLY TRIAGE ---")
    
    # 1. Load Raw Harvest
    if not RAW_HARVEST.exists():
        print("❌ Error: Raw harvest missing. Run Librarian first.")
        return
    with open(RAW_HARVEST, 'r') as f:
        raw_targets = json.load(f).get("targets", [])
    print(f"[1] Raw targets in library: {len(raw_targets)}")

    # 2 & 3. Assets Check & Pathing
    valid_assets = []
    comp_dir = CATALOG_DIR / "comp_stars"
    for t in raw_targets:
        comp_file = comp_dir / f"{t['star_name'].lower().replace(' ', '_')}.json"
        if comp_file.exists():
            valid_assets.append(t)
    print(f"[2/3] Targets with valid catalog assets: {len(valid_assets)}")

    # 4 & 5. Visibility & Horizon Veto
    loc = gps_location.get_earth_location()
    now = Time(datetime.utcnow())
    altaz_frame = AltAz(obstime=now, location=loc)
    
    tonight = []
    for t in valid_assets:
        coord = SkyCoord(ra=t['ra']*u.deg, dec=t['dec']*u.deg, frame='icrs')
        altaz = coord.transform_to(altaz_frame)
        
        alt = altaz.alt.deg
        az = altaz.az.deg
        
        # Veto 1: Below 30 degree baseline
        if alt < 30: continue
        
        # Veto 2: Local obstructions (Roof/Trees)
        if is_obstructed(az, alt): continue
        
        t['current_alt'] = round(alt, 2)
        tonight.append(t)
    
    print(f"[4/5] Targets above 30° and clear of obstructions: {len(tonight)}")

    # 6. Final Flight Plan Generation
    plan = {
        "generated_at": datetime.now().isoformat(),
        "count": len(tonight),
        "targets": tonight[:15] # Initial triage limit
    }

    with open(OUTPUT_PLAN, 'w') as f:
        json.dump(plan, f, indent=4)
    
    print(f"[6] SUCCESS: {OUTPUT_PLAN.name} generated. Funnel complete.")

if __name__ == "__main__":
    run_funnel()
