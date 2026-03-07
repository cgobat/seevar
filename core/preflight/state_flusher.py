#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/state_flusher.py
Version: 1.0.0
Objective: Preflight utility to flush stale system state and reset the dashboard to IDLE before a new flight.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("StateFlusher")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = PROJECT_ROOT / "data" / "system_state.json"

def flush_state():
    logger.info("🧹 Sweeping stale telemetry from system_state.json...")
    
    # Safe default idle state
    clean_state = {
        "state": "IDLE",
        "sub": "STANDBY",
        "msg": "Preflight complete. Awaiting Flight Controller...",
        "flight_log": ["✅ Preflight pipeline executed.", "⏳ Standing by for nightfall..."],
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Added the Date!
        "storage": {
            "total_gb": 0.0,
            "free_gb": 0.0,
            "percent": 0.0,
            "status": "UNKNOWN"
        }
    }
    
    with open(STATE_FILE, "w") as f:
        json.dump(clean_state, f, indent=4)
        
    logger.info("✅ Pipe flushed. Dashboard should now read IDLE.")

if __name__ == "__main__":
    flush_state()
