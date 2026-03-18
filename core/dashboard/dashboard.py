#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/dashboard/dashboard.py
Version: 4.6.1
Objective: Fixed startup + real location + current_target support
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

# ---------------------------------------------------------------------------
# Flask
# ---------------------------------------------------------------------------
TEMPLATE_DIR = BASE_DIR / "templates"
app = Flask(__name__, template_folder=str(TEMPLATE_DIR))

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

    if HW_CACHE["data"]["storage_mb"] in ("N/A", None):
        try:
            buf = DATA_DIR / "local_buffer"
            total = sum(f.stat().st_size for f in buf.rglob("*") if f.is_file()) if buf.exists() else 0
            HW_CACHE["data"]["storage_mb"] = round(total / (1024*1024), 1)
        except:
            pass

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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_config(file_path: str) -> dict:
    path = Path(os.path.expanduser(file_path))
    if path.exists():
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except Exception:
            pass
    return {}

def load_json_file(path: Path, default):
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return default

def load_plan() -> list:
    data = load_json_file(PLAN_FILE, [])
    return data if isinstance(data, list) else data.get("targets", []) if isinstance(data, dict) else []

# ---------------------------------------------------------------------------
# Twilight engine
# ---------------------------------------------------------------------------
FLIGHT_WINDOW_CACHE = {"date": None, "text": "CALCULATING..."}
DUSK_CACHE = {"date": None, "dt": None}

def get_dusk_utc(lat: float, lon: float, elev: float):
    today_str = datetime.now().strftime("%Y-%m-%d")
    if DUSK_CACHE["date"] == today_str:
        return DUSK_CACHE["dt"]
    try:
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=elev*u.m)
        utc_now = datetime.now(timezone.utc)
        start_time = datetime(utc_now.year, utc_now.month, utc_now.day, 12, 0, tzinfo=timezone.utc)
        if utc_now.hour < 12:
            start_time -= timedelta(days=1)
        is_night = False
        for m in range(0, 24 * 60, 5):
            t_dt = start_time + timedelta(minutes=m)
            t = Time(t_dt)
            frame = AltAz(obstime=t, location=loc)
            sun_alt = get_sun(t).transform_to(frame).alt.deg
            if sun_alt <= -18.0 and not is_night:
                is_night = True
                DUSK_CACHE["date"] = today_str
                DUSK_CACHE["dt"]   = t_dt
                return t_dt
    except Exception as e:
        log.error("get_dusk_utc failed: %s", e)
    return None

def get_flight_window(lat: float, lon: float, elev: float) -> str:
    today_str = datetime.now().strftime("%Y-%m-%d")
    if FLIGHT_WINDOW_CACHE["date"] == today_str:
        return FLIGHT_WINDOW_CACHE["text"]
    try:
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=elev*u.m)
        utc_now = datetime.now(timezone.utc)
        start_time = datetime(utc_now.year, utc_now.month, utc_now.day, 12, 0, tzinfo=timezone.utc)
        if utc_now.hour < 12:
            start_time -= timedelta(days=1)
        dusk_str, dawn_str = None, None
        is_night = False
        for m in range(0, 24 * 60, 5):
            t_dt = start_time + timedelta(minutes=m)
            t = Time(t_dt)
            frame = AltAz(obstime=t, location=loc)
            sun_alt = get_sun(t).transform_to(frame).alt.deg
            if sun_alt <= -18.0 and not is_night:
                is_night = True
                dusk_str = t_dt.astimezone().strftime("%H:%M")
            elif sun_alt > -18.0 and is_night:
                is_night = False
                dawn_str = t_dt.astimezone().strftime("%H:%M")
                break
        if dusk_str and dawn_str:
            res = f"{dusk_str} - {dawn_str}"
        else:
            res = "NO ASTRONOMICAL NIGHT"
        FLIGHT_WINDOW_CACHE["date"] = today_str
        FLIGHT_WINDOW_CACHE["text"] = res
        return res
    except Exception as e:
        log.error("Flight window calc failed: %s", e)
        return "ERR - CHECK LOGS"

