#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/chart_fetcher.py
Version: 1.2.0
Objective: Step 2 - Cross-reference local reference_stars and fetch missing charts with a 90' FOV and Mag 15 limit.
"""
import json
import time
import requests
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("AAVSO_Step2")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = PROJECT_ROOT / "catalogs"
MASTER_HAUL_FILE = CATALOG_DIR / "aavso_master_haul.json"
REF_DIR = CATALOG_DIR / "reference_stars"

POLL_DELAY_SECONDS = 31.4

def fetch_missing_charts():
    if not MASTER_HAUL_FILE.exists():
        logger.error(f"❌ Master haul not found at {MASTER_HAUL_FILE}. Run Step 1 first.")
        sys.exit(1)
        
    with open(MASTER_HAUL_FILE, 'r') as f:
        targets = json.load(f)
        
    if not targets:
        logger.error("❌ Master haul is empty.")
        sys.exit(1)
        
    logger.info(f"📡 STEP 2: Auditing {len(targets)} targets against local reference_stars library...")
    
    api_hits = 0
    missing_count = 0
    
    for target in targets:
        star_name = target.get("name")
        if not star_name: continue
            
        safe_name = star_name.replace(" ", "_").upper()
        out_file = REF_DIR / f"{safe_name}_comps.json"
        
        # The Auditor: Check if chart is already in your reference_stars folder
        if out_file.exists():
            continue
            
        missing_count += 1
        if api_hits > 0:
            logger.info(f"⏳ Throttling: Waiting {POLL_DELAY_SECONDS}s...")
            time.sleep(POLL_DELAY_SECONDS)
            
        logger.info(f"🔭 Fetching missing Comparison Chart for {star_name} (FOV: 90')...")
        
        vsp_url = "https://apps.aavso.org/vsp/api/chart/"
        # 90 arcminute FOV injected here
        vsp_params = {
            "format": "json", 
            "star": star_name,
            "fov": 90,
            "maglimit": 15.0
        }
        
        try:
            res = requests.get(vsp_url, params=vsp_params, timeout=15)
            if res.status_code == 200:
                comps = res.json().get("photometry", [])
                with open(out_file, "w") as f:
                    json.dump(comps, f, indent=4)
                logger.info(f"✅ Cached {len(comps)} comparison stars to {out_file.name}")
            else:
                logger.warning(f"⚠️ VSP Error {res.status_code} for {star_name}: {res.text.strip()}")
        except Exception as e:
            logger.error(f"❌ Failed VSP fetch for {star_name}: {e}")
            
        api_hits += 1
        
    if missing_count == 0:
        logger.info("🎉 Vault is sealed. All comparison charts are already secured locally. Zero API calls needed.")
    else:
        logger.info(f"🏁 Step 2 Complete. Fetched {missing_count} missing charts.")

if __name__ == "__main__":
    fetch_missing_charts()
