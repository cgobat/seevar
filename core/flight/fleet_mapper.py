#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# PROJECT: Federation Fleet Command
# MODULE:  Hardware Schema Mapper
# VERSION: 1.4.17 (Infrastructure Baseline)
# OBJECTIVE: Query Alpaca Bridge and establish deterministic API endpoints.
# -----------------------------------------------------------------------------
import urllib.request
import json
import sys

ALPACA_URL = "http://127.0.0.1:5555"
SCHEMA_FILE = "/home/ed/seestar_organizer/config_fleet_schema.json"

def map_fleet():
    print("[MAPPER] Polling Alpaca Management API for configured devices...")
    try:
        req = urllib.request.urlopen(f"{ALPACA_URL}/management/v1/configureddevices", timeout=2.0)
        devices = json.loads(req.read().decode())['Value']
    except Exception as e:
        print(f"[ERROR] Alpaca bridge offline or unreachable: {e}")
        sys.exit(1)

    fleet_schema = {
        "bridge_url": ALPACA_URL,
        "telescopes": {}
    }

    for dev in devices:
        if dev.get("DeviceType") == "Telescope":
            name = dev.get("DeviceName", "Unknown")
            idx = dev.get("DeviceNumber")
            
            # Map specific identities
            identity = "unknown_unit"
            if "Alpha" in name or "S30" in name: identity = "williamina_s30"
            elif "Annie" in name: identity = "annie_s50"
            elif "Henrietta" in name: identity = "henrietta_s50"
            
            fleet_schema["telescopes"][identity] = {
                "name": name,
                "device_number": idx,
                "endpoints": {
                    "ra": f"/api/v1/telescope/{idx}/rightascension",
                    "dec": f"/api/v1/telescope/{idx}/declination",
                    "slewing": f"/api/v1/telescope/{idx}/slewing",
                    "tracking": f"/api/v1/telescope/{idx}/tracking"
                }
            }
            print(f"[MAPPER] Locked: {identity} -> DeviceNumber {idx}")

    with open(SCHEMA_FILE, 'w') as f:
        json.dump(fleet_schema, f, indent=4)
    
    print(f"[MAPPER] Schema written to {SCHEMA_FILE}")

if __name__ == "__main__":
    map_fleet()
