#!/usr/bin/env python3
import json
from pathlib import Path

TARGETS_FILE = Path("~/seestar_organizer/data/nightly_targets.json").expanduser()

class TargetLibrarian:
    def __init__(self):
        self.queue = {} # Using a dict for easy de-duplication

    def add_target(self, name, ra, dec, origin):
        """Merges targets and detects international priority."""
        if name in self.queue:
            # Multi-tagged!
            self.queue[name]['tags'].append(f"[{origin}]")
            self.queue[name]['priority'] = "CRITICAL"
        else:
            self.queue[name] = {
                "name": name,
                "ra": ra,
                "dec": dec,
                "tags": [f"[{origin}]"],
                "priority": "NORMAL"
            }

    def save(self):
        # Format for the ticker
        formatted = []
        for name, data in self.queue.items():
            tag_str = "".join(data['tags'])
            formatted.append({
                "name": f"{tag_str} {name}",
                "priority": data['priority']
            })
        with open(TARGETS_FILE, 'w') as f:
            json.dump(formatted, f, indent=2)
        return len(formatted)