# ---------------------------------------------------------------------------
# POSTFLIGHT BUILDER
# ---------------------------------------------------------------------------
def build_postflight(ledger: dict, dusk_dt) -> dict:
    entries = ledger.get("entries", {})
    plan_data  = load_json_file(PLAN_FILE, [])
    scheduled  = len(plan_data) if isinstance(plan_data, list) else len(plan_data.get("targets", []))
    attempted, observed, failed = 0, 0, 0
    log_rows   = []
    STATUS_FAIL = {"FAILED_QC", "FAILED_QC_LOW_SNR", "FAILED_SATURATED", "FAILED_NO_WCS", "ERROR"}

    for name, e in entries.items():
        obs_str = e.get("last_obs_utc")
        if not obs_str:
            continue
        try:
            ts = datetime.fromisoformat(obs_str.rstrip("Z")).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if dusk_dt and ts < dusk_dt:
            continue

        attempted += 1
        status = e.get("status", "PENDING")
        if status == "OBSERVED":
            observed += 1
            row_class = "ok"
        elif status in STATUS_FAIL:
            failed += 1
            row_class = "fail"
        else:
            row_class = "warn"

        zp_std = e.get("last_zp_std")
        zp_class = "z-bad" if zp_std is None else "z-good" if zp_std < 0.30 else "z-ok" if zp_std < 0.80 else "z-bad"
        mag_str = f"{e.get('last_mag'):.3f} ±{e.get('last_err'):.3f}" if e.get('last_mag') is not None else status.replace("FAILED_","")
        snr_str = f"{e.get('last_snr'):.0f}" if e.get('last_snr') is not None else "—"
        zp_str  = f"{e.get('last_zp'):.2f}±{zp_std:.2f}" if e.get('last_zp') is not None and zp_std is not None else "—"

        log_rows.append({
            "time": ts.strftime("%H:%M"),
            "name": name,
            "filter": e.get("last_filter", "—"),
            "mag_str": mag_str,
            "snr_str": snr_str,
            "zp_str": zp_str,
            "zp_class": zp_class,
            "row_class": row_class,
            "ts": ts.isoformat(),
        })

    log_rows.sort(key=lambda r: r["ts"], reverse=True)
    log_rows = log_rows[:5]
    for r in log_rows:
        del r["ts"]

    return {
        "scoreboard": {"scheduled": scheduled, "attempted": attempted, "observed": observed, "failed": failed},
        "overall": "orange" if failed > 0 else "green" if observed > 0 else "grey",
        "phot_led": "green" if observed > 0 else "orange" if attempted > 0 else "grey",
        "aavso_led": "grey",
        "log": log_rows,
    }

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    target_data = load_plan()
    config = load_config("~/seevar/config.toml")
    loc = config.get('location', {})
    fw_text = get_flight_window(loc.get('lat', 0.0), loc.get('lon', 0.0), loc.get('elevation', 0.0))
    return render_template('index.html', target_data=target_data, flight_window=fw_text)

@app.route('/telemetry')
def get_telemetry():
    config = load_config("~/seevar/config.toml")
    loc = config.get('location', {})
    dusk_dt = get_dusk_utc(loc.get('lat', 0.0), loc.get('lon', 0.0), loc.get('elevation', 0.0))
    
    state = {"gps_status": "NO-GPS-LOCK", "lat": loc.get('lat', 0), "lon": loc.get('lon', 0),
             "maidenhead": loc.get('maidenhead', "N/A"), "system_msg": "System Ready."}

    env = load_json_file(ENV_STATUS, {})
    if env:
        state.update(env)

    weather = {"status": "FETCHING", "icon": "❓"}
    weather_data = load_json_file(WEATHER_FILE, {})
    if weather_data:
        weather.update(weather_data)

    science = {"photometry": "grey", "aavso_ready": "grey", "siril_tail": []}
    if SIRIL_LOG.exists():
        try:
            with open(SIRIL_LOG) as f:
                science["siril_tail"] = [line.strip() for line in f.readlines()[-5:]]
        except OSError:
            pass

    orchestrator = {"state": "PARKED", "sub": "OFF-DUTY", "msg": "No state file found.", "flight_log": []}
    state_data = load_json_file(STATE_FILE, {})
    if state_data:
        orchestrator.update({
            "state": state_data.get("state", "PARKED"),
            "sub": state_data.get("sub", "OFF-DUTY"),
            "msg": state_data.get("msg", ""),
            "flight_log": state_data.get("flight_log", [])
        })

    current_target = state_data.get("current_target", {}) if state_data else {}
    ledger = load_json_file(LEDGER_FILE, {})
    postflight = build_postflight(ledger, dusk_dt)
    last_audit = ledger.get("metadata", {}).get("last_updated", "N/A")

    refresh_hw_cache()

    return jsonify({
        "gps_status": state.get("gps_status"),
        "lat": state.get("lat"),
        "lon": state.get("lon"),
        "maidenhead": state.get("maidenhead"),
        "system_msg": state.get("system_msg"),
        "weather": weather,
        "science": science,
        "orchestrator": orchestrator,
        "current_target": current_target,
        "hardware": HW_CACHE["data"],
        "last_audit": last_audit,
        "postflight": postflight,
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=False)
