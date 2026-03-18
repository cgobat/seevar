#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/post_to_pre_feedback.py
Version: 1.2.2
Objective: Updates the master targets.json with successful observation dates extracted from QC reports.
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = PROJECT_ROOT / "core" / "postflight" / "data" / "qc_report.json"
TARGETS_PATH = PROJECT_ROOT / "data" / "targets.json"

def apply_feedback():
    if not REPORT_PATH.exists(): 
        return
        
    with open(REPORT_PATH, 'r') as f:
        data = json.load(f)
        qc_results = data.get("results", [])
        
    if not TARGETS_PATH.exists(): 
        return
        
    with open(TARGETS_PATH, 'r') as f:
        targets = json.load(f)

    successful_targets = [r['target'] for r in qc_results if r.get('status') == "PASS"]
    now_str = datetime.now().strftime("%Y-%m-%d")

    for t in targets:
        if t.get('star_name') in successful_targets:
            t['last_observed'] = now_str

    with open(TARGETS_PATH, 'w') as f:
        json.dump(targets, f, indent=4)

if __name__ == "__main__":
    apply_feedback()
