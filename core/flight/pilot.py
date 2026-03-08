#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/pilot.py
Version: 2.4.0
Objective: Executive control of the S30-PRO with integrated Simulation Mode.
"""

import logging
from core.flight.fsm import SovereignFSM

logger = logging.getLogger("Pilot")

class Pilot:
    def __init__(self, sim_mode=False):
        self.sim_mode = sim_mode
        self.fsm = SovereignFSM()
        
        if self.sim_mode:
            logger.info("🎮 Pilot initialized in SIMULATION mode.")
        else:
            logger.info("🔭 Pilot initialized in HARDWARE mode.")

    def fly_mission(self, target, ra, dec, exp_time, count):
        """Execute a mission sequence."""
        self.fsm.update("SLEWING")
        print(f"🛰️ [Pilot] Target: {target} | RA: {ra} | DEC: {dec}")
        
        self.fsm.update("EXPOSING")
        print(f"📸 [Pilot] Capturing {count} frames at {exp_time}ms...")
        
        if self.sim_mode:
            print("🧪 [Sim] Generating mock FITS data...")
            
        self.fsm.update("IDLE")
        print(f"🏁 [Pilot] Mission {target} complete.")
        return True
