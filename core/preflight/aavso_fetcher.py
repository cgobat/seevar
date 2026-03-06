#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/aavso_fetcher.py
Version: 1.5.0
Objective: Authenticated AAVSO VSP query with local JSON caching for photometry reference.
"""

import requests
import json
import os
import tomllib
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("AAVSOFetcher")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = PROJECT_ROOT / "catalogs" / "reference_stars"

def get_api_key():
    """Retrieves target_key from the [aavso] section of the project configuration."""
    config_path = PROJECT_ROOT / "config.toml"
    if not config_path.exists():
        return None
    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("aavso", {}).get("target_key")
    except Exception:
        return None

def fetch_and_cache_comp_stars(star_name):
    """Queries AAVSO VSP and saves results to catalogs/reference_stars/."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    sanitized_name = star_name.replace(" ", "_").upper()
    cache_file = CACHE_DIR / f"{sanitized_name}_comps.json"

    logger.info(f"📡 Querying AAVSO VSP for {star_name}...")
    
    api_key = get_api_key()
    # 168 arcminutes = 2.8 degrees (S30 FOV)
    # maglimit 13.5 matches the S30's effective scientific limit
    url = f"https://www.aavso.org/apps/vsp/api/chart/?star={star_name}&fov=168&maglimit=13.5&format=json"
    
    if api_key:
        url += f"&api_key={api_key}"

    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            logger.error(f"❌ API Rejected Request: {response.status_code}")
            return False

        data = response.json()
        photometry = data.get('photometry', [])
        
        if not photometry:
            logger.warning(f"⚠️ No comparison stars found for {star_name}.")
            return False

        # Save to local cache for the photometry engine
        payload = {
            "target": star_name,
            "chart_id": data.get("chart_id"),
            "timestamp": data.get("timestamp"),
            "comparison_stars": photometry
        }

        with open(cache_file, 'w') as f:
            json.dump(payload, f, indent=4)
        
        logger.info(f"✅ Cached {len(photometry)} comparison stars to {cache_file}")
        return True

    except Exception as e:
        logger.error(f"❌ Fetch failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "CH CYG"
    fetch_and_cache_comp_stars(target)
