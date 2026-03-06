#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/neutralizer.py
Version: 2.4.0
Objective: 3-finger salute, generous 180s deep sleep, ping for life, then verify Zero-State.
"""

import requests
import json
import time
import sys

ALP_URL = "http://127.0.0.1:5555/api/v1/telescope/1/action"

def zwo_rpc_pulse(method, params=None):
    payload = {
        "Action": "method_sync",
        "Parameters": json.dumps({"method": method, **(params or {})}),
        "ClientID": "1",
        "ClientTransactionID": str(int(time.time()))
    }
    try:
        return requests.put(ALP_URL, data=payload, timeout=3).json().get("Value", {}).get("result", {})
    except:
        return None

def ping_engine():
    """The machine that goes 'ping'."""
    try:
        requests.get("http://127.0.0.1:5555/management/apiversions", timeout=2)
        return True
    except:
        return False

def enforce_zero_state():
    print("🧠 1. Severing connections & commanding park...")
    try:
        requests.post("http://127.0.0.1:5432/1/schedule/state", data={"action": "toggle"}, timeout=3)
    except:
        pass
        
    zwo_rpc_pulse("iscope_stop_view")
    time.sleep(2)
    zwo_rpc_pulse("scope_park")

    print("🔌 2. Hardware resetting. Sleeping for 180s...")
    time.sleep(180)

    print("🏥 3. Listening for the 'ping'...")
    ping_timeout = time.time() + 60
    is_alive = False
    while time.time() < ping_timeout:
        if ping_engine():
            print("✅ PING! The engine is breathing.")
            is_alive = True
            break
        print("... no pulse yet ...")
        time.sleep(5)
        
    if not is_alive:
        print("❌ Flatline. The telescope did not wake up.")
        return False

    print("📡 4. Polling brain for Parked & Idle state (Max 180s)...")
    state_timeout = time.time() + 180
    while time.time() < state_timeout:
        state = zwo_rpc_pulse("iscope_get_app_state")
        if isinstance(state, dict) and state.get("parked") == True and state.get("state") == "idle":
            print("✅ S30-PRO Zero-State Confirmed. Ready for mission.")
            return True
        print("... ZWO brain still initializing ...")
        time.sleep(5)
        
    print("❌ Timeout: Engine is awake but failed to reach Zero-State.")
    return False

if __name__ == "__main__":
    if not enforce_zero_state():
        sys.exit(1)
