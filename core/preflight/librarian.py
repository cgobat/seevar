#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/librarian.py
Version: 2.2.0
Objective: Managed the conversion of raw target lists into the Federation-standard catalog.
"""

import json
import logging
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Librarian")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = PROJECT_ROOT / "catalogs"
MASTER_CATALOG = CATALOG_DIR / "federation_catalog.json"
LEGACY_TARGETS = PROJECT_ROOT / "data" / "targets.json"

def purify_to_federation():
    """
    Ensures the master catalog exists and is in the correct format.
    Migrates legacy targets.json if federation_catalog.json is missing.
    """
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info("📚 Librarian: Assessing Library Integrity...")

    targets = []

    # Check if we need to migrate from the old data/targets.json
    if not MASTER_CATALOG.exists() and LEGACY_TARGETS.exists():
        logger.warning("♻️ Master catalog missing. Migrating legacy targets.json...")
        try:
            with open(LEGACY_TARGETS, 'r') as f:
                old_data = json.load(f)
                # Handle both list-style and dict-style legacy files
                targets = old_data if isinstance(old_data, list) else old_data.get("targets", [])
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    elif MASTER_CATALOG.exists():
        with open(MASTER_CATALOG, 'r') as f:
            data = json.load(f)
            targets = data.get("targets", [])
    else:
        logger.error("❌ No source data found! Place targets.json in data/ or federation_catalog.json in catalogs/.")
        return False

    # Standardize and Clean
    clean_targets = []
    for t in targets:
        # Ensure mandatory keys exist
        if 'name' not in t and 'star_name' in t:
            t['name'] = t.pop('star_name')
        
        if 'name' in t and 'ra' in t and 'dec' in t:
            # Ensure priority and conjunction flags exist
            if 'priority' not in t: t['priority'] = False
            if 'solar_conjunction' not in t: t['solar_conjunction'] = False
            clean_targets.append(t)

    # Save the canonical version
    payload = {
        "version": "2.2.0",
        "last_updated": str(Path(MASTER_CATALOG).stat().st_mtime if MASTER_CATALOG.exists() else "NEW"),
        "targets": clean_targets
    }

    with open(MASTER_CATALOG, 'w') as f:
        json.dump(payload, f, indent=4)
    
    logger.info(f"✅ Librarian Secured: {len(clean_targets)} targets locked in {MASTER_CATALOG}")
    return True

if __name__ == "__main__":
    purify_to_federation()
