#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: logic/dictionary_harvester.py
Version: 1.0.0
Objective: Execute all commands in seestar_dict.psv and record the actual S30 responses.
"""

import os
import requests
import tomllib

# Absolute Paths
BASE_DIR = os.path.expanduser("~/seestar_organizer")
PSV_PATH = os.path.join(BASE_DIR, "logic/seestar_dict.psv")
CONFIG_PATH = os.path.join(BASE_DIR, "config.toml")

def get_bridge_url():
    with open(CONFIG_PATH, "rb") as f:
        cfg = tomllib.load(f)
    return f"http://{cfg['hardware']['ip_address']}:{cfg['hardware']['port']}/1/command"

def main():
    if not os.path.exists(PSV_PATH):
        print("❌ Dictionary PSV not found.")
        return

    bridge_url = get_bridge_url()
    updated_lines = []

    with open(PSV_PATH, "r") as f:
        lines = f.readlines()
        header = lines[0]
        updated_lines.append(header)

        for line in lines[1:]:
            parts = line.strip().split('|')
            if len(parts) < 3: continue
            
            category, command, payload = parts[0], parts[1], parts[2]
            # Extract the actual command string after 'command='
            cmd_string = payload.split('command=')[-1]
            
            print(f"📡 Testing: {command} ({cmd_string})...", end=" ", flush=True)
            try:
                # We use a 2-second timeout to keep the script moving
                res = requests.post(bridge_url, data={"command": cmd_string}, timeout=2)
                # Clean the response to a single line, removing HTML if present
                clean_res = res.text.replace('\n', ' ').replace('\r', '').strip()[:50]
                updated_lines.append(f"{category}|{command}|{payload}|{clean_res}\n")
                print("✅")
            except Exception as e:
                updated_lines.append(f"{category}|{command}|{payload}|ERROR: {str(e)[:20]}\n")
                print("❌")

    with open(PSV_PATH, "w") as f:
        f.writelines(updated_lines)
    print(f"\n✨ Harvesting complete. {PSV_PATH} updated with real responses.")

if __name__ == "__main__":
    main()
