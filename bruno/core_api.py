#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: /home/ed/seestar_organizer/bruno/core_api.py
Version: 1.1.0
Objective: Core API wrapper handling multi-dialect JSON for Seestar S30-PRO.
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
        tid = self._get_next_transaction_id()
        
        if is_method_sync:
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
            return {"error": str(e), "success": False}
