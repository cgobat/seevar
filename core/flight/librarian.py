#!/usr/bin/env python3
import json, os, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TARGET_FILE = PROJECT_ROOT / "data" / "targets.json"

class TargetLibrarian:
    def __init__(self):
        self.queue = []

    def inject_aavso(self):
        """Re-injecting the French/International Alerts."""
        self.queue.append({"name": "[FR] T CRB", "priority": "CRITICAL"})

    def inject_knvws(self):
        """The Dutch 'Programma' Stars."""
        for s in ["SS Cyg", "U Gem", "Z Cam", "RR Lyr"]:
            self.queue.append({"name": f"[NL] {s}", "priority": "NORMAL"})

    def save(self):
        with open(TARGET_FILE, 'w') as f:
            json.dump(self.queue, f, indent=2)
        return len(self.queue)

if __name__ == "__main__":
    lib = TargetLibrarian()
    lib.inject_knvws()
    lib.inject_aavso()
    print(f"Librarian: {lib.save()} targets synced.")
