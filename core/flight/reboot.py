#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/reboot.py
Version: 1.2.0
Objective: Resilient hardware reboot sequence with network state and API readiness verification.
"""

import time
import subprocess
import requests
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import toml as tomllib

# Standardized Paths
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "config.toml"

def load_hardware_ip():
    """Extracts the Seestar IP from config.toml."""
    try:
        if not CONFIG_PATH.exists():
            return None
        with open(CONFIG_PATH, "rb") as f:
            cfg = tomllib.load(f)
        return cfg.get("hardware", {}).get("ip_address")
    except Exception:
        return None

def ping(ip):
    """Checks if the IP is reachable on the network."""
    cmd = ["ping", "-c", "1", "-W", "1", ip]
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def trigger_reboot():
    seestar_ip = load_hardware_ip()
    if not seestar_ip:
        print("❌ Reboot aborted: IP address not found in config.toml.")
        return False

    print(f"🚀 FEDERATION REBOOT: Targeting S30 at {seestar_ip}")

    # [1/4] Send Kill Command
    # We attempt to send the 'pi_reboot' through the bridge logic
    print("[1/4] Sending pi_reboot command...")
    try:
        # Port 5432 is typically the scheduler/bridge control port
        requests.post(f"http://{seestar_ip}:5432/control", data={"command": "pi_reboot"}, timeout=3)
    except:
        pass # Disconnection is expected

    # [2/4] Wait for Offline
    print("[2/4] Waiting for hardware to drop offline", end="", flush=True)
    timeout = time.time() + 60
    while ping(seestar_ip) and time.time() < timeout:
        print(".", end="", flush=True)
        time.sleep(2)
    print(" [OFFLINE]")

    # [3/4] Wait for Online
    print("[3/4] Waiting for OS to initialize WiFi", end="", flush=True)
    timeout = time.time() + 300 # 5 minute max boot time
    while not ping(seestar_ip) and time.time() < timeout:
        print(".", end="", flush=True)
        time.sleep(2)
    
    if not ping(seestar_ip):
        print("\n❌ Error: Hardware failed to return to network.")
        return False
    print(" [ONLINE]")

    # [4/4] Wait for API Readiness
    print("[4/4] Polling Alpaca API for readiness", end="", flush=True)
    timeout = time.time() + 120
    while time.time() < timeout:
        try:
            # Check the management API version as the 'I am awake' signal
            res = requests.get(f"http://{seestar_ip}:5555/management/apiversions", timeout=2)
            if res.status_code == 200:
                print(" [READY]")
                return True
        except:
            pass
        print(".", end="", flush=True)
        time.sleep(5)
    
    print("\n⚠️ Warning: Network is up, but API is not responding yet.")
    return False

if __name__ == "__main__":
    if trigger_reboot():
        sys.exit(0)
    else:
        sys.exit(1)
