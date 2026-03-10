#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: /home/ed/seestar_organizer/utils/harvest_manager.py
Version: 1.1.2
Objective: Tiered storage management. Harvests RAW from Workspace to RAID1 Archive.
"""
import shutil
import os
from pathlib import Path

WORKSPACE = Path("/home/ed/seestar_organizer/data/local_buffer")
RAID_PATH = Path("/mnt/raid1/AAVSO-archive")

def execute_harvest():
    if not RAID_PATH.exists():
        print("⚠️ Harvest halted: RAID1 archive inaccessible.")
        return

    # Archive RAW FITS to RAID1
    for f in WORKSPACE.glob("*_Raw.fits"):
        try:
            shutil.move(str(f), RAID_PATH / "raw" / f.name)
            print(f"📦 Archived: {f.name}")
        except Exception as e: print(f"❌ Archive fail: {e}")

if __name__ == "__main__":
    execute_harvest()
