#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/librarian.py
Version: 4.2.0
Objective: The Single Source of Truth. Manages metadata, purges corruption, 
           and validates charts for the Nightly Planner.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Librarian")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = PROJECT_ROOT / "catalogs"
DATA_DIR = PROJECT_ROOT / "data"
RAW_HARVEST = CATALOG_DIR / "campaign_targets.json"
REF_DIR = CATALOG_DIR / "reference_stars"
VALIDATED_CATALOG = CATALOG_DIR / "federation_catalog.json"

def inject_metadata(data, objective):
    """Standardizes the header for all Sovereign JSON files."""
    return {
        "metadata": {
            "objective": objective,
            "generated": datetime.now().isoformat(),
            "schema_version": "2026.1"
        },
        "data": data
    }

def process_library():
    logger.info("📚 Librarian: Commencing library audit...")

    if not RAW_HARVEST.exists():
        logger.error("❌ No harvest found.")
        return

    with open(RAW_HARVEST, 'r') as f:
        raw_data = json.load(f)
        targets = raw_data.get("targets", []) if isinstance(raw_data, dict) else raw_data

    # Deduplicate and Validate
    unique_map = {t['name']: t for t in targets if 'name' in t}
    valid_targets = []
    
    for name, target in unique_map.items():
        safe_name = name.replace(" ", "_").upper()
        if (REF_DIR / f"{safe_name}_comps.json").exists():
            valid_targets.append(target)

    # Save with full metadata header
    federated_data = inject_metadata(valid_targets, "Validated and deduplicated target list for nightly planning.")
    
    with open(VALIDATED_CATALOG, 'w') as f:
        json.dump(federated_data, f, indent=4)

    logger.info(f"✅ Librarian: {len(valid_targets)} targets federated with full metadata.")

if __name__ == "__main__":
    process_library()
