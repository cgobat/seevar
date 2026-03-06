#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/focuser_control.py
Version: 1.1.0
Objective: Interrogate the focuser position and manage the Auto Focus routine.
"""

import os
import sys
import json
import argparse
import requests

try:
    import tomllib
except ImportError:
    import toml as tomllib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PSV_PATH = os.path.join(BASE_DIR, "logic/seestar_dict.psv")
CONFIG_PATH = os.path.join(BASE_DIR, "config.toml")

def get_alpaca_url():
    try:
        with open(CONFIG_PATH, "rb") as f:
            cfg = tomllib.load(f)
        ip = cfg['hardware']['ip_address']
        return f"http://{ip}:5555/api/v1/telescope/0/action"
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        sys.exit(1)

def get_method_from_psv(target_command):
    if not os.path.exists(PSV_PATH):
        print(f"❌ Dictionary not found at {PSV_PATH}")
        sys.exit(1)
        
    try:
        with open(PSV_PATH, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 3 and parts[1].strip().lower() == target_command.lower():
                    return parts[2].split('command=')[-1].strip()
    except Exception:
        pass
    return None

def execute_native_command(api_url, method_str, params=None):
    if not method_str: return False, "No method string provided."

    internal_payload = {"method": method_str}
    if params: internal_payload["params"] = params

    alpaca_payload = {
        "Action": "method_sync",
        "Parameters": json.dumps(internal_payload),
        "ClientID": 1, "ClientTransactionID": 1
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        res = requests.put(api_url, data=alpaca_payload, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            inner_result = data.get("Value", {}).get("1", {}).get("result", {})
            return True, inner_result
        return False, f"HTTP {res.status_code}"
    except Exception as e:
        return False, f"Connection Error: {e}"

def main():
    parser = argparse.ArgumentParser(description="S30-PRO Federation Focuser Control")
    parser.add_argument("--auto", action="store_true", help="WARNING: Trigger the Auto Focus routine (Requires stars).")
    args = parser.parse_args()

    api_url = get_alpaca_url()
    print("🚀 Initiating Focuser Hardware Interrogation...")

    cmd_get = get_method_from_psv("Action Get_Focuser_Position")

    # 1. Get current position
    print(f"📡 Querying current focal step...")
    success, initial_pos = execute_native_command(api_url, cmd_get)
    
    if not success or not isinstance(initial_pos, int):
        print(f"❌ Failed to retrieve focuser position: {initial_pos}")
        sys.exit(1)

    print(f"✅ Focuser is currently at step: {initial_pos}")

    # 2. Handle Auto Focus (Only if explicitly requested)
    if args.auto:
        print("\n⚠️ Initiating Auto Focus Routine...")
        cmd_auto = get_method_from_psv("Action Start_Auto_Focus")
        success, res = execute_native_command(api_url, cmd_auto)
        if success:
            print(f"✅ Auto Focus triggered (Response: {res}). Motor is now hunting.")
        else:
            print(f"❌ Failed to trigger Auto Focus: {res}")
    else:
        print("\n✨ Interrogation complete. (Run with --auto when under the stars to trigger focusing).")

if __name__ == "__main__":
    main()
