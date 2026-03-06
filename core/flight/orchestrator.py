#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/orchestrator.py
Version: 2.4.0
Objective: Inject advanced hardware state (Dew Heater, Darks, LP Filter) alongside the target schedule.
"""

import os
import sys
import json
import time
import socket
import tempfile
import requests
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("FlightMaster")

class FlightMaster:
    def __init__(self):
        self.root = Path(__file__).resolve().parents[2]
        self.plan_path = self.root / "data/tonights_plan.json"
        self.state_file = self.root / "data/system_state.json"
        
        # Target the SSC Bridge's queue manager on Index 1
        self.bridge_schedule_url = "http://127.0.0.1:5432/1/schedule"

    def _atomic_state(self, state, sub, msg):
        data = {
            "state": state, "sub": sub, "msg": msg, 
            "updated": datetime.now().strftime('%H:%M:%S')
        }
        dir_name = self.state_file.parent
        dir_name.mkdir(parents=True, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, self.state_file)

    def _check_safety(self):
        self._atomic_state("PREFLIGHT", "BRIDGE_CHECK", "Pinging SSC Bridge...")
        try:
            with socket.create_connection(("127.0.0.1", 5432), timeout=1):
                return True
        except Exception:
            self._atomic_state("ERROR", "BRIDGE_OFFLINE", "Port 5432 unreachable.")
            return False

    def _triage_manifest(self):
        if not self.plan_path.exists():
            return []
        with open(self.plan_path, 'r') as f:
            plan = json.load(f)

        approved = []
        for t in plan.get("targets", []):
            if t.get("solar_conjunction") is True or "not observable" in t.get("observability_times", "").lower():
                continue
            approved.append(t)
        return approved

    def inject_to_bridge(self, targets):
        self._atomic_state("SLEWING", "INJECTING", f"Dispatching {len(targets)} targets to UI Queue...")
        
        # 1. Clear existing bridge schedule
        try:
            requests.post(f"{self.bridge_schedule_url}/clear", timeout=5)
            logger.info("🧹 Cleared old SSC schedule.")
        except: pass

        # 2. Inject Startup Sequence (Darks enabled)
        try:
            requests.post(f"{self.bridge_schedule_url}/startup", data={"auto_focus": "on", "dark_frames": "on"}, timeout=5)
            logger.info("⚙️ Injected Startup Sequence (Autofocus + Darks).")
        except Exception as e:
            logger.error(f"❌ Failed to inject startup: {e}")

        # 3. Inject Dew Heater (Set to 50%)
        try:
            requests.post(f"{self.bridge_schedule_url}/dew-heater", data={"power": "50", "action": "append"}, timeout=5)
            logger.info("🔥 Injected Dew Heater (50%).")
        except Exception as e:
            logger.warning(f"⚠️ Failed to inject Dew Heater: {e}")

        # 4. Append Targets to Bridge Queue
        for t in targets:
            name = t.get('star_name', 'Unknown')
            # Map LP filter explicitly based on the target payload
            lp_param = "on" if t.get('use_lp_filter') else "off"
            
            payload = {
                "targetName": name, 
                "ra": t.get('ra'), 
                "dec": t.get('dec'),
                "useJ2000": "on", 
                "panelTime": str(t.get('exposure_time_sec', 60)), 
                "gain": str(t.get('gain', 80)), 
                "useLPFilter": lp_param,
                "action": "append"
            }
            try:
                res = requests.post(f"{self.bridge_schedule_url}/image", data=payload, timeout=5)
                if res.status_code == 200:
                    logger.info(f"✅ Appended to UI Queue: {name} (LP: {lp_param})")
                else:
                    logger.error(f"❌ UI Queue rejected {name}: {res.status_code}")
            except Exception as e:
                logger.error(f"❌ Failed to append {name}: {e}")

        # 5. Inject Park Sequence
        try:
            requests.post(f"{self.bridge_schedule_url}/park", data={"action": "append"}, timeout=5)
            logger.info("🅿️ Injected Park Sequence.")
        except Exception as e:
            logger.error(f"❌ Failed to inject park: {e}")

        self._atomic_state("INTEGRATING", "ACTIVE", f"Tracking {len(targets)} targets.")

    def run_mission(self):
        logger.info("🚀 S30-PRO FEDERATION: FLIGHT MASTER STARTING")
        if not self._check_safety(): return
        targets = self._triage_manifest()
        if targets: self.inject_to_bridge(targets)
        logger.info("🏁 FLIGHT MASTER: MISSION HANDOVER COMPLETE")

if __name__ == "__main__":
    fm = FlightMaster()
    fm.run_mission()
