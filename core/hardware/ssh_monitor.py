#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/hardware/ssh_monitor.py
Version: 1.1.0
Objective: Establish an SSH connection to the Seestar SOC (ARM) to stream real-time logs for reverse-engineering port 4700 Sovereign commands. Includes an interactive menu for log selection.
"""

import sys
import tomllib
import paramiko
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = PROJECT_ROOT / "config.toml"

def get_seestar_ip() -> str:
    """Extract the IP address from config.toml."""
    if not CONFIG_FILE.exists():
        print(f"[ERROR] Config file not found: {CONFIG_FILE}")
        sys.exit(1)
        
    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)
        
    seestars = config.get("seestars", [])
    if not seestars:
        print("[ERROR] No [[seestars]] entries found in config.toml.")
        sys.exit(1)
        
    ip = seestars[0].get("ip")
    if not ip or ip == "TBD":
        print("[ERROR] No valid IP address defined for the first telescope in config.toml.")
        sys.exit(1)
        
    return ip

def select_log_command() -> str:
    """Prompt the user to select which log stream to monitor."""
    print("\nSelect log stream to monitor:")
    print("  1) systemd journal (journalctl -f)")
    print("  2) Kernel ring buffer (dmesg -w)")
    print("  3) Custom command (e.g., tail -f /var/log/syslog)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        return "journalctl -f"
    elif choice == '2':
        return "dmesg -w"
    elif choice == '3':
        cmd = input("Enter custom command: ").strip()
        return cmd if cmd else "journalctl -f"
    else:
        print("[!] Invalid choice. Defaulting to journalctl -f")
        return "journalctl -f"

def monitor_logs(ip: str, log_cmd: str, username: str = "pi", password: str = "raspberry"):
    """Establish SSH connection and stream the selected log."""
    print(f"\n[*] Initializing SSH connection to {ip} as {username}...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(ip, username=username, password=password, timeout=10)
        print(f"[SUCCESS] Connected to ARM SOC. Tailing logs via: {log_cmd}\n")
        print("-" * 60)
        
        stdin, stdout, stderr = client.exec_command(log_cmd, get_pty=True)
        
        for line in iter(stdout.readline, ""):
            print(line, end="")
            
    except KeyboardInterrupt:
        print("\n[*] Terminating SSH monitor pipeline...")
    except paramiko.AuthenticationException:
        print("\n[ERROR] Authentication failed. ZWO might have changed the default pi/raspberry credentials.")
    except Exception as e:
        print(f"\n[ERROR] Connection pipeline failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🔭 SeeVar Log Monitor v1.1.0")
    print("=" * 30)
    
    target_ip = get_seestar_ip()
    print(f"[*] Target IP resolved: {target_ip}")
    
    cmd = select_log_command()
    monitor_logs(target_ip, cmd)
