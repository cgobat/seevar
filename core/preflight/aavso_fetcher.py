#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/aavso_fetcher.py
Version: 1.4.0
Objective: Authenticated AAVSO VSP query using S30 FOV (168 arcmin) and mandatory maglimit.
"""

import requests
import json
import os
import tomllib
from pathlib import Path

def get_api_key():
    """Retrieves target_key from the [aavso] section of the project configuration."""
    config_path = Path(os.path.expanduser("~/seestar_organizer/config.toml"))
    if not config_path.exists():
        return None
    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("aavso", {}).get("target_key")
    except Exception:
        return None

def get_comp_stars(star_name):
    print(f"📡 Querying AAVSO Database for {star_name}...")
    
    api_key = get_api_key()
    
    # 168 arcminutes = 2.8 degrees (Standard S30 FOV)
    # maglimit is mandatory for JSON output; 9.0 covers bright neighbors for Algol (Mag 2.1)
    url = f"https://www.aavso.org/apps/vsp/api/chart/?star={star_name}&fov=168&maglimit=9.0&format=json"
    
    if api_key:
        url += f"&api_key={api_key}"
        print("🔑 Authentication: [target_key] active.")

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API Rejected Request (HTTP {response.status_code})")
            print(f"📝 Server Response: {response.text}")
            return

        data = response.json()
        print(f"\n🌟 Comparison Stars for {star_name}:")
        print(f"{'Label':<6} | {'V-Mag':<6} | {'B-V':<6} | {'RA':<12} | {'DEC':<12}")
        print("-" * 55)
        
        comps = data.get('photometry', [])
        if not comps:
            print("⚠️ No comparison stars found. Try expanding FOV or check star name.")
            return

        for star in comps:
            print(f"{star.get('label','N/A'):<6} | {star.get('v','N/A'):<6} | "
                  f"{star.get('bv','N/A'):<6} | {star.get('ra','N/A'):<12} | "
                  f"{star.get('dec','N/A'):<12}")
            
    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    get_comp_stars("Algol")
