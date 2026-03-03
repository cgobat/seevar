#!/usr/bin/env python3
# Version: 2.1.7 (Zero-Hardcode Edition)
from flask import Flask, render_template, jsonify
from pathlib import Path
import datetime, json, os, sys

# Federation Pathing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core.flight.vault_manager import VaultManager

app = Flask(__name__)
vault = VaultManager()

@app.route('/telemetry')
def telemetry():
    # Dynamic Maidenhead resolve
    obs = vault.get_observer_config()
    mhead = obs.get("maidenhead", "SEARCHING")
    
    # Load targets for the ticker
    target_file = Path("~/seestar_organizer/data/nightly_targets.json").expanduser()
    target_names = []
    if target_file.exists():
        with open(target_file, 'r') as f:
            targets = json.load(f)
            target_names = [t['name'] for t in targets]

    return jsonify({
        "maidenhead": mhead,
        "jdate": round(2440587.5 + (datetime.datetime.now(datetime.timezone.utc).timestamp() / 86400), 4),
        "target_names": target_names,
        "target_count": len(target_names),
        "raid_status": "green" if os.path.ismount("/mnt/raid1") else "red"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
