#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: logic/dashboard_poll.py
Version: 1.0.1
Objective: Real-time telemetry dashboard for Seestar S30-PRO hardware monitoring.
"""

import time
import os
from core_api import SeestarAPI

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def run_dashboard():
    api = SeestarAPI()
    
    print("Initializing Dashboard... Press Ctrl+C to exit.")
    time.sleep(1)

    try:
        while True:
            state = api.get_state()
            if state.get("ErrorNumber") != 0 or "Value" not in state:
                print(f"Connection Error: {state.get('ErrorMessage', 'Unknown error')}")
                time.sleep(2)
                continue

            v = state["Value"]["result"]
            
            clear_screen()
            print("=== SEESTAR S30-PRO TELEMETRY DASHBOARD ===")
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 43)
            
            # Navigation State
            ra = v.get("mount", {}).get("ra", "N/A")
            dec = v.get("mount", {}).get("dec", "N/A")
            track = "ACTIVE" if v.get("mount", {}).get("tracking") else "OFF"
            print(f"RA: {ra:<15} DEC: {dec:<15}")
            print(f"Tracking: {track:<10} Mode: {v.get('mount', {}).get('move_type', 'none')}")
            
            # Imaging State
            stack_count = v.get("setting", {}).get("stack", {}).get("capt_num", 0)
            print(f"Stacking: {v.get('pi_status', {}).get('is_stacked', 'False'):<8} Total Frames: {stack_count}")
            
            # Hardware Health
            bat = v.get("pi_status", {}).get("battery_capacity", 0)
            temp = v.get("pi_status", {}).get("temp", 0)
            disk = v.get("storage", {}).get("storage_volume", [{}])[0].get("used_percent", 0)
            
            print(f"Battery: {bat}% ({v.get('pi_status', {}).get('charger_status', 'Unknown')})")
            print(f"CPU Temp: {temp:.1f}°C    Disk Used: {disk}%")
            print("-" * 43)
            print("Status: System Active and Operational")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nDashboard Terminated.")

if __name__ == "__main__":
    run_dashboard()
