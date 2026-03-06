#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/filesystem_control.py
Version: 1.1.2
Objective: Manage S30 Samba mount and harvest images to a dedicated /images folder.
"""

import os
import sys
import shutil
import glob
import subprocess

try:
    import tomllib
except ImportError:
    import toml as tomllib

# Anchor to the project root dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config.toml")
MOUNT_PATH = os.path.join(BASE_DIR, "s30_storage")
IMAGE_STORAGE = os.path.join(BASE_DIR, "images") # Moved out of /data

def ensure_mount():
    if os.path.ismount(MOUNT_PATH): return True
    try:
        with open(CONFIG_PATH, "rb") as f:
            cfg = tomllib.load(f)
        ip = cfg['hardware']['ip_address']
        cmd = ["sudo", "mount", "-t", "cifs", "-o", f"username=guest,password=123456789,vers=3.0,uid={os.getuid()},gid={os.getgid()}", f"//{ip}/EMMC Images", MOUNT_PATH]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except: return False

def harvest_latest_image(purge=False):
    if not ensure_mount(): return None
    
    # Secure the images folder - exist_ok prevents the crash you saw
    os.makedirs(IMAGE_STORAGE, exist_ok=True)
    
    search_pattern = os.path.join(MOUNT_PATH, "MyWorks", "**", "*.*")
    files = [f for f in glob.glob(search_pattern, recursive=True) if f.lower().endswith(('.fits', '.jpg', '.png'))]
    if not files: return None
    
    files.sort(key=os.path.getmtime, reverse=True)
    latest_file = files[0]
    destination = os.path.join(IMAGE_STORAGE, os.path.basename(latest_file))
    
    shutil.copy2(latest_file, destination)
    if purge: os.remove(latest_file)
    return destination
