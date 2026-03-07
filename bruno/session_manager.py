#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: /home/ed/seestar_organizer/bruno/session_manager.py
Version: 1.0.1
Objective: Orchestrates GoTo, Solve, Sync, and Stacking sequences.
"""

import time
import logging
from core_api import SeestarAPI

class SessionManager:
    def __init__(self):
        self.api = SeestarAPI()
        logging.basicConfig(level=logging.INFO)

    def run_sequence(self, target_name, ra, dec):
        logging.info("Clearing active view locks...")
        self.api.post_action("iscope_stop_view")
        time.sleep(2)

        logging.info(f"Slewing to {target_name}...")
        self.api.post_action("set_app_setting", parameters={"goto_target_name": target_name})
        # Keyed Object Dialect for Sync
        self.api.post_action("scope_sync", parameters={"ra": ra, "dec": dec})
        time.sleep(10)

        logging.info("Triggering Plate Solve...")
        self.api.post_action("start_solve")
        
        # Poll for completion
        for _ in range(15):
            res = self.api.post_action("get_solve_result")
            if res.get("Value", {}).get("code") == 0:
                logging.info("Solve Successful. Syncing and Stacking.")
                self.api.post_action("scope_set_track_state", parameters=True)
                self.api.post_action("start_stack", parameters={"gain": 80, "restart": True}, is_method_sync=False)
                return True
            time.sleep(2)
        return False
