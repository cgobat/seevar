#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/fsm.py
Version: 1.0.0
Objective: The Finite State Machine governing S30-PRO Sovereign Operations.
"""

import logging

logger = logging.getLogger("FSM")

class SovereignFSM:
    def __init__(self):
        # Aligned with the Bridge states: IDLE, WORKING, SUCCESS, ERROR
        self.state = "IDLE"
        logger.info(f"🧠 FSM Initialized in state: {self.state}")

    def update(self, new_state):
        """Transition the internal state representation."""
        self.state = new_state
        logger.info(f"🔄 FSM State updated to: {self.state}")

    def get_status(self):
        """Return current operational state."""
        return self.state
