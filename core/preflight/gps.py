#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/gps.py
Version: 1.2.0
Objective: Bi-directional GPS provider. Reads from and writes hardware coordinates to config.toml.
"""

import tomllib
import logging
import sys
from pathlib import Path
from astropy.coordinates import EarthLocation
import astropy.units as u

# Align with structure for VaultManager access
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from core.flight.vault_manager import VaultManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("GPSProvider")

class GPSLocation:
    def __init__(self):
        self.vault = VaultManager()
        self._refresh_local_cache()

    def _refresh_local_cache(self):
        """Syncs internal variables with current Vault data."""
        cfg = self.vault.get_observer_config()
        self.lat = cfg.get('lat', 52.3874)
        self.lon = cfg.get('lon', 4.6462)
        self.height = cfg.get('elevation', 0.0)

    def update_config(self, lat, lon, height=None, maidenhead=None):
        """Writes new hardware coordinates back to config.toml."""
        logger.info(f"🛰️ Synchronizing hardware GPS to config: {lat}, {lon}")
        
        # Use vault_manager's sync method to handle the TOML writing
        # Note: sync_gps in vault_manager 1.2.0 expects (lat, lon, maidenhead)
        self.vault.sync_gps(lat, lon, maidenhead or "AUTO")
        
        # Reload cache to ensure get_earth_location is accurate
        self._refresh_local_cache()

    def get_earth_location(self):
        """Returns an Astropy EarthLocation object for astronomical math."""
        return EarthLocation(
            lat=self.lat * u.deg, 
            lon=self.lon * u.deg, 
            height=self.height * u.m
        )

# Global instance
gps_location = GPSLocation()

if __name__ == "__main__":
    # Test read
    loc = gps_location.get_earth_location()
    print(f"🌍 Current Federation Reference: {loc.geodetic}")
