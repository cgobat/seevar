#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/postflight/aavso_reporter.py
Version: 1.2.1
Objective: Generate AAVSO Extended Format reports in the dedicated data/reports/
           directory. Full 15-field Extended Format per AAVSO specification.
           Observer code sourced from VaultManager (observer_id key).
"""

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from core.flight.vault_manager import VaultManager


class AAVSOReporter:
    """
    Generates AAVSO Extended Format submission files.

    AAVSO Extended Format — 15 required fields (comma-delimited):
      NAME    : Variable star name (AAVSO designation)
      DATE    : Julian Date of observation (JD, 5 decimal places)
      MAG     : Magnitude (3 decimal places, or >X.X for fainter-than)
      MERR    : Magnitude error (3 decimal places)
      FILT    : Filter (CV, B, V, R, I, etc.)
      TRANS   : Transformed? YES / NO
      MTYPE   : Magnitude type: STD (differential) or DIF
      CNAME   : Comparison star name or label (e.g. 000-BBB-123)
      CMAG    : Comparison star magnitude
      KNAME   : Check star name or label (na if none)
      KMAG    : Check star magnitude (na if none)
      AMASS   : Airmass (na if unknown)
      GROUP   : Group ID for simultaneous multi-band obs (na if single)
      CHART   : AAVSO chart ID used for comp stars
      NOTES   : Free text notes (na if none)
    """

    def __init__(self):
        self.vault = VaultManager()
        self.report_dir = PROJECT_ROOT / "data" / "reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)

        conf = self.vault.get_observer_config()
        # VaultManager returns observer_id — map to obs_code
        self.obs_code = conf.get("observer_id", "")
        if not self.obs_code:
            raise ValueError(
                "observer_code missing from config.toml — "
                "AAVSO submissions require a valid observer code."
            )

    def _fmt_num(self, val, places=3) -> str:
        """Safely format numbers to a specific decimal place, allowing string fallbacks (e.g. '>14.5' or 'na')."""
        if isinstance(val, (float, int)):
            return f"{val:.{places}f}"
        return str(val)

    def finalize_report(self, observations: list) -> Path:
        """
        Write AAVSO Extended Format report to data/reports/.

        Each observation dict must contain:
          target  : str  — AAVSO star name
          jd      : float — Julian Date
          mag     : float|str — instrumental differential magnitude
          err     : float|str — magnitude uncertainty
          filter  : str  — filter code (CV, V, B, R, I)
          comp    : str  — comparison star label (AAVSO sequence ID)
          cmag    : float|str — comparison star catalogue magnitude
          kname   : str  — check star label (or 'na')
          kmag    : float|str — check star magnitude (or 'na')
          amass   : float|str — airmass (or 'na')
          chart   : str  — AAVSO chart ID
          notes   : str  — free notes (or 'na')
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"AAVSO_{self.obs_code}_{timestamp}.txt"
        save_path = self.report_dir / filename

        header = [
            "#TYPE=EXTENDED",
            f"#OBSCODE={self.obs_code}",
            "#SOFTWARE=SeeVar_v1.7",
            "#DELIM=,",
            "#DATE=JD",
            "#OBSTYPE=CCD",
            "#NAME,DATE,MAG,MERR,FILT,TRANS,MTYPE,CNAME,CMAG,KNAME,KMAG,AMASS,GROUP,CHART,NOTES",
        ]

        rows = []
        for obs in observations:
            amass = obs.get("amass", "na")
            kname = obs.get("kname", "na")
            kmag  = obs.get("kmag",  "na")
            chart = obs.get("chart", "na")
            notes = obs.get("notes", "na")

            row = (
                f"{obs['target']},"
                f"{self._fmt_num(obs['jd'], 5)},"
                f"{self._fmt_num(obs['mag'], 3)},"
                f"{self._fmt_num(obs['err'], 3)},"
                f"{obs['filter']},"
                f"NO,"
                f"STD,"
                f"{obs['comp']},"
                f"{self._fmt_num(obs['cmag'], 3)},"
                f"{kname},"
                f"{self._fmt_num(kmag, 3)},"
                f"{self._fmt_num(amass, 3)},"
                f"na,"
                f"{chart},"
                f"{notes}"
            )
            rows.append(row)

        with open(save_path, "w") as f:
            f.write("\n".join(header + rows) + "\n")

        return save_path


if __name__ == "__main__":
    rep = AAVSOReporter()
    print("[OK] AAVSO Reporter initialised.")
    print(f"     Observer code : {rep.obs_code}")
    print(f"     Report dir    : {rep.report_dir}")
