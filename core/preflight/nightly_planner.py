#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/nightly_planner.py
Version: 1.2.1 (Hardened)
Objective: Fixed Dusk/Dawn budget calculation for late-night runs.
"""

import os
import json
import toml
import ephem
import logging
import math
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NightlyPlanner")

def load_config():
    with open(os.path.expanduser("~/seestar_organizer/config.toml"), 'r') as f:
        return toml.load(f)

def is_due(target, now_date):
    last = target.get('last_observed')
    if not last: return True
    last_dt = datetime.strptime(last, "%Y-%m-%d")
    cadence = target.get('cadence_days', 1)
    return (now_date - last_dt).days >= cadence

def execute_planning():
    config = load_config()
    loc = config['location']
    
    obs = ephem.Observer()
    obs.lat, obs.lon = str(loc.get('lat', 52.38)), str(loc.get('lon', 4.64))
    obs.date = datetime.now(timezone.utc)
    obs.horizon = str(config.get('planner', {}).get('sun_altitude_limit', -18.0))
    
    # FIX: Ensure dusk is always the start of the current darkness window
    sun = ephem.Sun()
    sun.compute(obs)
    if float(sun.alt) < -0.314: # Sun is already below horizon (approx -18 deg)
        dusk = obs.previous_setting(ephem.Sun(), use_center=True)
    else:
        dusk = obs.next_setting(ephem.Sun(), use_center=True)
    
    dawn = obs.next_rising(ephem.Sun(), use_center=True)
    
    # Calculate budget (Seconds between dusk and dawn, minus 1 hour buffer)
    budget_sec = int((dawn - dusk) * 86400) - 3600
    
    if budget_sec <= 0:
        logger.warning("⚠️ Budget calculation failed or sun is up. Check coordinates/time.")
        return

    data_dir = os.path.expanduser(config['storage'].get('target_dir', '~/seestar_organizer/data'))
    targets_path = os.path.join(data_dir, "targets.json")
    
    if not os.path.exists(targets_path):
        logger.error(f"❌ Targets file missing: {targets_path}")
        return

    with open(targets_path, 'r') as f:
        targets = json.load(f)

    now_date = datetime.now()
    due_targets = [t for t in targets if is_due(t, now_date)]
    
    logger.info(f"📊 Filtering: {len(targets)} total -> {len(due_targets)} due. Budget: {budget_sec/3600:.1f}h")

    obs.date = obs.date # Use current time for real-time altitude check
    final_candidates = []
    for t in due_targets:
        star = ephem.FixedBody()
        star._ra = ephem.hours(t.get('ra', 0) / 15.0)
        star._dec = ephem.degrees(t.get('dec', 0))
        star.compute(obs)
        
        alt = float(star.alt) * 180.0 / math.pi
        if alt < loc.get('horizon_limit', 30.0): continue

        airmass = 1.0 / math.cos((90 - alt) * math.pi / 180.0)
        score = (2000 if t.get('priority') else 0) + (100 / airmass)
        final_candidates.append({**t, "score": score, "airmass": round(airmass, 2)})

    final_candidates.sort(key=lambda x: x['score'], reverse=True)
    plan = []
    remaining = budget_sec
    
    for c in final_candidates:
        if remaining <= 0: break
        slot_sec = 600 # 10 minute block
        plan.append({
            "name": c.get('star_name', 'Unknown'),
            "ra": c.get('ra'), "dec": c.get('dec'),
            "exposure_sec": 60, "frames": 4,
            "airmass": c['airmass']
        })
        remaining -= slot_sec

    with open(os.path.join(data_dir, "tonights_plan.json"), 'w') as f:
        json.dump(plan, f, indent=4)
    
    logger.info(f"✅ Created plan with {len(plan)} targets.")

if __name__ == "__main__":
    execute_planning()
