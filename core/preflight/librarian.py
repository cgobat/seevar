#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/librarian.py
Version: 2.3.0 (Self-Cleaning Grade)
Objective: Manages the 9-day backlog and flushes the queue during morning reconciliation.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

class Librarian:
    def __init__(self):
        self.root = Path(__file__).resolve().parents[2]
        self.targets_path = self.root / "data/targets.json"
        self.ledger_path = self.root / "data/ledger.json"
        self.plan_path = self.root / "data/tonights_plan.json"
        self.report_path = self.root / "data/flight_report.json"

    def _get_vampire_budget(self):
        month = datetime.now().month
        if month in [12, 1]: return 11.0    
        if month in [3, 4, 9, 10]: return 7.5 
        if month in [5, 6, 7]: return 0.0     
        return 8.0

    def generate_menu_and_plan(self):
        """Tiers 2 & 3: Creates the fresh afternoon Flight Contract."""
        budget = self._get_vampire_budget()
        limit = int((budget * 60) / 10)
        
        with open(self.targets_path, 'r') as f:
            master = json.load(f).get("targets", [])
        with open(self.ledger_path, 'r') as f:
            ledger = json.load(f)

        pending = [n for n, d in ledger["entries"].items() if d["status"] == "PENDING"]
        plan_targets = [t for t in master if t.get('star_name') in pending][:limit]

        plan = {
            "header": {
                "objective": f"The Flight Contract for {datetime.now().strftime('%Y-%m-%d')}",
                "slice_size": len(plan_targets),
                "vampire_hours": budget
            },
            "targets": plan_targets
        }

        with open(self.plan_path, 'w') as f:
            json.dump(plan, f, indent=4)
        print(f"🚀 Librarian: Afternoon plan signed for {len(plan_targets)} targets.")

    def reconcile_ledger(self):
        """Morning Reconciliation: Updates the Register and FLUSHES the queue."""
        STRIKE_LIMIT = 3
        if not self.report_path.exists():
            print("⚠️ Librarian: No flight report found. Skipping reconciliation.")
            self._flush_queue()
            return

        with open(self.report_path, 'r') as f:
            report = json.load(f)
        with open(self.ledger_path, 'r') as f:
            ledger = json.load(f)

        for entry in report.get("completed_targets", []):
            name = entry.get("star_name")
            if name in ledger["entries"]:
                target = ledger["entries"][name]
                if entry.get("status") == "COMPLETED":
                    target.update({"status": "COMPLETED", "last_success": entry.get("completed_at"), "attempts": 0})
                else:
                    target["attempts"] += 1
                    if target["attempts"] >= STRIKE_LIMIT: target["status"] = "FLAGGED"

        ledger["header"]["last_updated"] = datetime.now().isoformat()
        with open(self.ledger_path, 'w') as f:
            json.dump(ledger, f, indent=4)

        # Archive the evidence
        archive = self.root / f"logs/archive/report_{datetime.now().strftime('%Y%m%d')}.json"
        os.makedirs(archive.parent, exist_ok=True)
        self.report_path.rename(archive)
        
        self.generate_morning_briefing()
        self._flush_queue()

    def _flush_queue(self):
        """Clears the Flight Contract to prevent stale missions."""
        if self.plan_path.exists():
            flush_data = {
                "header": {
                    "objective": "FLUSHED: Waiting for Afternoon Planning",
                    "flushed_at": datetime.now().isoformat()
                },
                "targets": []
            }
            with open(self.plan_path, 'w') as f:
                json.dump(flush_data, f, indent=4)
            print("🧹 Librarian: Queue flushed. Ready for fresh afternoon slice.")

    def generate_morning_briefing(self):
        """Standard Observatory Summary Output."""
        with open(self.ledger_path, 'r') as f:
            ledger = json.load(f)
        width = 50
        completed = sum(1 for d in ledger["entries"].values() if d["status"] == "COMPLETED")
        print("\n" + "="*width + "\n🔭 MORNING BRIEFING: Survey Progress")
        print(f"✅ Targets Secured: {completed} / {ledger['header']['target_count']}")
        print("="*width + "\n")

if __name__ == "__main__":
    lib = Librarian()
    if "--reconcile" in sys.argv: lib.reconcile_ledger()
    else: lib.generate_menu_and_plan()
