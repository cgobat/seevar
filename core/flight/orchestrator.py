#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/orchestrator.py
Version: 2.0.0
Objective: Upload the mission JSON and trigger the state machine from a verified Zero-State.
"""

import requests
import sys
from neutralizer import enforce_zero_state

def launch(target_json):
    # 1. Guarantee the blank canvas
    if not enforce_zero_state():
        print("❌ Flight aborted. Cannot achieve Zero-State.")
        sys.exit(1)
        
    # 2. Upload the payload
    print(f"📤 Uploading {target_json} to the Schedule Bridge...")
    try:
        with open(target_json, 'rb') as f:
            res = requests.post("http://127.0.0.1:5432/1/schedule/upload", files={'schedule_file': f})
            
        if res.status_code == 200:
            # 3. Pull the trigger
            print("🔥 Ignition: Toggling State to WORKING...")
            requests.post("http://127.0.0.1:5432/1/schedule/state", data={"action": "toggle"})
            print("🚀 S30-PRO is in flight! The Startup Sequence has begun.")
        else:
            print(f"❌ Upload failed. Bridge responded: {res.status_code}")
    except Exception as e:
        print(f"❌ Execution failed: {e}")

if __name__ == "__main__":
    # Pointing to the AAVSO target we built earlier
    launch("/home/ed/seestar_organizer/tests/ch-cyg.json")
