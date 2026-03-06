#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: utils/dictionary_harvester.py
Version: 2.0.0
Objective: Execute commands in seestar_dict.psv via the pure Alpaca REST API and record JSON responses.
"""

import os
import requests
import sys
import json

try:
    import tomllib
except ImportError:
    import toml as tomllib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSV_PATH = os.path.join(BASE_DIR, "logic/seestar_dict.psv")
CONFIG_PATH = os.path.join(BASE_DIR, "config.toml")

DANGEROUS_KEYWORDS = ['slew', 'goto', 'park', 'reboot', 'shutdown', 'horizon', 'move']

def get_alpaca_url():
    try:
        with open(CONFIG_PATH, "rb") as f:
            cfg = tomllib.load(f)
        # Using the dedicated Alpaca port 5555 discovered via peer intel
        # If your config still points to 5432, we override it here for the API
        ip = cfg['hardware']['ip_address']
        return f"http://{ip}:5555/api/v1/telescope/0/action"
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        sys.exit(1)

def main():
    if not os.path.exists(PSV_PATH):
        print(f"❌ Dictionary not found at {PSV_PATH}")
        return

    api_url = get_alpaca_url()
    active_mode = "--active" in sys.argv
    updated_lines = []

    print(f"📡 Alpaca Harvester started (Active Mode: {active_mode})")
    print(f"🔗 Targeting Bridge API: {api_url}")

    with open(PSV_PATH, "r") as f:
        lines = f.readlines()
        header = lines[0]
        updated_lines.append(header)

        for line in lines[1:]:
            parts = line.strip().split('|')
            if len(parts) < 4: continue
            
            category, command_name, payload, _ = parts[0], parts[1], parts[2], parts[3]
            
            # Extract the raw native method from the old payload string (command=...)
            method_str = payload.split('command=')[-1]
            
            is_dangerous = any(k in method_str.lower() or k in command_name.lower() for k in DANGEROUS_KEYWORDS)
            
            if is_dangerous and not active_mode:
                print(f"⚠️  Skipping Dangerous: {command_name} (use --active to run)")
                updated_lines.append(f"{category}|{command_name}|{payload}|SKIPPED (Dangerous)\n")
                continue

            print(f"📡 Polling: {command_name}...", end=" ", flush=True)
            
            # The Master Key Payload
            alpaca_payload = {
                "Action": "method_sync",
                "Parameters": json.dumps({"method": method_str}),
                "ClientID": 1,
                "ClientTransactionID": 1
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}

            try:
                res = requests.put(api_url, data=alpaca_payload, headers=headers, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    # Try to drill down to the actual result inside the Russian Doll
                    try:
                        inner_val = data.get("Value", {}).get("1", {}).get("result", data)
                        clean_res = json.dumps(inner_val)[:70] + "..." # Snippet for the PSV
                    except:
                        clean_res = str(data)[:70] + "..."
                        
                    updated_lines.append(f"{category}|{command_name}|{payload}|{clean_res}\n")
                    print("✅")
                else:
                    updated_lines.append(f"{category}|{command_name}|{payload}|HTTP {res.status_code}\n")
                    print(f"❌ (HTTP {res.status_code})")
            except Exception as e:
                updated_lines.append(f"{category}|{command_name}|{payload}|TIMEOUT/ERR\n")
                print("❌")

    with open(PSV_PATH, "w") as f:
        f.writelines(updated_lines)
    
    print(f"\n✨ Harvest complete. Pure JSON dictionary updated at {PSV_PATH}")

if __name__ == "__main__":
    main()
