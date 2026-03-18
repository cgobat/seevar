#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: dev/utils/mount_guard.py
Version: 1.1.1
Objective: Check if the specified target is mounted and the required data directory exists.
"""

import os
import sys
import argparse

def check_mount(mount_point, required_dir):
    # Check if the base RAID is mounted
    if not os.path.ismount(mount_point):
        return False
    # Check if the data subdirectory exists
    if not os.path.isdir(required_dir):
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SeeVar Mount Guard")
    parser.add_argument("--base", default="/mnt/raid1", help="Base mount point to verify")
    parser.add_argument("--data", default="/mnt/raid1/data", help="Required data directory")
    args = parser.parse_args()

    if check_mount(args.base, args.data):
        print(f"✅ SeeVar: Mount confirmed and data folder present at {args.base}.")
        sys.exit(0)
    else:
        print(f"❌ SeeVar: CRITICAL - Mount {args.base} not mounted or {args.data} missing.")
        sys.exit(1)
