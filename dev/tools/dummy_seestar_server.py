#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: ~/seevar/dev/tools/dummy_seestar_server.py
Version: 1.0.0
Objective: Local TCP server simulating the Seestar port 4700 JSON-RPC API for client testing.
"""
import socket
import json
import sys

def start_dummy_server():
    host = '0.0.0.0'
    port = 4700

    print(f"Starting Dummy Seestar Server on {host}:{port}...")
    print("Waiting for RPC client connections (Press Ctrl+C to stop)\n")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen()

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"[{addr[0]}] Client connected.")
                    try:
                        while True:
                            data = conn.recv(4096)
                            if not data:
                                break
                            
                            payload_str = data.decode('utf-8').strip()
                            print(f"\n[<] Received Payload:\n{payload_str}")
                            
                            try:
                                payload = json.loads(payload_str)
                                req_id = payload.get("id", 1)
                                method = payload.get("method", "unknown_method")
                                
                                # Route specific dummy responses based on the method
                                if method == "pi_is_verified":
                                    result = True
                                elif method == "get_device_state":
                                    result = {"device": {"name": "Dummy S30 Pro", "firmware_ver_int": 9999}}
                                elif method == "scope_get_ra_dec":
                                    result = [20.166667, -51.92, 21.268408]
                                elif method == "get_camera_state":
                                    result = {"state": "idle", "name": "Seestar S30", "temp": 15.5}
                                else:
                                    # Catch-all generic response for other commands
                                    result = {"status": "success", "mock_data": f"Acknowledge {method}"}

                                # Build strict JSON-RPC 2.0 response
                                response = {
                                    "jsonrpc": "2.0",
                                    "id": req_id,
                                    "result": result
                                }
                                
                                response_str = json.dumps(response)
                                print(f"[>] Sending Response:\n{response_str}")
                                conn.sendall(response_str.encode('utf-8'))
                                
                            except json.JSONDecodeError:
                                print("[!] Error: Received invalid JSON.")
                                error_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
                                conn.sendall(json.dumps(error_resp).encode('utf-8'))

                    except Exception as e:
                        print(f"[-] Connection error with {addr[0]}: {e}")
                    
                    print(f"[{addr[0]}] Client disconnected.\n")

    except KeyboardInterrupt:
        print("\nShutting down dummy server.")
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_dummy_server()
