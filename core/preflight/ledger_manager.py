#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/ledger_manager.py
Version: 2.2.1
Objective: The High-Authority Mission Brain. Manages dynamic target cadence
           (1/20th rule) and observation history. Cadence parameters loaded
           from config.toml [planner] — tunable without code changes.
"""

import json
import logging
import tomllib
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Ledger")

PROJECT_ROOT    = Path(__file__).resolve().parents[2]
LEDGER_FILE     = PROJECT_ROOT / "data" / "ledger.json"
FEDERATED_CATALOG = PROJECT_ROOT / "catalogs" / "federation_catalog.json"
TONIGHTS_PLAN   = PROJECT_ROOT / "data" / "tonights_plan.json"
CONFIG_PATH     = PROJECT_ROOT / "config.toml"

# ---------------------------------------------------------------------------
# Load cadence parameters from config.toml
# Falls back to 1/20th rule defaults if section or key is missing
# ---------------------------------------------------------------------------

def _load_cadence_config() -> tuple[float, float]:
    """
    Returns (cadence_divisor, cadence_fallback_days) from config.toml [planner].
    Defaults: divisor=20 (1/20th rule), fallback=3.0 days.
    """
    defaults = (20.0, 3.0)
    try:
        with open(CONFIG_PATH, "rb") as f:
            config = tomllib.load(f)
        planner = config.get("planner", {})
        divisor  = float(planner.get("cadence_divisor",      defaults[0]))
        fallback = float(planner.get("cadence_fallback_days", defaults[1]))
        return divisor, fallback
    except Exception as e:
        logger.warning("Could not load cadence config: %s — using defaults", e)
        return defaults


CADENCE_DIVISOR, CADENCE_FALLBACK_DAYS = _load_cadence_config()
logger.info("Cadence — divisor: 1/%.0f  fallback: %.1f days",
            CADENCE_DIVISOR, CADENCE_FALLBACK_DAYS)


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path: Path, data: dict, objective: str):
    output = {
        "#objective": objective,
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "schema_version": "2026.1"
        },
        "entries": data
    }
    with open(path, 'w') as f:
        json.dump(output, f, indent=4)


# ---------------------------------------------------------------------------
# Core cadence engine
# ---------------------------------------------------------------------------

def execute_ledger_sync():
    catalog_raw = load_json(FEDERATED_CATALOG)
    targets = catalog_raw.get("data", []) if isinstance(catalog_raw, dict) \
              else catalog_raw

    ledger_raw = load_json(LEDGER_FILE)
    entries    = ledger_raw.get("entries", {})

    now       = datetime.now()
    due_names = []

    for t in targets:
        name = t['name'].replace(" ", "_").upper()

        if name not in entries:
            entries[name] = {
                "status":       "PENDING",
                "last_success": None,
                "attempts":     0,
                "priority":     "NORMAL"
            }

        last_success = entries[name].get("last_success")

        if not last_success:
            due_names.append(name)
        else:
            last_date = datetime.fromisoformat(last_success)

            # Dynamic cadence — period / divisor (default 1/20th rule)
            # Fallback for targets without a known period
            period = t.get("period_days")
            if period is not None and float(period) > 0:
                cadence_days = float(period) / CADENCE_DIVISOR
            else:
                cadence_days = CADENCE_FALLBACK_DAYS

            if now - last_date > timedelta(days=cadence_days):
                due_names.append(name)

    plan_data       = load_json(TONIGHTS_PLAN)
    visible_targets = plan_data.get("targets", []) if isinstance(plan_data, dict) \
                      else plan_data

    due_plan = [t for t in visible_targets
                if t['name'].replace(" ", "_").upper() in due_names]

    save_json(LEDGER_FILE, entries,
              "Master Observational Register and Status Ledger")

    final_plan = {
        "#objective": "Tactical flight plan filtered by dynamic cadence ledger.",
        "metadata": {
            "generated":       now.isoformat(),
            "due_count":       len(due_plan),
            "cadence_divisor": CADENCE_DIVISOR,
            "fallback_days":   CADENCE_FALLBACK_DAYS,
        },
        "targets": due_plan
    }

    with open(TONIGHTS_PLAN, 'w') as f:
        json.dump(final_plan, f, indent=4)

    logger.info("✅ Ledger Sync: %d targets due (divisor=1/%.0f fallback=%.1fd)",
                len(due_plan), CADENCE_DIVISOR, CADENCE_FALLBACK_DAYS)


if __name__ == "__main__":
    execute_ledger_sync()
