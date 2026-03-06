#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/camera_control.py
Version: 1.1.0
Objective: Manage S30 imaging pipeline using iscope_ native methods.
"""

import os
import json
import requests
import time

# Target the Alpaca bridge which handles our method_sync translation
ALPACA_URL = "http://127.0.0.1:5555/api/v1/telescope/1/action"

def execute_iscope_command(method, params=None):
    """Generic wrapper for iscope_ native commands via the bridge."""
    payload = {
        "Action": "method_sync",
        "Parameters": json.dumps({
            "method": method,
            "params": params if params else {}
        }),
        "ClientID": 1,
        "ClientTransactionID": int(time.time())
    }
    try:
        res = requests.put(ALPACA_URL, data=payload, timeout=10)
        return res.json().get("Value", {})
    except Exception as e:
        return {"error": str(e)}

def start_star_view(exp_ms=1000, gain=80):
    """Transitions the S30 into active star-imaging mode."""
    return execute_iscope_command("iscope_start_view", {
        "mode": "star",
        "exp_ms": exp_ms,
        "gain": gain,
        "lp_filter": False
    })

def stop_view():
    """Stops the current imaging stream."""
    return execute_iscope_command("iscope_stop_view")

def get_view_status():
    """Retrieves current camera/view telemetry."""
    return execute_iscope_command("get_view_state")
