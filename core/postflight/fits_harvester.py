#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/fits_harvester.py
Version: 1.1.0
Objective: Transfer raw FITS from Seestar's internal 'MyWorks' to the Pi's physical USB vault.
"""

import os
import shutil
import glob
from pathlib import Path

# The exact paths discovered on the S30-pro
REMOTE_MOUNT = Path(os.path.expanduser("~/seestar_organizer/s30_storage/MyWorks"))
LOCAL_BUFFER = Path("/mnt/usb_buffer/data/local_buffer")

def harvest_fits():
    print("\n📦 === FITS HARVESTER INITIATED ===")
    
    # Ensure local physical buffer exists
    LOCAL_BUFFER.mkdir(parents=True, exist_ok=True)
    
    if not REMOTE_MOUNT.exists():
        print(f"❌ FATAL: Seestar storage is not reachable at {REMOTE_MOUNT}")
        return False

    print(f"🔍 Scanning {REMOTE_MOUNT} for raw FITS data...")
    search_pattern = str(REMOTE_MOUNT / "**/*.fit*")
    
    # Grab all FITS files (in a production run, we'd filter by modified date)
    all_fits = glob.glob(search_pattern, recursive=True)
    
    if not all_fits:
        print("⚠️ No FITS files found in MyWorks. (Did the 'Save all FITS' setting get turned off?)")
        return False
        
    print(f"🎯 Found {len(all_fits)} FITS file(s). Commencing transfer to USB vault...")
    
    transferred = 0
    for file_path in all_fits:
        src = Path(file_path)
        dest = LOCAL_BUFFER / src.name
        
        # Skip if already safely in the vault
        if dest.exists() and dest.stat().st_size == src.stat().st_size:
            continue
            
        try:
            print(f"  📥 Securing: {src.name}")
            shutil.copy2(src, dest)
            transferred += 1
        except Exception as e:
            print(f"  ❌ Error copying {src.name}: {e}")

    if transferred > 0:
        print(f"✅ Harvest Complete: {transferred} new files secured to {LOCAL_BUFFER}.")
    else:
        print("✅ Vault is up to date. No new files needed transferring.")
        
    return True

if __name__ == "__main__":
    harvest_fits()
