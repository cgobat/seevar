#!/usr/bin/env python3
"""
Filename: boot_audit.py
Version: 1.3.0 (Monkel)
Objective: Audit network. Trigger AP fallback if 'Home' is missing.
"""

import subprocess
import json
from pathlib import Path

STATUS_PATH = Path("/dev/shm/env_status.json")
HOME_SSID = "Ziggo" # Hardcoded for current operator

def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def is_home_wifi():
    res = run_cmd(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"])
    return f"yes:{HOME_SSID}" in res.stdout

def trigger_ap():
    """Fallback to Access Point mode if home/known networks fail."""
    # Hardcoded AP setup for field access
    run_cmd(["nmcli", "con", "up", "Seestar_Sentry_AP"]) 

def run_audit():
    home_present = is_home_wifi()
    
    status = {
        "profile": "HOME" if home_present else "FIELD",
        "nas_reachable": False,
        "storage_mode": "PRIMARY" if home_present else "LIFEBOAT"
    }

    if not home_present:
        trigger_ap()
    else:
        # Quick ping to verify NAS at home
        nas = run_cmd(["ping", "-c", "1", "192.168.178.55"])
        status["nas_reachable"] = (nas.returncode == 0)

    with open(STATUS_PATH, "w") as f:
        json.dump(status, f)

if __name__ == "__main__":
    run_audit()
