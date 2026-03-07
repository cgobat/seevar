#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/librarian.py
Version: 2.2.0
Objective: Securely harvest binary FITS to RAID1; prepare for NAS archival.
"""

import os
import logging
from pathlib import Path
from astropy.io import fits
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] 📚 %(message)s')
logger = logging.getLogger("Librarian")

class Librarian:
    def __init__(self, vault_path="data/local_buffer"):
        """
        Initializes the Librarian on the RAID1 'data/' mount.
        """
        self.vault = Path(vault_path)
        self.vault.mkdir(parents=True, exist_ok=True)
        # NAS target for final monthly reports
        self.nas_archive = Path("/mnt/astronas/AAVSO-reports")

    def audit_header(self, filepath):
        """Forensics: Ensure the 'Diamond' is valid FITS data."""
        try:
            with fits.open(filepath) as hdul:
                hdr = hdul[0].header
                required = ['RA', 'DEC', 'OBJECT', 'EXPTIME']
                if not all(k in hdr for k in required):
                    logger.warning(f"⚠️ Header gaps in {filepath.name}")
                return True
        except Exception as e:
            logger.error(f"❌ Corruption in {filepath.name}: {e}")
            return False

    def secure_frame(self, binary_content, target_name):
        """Writes binary stream from Pilot to RAID1."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{target_name.replace(' ', '_')}_{timestamp}_RAW.fits"
        target_path = self.vault / filename

        try:
            with open(target_path, "wb") as f:
                f.write(binary_content)
            
            if self.audit_header(target_path):
                logger.info(f"💎 Vaulted to RAID1: {filename}")
                return target_path
            return None
        except Exception as e:
            logger.error(f"❌ RAID1 Write Failure: {e}")
            return None

    def archive_to_nas(self, month_str):
        """
        Placeholder for the 'AAVSO Month' archival.
        Example month_str: '03-2026'
        """
        dest = self.nas_archive / month_str
        dest.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 NAS Archive path prepared: {dest}")
        # Logic for moving processed fits to follow...

if __name__ == "__main__":
    lib = Librarian()
    print(f"Librarian active. RAID1 Vault: {lib.vault}")
