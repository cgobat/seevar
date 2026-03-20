#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: dev/utils/comp_purger.py
Version: 1.1.1
Objective: Prunes orphaned comparison star charts in the SeeVar catalog.
"""

import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Janitor")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REF_DIR = PROJECT_ROOT / "catalogs" / "reference_stars"

def purge_fluff():
    if not REF_DIR.exists():
        logger.info("📂 Reference directory not found. Skipping purge.")
        return

    files = list(REF_DIR.glob("*.json"))
    purged = 0
    for f in files:
        if f.stat().st_size < 100:
            f.unlink()
            purged += 1
    
    logger.info(f"🧹 Janitor: Cleaned {purged} corrupted chart files.")

if __name__ == "__main__":
    purge_fluff()
