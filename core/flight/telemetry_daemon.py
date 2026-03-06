#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/telemetry_daemon.py
Version: 1.1.0
Objective: Continuously poll Seestar hardware via Alpaca API and atomically update hardware_telemetry.json.
"""

import os
import sys
import json
import time
import requests

try:
    import tomllib
except ImportError:
    import toml as tomllib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PSV_PATH = os.path.join(BASE_DIR, "logic/seestar_dict.psv")
CONFIG_PATH = os.path.join(BASE_DIR, "config.toml")
DATA_DIR = os.path.join(BASE_DIR, "data")
TELEMETRY_FILE = os.path.join(DATA_DIR, "hardware_telemetry.json")
TMP_TELEMETRY_FILE = os.path.join(DATA_DIR, "hardware_telemetry.json.tmp")

def get_alpaca_url():
    try:
        with open(CONFIG_PATH, "rb") as f:
            cfg = tomllib.load(f)
        ip = cfg['hardware']['ip_address']
        return f"http://{ip}:5555/api/v1/telescope/0/action"
    except Exception:
        return None

def get_method_from_psv(target_command):
    try:
        with open(PSV_PATH, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 3 and parts[1].strip().lower() == target_command.lower():
                    return parts[2].split('command=')[-1].strip()
    except Exception:
        pass
    return None

def fetch_data(api_url, method_str):
    if not method_str: return None
    payload = {
        "Action": "method_sync",
        "Parameters": json.dumps({"method": method_str}),
        "ClientID": 1, "ClientTransactionID": 1
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        res = requests.put(api_url, data=payload, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get("Value", {}).get("1", {}).get("result", {})
    except Exception:
        pass
    return None

def write_atomic_state(state_dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(TMP_TELEMETRY_FILE, 'w') as f:
            json.dump(state_dict, f, indent=4)
        os.replace(TMP_TELEMETRY_FILE, TELEMETRY_FILE)
    except Exception as e:
        print(f"⚠️ Failed to write telemetry: {e}")

def main():
    api_url = get_alpaca_url()
    if not api_url:
        print("❌ Could not load bridge IP from config.")
        sys.exit(1)

    print("🚀 Telemetry Daemon (Isolated) Initialized.")
    print(f"📡 Polling {api_url} every 3 seconds...")
    print(f"💾 Updating {TELEMETRY_FILE} atomically.")

    cmd_device_state = get_method_from_psv("Action Get_Device_State")

    while True:
        state_data = fetch_data(api_url, cmd_device_state)
        current_time = time.time()

        if state_data:
            battery = state_data.get("pi_status", {}).get("battery_capacity", "N/A")
            storage_free = state_data.get("storage", {}).get("storage_volume", [{}])[0].get("free_mb", "N/A")
            
            payload = {
                "link_status": "ACTIVE",
                "battery": battery,
                "storage_mb": storage_free,
                "last_update": current_time
            }
            write_atomic_state(payload)
        else:
            payload = {
                "link_status": "OFFLINE",
                "battery": "N/A",
                "storage_mb": "N/A",
                "last_update": current_time
            }
            write_atomic_state(payload)

        time.sleep(3)

if __name__ == "__main__":
    main()
