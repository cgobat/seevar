#!/usr/bin/env python3
"""
Filename: main.py
Version: 1.3.0 (Monkel)
Objective: The Kwetal Sentry. State-aware daemon that respects 
           environmental gates (Network & GPS).
"""

import time
import json
from pathlib import Path

# Volatile RAM storage established in boot_audit.py
STATUS_PATH = Path("/dev/shm/env_status.json")

def get_system_state():
    try:
        with open(STATUS_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default fallback if audit hasn't finished
        return {"profile": "UNKNOWN", "gps_status": "WAITING"}

def main_loop():
    print("--- Kwetal Sentry v1.3.0 Active ---")
    
    while True:
        state = get_system_state()
        profile = state.get("profile", "FIELD")
        gps_fixed = (state.get("gps_status") == "FIXED")

        # THE HARD GATE: If in Field mode, we require a GPS fix to proceed.
        if profile == "FIELD" and not gps_fixed:
            # Standby mode. Do not initiate Preflight.
            time.sleep(10)
            continue

        # Logic for HOME or FIELD+FIXED goes here
        # run_preflight(state)
        
        time.sleep(5)

if __name__ == "__main__":
    main_loop()
