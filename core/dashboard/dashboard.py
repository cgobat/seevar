#!/usr/bin/env python3
# S30-PRO Federation Dashboard (v1.5.8 - REDA Branch)
from flask import Flask, render_template, jsonify
import sys, os
from pathlib import Path

# Force the project root for the Vault and Templates
PROJECT_ROOT = Path("/home/ed/seestar_organizer")
TEMPLATE_DIR = PROJECT_ROOT / "core/dashboard/templates"

sys.path.append(str(PROJECT_ROOT))
from core.flight.vault_manager import VaultManager

# Explicitly anchor the templates to the RAID/Project path
app = Flask(__name__, template_folder=str(TEMPLATE_DIR))
vault = VaultManager()

@app.route('/')
def index():
    # Final check: Is the UI actually there?
    if not os.path.exists(os.path.join(str(TEMPLATE_DIR), "index.html")):
        return "CRITICAL ERROR: RAID UI ASSETS MISSING", 500
    return render_template('index.html')

@app.route('/telemetry')
def telemetry():
    obs = vault.get_observer_config()
    return jsonify({
        "maidenhead": obs.get("maidenhead", "JO22hj"),
        "status": "EXTERNAL_BRIDGE_UP"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=False)
