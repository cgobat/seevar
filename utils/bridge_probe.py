#!/usr/bin/env python3
import socket

def probe_bridge(ip="127.0.0.1", port=5555):
    print(f"🔍 Probing Alpaca Bridge on {ip}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((ip, port))
        print(f"✅ SUCCESS: Bridge is listening on Port {port}.")
        s.close()
    except Exception as e:
        print(f"❌ FAIL: Port {port} is closed or unreachable. Error: {e}")

if __name__ == "__main__":
    probe_bridge()
