#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Weather Sentinel (v1.5.6) - Vampire Threshold
import json, os, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
from core.flight.vault_manager import VaultManager

class WeatherSentinel:
    def __init__(self):
        self.vault = VaultManager()
        self.seeing_cache = PROJECT_ROOT / "core/flight/data/seeing_cache.json"

    def get_consensus(self):
        # Default to safe, then check "Vampire" requirements
        transparency = "UNKNOWN"
        if self.seeing_cache.exists():
            with open(self.seeing_cache, 'r') as f:
                transparency = json.load(f).get("transparency", "AVERAGE")

        # THE VAMPIRE THRESHOLD
        # Critical targets require 'EXCELLENT' or 'GOOD' transparency
        is_excellent = transparency in ["EXCELLENT", "GOOD"]
        
        print(f"--- [REDA] SKY AUDIT: {transparency} ---")
        status = "PROCEED" if is_excellent else "SCRUBBED (LOW TRANS)"
        return {"status": status, "led": "led-green" if is_excellent else "led-red"}

if __name__ == "__main__":
    print(json.dumps(WeatherSentinel().get_consensus()))
