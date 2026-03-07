#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/science_processor.py
Version: 2.0.0
Objective: Automate Siril Green-channel extraction for high-precision Photometry.
"""

import os
import logging
from pysiril.siril_interface import SirilInter
from pathlib import Path

logger = logging.getLogger("ScienceProcessor")

class ScienceProcessor:
    def __init__(self, base_work_dir="data/process"):
        self.base_path = Path(base_work_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.siril = SirilInter()

    def process_green_stack(self, target_name):
        """
        Executes the Siril Green-Extraction Pipeline.
        Mirrors the peer-provided workflow: Flat Calibration -> Extract G -> Stack.
        """
        logger.info(f"🧪 Siril Pipeline started for {target_name}...")
        try:
            self.siril.activate_interface()
            
            # Step 1: Set Workspace
            self.siril.execute_command(f'cd "{self.base_path.absolute()}"')
            
            # Step 2: Calibrate (keeping CFA intact to avoid interpolation)
            # Assumes master-flat already exists in the process folder
            self.siril.execute_command('convert light_ -out=./')
            self.siril.execute_command('calibrate light_ -flat=master-flat -cfa')
            
            # Step 3: Pure Green Extraction (G1+G2)
            self.siril.execute_command('extract pp_light_ -green')
            
            # Step 4: Registration & Stacking
            self.siril.execute_command('register g_pp_light_')
            self.siril.execute_command(f'stack r_g_pp_light_ rej 3 3 -norm=none -out={target_name}_Green_Final')
            
            logger.info(f"✅ Green Stack Generated: {target_name}_Green_Final.fits")
            return self.base_path / f"{target_name}_Green_Final.fits"
            
        except Exception as e:
            logger.error(f"❌ Siril Pipeline Failure: {e}")
            return None
        finally:
            self.siril.close()

if __name__ == "__main__":
    # Internal test
    proc = ScienceProcessor()
    print("🔬 ScienceProcessor initialized and ready for Siril interface.")
