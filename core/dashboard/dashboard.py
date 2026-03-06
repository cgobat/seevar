#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/dashboard/dashboard.py
Version: 4.0.0
Objective: Flawless integration with the original 13KB frontend. Dynamic config loading.
"""

import json, os, sys, time
import requests
import tomllib
from flask import Flask, render_template, jsonify
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PLAN_FILE = DATA_DIR / "tonights_plan.json"
STATE_FILE = DATA_DIR / "system_state.json"
LEDGER_FILE = DATA_DIR / "ledger.json"

sys.path.append(str(PROJECT_ROOT))
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))

def load_config(file_path):
    path = Path(os.path.expanduser(file_path))
    if path.exists():
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except: pass
    return {}

def get_seestar_ip():
    """Dynamically parses the telescope IP from configurations."""
    alp_cfg = load_config("~/seestar_alp/device/config.toml")
    ip = alp_cfg.get("device", {}).get("ip")
    if ip: return ip
    
    org_cfg = load_config("~/seestar_organizer/config.toml")
    ip = org_cfg.get("seestar", {}).get("ip")
    if ip: return ip
    
    return None

def get_location_data():
    """Dynamically parses maidenhead from config.toml."""
    org_cfg = load_config("~/seestar_organizer/config.toml")
    
    obs = org_cfg.get("observer", {})
    if "maidenhead" in obs: return obs["maidenhead"]
    
    loc = org_cfg.get("location", {})
    if "maidenhead" in loc: return loc["maidenhead"]
    
    return "NO-GPS-LOCK"

def fetch_hardware_vitals():
    """Attempts Alpaca Bridge first, falls back to dynamic direct IP."""
    # 1. Alpaca Bridge
    try:
        payload = {"Action": "method_sync", "Parameters": '{"method":"get_device_state"}', "ClientID": "1", "ClientTransactionID": "1"}
        res = requests.put("http://127.0.0.1:5555/api/v1/telescope/1/action", data=payload, timeout=1.0)
        if res.status_code == 200:
            val = res.json().get("Value", {}).get("result", {})
            if val:
                pi = val.get("pi_status", {})
                stor = val.get("storage", {}).get("storage_volume", [{}])[0]
                # Returning raw numbers because the JS does parseInt() and adds the % and MB strings
                return {"link_status": "ACTIVE", "battery": str(pi.get('battery_capacity', 'N/A')), "storage_mb": str(stor.get('free_mb', 'N/A'))}
    except: pass

    # 2. Dynamic Direct IP Fallback
    ip = get_seestar_ip()
    if ip:
        try:
            res = requests.get(f"http://{ip}/api/v1/system/status", timeout=1.0)
            if res.status_code == 200:
                data = res.json().get("result", {})
                return {"link_status": "ACTIVE", "battery": str(data.get('battery', 'N/A')), "storage_mb": str(data.get('free_storage', 'N/A'))}
        except: pass

    return {"link_status": "OFFLINE", "battery": "N/A", "storage_mb": "N/A"}

@app.route('/')
def index():
    # Pass targets via Jinja2 template as required by index.html
    targets = []
    if PLAN_FILE.exists():
        try:
            with open(PLAN_FILE, 'r') as f:
                data = json.load(f)
                targets = data if isinstance(data, list) else data.get("targets", [])
        except: pass
    return render_template('index.html', target_data=targets)

@app.route('/telemetry')
def telemetry():
    state = {"state": "PARKED", "sub": "OFF-DUTY", "msg": "System Ready."}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                state.update(json.load(f))
        except: pass

    audit = "NEVER"
    if LEDGER_FILE.exists():
        audit = time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(LEDGER_FILE)))

    return jsonify({
        "maidenhead": get_location_data(),
        "orchestrator": state,
        "hardware": fetch_hardware_vitals(),
        "last_audit": audit
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
