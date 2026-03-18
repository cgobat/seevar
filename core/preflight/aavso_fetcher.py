#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/aavso_fetcher.py
Version: 1.6.1
Objective: Step 1 - Haul scientific targets from AAVSO Target Tool API and append strict CADENCE.md sampling rules.
"""

import json
import requests
import sys
import logging
import tomllib
from datetime import datetime
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("AAVSO_Step1")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.toml"
CATALOG_DIR = PROJECT_ROOT / "catalogs"
MASTER_HAUL_FILE = CATALOG_DIR / "campaign_targets.json"

MAG_LIMIT = 15.0
MIN_DEC = -7.62

def get_aavso_key():
    try:
        with open(CONFIG_PATH, "rb") as f:
            cfg = tomllib.load(f)
        return cfg.get("aavso", {}).get("target_key")
    except Exception:
        logger.error("❌ Failed to read target_key from config.toml")
        sys.exit(1)

def haul_and_filter(api_key):
    logger.info("📡 STEP 1: Connecting to AAVSO Target API...")
    url = f"https://filter.aavso.org/api/v1/targets?apikey={api_key}&obs_section=all"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        raw_targets = response.json()
        logger.info(f"📥 Retrieved {len(raw_targets)} raw targets.")

        targets = []
        for t in raw_targets:
            try:
                mag = float(t.get('max_mag', 0))
            except (ValueError, TypeError):
                continue
                
            if mag > MAG_LIMIT:
                continue
                
            if float(t.get('dec', -90)) < MIN_DEC:
                continue

            var_type = str(t.get('type', '')).upper()
            
            # Match DAILY_TYPES from ledger_manager.py
            if any(x in var_type for x in ['CV', 'UG', 'UGSS', 'RR', 'NA', 'NB', 'NC', 'NR', 'ZAND']):
                rec_cadence = 1
            else:
                rec_cadence = 3

            targets.append({
                "name": t['name'],
                "ra": float(t['ra']),
                "dec": float(t['dec']),
                "type": var_type,
                "max_mag": mag,
                "recommended_cadence_days": rec_cadence,
                "priority": 2,
                "duration": 600
            })

        seen = {}
        for t in targets:
            canon = re.sub(r' V0+(\d)', r'V \1', t['name'])
            t['name'] = canon
            seen[canon] = t
            
        targets = list(seen.values())
        logger.info(f"  → After dedup + name normalisation: {len(targets)} unique targets")

        output_data = {
            "#objective": "Master haul of AAVSO targets filtered by local horizon and assigned CADENCE.md rules.",
            "metadata": {
                "generated": datetime.now().isoformat(),
                "schema_version": "2026.1",
                "source": "AAVSO Target Tool API",
                "target_count": len(targets)
            },
            "targets": targets
        }

        with open(MASTER_HAUL_FILE, "w") as f:
            json.dump(output_data, f, indent=4)

        logger.info(f"✅ Target Base Secured: {len(targets)} scientifically observable targets locked.")

    except Exception as e:
        logger.error(f"❌ Failed to fetch or filter targets: {e}")
        sys.exit(1)

if __name__ == "__main__":
    key = get_aavso_key()
    haul_and_filter(key)
