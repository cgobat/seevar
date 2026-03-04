#!/usr/bin/env python3

import requests
import time
import json

# --- 1. The Configuration ---
SSC_GOTO_URL = "http://127.0.0.1:5432/1/goto"
ALPACA_ACTION_URL = "http://127.0.0.1:5555/api/v1/telescope/1/action"

# R Leo Coordinates (Standard HMS/DMS format accepted by the form)
TARGET_DATA = {
    "targetName": "R Leo",
    "searchFor": "VS", # Variable Star
    "ra": "09h47m33s",
    "dec": "+11d25m44s"
}

def command_slew():
    print(f"🌟 Commanding slew to {TARGET_DATA['targetName']} (Port 5432)...")
    try:
        # We send the POST request simulating the HTML form submission
        response = requests.post(SSC_GOTO_URL, data=TARGET_DATA, timeout=5)
        if response.status_code == 200:
            print("✅ Goto command accepted by the Muscles!")
            return True
        else:
            print(f"❌ Command failed with HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error hitting port 5432: {e}")
        return False

def watch_telemetry(duration=30):
    print("\n🎧 Opening Wiretap on Port 5555 (Monitoring Alt/Az)...")
    print("------------------------------------------------------")
    
    # The exact JSON-RPC payload we discovered for horizon coordinates
    telemetry_payload = {
        "Action": "method_sync",
        "Parameters": json.dumps({"method": "scope_get_horiz_coord", "params": {}}),
        "ClientID": "1",
        "ClientTransactionID": "1000"
    }
    
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        try:
            res = requests.put(ALPACA_ACTION_URL, data=telemetry_payload, timeout=2)
            if res.status_code == 200:
                data = res.json()
                # Parse the response [Altitude, Azimuth]
                if "Value" in data and "result" in data["Value"]:
                    alt, az = data["Value"]["result"]
                    print(f"🔭 Live Position -> Altitude: {alt:>7.2f}° | Azimuth: {az:>7.2f}°")
                else:
                    print("⚠️ Waiting for valid coordinate payload...")
            else:
                print(f"⚠️ Alpaca bridge returned HTTP {res.status_code}")
                
        except Exception as e:
            print(f"⚠️ Telemetry read error: {e}")
            
        time.sleep(2) # Rest for 2 seconds before polling again
        
    print("------------------------------------------------------")
    print("🏁 Telemetry wiretap closed.")

if __name__ == "__main__":
    print("🚀 Initiating Dry-Run Slew Test...")
    # Step 1: Send the Slew Command
    if command_slew():
        # Step 2: Listen to the movement for 30 seconds
        watch_telemetry(duration=30)
