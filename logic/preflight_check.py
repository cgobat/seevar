#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: logic/preflight_check.py
Version: 1.0.0
Objective: Validates hardware readiness (leveling, battery, and sync) for automation.
"""

import sys
from core_api import SeestarAPI

def run_preflight():
    api = SeestarAPI()
    state = api.get_state()
    
    if state.get("ErrorNumber") != 0:
        print("CRITICAL: Cannot communicate with seestar.service.")
        sys.exit(1)

    v = state["Value"]["result"]
    checks_passed = True

    print("--- Seestar Preflight Readiness Check ---")

    # 1. Leveling Check (Balance Sensor)
    level_angle = v.get("balance_sensor", {}).get("data", {}).get("angle", 99)
    if level_angle < 3.0:
        print(f"[PASS] Leveling: {level_angle}° (Optimal)")
    else:
        print(f"[FAIL] Leveling: {level_angle}° (Mount must be below 3.0°)")
        checks_passed = False

    # 2. Battery Check
    battery = v.get("pi_status", {}).get("battery_capacity", 0)
    if battery > 20:
        print(f"[PASS] Battery: {battery}%")
    else:
        print(f"[FAIL] Battery: {battery}% (Insufficient for automation)")
        checks_passed = False

    # 3. Storage Check
    disk_used = v.get("storage", {}).get("storage_volume", [{}])[0].get("used_percent", 100)
    if disk_used < 95:
        print(f"[PASS] Storage: {disk_used}% used")
    else:
        print(f"[FAIL] Storage: {disk_used}% used (Disk nearly full)")
        checks_passed = False

    # 4. Service Verification (SSC Logic)
    verified = v.get("device", {}).get("is_verified", False)
    if verified:
        print("[PASS] Service: Firmware Verified")
    else:
        print("[FAIL] Service: Firmware Not Verified")
        checks_passed = False

    print("-----------------------------------------")
    if checks_passed:
        print("RESULT: Telescope is READY for automation.")
        sys.exit(0)
    else:
        print("RESULT: Preflight FAILED. Correct issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    run_preflight()
