#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: logic/core_api.py
Version: 1.0.0
Objective: Core API wrapper for Seestar S30-PRO, handling multi-dialect JSON 
payloads and state-safe HTTP communication.
"""

import requests
import json
import logging

class SeestarAPI:
    def __init__(self, ip="127.0.0.1", port=5555, dev_num=1):
        self.base_url = f"http://{ip}:{port}/api/v1/telescope/{dev_num}/action"
        self.session = requests.Session()
        self.client_id = 1
        self.transaction_id = 1000

    def _get_next_transaction_id(self):
        self.transaction_id += 1
        return self.transaction_id

    def post_action(self, action_name, parameters=None, is_method_sync=True):
        """
        Handles the split logic between direct Actions and method_sync wrappers.
        """
        tid = self._get_next_transaction_id()
        
        # Build the payload based on the Seestar "Dialects"
        if is_method_sync:
            # Dialect: method_sync (Used for most GET/SET hardware calls)
            payload = {
                "Action": "method_sync",
                "Parameters": json.dumps({
                    "method": action_name,
                    "params": parameters if parameters is not None else {}
                }),
                "ClientID": self.client_id,
                "ClientTransactionID": tid
            }
        else:
            # Dialect: Direct Action (Used for Mosaic, Shutdown, PlaySound)
            payload = {
                "Action": action_name,
                "Parameters": json.dumps(parameters) if parameters else "{}",
                "ClientID": self.client_id,
                "ClientTransactionID": tid
            }

        try:
            response = self.session.put(self.base_url, data=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Seestar API Error: {e}")
            return {"error": str(e), "success": False}

    # --- High Level Logic Mapped from .bru files ---

    def get_state(self):
        """Unified device telemetry poll."""
        return self.post_action("get_device_state")

    def sync_coordinates(self, ra, dec):
        """Syncs the mount to specific RA/Dec coordinates (Keyed Object dialect)."""
        return self.post_action("scope_sync", parameters=[ra, dec])

    def set_gain(self, value):
        """Sets ISO/Gain (Positional Array dialect, lowercase key)."""
        return self.post_action("set_control_value", parameters=["gain", value])

    def shutdown(self):
        """Executes hardware shutdown sequence."""
        return self.post_action("pi_shutdown", is_method_sync=True)

    def start_mosaic(self, target_name, ra, dec, panels=(2, 2)):
        """Initiates a mosaic sequence (Direct Action dialect)."""
        params = {
            "target_name": target_name,
            "ra": ra,
            "dec": dec,
            "ra_num": panels[0],
            "dec_num": panels[1],
            "is_j2000": True,
            "gain": 80
        }
        return self.post_action("start_mosaic", parameters=params, is_method_sync=False)

if __name__ == "__main__":
    # Quick connectivity test
    api = SeestarAPI()
    print("Testing connection to Seestar...")
    print(api.get_state())
