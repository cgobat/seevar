#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/horizon.py
Version: 1.1.0
Objective: Veto targets based on local obstructions using Az/Alt mapping.
"""

import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.toml"

# Default Haarlem Obstructions (Fallback)
DEFAULT_OBSTRUCTIONS = [
    {"az_start": 150, "az_end": 210, "min_alt": 45}, # Roof obstruction
    {"az_start": 300, "az_end": 350, "min_alt": 55}, # Tree in NW
]

def load_obstructions():
    """Loads obstruction zones from config.toml or returns defaults."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "rb") as f:
                config = tomllib.load(f)
                return config.get("site", {}).get("obstructions", DEFAULT_OBSTRUCTIONS)
        except Exception:
            return DEFAULT_OBSTRUCTIONS
    return DEFAULT_OBSTRUCTIONS

def is_obstructed(az, alt):
    """
    Checks if a given Alt/Az coordinate is blocked by local terrain/buildings.
    Returns True if obstructed, False if clear.
    """
    obstructions = load_obstructions()
    for obs in obstructions:
        if obs["az_start"] <= az <= obs["az_end"]:
            if alt < obs["min_alt"]:
                return True
    
    # Global floor: No science below 15 degrees due to atmospheric extinction
    if alt < 15:
        return True
        
    return False

if __name__ == "__main__":
    # Quick Test
    test_az, test_alt = 180, 30
    result = is_obstructed(test_az, test_alt)
    print(f"🔭 Testing Az:{test_az} Alt:{test_alt} -> Obstructed: {result}")
