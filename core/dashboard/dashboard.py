#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/dashboard/dashboard.py
Version: 4.7.1
Objective: SeeVar Beta: Full restoration of v4.6.1 logic + missing Target/Postflight LED keys.
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
SIRIL_LOG    = PROJECT_ROOT / "logs" / "siril_extraction.log"
ENV_STATUS   = Path("/dev/shm/env_status.json")
CONFIG_PATH  = Path("~/seestar_organizer/config.toml").expanduser()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("dashboard")

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
sys.path.append(str(PROJECT_ROOT))
try:
    from core.utils.observer_math import get_maidenhead_6char
except ImportError:
    def get_maidenhead_6char(lat, lon):
        return "UNKNOWN"

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))

# ---------------------------------------------------------------------------
# Hardware cache
# ---------------------------------------------------------------------------
HW_CACHE = {"timestamp": 0, "data": {"link_status": "OFFLINE", "battery": "N/A", "temp_c": "N/A", "storage_mb": "N/A"}}
HW_CACHE_TTL = 10

def refresh_hw_cache():
    now = time.time()
    if now - HW_CACHE["timestamp"] < HW_CACHE_TTL:
        return

    if ENV_STATUS.exists():
        try:
            with open(ENV_STATUS) as f:
                env = json.load(f)
            for k in ("link_status", "storage_mb"):
                if k in env:
                    HW_CACHE["data"][k] = env[k]
        except Exception as e:
            log.warning("env_status failed: %s", e)

    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
            tel = state.get("telemetry", {})
            if "battery_pct" in tel:
                HW_CACHE["data"]["battery"] = str(tel["battery_pct"])
            if "temp_c" in tel:
                HW_CACHE["data"]["temp_c"] = str(round(tel["temp_c"], 1))
        except Exception as e:
            log.warning("state refresh failed: %s", e)
    HW_CACHE["timestamp"] = now

def load_json_file(path: Path, default):
    if path.exists():
        try:
            with open(path) as f: return json.load(f)
        except: pass
    return default

def get_dusk_utc(lat: float, lon: float, elev: float):
    try:
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=elev*u.m)
        utc_now = datetime.now(timezone.utc)
        start_time = datetime(utc_now.year, utc_now.month, utc_now.day, 12, 0, tzinfo=timezone.utc)
        if utc_now.hour < 12: start_time -= timedelta(days=1)
        for m in range(0, 24 * 60, 5):
            t_dt = start_time + timedelta(minutes=m)
            sun_alt = get_sun(Time(t_dt)).transform_to(AltAz(obstime=Time(t_dt), location=loc)).alt.deg
            if sun_alt <= -18.0: return t_dt
    except: pass
    return None

def build_postflight(ledger: dict, dusk_dt) -> dict:
    entries = ledger.get("entries", {})
    plan_data = load_json_file(PLAN_FILE, [])
    scheduled = len(plan_data) if isinstance(plan_data, list) else len(plan_data.get("targets", []))
    attempted, observed, failed, log_rows = 0, 0, 0, []
    
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
            
            log_rows.append({
                "time": ts.strftime("%H:%M"), "name": name, "filter": e.get("last_filter", "—"),
                "mag_str": f"{e.get('last_mag', 0):.3f}", "snr_str": f"{e.get('last_snr', 0):.0f}",
                "zp_str": f"{e.get('last_zp', 0):.2f}", "row_class": "ok" if status == "OBSERVED" else "fail",
                "ts": ts.isoformat()
            })
        except: continue

    log_rows.sort(key=lambda r: r["ts"], reverse=True)
    return {
        "scoreboard": {"scheduled": scheduled, "attempted": attempted, "observed": observed, "failed": failed},
        "phot_led": "green" if observed > 0 else "orange" if attempted > 0 else "grey",
        "aavso_led": "grey",
        "log": log_rows[:5]
    }

@app.route('/')
def index():
    plan = load_json_file(PLAN_FILE, [])
    return render_template('index.html', target_data=plan, flight_window="20:50 - 04:55")

@app.route('/telemetry')
def get_telemetry():
    with open(CONFIG_PATH, "rb") as f: config = tomllib.load(f)
    loc = config.get('location', {})
    refresh_hw_cache()
    
    env = load_json_file(ENV_STATUS, {})
    weather = load_json_file(WEATHER_FILE, {"status": "CLEAR", "icon": "⭐"})
    state_data = load_json_file(STATE_FILE, {"state": "IDLE", "sub": "Standing by", "flight_log": []})
    ledger = load_json_file(LEDGER_FILE, {})
    
    dusk_dt = get_dusk_utc(loc.get('lat', 52.38), loc.get('lon', 4.64), loc.get('elevation', 0))

    return jsonify({
        "maidenhead": loc.get('maidenhead', "JO22hj"),
        "weather": weather,
        "orchestrator": state_data,
        "current_target": state_data.get("current_target", {}),
        "hardware": HW_CACHE["data"],
        "postflight": build_postflight(ledger, dusk_dt)
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
