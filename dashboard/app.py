from flask import Flask, render_template
import json, os
from pathlib import Path

PROJECT_ROOT = Path("~/seestar_organizer").expanduser()
STATUS_PATH = Path("/dev/shm/env_status.json")
PLAN_PATH = PROJECT_ROOT / "data/tonights_plan.json"
QC_PATH = PROJECT_ROOT / "core/postflight/data/qc_report.json"

app = Flask(__name__)

@app.route("/")
def index():
    try:
        with open(STATUS_PATH, "r") as f: env = json.load(f)
    except: env = {"maidenhead": "HUNTING", "targets": "OFFLINE", "targets_led": "led-red"}

    try:
        with open(PLAN_PATH, "r") as f:
            plan_data = json.load(f)
            plan_list = plan_data if isinstance(plan_data, list) else plan_data.get('targets', [])
    except: plan_list = []

    try:
        if QC_PATH.exists():
            with open(QC_PATH, "r") as f: qc_list = json.load(f)[-10:]
        else: qc_list = []
    except: qc_list = []

    return render_template("index.html", env=env, plan=plan_list, qc=qc_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
