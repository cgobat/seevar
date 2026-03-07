#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/pilot.py
Version: 2.3.0
Objective: Executive control of the S30-PRO; integrates RAID1 storage and NAS-aware syncing.
"""

import sys
import time
import json
import logging
from pathlib import Path

# Aligning with PROJECT_ROOT from FILE_MANIFEST.md
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from logic.STATE_MACHINE import SovereignFSM
from core.postflight.librarian import Librarian

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] 👩‍✈️ %(message)s')
logger = logging.getLogger("Pilot")

class Pilot:
    def __init__(self):
        self.fsm = SovereignFSM()
        # Librarian defaults to our RAID1: data/local_buffer
        self.librarian = Librarian(vault_path=PROJECT_ROOT / "data/local_buffer")
        
        self.qc_dir = PROJECT_ROOT / "data/qc"
        self.qc_dir.mkdir(parents=True, exist_ok=True)
        
        # Home status detection
        self.nas_path = Path("/mnt/astronas/AAVSO-reports")
        self.is_home = self.nas_path.exists() and os.access(self.nas_path, os.W_OK)
        
        if self.is_home:
            logger.info("🏠 Location: HOME. NAS Archiving enabled for post-flight.")
        else:
            logger.warning("🛰️ Location: FIELD. RAID1 will act as primary Black Box.")

    def _update_qc_ledger(self, entry):
        """Rotates QC logs daily to prevent SD card bloat."""
        datestamp = time.strftime("%Y-%m-%d")
        qc_file = self.qc_dir / f"qc_{datestamp}.json"
        
        data = []
        if qc_file.exists():
            try:
                with open(qc_file, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                data = []
        
        data.append(entry)
        with open(qc_file, 'w') as f:
            json.dump(data, f, indent=4)

    def fly_mission(self, target_name, ra, dec, exp_ms, count):
        """The core Photometry execution loop."""
        if not self.fsm.check_veto_sensors():
            logger.critical("STOP: Hardware Safety Veto triggered.")
            return

        self.fsm.initialize_hardware()
        
        if not self.fsm.navigate_to_target(ra, dec):
            logger.error(f"Navigation Failure: {target_name} is unreachable.")
            return

        logger.info(f"Science Phase: {count} x {exp_ms/1000}s frames for {target_name}")
        
        for i in range(1, count + 1):
            raw_binary = self.fsm.capture_science_frame(exp_ms)
            
            if raw_binary:
                # Direct to RAID1
                fits_path = self.librarian.secure_frame(raw_binary, target_name)
                
                if fits_path:
                    self._update_qc_ledger({
                        "file": fits_path.name,
                        "target": target_name,
                        "status": "PASS",
                        "timestamp": time.strftime("%H:%M:%S")
                    })
            else:
                logger.error(f"Frame {i} Lost. Verify Alpaca Bridge.")

        # POST-FLIGHT: If we are home, we can trigger the Librarian's NAS archive
        if self.is_home:
            month_tag = time.strftime("%m-%Y")
            self.librarian.archive_to_nas(month_tag)

if __name__ == "__main__":
    mission_pilot = Pilot()
    # Example: Run 5 frames of CH Cyg
    mission_pilot.fly_mission("CH Cyg", 291.137, 50.241, 60000, 5)
