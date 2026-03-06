#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/mount_control.py
Version: 1.4.3
Objective: Secure mount orientation by parsing nested JSON-RPC responses from the Alpaca bridge.
"""

import os
import sys
import json
import requests
import time

# The Alpaca bridge on port 5555 is the verified source for 'Value' nested responses.
# Index /1/ is designated for the S30.
BRIDGE_URL = "http://127.0.0.1:5555/api/v1/telescope/1/action"

def get_mount_coords():
    """Interrogates the Alpaca bridge for equatorial coordinates via native method_sync."""
    payload = {
        "Action": "method_sync",
        "Parameters": json.dumps({"method": "scope_get_equ_coord"}),
        "ClientID": 999,
        "ClientTransactionID": int(time.time())
    }
    
    try:
        # Alpaca actions typically require PUT requests
        response = requests.put(BRIDGE_URL, data=payload, timeout=5)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        # Accessing the nested 'Value' block where the hardware JSON-RPC response lives
        if "Value" in data:
            # Depending on bridge version, Value might be a string or a dict
            inner_val = data["Value"]
            if isinstance(inner_val, str):
                inner_val = json.loads(inner_val)
            
            # Navigate to the result block for RA and Dec
            if "result" in inner_val:
                res = inner_val["result"]
                return {
                    "ra": res.get("ra"),
                    "dec": res.get("dec")
                }
        return None
            
    except Exception:
        return None

if __name__ == "__main__":
    coords = get_mount_coords()
    if coords and coords.get("ra") is not None:
        print(f"✨ Orientation Secured: RA {coords['ra']:.4f} | DEC {coords['dec']:.4f}")
    else:
        # Fallback to general status if specific coordinates fail
        print("⚠️ Equatorial coordinates not found in current stream.")
