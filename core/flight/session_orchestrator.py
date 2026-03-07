#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/session_orchestrator.py
Version: 1.2.0
Objective: Executive Orchestrator. Ties Flight operations to Postflight science.
"""

import sys
import logging
import time
from pathlib import Path

# Aligning with PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from core.flight.pilot import Pilot
from core.postflight.science_processor import ScienceProcessor

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [ORCHESTRATOR] 💎 %(message)s'
)
logger = logging.getLogger("Executive")

class Orchestrator:
    def __init__(self):
        self.pilot = Pilot()
        self.processor = ScienceProcessor()

    def run_mission(self, target_name, ra, dec, exp_ms, count):
        """The Complete Sovereignty Lifecycle: Acquisition -> Extraction."""
        logger.info(f"🌌 Starting mission for: {target_name}")
        
        # 1. Acquisition (The Pilot commands the Librarian to RAID1)
        self.pilot.fly_mission(target_name, ra, dec, exp_ms, count)
        
        # 2. Science Extraction (The Siril-backed Green Squeeze)
        logger.info(f"🧪 Handing over {target_name} to Science Processor...")
        final_fits = self.processor.process_green_stack(target_name.replace(" ", "_"))
        
        if final_fits:
            logger.info(f"🏆 Mission Success. Green-Mono Diamond ready: {final_fits}")
        else:
            logger.error("⚠️ Flight succeeded, but Science processing failed.")

if __name__ == "__main__":
    # Saturday Night Run
    boss = Orchestrator()
    boss.run_mission("T Uma", 188.256, 59.486, 60000, 10)
