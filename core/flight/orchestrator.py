#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/orchestrator.py
Version: 2.1.0
Objective: Upload the mission JSON and trigger the state machine from a verified Zero-State.
"""

import requests
import sys
import json
from pathlib import Path

# Structural path resolution
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

# Import sibling flight module
try:
    from core.flight.neutralizer import enforce_zero_state
except ImportError:
    # Fallback if running in a way that namespaces differ
    from neutralizer import enforce_zero_state

PLAN_FILE = PROJECT_ROOT / "data" / "tonights_plan.json"
BRIDGE_URL = "http://127.0.0.1:5432/1/schedule"

def launch():
    print("🚀 S30-PRO FEDERATION: INITIATING LAUNCH SEQUENCE")
    
    # 1. Verification
    if not PLAN_FILE.exists():
        print(f"❌ Error: Mission plan missing at {PLAN_FILE}. Run Consolidator first.")
        return False

    # 2. Guarantee the blank canvas (Neutralizer)
    if not enforce_zero_state():
        print("❌ Flight aborted: Hardware refused to reach Zero-State.")
        return False
        
    # 3. Upload the payload
    print(f"📤 Uploading {PLAN_FILE.name} to the Schedule Bridge...")
    try:
        with open(PLAN_FILE, 'rb') as f:
            res = requests.post(f"{BRIDGE_URL}/upload", files={'schedule_file': f}, timeout=10)
            
        if res.status_code == 200:
            # 4. Pull the trigger
            print("🔥 Ignition: Toggling Bridge State to WORKING...")
            requests.post(f"{BRIDGE_URL}/state", data={"action": "toggle"}, timeout=5)
            print("✨ S30-PRO is in flight! Monitoring mission progress now.")
            return True
        else:
            print(f"❌ Upload failed. Bridge responded with HTTP {res.status_code}")
            return False
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        return False

if __name__ == "__main__":
    if launch():
        sys.exit(0)
    else:
        sys.exit(1)
