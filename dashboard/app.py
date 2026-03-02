#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# PROJECT: Federation Fleet Command
# MODULE:  Telemetry Orchestrator (Dashboard)
# VERSION: 1.4.13 (Bommel Baseline)
# OBJECTIVE: Real-time status aggregation for multi-unit Seestar deployment.
# -----------------------------------------------------------------------------
from flask import Flask, render_template
import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))

def get_telemetry():
    """Aggregates local vitals and fleet state from RAM-disk."""
    path = "/dev/shm/env_status.json"
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "maidenhead": "JO22hj",
        "williamina_led": "led-grey",
        "annie_led": "led-grey",
        "henrietta_led": "led-grey",
        "gps_led": "led-red",
        "pps_offset": "WAIT",
        "fog_led": "led-grey",
        "jd": "0000000.0000"
    }

@app.route('/')
def index():
    return render_template('index.html', env=get_telemetry())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, threaded=True)
