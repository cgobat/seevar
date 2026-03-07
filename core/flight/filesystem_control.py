#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/filesystem_control.py
Version: 1.2.0
Objective: Optimized S30 Samba management and image harvesting with performance indexing.
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path

try:
    import tomllib
except ImportError:
    import toml as tomllib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("FilesystemControl")

# Standardized Paths
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "config.toml"
MOUNT_PATH = BASE_DIR / "s30_storage"
IMAGE_STORAGE = BASE_DIR / "images"

def ensure_mount():
    """Verifies or establishes the Samba connection to the Seestar eMMC."""
    if os.path.ismount(str(MOUNT_PATH)):
        return True
    
    logger.info("📡 Attempting to mount S30 internal storage...")
    try:
        if not CONFIG_PATH.exists():
            logger.error("❌ config.toml missing. Cannot find IP address.")
            return False

        with open(CONFIG_PATH, "rb") as f:
            cfg = tomllib.load(f)
        
        ip = cfg.get('hardware', {}).get('ip_address')
        if not ip:
            logger.error("❌ No IP address found in config.toml [hardware] section.")
            return False

        # Mount command using recommended S30 parameters
        cmd = [
            "sudo", "mount", "-t", "cifs", 
            "-o", f"username=guest,password=123456789,vers=3.0,uid={os.getuid()},gid={os.getgid()}", 
            f"//{ip}/EMMC Images", str(MOUNT_PATH)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info("✅ S30 Storage Mounted successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Mount failed: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected mount error: {e}")
        return False

def harvest_latest_images(purge=False):
    """Identifies and moves new images from the telescope to local storage."""
    if not ensure_mount():
        return []

    IMAGE_STORAGE.mkdir(exist_ok=True)
    
    harvested = []
    # Search specifically in MyWorks for FITS and JPG/PNG
    works_path = MOUNT_PATH / "MyWorks"
    if not works_path.exists():
        logger.warning("⚠️ MyWorks directory not found on mount.")
        return []

    # Efficiently find files modified in the last 24 hours (or just use latest)
    # Here we look for all FITS files as they are the primary science goal
    for file_path in works_path.rglob("*.*"):
        if file_path.suffix.lower() in ['.fits', '.jpg', '.png']:
            dest = IMAGE_STORAGE / file_path.name
            if not dest.exists():
                logger.info(f"🚚 Harvesting: {file_path.name}")
                shutil.copy2(file_path, dest)
                harvested.append(str(dest))
                
                if purge:
                    try:
                        file_path.unlink()
                        logger.info(f"🧹 Purged from S30: {file_path.name}")
                    except Exception as e:
                        logger.warning(f"Could not purge {file_path.name}: {e}")

    return harvested

if __name__ == "__main__":
    files = harvest_latest_images()
    print(f"✅ Harvest Complete. {len(files)} new assets secured.")
