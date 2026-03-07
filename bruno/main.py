#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: /home/ed/seestar_organizer/bruno/main.py
Version: 1.0.2
Objective: Central entry point for Seestar logic research and control.
"""

import os
import sys
from core_api import SeestarAPI

def menu():
    api = SeestarAPI()
    while True:
        print("\n=== SEESTAR RESEARCH & CONTROL CENTER ===")
        print("1. Run Preflight Safety Check")
        print("2. Launch Real-Time Dashboard")
        print("3. Start Automated Session (GoTo/Solve/Stack)")
        print("4. Exit")
        
        choice = input("\nSelect Option: ")

        if choice == '1':
            from preflight_check import run_preflight
            run_preflight()
        elif choice == '2':
            os.system("python3 dashboard_poll.py")
        elif choice == '3':
            from session_manager import SessionManager
            try:
                target = input("Target Name: ")
                ra = float(input("RA (decimal): "))
                dec = float(input("DEC (decimal): "))
                mgr = SessionManager()
                mgr.run_sequence(target, ra, dec)
            except ValueError:
                print("Invalid numerical input.")
        elif choice == '4':
            break

if __name__ == "__main__":
    menu()
