#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/validator.py
Version: 3.1.0
Objective: Step 3 - Strictly deduplicate targets using the latest last_data_point timestamp, and validate against local comparison charts.
"""
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Validator")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = PROJECT_ROOT / "catalogs"
MASTER_HAUL = CATALOG_DIR / "aavso_master_haul.json"
REF_DIR = CATALOG_DIR / "reference_stars"
FEDERATION_CATALOG = CATALOG_DIR / "federation_catalog.json"

def validate_targets():
    if not MASTER_HAUL.exists():
        logger.error(f"❌ Master haul not found at {MASTER_HAUL}. Run Step 1.")
        return

    with open(MASTER_HAUL, 'r') as f:
        raw_targets = json.load(f)

    # 1. STRICT SCIENTIFIC DEDUPLICATION
    unique_targets_dict = {}
    duplicates = 0
    
    for t in raw_targets:
        star_name = t.get("name", "").strip()
        if not star_name:
            continue
            
        if star_name not in unique_targets_dict:
            unique_targets_dict[star_name] = t
        else:
            # A duplicate is found. Compare the 'last_data_point' timestamps.
            current_winner_time = unique_targets_dict[star_name].get("last_data_point", 0)
            contender_time = t.get("last_data_point", 0)
            
            if contender_time > current_winner_time:
                unique_targets_dict[star_name] = t # Overwrite with the newer, active data
                
            duplicates += 1

    logger.info(f"⚖️ STEP 3: Deduplicating... Found {len(unique_targets_dict)} unique stars ({duplicates} duplicates purged).")

    # 2. VALIDATION
    valid_targets = []
    dropped = 0

    for star_name, t in unique_targets_dict.items():
        safe_name = star_name.replace(" ", "_").upper()
        comp_file = REF_DIR / f"{safe_name}_comps.json"

        if comp_file.exists():
            try:
                with open(comp_file, 'r') as cf:
                    comps = json.load(cf)
                    if len(comps) > 0:
                        valid_targets.append(t)
                    else:
                        logger.warning(f"⚠️ {star_name} has an empty chart file. Dropping.")
                        dropped += 1
            except json.JSONDecodeError:
                logger.error(f"❌ {star_name} chart file is corrupted. Dropping.")
                dropped += 1
        else:
            logger.warning(f"⚠️ {star_name} is missing its comparison chart. Dropping.")
            dropped += 1

    with open(FEDERATION_CATALOG, 'w') as f:
        json.dump(valid_targets, f, indent=4)

    logger.info(f"✅ Validation Complete: {len(valid_targets)} unique targets locked into federation_catalog.json ({dropped} dropped).")

if __name__ == "__main__":
    validate_targets()
