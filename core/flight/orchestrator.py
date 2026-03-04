#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Objective: Single-Point Flight Master. 
Logic: Safety -> Manifest Triage -> Atomic State Tracking -> Alpaca Injection.
Version: 2.1.0 (Hardened Federation Standard)
"""

import os, sys, json, time, requests, logging, socket, tempfile
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("FlightMaster")

class FlightMaster:
    def __init__(self):
        self.root = Path(__file__).resolve().parents[2]
        self.plan_path = self.root / "data/tonights_plan.json"
        # Standardized state path for Dashboard visibility
        self.state_file = self.root / "data/system_state.json"
        self.bridge_url = "http://127.0.0.1:5432/0/schedule"

    def _atomic_state(self, state, sub, msg):
        """Atomic write pattern: prevents Dashboard read-collisions."""
        data = {
            "state": state, 
            "sub": sub, 
            "msg": msg, 
            "updated": datetime.now().strftime('%H:%M:%S')
        }
        dir_name = self.state_file.parent
        fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, self.state_file)

    def _check_safety(self):
        self._atomic_state("PREFLIGHT", "BRIDGE_CHECK", "Pinging Alpaca Bridge...")
        try:
            with socket.create_connection(("127.0.0.1", 5432), timeout=1):
                logger.info("📡 Alpaca Bridge: ONLINE")
                return True
        except:
            self._atomic_state("ERROR", "BRIDGE_OFFLINE", "Port 5432 unreachable.")
            logger.error("❌ Alpaca Bridge: OFFLINE.")
            return False

    def _triage_manifest(self):
        """The 'Reality Filter' logic: Solar and Horizon Veto."""
        if not self.plan_path.exists():
            self._atomic_state("ERROR", "PLAN_MISSING", "tonights_plan.json not found.")
            return []

        with open(self.plan_path, 'r') as f:
            plan = json.load(f)

        raw_targets = plan.get("targets", [])
        approved = []

        self._atomic_state("EVALUATING", "TRIAGE", f"Checking {len(raw_targets)} targets...")

        for t in raw_targets:
            name = t.get('star_name') or "Unknown"
            
            # 1. Solar Conjunction Veto (Hardware Safety)
            if t.get("solar_conjunction") is True:
                logger.warning(f"  ⏭️ Skipping {name}: Solar Conjunction")
                continue
            
            # 2. Horizon Veto (Science Integrity)
            obs = t.get("observability_times", "")
            if isinstance(obs, str) and "not observable" in obs.lower():
                logger.warning(f"  ⏭️ Skipping {name}: Below Horizon")
                continue

            approved.append(t)
            
        logger.info(f"🎯 Triage Complete: {len(approved)}/{len(raw_targets)} targets approved.")
        return approved

    def inject_to_bridge(self, targets):
        """Handover to the Alpaca Proxy schedule."""
        self._atomic_state("SLEWING", "INJECTING", f"Dispatching {len(targets)} targets...")
        
        # Clear existing schedule
        try:
            requests.post(f"{self.bridge_url}/clear", timeout=2)
        except: pass

        for t in targets:
            name = t.get('star_name') or t.get('name')
            try:
                # Sequence: Startup -> Image
                requests.post(f"{self.bridge_url}/startup", data={"auto_focus":"on","dark_frames":"off"})
                requests.post(f"{self.bridge_url}/image", data={
                    "targetName": name, 
                    "ra": t['ra'], "dec": t['dec'],
                    "useJ2000": "on", "panelTime": "240", 
                    "gain": "80", "action": "append"
                })
                logger.info(f"  ✅ Dispatched: {name}")
            except Exception as e:
                logger.error(f"  ❌ Failed to inject {name}: {e}")

        self._atomic_state("INTEGRATING", "ACTIVE", f"Tracking {len(targets)} targets.")

    def run_mission(self):
        logger.info("🚀 S30-PRO FEDERATION: FLIGHT MASTER STARTING")
        if not self._check_safety(): return
        
        targets = self._triage_manifest()
        if not targets: 
            self._atomic_state("IDLE", "EMPTY_PLAN", "No observable targets.")
            return

        self.inject_to_bridge(targets)
        logger.info("🏁 FLIGHT MASTER: MISSION HANDOVER COMPLETE")

if __name__ == "__main__":
    fm = FlightMaster()
    fm.run_mission()
