#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: logic/session_manager.py
Version: 1.0.0
Objective: Orchestrates the automated GoTo, Solve, Sync, and Stack sequence.
"""

import time
import logging
from core_api import SeestarAPI

class SessionManager:
    def __init__(self):
        self.api = SeestarAPI()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def run_sequence(self, target_name, ra, dec):
        logging.info(f"Starting session for target: {target_name}")

        # 1. Clear State: Stop any active view or stack processes
        logging.info("Stopping active view/locks...")
        self.api.post_action("iscope_stop_view")
        time.sleep(2)

        # 2. Slewing: Set target name and initiate GoTo
        logging.info(f"Slewing to RA: {ra}, DEC: {dec}...")
        # Note: Using set_app_setting for target naming as seen in Bruno specs
        self.api.post_action("set_app_setting", parameters={"goto_target_name": target_name})
        self.api.post_action("scope_sync", parameters={"ra": ra, "dec": dec})
        
        # Wait for slew to stabilize (simplified wait logic)
        time.sleep(10)

        # 3. Plate Solving: Verify and align
        logging.info("Initiating Plate Solve...")
        self.api.post_action("start_solve")
        
        # Poll for solve result
        solved = False
        for _ in range(15):  # 30-second timeout
            result = self.api.post_action("get_solve_result")
            if result.get("Value", {}).get("code") == 0:
                logging.info("Plate Solve Successful.")
                solved = True
                break
            time.sleep(2)

        if not solved:
            logging.error("Plate Solve failed. Aborting session.")
            return False

        # 4. Final Sync: Sync coordinates to actual solve result
        last_solve = self.api.post_action("get_last_solve_result")
        res = last_solve.get("Value", {}).get("result", {})
        if res:
            logging.info("Syncing mount to solved coordinates...")
            self.api.sync_coordinates(res.get("ra"), res.get("dec"))

        # 5. Tracking and Stacking
        logging.info("Enabling tracking and starting stack...")
        self.api.post_action("scope_set_track_state", parameters=True)
        # Use start_stack macro dialect
        self.api.post_action("start_stack", parameters={"gain": 80, "restart": True}, is_method_sync=False)

        logging.info("Session sequence complete. Stacking in progress.")
        return True

if __name__ == "__main__":
    # Example: Target M42 (Orion Nebula)
    # Coordinates for testing purposes; ensure these are valid for your current sky
    mgr = SessionManager()
    mgr.run_sequence("M42", 5.58, -5.38)
