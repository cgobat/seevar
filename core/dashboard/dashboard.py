#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/dashboard/dashboard.py
Version: 2.0.0 (Wolle/Silicon Grade)
Objective: Serves the 3-block swipeable dashboard on port 5050.
"""

from flask import Flask, render_template, jsonify
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
ROOT = Path(__file__).resolve().parents[2]

def get_jdate():
    """Calculates current Julian Date for the header."""
    now = datetime.utcnow()
    # Simplified JDate calculation for the dashboard display
    a = (14 - now.month) // 12
    y = now.year + 4800 - a
    m = now.month + 12 * a - 3
    jd = now.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return round(jd + (now.hour - 12) / 24 + now.minute / 1440 + now.second / 86400, 4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/telemetry')
def telemetry():
    """Aggregates the Pillars of Truth for the frontend."""
    try:
        with open(ROOT / "core/flight/data/system_state.json", 'r') as f:
            state = json.load(f)
        with open(ROOT / "core/flight/data/tonights_plan.json", 'r') as f:
            plan = json.load(f)
            
        return jsonify({
            "jdate": get_jdate(),
            "maidenhead": "JO22ni", # To be replaced by observer_math.py logic
            "state": state,
            "plan_count": len(plan.get("targets", []))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Landed on port 5050 to avoid systemd interference
    app.run(host='0.0.0.0', port=5050, debug=False)
