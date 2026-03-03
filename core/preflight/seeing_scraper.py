#!/usr/bin/env python3
import urllib.request
import re
import json
import os
import sys
from pathlib import Path

# Locate the Vault
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core.flight.vault_manager import VaultManager

CACHE_PATH = os.path.expanduser("~/seestar_organizer/core/flight/data/seeing_cache.json")

def scrape_seeing():
    vault = VaultManager()
    obs = vault.get_observer_config()
    lat, lon = obs.get("lat", 52.38), obs.get("lon", 4.60)
    
    # Construct URL based on Vault Location
    url = f"https://www.meteoblue.com/en/weather/outdoorsports/seeing/{lat}N{lon}E"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SeestarFederation/2.0'}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # Extract Seeing (Arcsec) - Looking for patterns like "1.24" or "0.85"
            arcsec_match = re.search(r'(\d+\.\d+)"', html)
            arcsec = arcsec_match.group(1) if arcsec_match else "N/A"
            
            # Simplified transparency logic for the dash
            transparency = "CLEAR" if float(arcsec) < 1.5 else "HAZY"
            
            data = {
                "arcsec": arcsec,
                "transparency": transparency,
                "timestamp": int(os.path.getmtime(CACHE_PATH)) if os.path.exists(CACHE_PATH) else 0
            }
            
            with open(CACHE_PATH, 'w') as f:
                json.dump(data, f)
            return data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(json.dumps(scrape_seeing(), indent=2))
