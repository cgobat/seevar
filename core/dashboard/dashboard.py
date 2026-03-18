#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/dashboard/dashboard.py
Version: 4.7.6
Objective: SeeVar Beta: Full v4.6.1 logic restoration. Fixed Mag/Period ticker and Postflight LEDs.
"""

import json
import logging
import os
import sys
import time
import tomllib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from flask import Flask, render_template, jsonify

from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, get_sun
from astropy.time import Time

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR     = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR     = PROJECT_ROOT / "data"
PLAN_FILE    = DATA_DIR / "tonights_plan.json"
STATE_FILE   = DATA_DIR / "system_state.json"
LEDGER_FILE  = DATA_DIR / "ledger.json"
WEATHER_FILE = DATA_DIR / "weather_state.json"
ENV_STATUS   = Path("/dev/shm/env_status.json")
CONFIG_PATH  = Path("~/seestar_organizer/config.toml").expanduser()

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.WARNING)
sys.path.append(str(PROJECT_ROOT))
try:
    from core.utils.observer_math import get_maidenhead_6char
except ImportError:
    def get_maidenhead_6char(lat, lon): return "UNKNOWN"

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))

# ---------------------------------------------------------------------------
# Hardware Cache (v4.6.1)
# ---------------------------------------------------------------------------
HW_CACHE = {"timestamp": 0, "data": {"link_status": "OFFLINE", "battery": "N/A", "temp_c": "N/A", "storage_mb": "N/A"}}

def refresh_hw_cache():
    now = time.time()
    if now - HW_CACHE["timestamp"] < 10: return
    if ENV_STATUS.exists():
        try:
            with open(ENV_STATUS) as f:
                env = json.load(f)
            for k in ("link_status", "storage_mb"):
                if k in env: HW_CACHE["data"][k] = env[k]
        except: pass
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
            tel = state.get("telemetry", {})
            if "battery_pct" in tel: HW_CACHE["data"]["battery"] = str(tel["battery_pct"])
            if "temp_c" in tel: HW_CACHE["data"]["temp_c"] = str(round(tel["temp_c"], 1))
        except: pass
    HW_CACHE["timestamp"] = now

def load_json(path, default):
    if path.exists():
        try:
            with open(path) as f: return json.load(f)
        except: pass
    return default

def get_dusk_utc(lat, lon, elev):
    try:
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=elev*u.m)
        utc_now = datetime.now(timezone.utc)
        start_time = datetime(utc_now.year, utc_now.month, utc_now.day, 12, 0, tzinfo=timezone.utc)
        if utc_now.hour < 12: start_time -= timedelta(days=1)
        for m in range(0, 24 * 60, 5):
            t_dt = start_time + timedelta(minutes=m)
            alt = get_sun(Time(t_dt)).transform_to(AltAz(obstime=Time(t_dt), location=loc)).alt.deg
            if alt <= -18.0: return t_dt
    except: pass
    return None

def build_postflight(ledger, dusk_dt):
    entries = ledger.get("entries", {})
    plan_data = load_json(PLAN_FILE, [])
    scheduled = len(plan_data) if isinstance(plan_data, list) else len(plan_data.get("targets", []))
    attempted, observed, failed, rows = 0, 0, 0, []
    
    for name, e in entries.items():
        obs_str = e.get("last_obs_utc")
        if not obs_str: continue
        try:
            ts = datetime.fromisoformat(obs_str.rstrip("Z")).replace(tzinfo=timezone.utc)
            if dusk_dt and ts < dusk_dt: continue
            attempted += 1
            status = e.get("status", "PENDING")
            if status == "OBSERVED": observed += 1
            elif "FAILED" in status or status == "ERROR": failed += 1
            rows.append({
                "time": ts.strftime("%H:%M"), "name": name, 
                "mag": f"{e.get('last_mag', 0):.3f}", "snr": f"{e.get('last_snr', 0):.0f}",
                "ts": ts.isoformat()
            })
        except: continue
    rows.sort(key=lambda r: r["ts"], reverse=True)
    return {
        "scoreboard": {"scheduled": scheduled, "attempted": attempted, "observed": observed, "failed": failed},
        "phot_led": "green" if observed > 0 else "orange" if attempted > 0 else "grey",
        "aavso_led": "grey",
        "log": rows[:5]
    }

@app.route('/')
def index():
    plan = load_json(PLAN_FILE, [])
    return render_template('index.html', target_data=plan, flight_window="20:50 - 04:55")

@app.route('/telemetry')
def get_telemetry():
    try:
        with open(CONFIG_PATH, "rb") as f: config = tomllib.load(f)
    except: config = {}
    loc = config.get('location', {})
    refresh_hw_cache()
    
    dusk_dt = get_dusk_utc(loc.get('lat', 52.38), loc.get('lon', 4.64), loc.get('elevation', 0))
    return jsonify({
        "maidenhead": loc.get('maidenhead', "JO22hj"),
        "weather": load_json(WEATHER_FILE, {"status": "CLEAR", "icon": "⭐"}),
        "orchestrator": load_json(STATE_FILE, {"state": "IDLE", "sub": "Standing by", "flight_log": []}),
        "hardware": HW_CACHE["data"],
        "postflight": build_postflight(load_json(LEDGER_FILE, {}), dusk_dt)
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
