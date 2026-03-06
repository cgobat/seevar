#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/disk_usage_monitor.py
Version: 1.0.1
Objective: Monitor S30 internal storage via SMB mount and update system state.
"""

import shutil
import json
import os
from pathlib import Path

# Path to the S30 SMB mount as defined in the Seestar Organizer structure
S30_MOUNT = Path(os.path.expanduser("~/seestar_organizer/s30_storage"))
# System state location in the physical USB buffer
STATE_FILE = Path("/mnt/usb_buffer/data/system_state.json")

def check_storage():
    print("💾 === S30 STORAGE MONITOR === 💾")
    
    if not S30_MOUNT.exists():
        print(f"❌ Error: S30 mount not found at {S30_MOUNT}")
        return

    # Get disk usage stats via shutil
    stat = shutil.disk_usage(S30_MOUNT)
    
    total_gb = stat.total / (1024**3)
    used_gb = stat.used / (1024**3)
    free_gb = stat.free / (1024**3)
    percent_used = (stat.used / stat.total) * 100

    print(f"📊 Total: {total_gb:.1f} GB | Used: {used_gb:.1f} GB | Free: {free_gb:.1f} GB")
    print(f"⚠️ Usage: {percent_used:.1f}%")

    # Update system_state.json for the Dashboard
    state = {}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        except json.JSONDecodeError:
            state = {}

    state['storage'] = {
        "total_gb": round(total_gb, 1),
        "free_gb": round(free_gb, 1),
        "percent": round(percent_used, 1),
        "status": "CRITICAL" if percent_used > 90 else "OK"
    }

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)
    
    print("✅ Dashboard state updated.")

if __name__ == "__main__":
    check_storage()
