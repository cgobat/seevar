#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/librarian.py
Version: 3.1.0
Objective: Ingest campaign_targets.json and stage it as the raw_catalog for purification.
"""

import json
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Librarian")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = PROJECT_ROOT / "catalogs"
# Pointing directly to the file you actually have
RAW_AAVSO_FILE = CATALOG_DIR / "campaign_targets.json"
STAGED_CATALOG = CATALOG_DIR / "raw_targets.json"

def ingest_aavso():
    if not RAW_AAVSO_FILE.exists():
        logger.error(f"❌ Target list not found at {RAW_AAVSO_FILE}")
        sys.exit(1)
        
    try:
        with open(RAW_AAVSO_FILE, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to parse {RAW_AAVSO_FILE}. Error: {e}")
        sys.exit(1)
        
    if not data:
        logger.error("❌ The campaign targets file is empty. Aborting.")
        sys.exit(1)
        
    with open(STAGED_CATALOG, 'w') as f:
        json.dump(data, f, indent=4)
        
    logger.info(f"✅ Librarian successfully staged {len(data)} targets to {STAGED_CATALOG}")

if __name__ == "__main__":
    ingest_aavso()
