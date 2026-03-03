#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/fits_auditor.py
Version: 1.3.0 (Photometry Complete)
Objective: Scrapes full AAVSO-relevant keyword set for scientific submission.
"""

import os
import json
from pathlib import Path
from astropy.io import fits
from datetime import datetime

class FITSAuditor:
    def __init__(self):
        self.root = Path(__file__).resolve().parents[2]
        self.report_path = self.root / "data/flight_report.json"

    def audit_session(self, session_dir):
        results = []
        fits_files = list(Path(session_dir).glob("*.fits"))
        
        for f_path in fits_files:
            try:
                with fits.open(f_path) as hdul:
                    hdr = hdul[0].header
                    
                    # 1. Identity & Hardware
                    observer = hdr.get('OBSERVER', 'Unknown')
                    telescop = hdr.get('TELESCOP', 'Unknown')
                    instrume = hdr.get('INSTRUME', 'Unknown')

                    # 2. Coordinates & Targeting
                    target = hdr.get('OBJECT', 'Unknown')
                    auid   = hdr.get('AUID', 'N/A')
                    ra_fits = hdr.get('RA', 0.0)
                    dec_fits = hdr.get('DEC', 0.0)

                    # 3. Scientific Metrics (V-Graph Ready)
                    magzero = hdr.get('MAGZERO', hdr.get('ZMAG', 0.0))
                    fwhm    = hdr.get('FWHM', 0.0)
                    saturate = hdr.get('SATURATE', 65535) # Default for 16-bit
                    
                    results.append({
                        "star_name": target,
                        "status": "COMPLETED" if observer != 'Unknown' else "FAILED",
                        "metadata": {
                            "observer": observer,
                            "telescop": telescop,
                            "auid": auid,
                            "ra": ra_fits,
                            "dec": dec_fits,
                            "fwhm": fwhm,
                            "magzero": magzero,
                            "saturate": saturate
                        }
                    })
            except Exception as e:
                print(f"❌ Error auditing {f_path.name}: {e}")

        self._write_report(results)

    def _write_report(self, results):
        report = {"completed_targets": results}
        with open(self.report_path, 'w') as f:
            json.dump(report, f, indent=4)
