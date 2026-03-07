#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/consolidator.py
Version: 4.4.0
Objective: Step 4 - Calculate dark period, filter by horizon, and fully map AAVSO payload to legacy Dashboard UI schema.
"""
import json
import math
import sys
import logging
from datetime import datetime
from pathlib import Path

try:
    import ephem
except ImportError:
    print("❌ Error: 'ephem' module required. Run: pip install ephem")
    sys.exit(1)

try:
    import tomllib
except ImportError:
    import toml as tomllib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Consolidator")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.toml"
FEDERATION_CATALOG = PROJECT_ROOT / "catalogs" / "federation_catalog.json"
PLAN_FILE = PROJECT_ROOT / "data" / "tonights_plan.json"
OBSERVABLE_FILE = PROJECT_ROOT / "data" / "observable_targets.json"

def get_observatory_config():
    if not CONFIG_PATH.exists():
        logger.error(f"❌ config.toml missing at {CONFIG_PATH}")
        sys.exit(1)
    
    try:
        with open(CONFIG_PATH, "rb") as f:
            cfg = tomllib.load(f)
            
        loc = cfg.get("location")
        if not loc:
            logger.error("❌ [location] section missing in config.toml")
            sys.exit(1)
            
        return {
            "lat": str(loc["lat"]),
            "lon": str(loc["lon"]),
            "elevation": float(loc["elevation"]),
            "horizon_limit": float(loc["horizon_limit"])
        }
    except KeyError as e:
        logger.error(f"❌ CRITICAL: Missing required parameter {e} in config.toml [location]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed parsing config.toml: {e}")
        sys.exit(1)

def consolidate_plan():
    config = get_observatory_config()
    logger.info(f"🌌 STEP 4: Initializing Orbital Mechanics for GPS Location (Lat: {config['lat']}, Lon: {config['lon']})...")
    
    if not FEDERATION_CATALOG.exists():
        logger.error(f"❌ {FEDERATION_CATALOG.name} not found. Run Step 3 first.")
        sys.exit(1)

    with open(FEDERATION_CATALOG, 'r') as f:
        targets = json.load(f)

    obs = ephem.Observer()
    obs.lat = config['lat']
    obs.lon = config['lon']
    obs.elevation = config['elevation']
    obs.horizon = '-18' 

    now = ephem.now()
    obs.date = now
    
    try:
        sunset = obs.next_setting(ephem.Sun())
        obs.date = sunset
        dark_start = obs.next_setting(ephem.Sun(), use_center=True)
        obs.date = dark_start
        dark_end = obs.next_rising(ephem.Sun(), use_center=True)
    except ephem.AlwaysUpError:
        logger.error("❌ No astronomical darkness available tonight.")
        sys.exit(1)
    except ephem.NeverUpError:
        pass

    logger.info(f"🌙 Dark Window: {ephem.localtime(dark_start).strftime('%H:%M')} to {ephem.localtime(dark_end).strftime('%H:%M')}")

    flight_plan = []
    mid_darkness = ephem.Date(dark_start + (dark_end - dark_start) / 2)
    obs.date = mid_darkness

    for t in targets:
        star = ephem.FixedBody()
        star._ra = ephem.hours(str(t['ra']) if ':' in str(t['ra']) else str(float(t['ra']) * 24 / 360)) 
        star._dec = ephem.degrees(str(t['dec']))
        star.compute(obs)
        
        alt_deg = math.degrees(star.alt)
        
        if alt_deg >= config['horizon_limit']:
            # --- THE UI SCHEMA MAPPING BLOCK ---
            
            # 1. Map the name
            t['star_name'] = t.get('name', 'UNKNOWN_STAR')
            
            # 2. Map the type
            t['var_type'] = t.get('type', 'UNK')
            
            # 3. Extract the constellation (LOC) from the star name if missing
            star_parts = t['star_name'].split()
            t['constellation'] = t.get('constellation') or (star_parts[-1] if len(star_parts) > 1 else 'UNK')
            
            # 4. Map the min/max magnitudes
            t['max_mag'] = t.get('mag_max') or t.get('max_mag', '--')
            t['min_mag'] = t.get('mag_min') or t.get('min_mag', '--')
            
            # -----------------------------------
            
            t['tonight_alt'] = round(alt_deg, 1)
            flight_plan.append(t)

    flight_plan.sort(key=lambda x: x['tonight_alt'], reverse=True)

    plan_data = {
        "mission_date": ephem.localtime(now).strftime("%Y-%m-%d"),
        "darkness_start": ephem.localtime(dark_start).strftime("%H:%M:%S"),
        "darkness_end": ephem.localtime(dark_end).strftime("%H:%M:%S"),
        "total_targets": len(flight_plan),
        "targets": flight_plan
    }

    # Save to both target files to ensure UI updates
    with open(PLAN_FILE, 'w') as f:
        json.dump(plan_data, f, indent=4)
    with open(OBSERVABLE_FILE, 'w') as f:
        json.dump(plan_data, f, indent=4)

    logger.info(f"🚀 Secured: {len(flight_plan)} targets clear the {config['horizon_limit']}° horizon limit tonight.")

if __name__ == "__main__":
    consolidate_plan()
