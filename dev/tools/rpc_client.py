#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: ~/seevar/dev/tools/rpc_client.py
Version: 2.0.0
Objective: Interactive JSON-RPC client for Seestar port 4700 using pre-built sovereign payloads.
"""
import socket
import json
import os
import sys

def load_target_ip():
    config_path = os.path.expanduser("~/seevar/config.toml")
    try:
        import tomllib
        with open(config_path, "rb") as f:
            return tomllib.load(f).get("seestar", {}).get("ip_address", "10.0.0.1")
    except ImportError:
        import tomli
        with open(config_path, "rb") as f:
            return tomli.load(f).get("seestar", {}).get("ip_address", "10.0.0.1")
    except Exception as e:
        print(f"Error reading config.toml: {e}")
        sys.exit(1)

def load_payloads():
    payloads_path = os.path.expanduser("~/seevar/data/sovereign_payloads.json")
    try:
        with open(payloads_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading payloads: {e}\nPlease run sovereign_payload_builder.py first.")
        sys.exit(1)

def send_command(ip, payload):
    port = 4700
    print(f"\n[>] Sending to {ip}:{port}:\n{json.dumps(payload, indent=2)}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect((ip, port))
            s.sendall(json.dumps(payload).encode('utf-8'))
            
            response = s.recv(4096)
            print("[<] Response:")
            print(json.dumps(json.loads(response.decode('utf-8')), indent=2))
    except Exception as e:
        print(f"[!] Connection failed: {e}")

def main():
    ip = load_target_ip()
    categories = load_payloads()
    
    # Flatten the payload dictionary for the interactive menu
    flat_payloads = []
    for cat, methods in categories.items():
        for method_name, payload in methods.items():
            flat_payloads.append((cat, method_name, payload))
            
    while True:
        print("\n--- Seestar Sovereign RPC Client ---")
        print(f"Target IP: {ip}")
        print("0. Exit")
        print("1. Custom Handshake (pi_is_verified)")
        
        for idx, (cat, method, _) in enumerate(flat_payloads, start=2):
            print(f"{idx}. [{cat}] {method}")
            
        choice = input("\nSelect a command to send: ")
        
        if choice == '0':
            print("Exiting.")
            break
        elif choice == '1':
            send_command(ip, {"id": 0, "method": "pi_is_verified", "jsonrpc": "2.0"})
        else:
            try:
                idx = int(choice) - 2
                if 0 <= idx < len(flat_payloads):
                    _, _, payload = flat_payloads[idx]
                    send_command(ip, payload)
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")

if __name__ == "__main__":
    main()
