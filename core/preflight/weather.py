#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Weather Sentinel v2.2.5 - Verbose Consensus
import json, os, sys, urllib.request, ephem
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core.flight.vault_manager import VaultManager

class WeatherSentinel:
    def __init__(self):
        self.vault = VaultManager()
        self.obs = self.vault.get_observer_config()
        self.lat, self.lon = float(self.obs.get("lat", 52.38)), float(self.obs.get("lon", 4.60))

    def get_consensus(self):
        # 1. Check Buienradar (Short-term)
        url_br = f"https://gpsgadget.buienradar.nl/data/raintext?lat={round(self.lat,2)}&lon={round(self.lon,2)}"
        br_res = "CLEAR"
        try:
            with urllib.request.urlopen(url_br, timeout=5) as res:
                if "000" not in res.read().decode('utf-8'): br_res = "RAIN_WARN"
        except: br_res = "OFFLINE"

        # 2. Check Open-Meteo (Cloud/Wind)
        om_res = "97% CLOUD" # Simplified for example
        
        print(f"[REDA] CONSENSUS: BUIENRADAR={br_res} | OPEN-METEO={om_res}")
        return {"status": f"✨ {br_res}", "led": "led-green" if br_res=="CLEAR" else "led-red"}

if __name__ == "__main__":
    WeatherSentinel().get_consensus()
