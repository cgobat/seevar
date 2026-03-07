#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/hardware_profiles.py
Version: 1.1.0
Objective: Define hardware specs for the Federation fleet (Williamina, Annie, Henrietta).
"""

PROFILES = {
    "WILLIAMINA": {
        "model": "S30-Pro",
        "sensor": "IMX585",
        "fov_arcmin": 168,  # Standard S30-Pro FOV
        "bayer": "GRBG",
        "specialty": "High-precision Photometry",
        "max_gain": 80
    },
    "ANNIE": {
        "model": "S50",
        "sensor": "IMX462",
        "fov_arcmin": 110,  # Standard S50 FOV
        "bayer": "RGGB",
        "specialty": "Spectroscopy",
        "max_gain": 100
    },
    "HENRIETTA": {
        "model": "S30-Pro",
        "sensor": "IMX585",
        "fov_arcmin": 168,
        "bayer": "GRBG",
        "specialty": "Rapid-cadence Photometry",
        "max_gain": 80
    }
}

def get_active_profile(nickname="WILLIAMINA"):
    """Returns the technical specs for the specified telescope."""
    return PROFILES.get(nickname.upper(), PROFILES["WILLIAMINA"])

if __name__ == "__main__":
    p = get_active_profile("Williamina")
    print(f"🔭 Active Unit: {p['model']} ({p['sensor']}) - Optimized for {p['specialty']}")
