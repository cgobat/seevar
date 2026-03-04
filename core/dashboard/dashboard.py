#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# S30-PRO Federation Dashboard (v3.1.0 - Ledger Sync & Professional UI)
import json, os, sys, time
from flask import Flask, render_template, jsonify
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[1]
TEMPLATE_DIR = BASE_DIR / "templates"
DATA_FILE = PROJECT_ROOT / "data" / "tonights_plan.json"
STATE_FILE = PROJECT_ROOT / "data" / "system_state.json"
LEDGER_FILE = PROJECT_ROOT / "data" / "ledger.json"

sys.path.append(str(PROJECT_ROOT))
from core.flight.vault_manager import VaultManager

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))
vault = VaultManager()

@app.route('/')
def index():
    targets = []
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                targets = data.get("targets", [])
        except: pass
            
    if not targets:
        targets = [{"star_name": "AWAITING FLIGHT PLAN", "priority": False}]

    return render_template('index.html', target_data=targets)

@app.route('/telemetry')
def telemetry():
    obs = vault.get_observer_config()
    state_data = {"state": "PARKED", "sub": "OFF-DUTY", "msg": "Waiting for hardware..."}
    
    # Read Orchestrator State
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                state_data.update(json.load(f))
        except: pass

    # Read Ledger 'Last Modified' Timestamp
    audit_time = "NEVER"
    if LEDGER_FILE.exists():
        try:
            mtime = os.path.getmtime(LEDGER_FILE)
            audit_time = time.strftime('%H:%M:%S', time.localtime(mtime))
        except: pass

    return jsonify({
        "maidenhead": obs.get("maidenhead", "JO22hj"),
        "orchestrator": state_data,
        "last_audit": audit_time
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=False)
