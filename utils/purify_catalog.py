#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: utils/purify_catalog.py
Version: 2.0.0
Objective: Clean and standardize raw AAVSO targets into the strict federation_catalog.json format.
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGED_CATALOG = PROJECT_ROOT / "catalogs" / "raw_targets.json"
FEDERATION_CATALOG = PROJECT_ROOT / "catalogs" / "federation_catalog.json"

def purify():
    if not STAGED_CATALOG.exists():
        print(f"❌ Error: {STAGED_CATALOG} not found. Run librarian.py first.")
        sys.exit(1)

    with open(STAGED_CATALOG, 'r') as f:
        raw_data = json.load(f)

    purified = []
    for entry in raw_data:
        clean_entry = {
            "name": entry.get("name", "Unknown"),
            "ra": entry.get("ra", ""),
            "dec": entry.get("dec", ""),
            "priority": entry.get("priority", 1),
            "duration": entry.get("duration", 600)
        }
        if clean_entry["ra"] and clean_entry["dec"]:
            purified.append(clean_entry)
        else:
            print(f"⚠️ Dropped {clean_entry['name']} due to missing coordinates.")

    with open(FEDERATION_CATALOG, 'w') as f:
        json.dump(purified, f, indent=4)
        
    print(f"✨ Purified {len(purified)} valid targets into {FEDERATION_CATALOG}")

if __name__ == "__main__":
    purify()
