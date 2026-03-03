#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/librarian.py
Version: 2.4.0 (Photometry Briefing Grade)
Objective: Reconciles verified FITS data and reports Bayer/Gain status.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

class Librarian:
    def __init__(self):
        self.root = Path(__file__).resolve().parents[2]
        self.ledger_path = self.root / "data/ledger.json"
        self.report_path = self.root / "data/flight_report.json"
        self.targets_path = self.root / "data/targets.json"
        self.plan_path = self.root / "data/tonights_plan.json"

    def _get_vampire_budget(self):
        month = datetime.now().month
        if month in [12, 1]: return 11.0    
        if month in [3, 4, 9, 10]: return 7.5 
        return 8.0

    def reconcile_ledger(self):
        """Morning Reconciliation: Updates Ledger from FITS Verified Report."""
        if not self.report_path.exists():
            print("⚠️ Librarian: No verified report found.")
            return

        with open(self.report_path, 'r') as f:
            report = json.load(f)
        with open(self.ledger_path, 'r') as f:
            ledger = json.load(f)

        for entry in report.get("completed_targets", []):
            name = entry.get("star_name")
            if name in ledger["entries"]:
                # Update with verified photometry metadata
                ledger["entries"][name].update({
                    "status": entry["status"],
                    "last_success": entry.get("completed_at"),
                    "metadata": entry.get("metadata", {})
                })

        with open(self.ledger_path, 'w') as f:
            json.dump(ledger, f, indent=4)
        
        self.generate_morning_briefing(report)

    def generate_morning_briefing(self, report):
        """Displays Bayer, Gain, and WCS status for the session."""
        width = 60
        v_window = self._get_vampire_budget()
        targets = report.get("completed_targets", [])

        print("\n" + "="*width)
        print(f"🔭 FEDERATION OBSERVATORY: MORNING BRIEFING | Window: {v_window}h")
        print("="*width)
        print(f"{'TARGET':<15} | {'STATUS':<10} | {'GAIN':<6} | {'BAYER':<6} | {'WCS'}")
        print("-"*width)

        for t in targets:
            meta = t.get("metadata", {})
            wcs = "✅" if meta.get("wcs_verified") else "❌"
            print(f"{t['star_name']:<15} | {t['status']:<10} | {meta.get('gain'):<6} | {meta.get('bayer'):<6} | {wcs}")

        print("="*width + "\n")

if __name__ == "__main__":
    lib = Librarian()
    if "--reconcile" in sys.argv: lib.reconcile_ledger()
