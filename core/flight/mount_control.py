#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/mount_control.py
Version: 1.5.0
Objective: Centralized mount controller for coordinate retrieval and target acquisition.
"""

import json
import requests
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("MountControl")

BRIDGE_URL = "http://127.0.0.1:5555/api/v1/telescope/1/action"

def _call_bridge(method, params=None):
    """Internal helper for Alpaca JSON-RPC communication."""
    payload = {
        "Action": "method_sync",
        "Parameters": json.dumps({"method": method, **(params or {})}),
        "ClientID": 999,
        "ClientTransactionID": int(time.time())
    }
    try:
        response = requests.put(BRIDGE_URL, data=payload, timeout=5)
        if response.status_code != 200:
            return None
        
        data = response.json()
        val = data.get("Value")
        if isinstance(val, str):
            val = json.loads(val)
        return val.get("result") if val else None
    except Exception as e:
        logger.debug(f"Bridge call failed: {e}")
        return None

def get_mount_coords():
    """Retrieves current equatorial coordinates."""
    res = _call_bridge("scope_get_equ_coord")
    if res:
        return {"ra": res.get("ra"), "dec": res.get("dec")}
    return None

def slew_to_target(ra, dec):
    """Commands the mount to slew to specific J2000 coordinates."""
    logger.info(f"🔭 Slew Initiated: RA {ra:.4f} | DEC {dec:.4f}")
    # Note: S30 internal engine usually expects 'iscope_start_view' or 'scope_goto'
    params = {"ra": ra, "dec": dec, "lp": 0} 
    res = _call_bridge("scope_goto", params)
    return res is not None

def is_tracking():
    """Checks if the mount is currently tracking."""
    res = _call_bridge("get_setting")
    if res:
        return res.get("is_tracking", False)
    return False

if __name__ == "__main__":
    coords = get_mount_coords()
    if coords and coords.get("ra") is not None:
        logger.info(f"✨ Orientation Secured: RA {coords['ra']:.4f} | DEC {coords['dec']:.4f}")
    else:
        logger.warning("⚠️ Mount orientation unavailable.")
