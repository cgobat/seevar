#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/dashboard/dashboard.py
Version: 4.4.6
Objective: Flawless integration with caching, Weather Emoticon, Postflight Science telemetry, and dynamic 6-char Maidenhead.
"""
import json, os, sys, time, requests, tomllib
from flask import Flask, render_template, jsonify
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PLAN_FILE = DATA_DIR / "tonights_plan.json"
STATE_FILE = DATA_DIR / "system_state.json"
LEDGER_FILE = DATA_DIR / "ledger.json"
WEATHER_FILE = DATA_DIR / "weather_state.json"
SIRIL_LOG = PROJECT_ROOT / "logs" / "siril_extraction.log"

sys.path.append(str(PROJECT_ROOT))
from core.utils.observer_math import get_maidenhead_6char

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))

HW_CACHE = {"timestamp": 0, "data": {"link_status": "OFFLINE", "battery": "N/A", "storage_mb": "N/A"}}

def load_config(file_path):
    path = Path(os.path.expanduser(file_path))
    if path.exists():
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except: pass
    return {}

def get_seestar_ip():
    alp_cfg = load_config("~/seestar_alp/device/config.toml")
    ip = alp_cfg.get("device", {}).get("ip")
    if ip: return ip
    org_cfg = load_config("~/seestar_organizer/config.toml")
    ip = org_cfg.get("seestar", {}).get("ip")
    if ip: return ip
    return None

def get_location_data():
    org_cfg = load_config("~/seestar_organizer/config.toml")
    loc = org_cfg.get("location", {})
    lat, lon = loc.get("lat"), loc.get("lon")
    
    # Prioritize the dynamic 6-character math
    if lat is not None and lon is not None:
        return get_maidenhead_6char(float(lat), float(lon))
        
    # Fallback to config strings if math fails
    obs = org_cfg.get("observer", {})
    if "maidenhead" in obs: return obs["maidenhead"]
    if "maidenhead" in loc: return loc["maidenhead"]
    return "NO-GPS-LOCK"

def fetch_hardware_vitals():
    global HW_CACHE
    if time.time() - HW_CACHE["timestamp"] < 5:
        return HW_CACHE["data"]
    try:
        payload = {"Action": "method_sync", "Parameters": '{"method":"get_device_state"}', "ClientID": "1", "ClientTransactionID": "1"}
        res = requests.put("http://127.0.0.1:5555/api/v1/telescope/1/action", data=payload, timeout=2.0)
        if res.status_code == 200:
            val = res.json().get("Value", {}).get("result", {})
            if val:
                pi = val.get("pi_status", {})
                stor = val.get("storage", {}).get("storage_volume", [{}])[0]
                HW_CACHE["data"] = {"link_status": "ACTIVE", "battery": str(pi.get('battery_capacity', 'N/A')), "storage_mb": str(stor.get('free_mb', 'N/A'))}
                HW_CACHE["timestamp"] = time.time()
                return HW_CACHE["data"]
    except: pass
    ip = get_seestar_ip()
    if ip:
        try:
            res = requests.get(f"http://{ip}/api/v1/system/status", timeout=2.0)
            if res.status_code == 200:
                data = res.json().get("result", {})
                HW_CACHE["data"] = {"link_status": "ACTIVE", "battery": str(data.get('battery', 'N/A')), "storage_mb": str(data.get('free_storage', 'N/A'))}
                HW_CACHE["timestamp"] = time.time()
                return HW_CACHE["data"]
        except: pass
    HW_CACHE["data"] = {"link_status": "OFFLINE", "battery": "N/A", "storage_mb": "N/A"}
    HW_CACHE["timestamp"] = time.time()
    return HW_CACHE["data"]

@app.route('/')
def index():
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

    weather = {"status": "FETCHING", "icon": "❓"}
    if WEATHER_FILE.exists():
        try:
            with open(WEATHER_FILE, 'r') as f:
                weather.update(json.load(f))
        except: pass

    audit = "NEVER"
    if LEDGER_FILE.exists():
        audit = time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(LEDGER_FILE)))

    science = {"photometry": "grey", "aavso_ready": "grey", "siril_tail": []}
    if SIRIL_LOG.exists():
        try:
            with open(SIRIL_LOG, 'r') as f:
                science["siril_tail"] = [line.strip() for line in f.readlines()[-5:]]
        except: pass

    if (DATA_DIR / "reports").exists() and list((DATA_DIR / "reports").glob("*.txt")):
        science["aavso_ready"] = "green"

    qc_path = PROJECT_ROOT / "core/postflight/data/qc_report.json"
    if qc_path.exists():
        try:
            with open(qc_path, 'r') as f:
                qc = json.load(f)
                science["photometry"] = "green" if qc.get("status") == "PASS" else "orange"
        except: pass

    return jsonify({
        "maidenhead": get_location_data(),
        "orchestrator": state,
        "hardware": fetch_hardware_vitals(),
        "weather": weather,
        "science": science,
        "last_audit": audit
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
