#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Objective: Fetches AAVSO comparison data using TOML auth, URL encoding, and file-locking.
Path: ~/seestar_organizer/core/preflight/fetcher.py
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import logging
import tomllib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VSP_Fetcher")

LOCK_FILE = os.path.expanduser("~/.vsp_fetcher.lock")
CONFIG_PATH = os.path.expanduser("~/seestar_organizer/config.toml")

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, 'r') as f:
            try:
                pid = int(f.read().strip())
                os.kill(pid, 0)
                return False
            except (ValueError, OSError):
                os.remove(LOCK_FILE)
    
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    return True

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        logger.error(f"❌ Config file not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)

def fetch_sequence(star_name, api_key):
    # Properly URL-encode the star name to handle '+' and spaces safely
    star_encoded = urllib.parse.quote(star_name)
    url = (
        "https://apps.aavso.org/vsp/api/chart/"
        f"?star={star_encoded}"
        f"&format=json&fov=60&maglimit=18.0"
        f"&api_key={api_key.strip()}"
    )

    req = urllib.request.Request(url)
    req.add_header("User-Agent", "SeestarOrganizer/2.6 (Contact: ed@S30-pro)")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            if not isinstance(data, dict) or "photometry" not in data:
                return False

            normalized = {
                "target": {
                    "star": data.get("star"),
                    "auid": data.get("auid"),
                    "ra_hms": data.get("ra"),
                    "dec_dms": data.get("dec")
                },
                "chart": {
                    "chart_id": data.get("chartid"),
                    "fov_arcmin": data.get("fov"),
                    "maglimit": data.get("maglimit")
                },
                "comparison_stars": data.get("photometry", [])
            }

            seq_dir = os.path.expanduser('~/seestar_organizer/data/comp_stars')
            os.makedirs(seq_dir, exist_ok=True)
            # Use safe filename replacing spaces and plus signs
            safe_filename = star_name.lower().replace(' ', '_').replace('+', '_plus_')
            save_path = os.path.join(seq_dir, f"{safe_filename}.json")

            with open(save_path, 'w') as f:
                json.dump(normalized, f, indent=4)

            logger.info(f"✅ Secured {len(normalized['comparison_stars'])} comps for {star_name}")
            return True
    except urllib.error.HTTPError as e:
        logger.error(f"❌ HTTP Error for {star_name}: {e.code} {e.reason}")
        return False
    except Exception as e:
        logger.error(f"❌ Fetch failed for {star_name}: {e}")
        return False

def run_enrichment():
    if not acquire_lock():
        logger.warning("🛑 Another fetcher is running. Exiting cleanly.")
        sys.exit(0)

    try:
        config = load_config()
        api_key = config.get("aavso", {}).get("target_key")
        
        if not api_key:
            logger.error("❌ AAVSO 'target_key' not found in config.toml! Aborting.")
            sys.exit(1)

        target_dir = os.path.expanduser('~/seestar_organizer/data')
        
        # Look for the target files dynamically
        plan_path = os.path.join(target_dir, "targets.json")
        if not os.path.exists(plan_path):
            plan_path = os.path.join(target_dir, "campaign_targets.json")
            if not os.path.exists(plan_path):
                logger.info("ℹ️ No target JSON files found. Nothing to fetch.")
                sys.exit(0)

        with open(plan_path, 'r') as f:
            campaign_data = json.load(f)
            
        # Handle both flat list and dictionary formats
        if isinstance(campaign_data, list):
            targets = campaign_data
        elif isinstance(campaign_data, dict):
            targets = campaign_data.get('targets', [])
        else:
            targets = []

        seq_dir = os.path.expanduser('~/seestar_organizer/data/comp_stars')

        for entry in targets:
            star = entry.get('star_name') or entry.get('name')
            if not star: continue
            
            safe_filename = star.lower().replace(' ', '_').replace('+', '_plus_')
            if os.path.exists(os.path.join(seq_dir, f"{safe_filename}.json")):
                continue

            if fetch_sequence(star, api_key):
                logger.info("Throttling: 31.4s sleep...")
                time.sleep(31.4)
                
    finally:
        release_lock()

if __name__ == "__main__":
    run_enrichment()
