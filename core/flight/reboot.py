#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/reboot.py
Version: 1.1.0
Objective: Issue a hard reboot to a Seestar, monitor network state, and verify API readiness.
"""

import time
import subprocess
import requests
import os
import sys

try:
    import tomllib
except ImportError:
    import toml as tomllib # Fallback for Python < 3.11

def load_configs():
    """Extract IPs and ports from the absolute paths of the TOML files."""
    # Defining absolute paths based on your latest input
    MAIN_CONFIG = os.path.expanduser("~/seestar_organizer/config.toml")
    ALP_CONFIG = os.path.expanduser("~/seestar_alp/device/config.toml")
    
    try:
        if not os.path.exists(MAIN_CONFIG):
            raise FileNotFoundError(f"Missing Main Config: {MAIN_CONFIG}")
        if not os.path.exists(ALP_CONFIG):
            raise FileNotFoundError(f"Missing ALP Config: {ALP_CONFIG}")

        with open(MAIN_CONFIG, "rb") as f:
            main_cfg = tomllib.load(f)
        with open(ALP_CONFIG, "rb") as f:
            alp_cfg = tomllib.load(f)
            
        # Extract bridge info from organizer config
        bridge_ip = main_cfg["hardware"]["ip_address"]
        bridge_port = main_cfg["hardware"]["port"]
        
        # Extract Seestar IP from the ALP config federation list
        seestar_ip = alp_cfg["seestars"][0]["ip_address"] 
        
        return f"http://{bridge_ip}:{bridge_port}/1/command", seestar_ip
    except Exception as e:
        print(f"❌ Config parsing error: {e}")
        sys.exit(1)

def ping(host):
    """Returns True if host responds to a ping request."""
    command = ["ping", "-c", "1", "-W", "1", host]
    return subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def main():
    bridge_url, seestar_ip = load_configs()
    print(f"🚀 Initializing reboot sequence for Seestar at {seestar_ip}...")

    # [1/4] Send Kill Command
    print(f"[1/4] Sending kill command via bridge ({bridge_url})...")
    try:
        requests.post(bridge_url, data={"command": "pi_reboot"}, timeout=5)
    except requests.exceptions.RequestException:
        pass # Connection drop is expected

    # [2/4] Wait for Offline
    print("[2/4] Waiting for Seestar to drop off the network", end="", flush=True)
    while ping(seestar_ip):
        print(".", end="", flush=True)
        time.sleep(2)
    print(" [OFFLINE]")

    # [3/4] Wait for Online
    print("[3/4] Waiting for Android OS to boot and reconnect WiFi", end="", flush=True)
    while not ping(seestar_ip):
        print(".", end="", flush=True)
        time.sleep(2)
    print(" [ONLINE]")

    # [4/4] Wait for API Initialization
    print("[4/4] Waiting for Seestar Alpaca daemon to initialize", end="", flush=True)
    while True:
        try:
            res = requests.post(bridge_url, data={"command": "get_event_state"}, timeout=3)
            if "{" in res.text:
                break
        except requests.exceptions.RequestException:
            pass
        print(".", end="", flush=True)
        time.sleep(3)
    
    print(" [READY]")
    print(f"✅ Seestar {seestar_ip} is fully zeroed out and ready for operations.")

if __name__ == "__main__":
    main()
