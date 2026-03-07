#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/flight-to-post-handover.py
Version: 1.2.0
Objective: Passive bridge between flight execution and post-processing. Manages harvest and ledger updates.
"""

import sys
import logging
import json
from datetime import datetime
from pathlib import Path

# Structural path resolution
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from core.flight.filesystem_control import harvest_latest_images
from core.flight.neutralizer import enforce_zero_state

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Handover")

LEDGER_PATH = PROJECT_ROOT / "data" / "ledger.json"

def process_handover(shutdown_after=True):
    logger.info("🏁 MISSION COMPLETE: Initiating Handover Sequence...")

    # 1. Harvest the Data
    # Move files from S30 eMMC to local /images
    new_files = harvest_latest_images(purge=False) # Keep on S30 for now as backup
    logger.info(f"🚚 Harvested {len(new_files)} new files for processing.")

    # 2. Update the Ledger
    # This prevents the Audit script from scheduling these targets tomorrow
    if new_files:
        try:
            with open(LEDGER_PATH, 'r') as f:
                ledger = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            ledger = []

        # Simple entry for the night's success
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "event": "Mission Handover",
            "files_count": len(new_files),
            "status": "SUCCESS"
        }
        ledger.append(entry)

        with open(LEDGER_PATH, 'w') as f:
            json.dump(ledger, f, indent=4)
        logger.info("📒 Ledger updated with mission success.")

    # 3. Secure the Hardware
    if shutdown_after:
        logger.info("🔋 Battery Preservation: Neutralizing and Parking...")
        enforce_zero_state()
        # If we had a direct 'poweroff' RPC, we would call it here.
        # For now, Parking is the safest 'low-power' state.

    logger.info("✨ Handover Complete. Post-processing can now begin.")
    return True

if __name__ == "__main__":
    process_handover(shutdown_after=True)
