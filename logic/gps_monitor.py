#!/usr/bin/env python3
"""
Filename: logic/gps_monitor.py
Version: 1.3.0 (Monkel)
Objective: Monitor GPSD for a 3D fix and update volatile status.
           Strictly for v1.3 Discovery Phase.
"""

import json
import time
import os
from pathlib import Path
from gps import gps, WATCH_ENABLE

STATUS_PATH = Path("/dev/shm/env_status.json")

def update_status():
    session = gps(mode=WATCH_ENABLE)
    
    # Load existing network status from boot_audit
    try:
        with open(STATUS_PATH, "r") as f:
            status = json.load(f)
    except:
        status = {"profile": "FIELD", "gps_status": "WAITING"}

    while True:
        report = session.next()
        if getattr(report, 'mode', 0) == 3:  # 3D Fix acquired
            status["gps_status"] = "FIXED"
            status["lat"] = round(getattr(report, 'lat', 0.0), 5)
            status["lon"] = round(getattr(report, 'lon', 0.0), 5)
            status["last_update"] = time.time()
            
            with open(STATUS_PATH, "w") as f:
                json.dump(status, f)
            break
        time.sleep(2)

if __name__ == "__main__":
    update_status()
