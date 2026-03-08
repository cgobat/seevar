#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/science_processor.py
Version: 2.1.0
Objective: Automate Siril Green-channel extraction using native siril-cli.
"""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger("ScienceProcessor")

class ScienceProcessor:
    def __init__(self, base_work_dir="data/process"):
        self.base_path = Path(base_work_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def process_green_stack(self, target_name):
        """
        Generates a Siril Script (.ssf) and executes it via native siril-cli.
        """
        script_path = self.base_path / "siril_script.ssf"
        
        # Native Siril commands for Green Channel extraction
        siril_commands = [
            f'cd "{self.base_path.absolute()}"',
            'convert light -out=./',
            'calibrate light -flat=master-flat -cfa',
            'extract pp_light -green',
            'register g_pp_light',
            f'stack r_g_pp_light rej 3 3 -norm=none -out={target_name}_Green_Final',
            'close'
        ]
        
        try:
            with open(script_path, 'w') as f:
                f.write('\n'.join(siril_commands))
            
            logger.info(f"🧪 Executing Siril CLI script for {target_name}...")
            
            # Use the binary installed via apt-get
            result = subprocess.run(
                ['siril-cli', '-s', str(script_path)], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Green Stack Generated: {target_name}_Green_Final.fits")
                return True
            else:
                logger.error(f"❌ Siril CLI Error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Pipeline Failure: {e}")
            return False
