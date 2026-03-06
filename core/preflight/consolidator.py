#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/consolidator.py
Version: 1.1.0
Objective: Unified funnel with "Solar Veto" to scrub targets in conjunction.
"""

import json, sys, os, time
from pathlib import Path
from datetime import datetime, timedelta
from astropy.coordinates import SkyCoord, AltAz
from astropy.time import Time
import astropy.units as u

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.preflight.gps import gps_location
from core.preflight.horizon import is_obstructed

DATA_DIR = PROJECT_ROOT / "data"
CATALOG_DIR = PROJECT_ROOT / "catalogs"
RAW_HARVEST = CATALOG_DIR / "campaign_targets.json"
LEDGER_FILE = DATA_DIR / "ledger.json"
OUTPUT_PLAN = DATA_DIR / "tonights_plan.json"

def run_consolidated_funnel():
    print(f"--- 🌌 CONSOLIDATED FUNNEL [SOLAR VETO ACTIVE] ---")
    
    if not RAW_HARVEST.exists(): return
    with open(RAW_HARVEST, 'r') as f:
        targets = json.load(f).get("targets", [])

    # Step 1: Solar & Cadence Filters
    #
    filtered = [t for t in targets if not t.get('solar_conjunction', False)]
    print(f"[1] Post-Solar Veto: {len(filtered)}")

    # Step 2: Math Block
    loc = gps_location.get_earth_location()
    altaz_frame = AltAz(obstime=Time(datetime.now()), location=loc)
    
    tonight = []
    for t in filtered:
        coord = SkyCoord(ra=t['ra']*u.deg, dec=t['dec']*u.deg, frame='icrs')
        altaz = coord.transform_to(altaz_frame)
        alt, az = altaz.alt.deg, altaz.az.deg
        
        if alt >= 30 and not is_obstructed(az, alt):
            t['current_alt'] = round(alt, 2)
            tonight.append(t)
    
    with open(OUTPUT_PLAN, 'w') as f:
        json.dump(tonight[:20], f, indent=4)
    print(f"[SUCCESS] {len(tonight)} targets ready.")

if __name__ == "__main__":
    run_consolidated_funnel()
