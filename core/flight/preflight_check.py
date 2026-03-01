#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/preflight_check.py
Version: 1.4.6 (Kriel)
"""
import json, os, sys, socket, time, subprocess, re, tomllib, urllib.request
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core.preflight.target_evaluator import TargetEvaluator

CONFIG_PATH = os.path.expanduser("~/seestar_organizer/config.toml")
SHM_STATUS = "/dev/shm/env_status.json"

def check_vitals():
    with open(CONFIG_PATH, "rb") as f: cfg = tomllib.load(f)
    
    # 📡 GPS & Time
    try:
        with socket.create_connection(("127.0.0.1", 2947), timeout=1) as s:
            s.sendall(b'?WATCH={"enable":true,"json":true};\n')
            msg = json.loads(s.makefile().readline())
            gps_stat, lat, lon = ("OK", msg.get('lat'), msg.get('lon')) if msg.get('class') == 'TPV' else ("WAITING", 0, 0)
    except: gps_stat, lat, lon = "BAD", 0, 0

    try:
        res = subprocess.check_output(['chronyc', 'tracking'], text=True)
        stratum = int(re.search(r"Stratum\s+:\s+(\d+)", res).group(1))
        pps_led, offset = ("led-green", f"{float(re.search(r'Last offset\s+:\s+([+-]?\d+\.\d+)', res).group(1))*1000:.2f}ms") if stratum < 16 else ("led-orange", "SYNCING")
    except: pps_led, offset = "led-red", "NO SYNC"

    # 🎯 Tactical Queue
    evaluator = TargetEvaluator()
    manifest = evaluator.evaluate()

    # 📦 Science Log Check (for the Science LED)
    qc_path = Path("~/seestar_organizer/core/postflight/data/qc_report.json").expanduser()
    science_led = "led-green" if qc_path.exists() and os.path.getsize(qc_path) > 2 else "led-grey"

    status = {
        "maidenhead": cfg.get("location", {}).get("maidenhead", "JO22hj"),
        "gps_led": "led-green" if gps_stat == "OK" else "led-orange",
        "pps_led": pps_led,
        "pps_offset": offset,
        "weather_led": "led-orange", # Environment
        "fog_led": "led-grey",       # Hardware Pending
        "science_led": science_led,  # Accountant Status
        "targets": manifest['status'],
        "targets_led": manifest['led'],
        "jd": round(2440587.5 + time.time() / 86400.0, 4),
        "bridge": "led-green" if socket.socket().connect_ex(('127.0.0.1', 5432)) == 0 else "led-red"
    }

    with open(SHM_STATUS, 'w') as f: json.dump(status, f)
    print(f"✅ Preflight Complete: {status['maidenhead']} | GPS: {gps_stat}")

if __name__ == "__main__":
    check_vitals()
