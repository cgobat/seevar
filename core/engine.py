#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/engine.py
Version: 1.0.0
Objective: Monolithic process manager to run the Dashboard and Telemetry Daemon as a single unified service.
"""

import os
import sys
import time
import signal
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_SCRIPT = os.path.join(BASE_DIR, "dashboard/dashboard.py")
TELEMETRY_SCRIPT = os.path.join(BASE_DIR, "flight/telemetry_daemon.py")

processes = []

def terminate_processes(signum, frame):
    print("\n🛑 Federation Engine shutting down... Terminating subsystems.")
    for p in processes:
        p.terminate()
    time.sleep(1)
    print("✅ All systems offline.")
    sys.exit(0)

def main():
    # Catch termination signals from the user (Ctrl+C) or Systemd
    signal.signal(signal.SIGINT, terminate_processes)
    signal.signal(signal.SIGTERM, terminate_processes)

    print("🚀 Igniting the S30-PRO Federation Engine...")

    # 1. Start the Web Dashboard
    print("🌐 Spinning up Web Dashboard (Port 5050)...")
    p_dash = subprocess.Popen([sys.executable, DASHBOARD_SCRIPT])
    processes.append(p_dash)

    # 2. Start the Telemetry Daemon
    print("📡 Spinning up Hardware Telemetry Daemon...")
    p_telem = subprocess.Popen([sys.executable, TELEMETRY_SCRIPT])
    processes.append(p_telem)

    print("✅ Engine running natively. Supervised subsystems are active.")

    # Keep the main supervisor thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
