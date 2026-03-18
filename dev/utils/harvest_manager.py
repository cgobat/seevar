#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: dev/utils/harvest_manager.py
Version: 1.3.1
Objective: SeeVar Harvester - Supports simulation data (.fit) and real FITS.
"""

import shutil
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# The 'Source' is now dynamically pointing to the active project buffer
SIM_SOURCE = PROJECT_ROOT / "data" / "local_buffer"

# The 'Destination' is your specific RAID Archive
RAID_PATH = Path("/mnt/raid1/data/AAVSO-archive")

def execute_harvest():
    if not SIM_SOURCE.exists():
        print(f"⚠️ Harvest halted: Source buffer at {SIM_SOURCE} inaccessible.")
        return

    if not RAID_PATH.exists():
        print(f"⚠️ Harvest halted: RAID archive at {RAID_PATH} inaccessible.")
        return

    (RAID_PATH / "raw").mkdir(parents=True, exist_ok=True)

    count = 0
    # Look for both .fit (sim) and .fits (real)
    for ext in ["*.fit", "*.fits"]:
        for f in SIM_SOURCE.glob(ext):
            try:
                # We use copy instead of move for simulation data 
                # so the 'Buffer of Plenty' stays full for re-runs.
                shutil.copy2(str(f), RAID_PATH / "raw" / f.name)
                count += 1
            except Exception as e:
                print(f"❌ Fail for {f.name}: {e}")

    print(f"✅ Harvest: {count} simulation files mirrored to RAID Archive.")

if __name__ == "__main__":
    execute_harvest()
