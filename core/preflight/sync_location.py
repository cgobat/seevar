#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/sync_location.py
Version: 1.3.0
Objective: Synchronize S30 location using the verified open Port 80.
"""

import requests
import time

S30_IP = "192.168.178.26"
PORT = 80

def sync_haarlem():
    print(f"🌍 Pushing Haarlem coordinates to Port {PORT}...")
    
    # Precise Haarlem, NL coordinates
    payload = {
        "lat": 52.3874,
        "lon": 4.6462,
        "timezone": "Europe/Amsterdam",
        "timestamp": int(time.time())
    }
    
    try:
        # Some firmware versions use /api/location, others use /set_location
        url = f"http://{S30_IP}:{PORT}/api/location"
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            print("✅ Success! Williamina now knows she's in Haarlem.")
        else:
            print(f"⚠️ Port 80 rejected JSON. Trying legacy GET params...")
            fallback_url = f"http://{S30_IP}:{PORT}/api/set_location?lat=52.3874&lon=4.6462"
            requests.get(fallback_url, timeout=5)
            print("✅ Legacy command sent to Port 80.")

    except Exception as e:
        print(f"❌ Failed to reach Port 80: {e}")

if __name__ == "__main__":
    sync_haarlem()
