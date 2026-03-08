#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/ledger_manager.py
Version: 2.1.0
Objective: The High-Authority Mission Brain. Manages target cadence and observation history to determine if a new observation is in order.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Ledger")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LEDGER_FILE = PROJECT_ROOT / "data" / "ledger.json"
FEDERATED_CATALOG = PROJECT_ROOT / "catalogs" / "federation_catalog.json"
TONIGHTS_PLAN = PROJECT_ROOT / "data" / "tonights_plan.json"

# Sovereign Cadence Policy
STANDARD_CADENCE_DAYS = 3

def load_json(path):
    if not path.exists(): return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data, objective):
    header = {
        "objective": objective,
        "last_updated": datetime.now().isoformat(),
        "schema_version": "2026.1"
    }
    # Ensure structure: Metadata + Entries
    output = {"metadata": header, "entries": data if "entries" not in data else data.get("entries")}
    with open(path, 'w') as f:
        json.dump(output, f, indent=4)

def execute_ledger_sync():
    # 1. Intake from Federated Catalog
    catalog_raw = load_json(FEDERATED_CATALOG)
    targets = catalog_raw.get("data", [])
    
    # 2. Load Ledger
    ledger_data = load_json(LEDGER_FILE)
    entries = ledger_data.get("entries", {})
    
    now = datetime.now()
    due_names = []
    
    # 3. Synchronize and Apply Cadence Logic
    for t in targets:
        name = t['name'].replace(" ", "_").upper()
        
        if name not in entries:
            entries[name] = {
                "status": "PENDING",
                "last_success": None,
                "attempts": 0,
                "priority": "NORMAL"
            }
        
        last_success_str = entries[name].get("last_success")
        if not last_success_str:
            due_names.append(name)
        else:
            last_date = datetime.fromisoformat(last_success_str)
            if now - last_date > timedelta(days=STANDARD_CADENCE_DAYS):
                due_names.append(name)

    # 4. Final Triage of Tonight's Plan
    plan_raw = load_json(TONIGHTS_PLAN)
    visible_targets = plan_raw.get("targets", [])
    
    # Filter visible targets against 'Due' list from Ledger
    due_plan = [t for t in visible_targets if t['name'].replace(" ", "_").upper() in due_names]
    
    # 5. Persist the Ledger and the Filtered Plan
    save_json(LEDGER_FILE, entries, "Master Observational Register and Status Ledger")
    
    plan_raw["targets"] = due_plan
    plan_raw["metadata"]["objective"] = "Tactical flight plan filtered by Ledger Cadence."
    plan_raw["metadata"]["generated"] = now.isoformat()
    plan_raw["metadata"]["due_count"] = len(due_plan)
    
    with open(TONIGHTS_PLAN, 'w') as f:
        json.dump(plan_raw, f, indent=4)

    logger.info(f"✅ Ledger Sync Complete: {len(due_plan)} targets marked as 'DUE' for tonight.")

if __name__ == "__main__":
    execute_ledger_sync()
