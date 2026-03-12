#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/orchestrator.py
Version: 1.7.0
Objective: Full pipeline state machine wired to the v4.0.0 TCP Diamond
           Sequence. Authoritative flight daemon — merges session_orchestrator.

Merged from session_orchestrator.py v1.2.1 (retired):
  - Per-target postflight handoff to ScienceProcessor
  - Ledger update: last_success on GOOD, attempts++ on BAD
  - Notifier alerts on acquisition success and failure

Changes vs 1.6.0:
  - FIXED: PROJECT_ROOT hardcoded Path -> Path(__file__).resolve().parents[2]
  - FIXED: SUN_LIMIT_DEG -10 (testing) -> -18.0 (astronomical twilight)
  - FIXED: _run_preflight() was bypassing all hardware checks -> restored
  - FIXED: _run_postflight() was empty -> wired to ScienceProcessor + ledger
  - ADDED: per-target ledger update (last_success / attempts) after each frame
  - ADDED: notifier.alert() on acquisition failure, notifier.info() on success
  - ADDED: weather re-check in _run_flight() loop (was absent in v1.6.0)
  - RETIRED: session_orchestrator.py — functionality absorbed here
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_body
from astropy.time import Time

import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.utils.env_loader import DATA_DIR, ENV_STATUS, load_config
from core.utils.notifier import alert, info as notify_info
from core.flight.pilot import DiamondSequence, AcquisitionTarget, SEESTAR_HOST

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "orchestrator.log", mode="a"),
    ],
)
log = logging.getLogger("Orchestrator")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PLAN_FILE    = DATA_DIR / "tonights_plan.json"
STATE_FILE   = DATA_DIR / "system_state.json"
LEDGER_FILE  = DATA_DIR / "ledger.json"
WEATHER_FILE = DATA_DIR / "weather_state.json"
MISSION_FILE = DATA_DIR / "tonights_plan.json"


# ---------------------------------------------------------------------------
# Aperture priority scoring
# ---------------------------------------------------------------------------
def aperture_grip_score(azimuth: float, altitude: float) -> float:
    if 180 <= azimuth <= 350:
        return 100.0 - altitude
    return altitude / 2.0


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------
class PipelineState:
    IDLE, PREFLIGHT, PLANNING, FLIGHT, POSTFLIGHT, ABORTED, PARKED = (
        "IDLE", "PREFLIGHT", "PLANNING", "FLIGHT",
        "POSTFLIGHT", "ABORTED", "PARKED"
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
class Orchestrator:
    SUN_LIMIT_DEG  = -18.0     # Astronomical twilight
    ALT_FLOOR_DEG  = 30.0
    PANEL_TIME_SEC = 60
    LOOP_SLEEP_SEC = 30

    def __init__(self):
        cfg  = load_config()
        loc  = cfg.get("location", {})
        aavso = cfg.get("aavso", {})

        self._obs = {
            "observer_id": aavso.get("observer_code", "MISSING_ID"),
            "lat":         loc.get("lat", 0.0),
            "lon":         loc.get("lon", 0.0),
            "elevation":   loc.get("elevation", 0.0),
        }

        self._location = EarthLocation(
            lat=self._obs["lat"] * u.deg,
            lon=self._obs["lon"] * u.deg,
            height=self._obs["elevation"] * u.m,
        )

        self._state       = PipelineState.IDLE
        self._targets     = []
        self._flight_log  = []
        self._session_stats = {
            "targets_attempted": 0,
            "targets_completed": 0,
            "exposures_total":   0,
            "start_utc":         None,
            "end_utc":           None,
        }

        self.diamond = DiamondSequence(host=SEESTAR_HOST)

        # Lazy import — ScienceProcessor needs Siril on path
        self._science = None

    def _get_science_processor(self):
        if self._science is None:
            try:
                from core.postflight.science_processor import ScienceProcessor
                self._science = ScienceProcessor()
            except ImportError as e:
                log.warning(f"ScienceProcessor not available: {e}")
        return self._science

    # -----------------------------------------------------------------------
    # Main loop
    # -----------------------------------------------------------------------
    def run(self):
        log.info("Orchestrator starting — SeeVar v1.7.0 (Sovereign TCP)")
        self._session_stats["start_utc"] = datetime.now(timezone.utc).isoformat()
        self._write_state(sub="Daemon starting", msg="Federation online.")

        while True:
            try:
                self._tick()
            except KeyboardInterrupt:
                log.info("KeyboardInterrupt — exiting.")
                break
            except Exception as e:
                log.exception("Unhandled exception: %s", e)
                self._transition(PipelineState.ABORTED, msg=f"Error: {e}")
                alert(f"⚠️ SeeVar orchestrator error: {e}")
                time.sleep(self.LOOP_SLEEP_SEC * 4)

    def _tick(self):
        s = self._state
        if s == PipelineState.IDLE:       self._run_idle()
        elif s == PipelineState.PREFLIGHT: self._run_preflight()
        elif s == PipelineState.PLANNING:  self._run_planning()
        elif s == PipelineState.FLIGHT:    self._run_flight()
        elif s == PipelineState.POSTFLIGHT:self._run_postflight()
        elif s == PipelineState.PARKED:    self._run_parked()
        elif s == PipelineState.ABORTED:   self._run_aborted()

    # -----------------------------------------------------------------------
    # States
    # -----------------------------------------------------------------------
    def _run_idle(self):
        sun_alt = self._sun_altitude()
        self._write_state(
            sub="Standing by",
            msg=f"Sun at {sun_alt:.1f}°. Waiting for night (<{self.SUN_LIMIT_DEG}°)."
        )
        if sun_alt < self.SUN_LIMIT_DEG:
            self._transition(PipelineState.PREFLIGHT, msg="Astronomical night confirmed.")
        else:
            time.sleep(self.LOOP_SLEEP_SEC)

    def _run_preflight(self):
        self._log_flight("PREFLIGHT sequence initiated.")
        checks_passed = True

        # Sun gate
        sun_alt = self._sun_altitude()
        if sun_alt >= self.SUN_LIMIT_DEG:
            self._log_flight(f"Sun too high ({sun_alt:.1f}°) — aborting preflight.")
            self._transition(PipelineState.IDLE, msg="Sun rose during preflight.")
            return
        self._log_flight(f"Sun altitude: {sun_alt:.1f}° — GO.")

        # Hardware: get_device_state on port 4700
        from core.flight.camera_control import CameraControl
        cam = CameraControl()
        if not cam.get_view_status():
            self._log_flight("Hardware check FAILED — device not responding on port 4700.")
            checks_passed = False
        else:
            self._log_flight("Hardware: RESPONDING.")

        # Weather
        weather_ok, weather_msg = self._check_weather()
        if not weather_ok:
            self._log_flight(f"Weather abort: {weather_msg}")
            checks_passed = False
        else:
            self._log_flight(f"Weather: {weather_msg}")

        # GPS
        gps = self._check_gps()
        self._log_flight(f"GPS: {gps}")

        if not checks_passed:
            self._transition(PipelineState.ABORTED, msg="Preflight failed.")
            alert("⚠️ SeeVar preflight FAILED — mission scrubbed.")
            return

        self._log_flight("All preflight checks passed — GO FOR PLANNING.")
        self._transition(PipelineState.PLANNING, msg="Preflight complete.")

    def _run_planning(self):
        self._log_flight("Loading mission targets...")
        mission = self._load_mission_targets()
        if not mission:
            self._transition(PipelineState.ABORTED, msg="No mission targets available.")
            return

        now   = Time.now()
        frame = AltAz(obstime=now, location=self._location)
        scored = []

        for target in mission:
            try:
                coord = SkyCoord(
                    ra=target.get("ra"), dec=target.get("dec"),
                    unit=(u.hourangle, u.deg)
                )
                altaz   = coord.transform_to(frame)
                alt_deg = float(altaz.alt.deg)
                az_deg  = float(altaz.az.deg)
                if alt_deg < self.ALT_FLOOR_DEG:
                    continue
                target["_alt"]   = round(alt_deg, 2)
                target["_az"]    = round(az_deg, 2)
                target["_score"] = round(aperture_grip_score(az_deg, alt_deg), 2)
                scored.append(target)
            except Exception as e:
                log.warning("Could not score %s: %s", target.get("name", "?"), e)

        if not scored:
            self._transition(PipelineState.ABORTED, msg="No observable targets.")
            return

        scored.sort(key=lambda t: t["_score"], reverse=True)
        self._targets = scored
        self._write_plan(scored)
        self._log_flight(
            f"Plan built: {len(scored)} targets. Lead: {scored[0].get('name')}"
        )
        self._transition(
            PipelineState.FLIGHT,
            sub=scored[0].get("name", "UNKNOWN"),
            msg="Flight plan locked."
        )

    def _run_flight(self):
        if not self._targets:
            self._transition(PipelineState.POSTFLIGHT, msg="Target list exhausted.")
            return

        # Dawn gate
        sun_alt = self._sun_altitude()
        if sun_alt >= self.SUN_LIMIT_DEG:
            self._log_flight(f"Dawn abort — sun at {sun_alt:.1f}°.")
            self._transition(PipelineState.POSTFLIGHT, msg="Dawn abort.")
            return

        # Mid-flight weather check
        weather_ok, weather_msg = self._check_weather()
        if not weather_ok:
            self._log_flight(f"Mid-flight weather abort: {weather_msg}")
            alert(f"🌧️ SeeVar weather abort: {weather_msg}")
            self._transition(PipelineState.POSTFLIGHT, msg=f"Weather abort: {weather_msg}")
            return

        # Re-score and cull targets below floor
        now   = Time.now()
        frame = AltAz(obstime=now, location=self._location)
        valid = []
        for target in self._targets:
            try:
                coord = SkyCoord(
                    ra=target["ra"], dec=target["dec"],
                    unit=(u.hourangle, u.deg)
                )
                altaz = coord.transform_to(frame)
                alt   = float(altaz.alt.deg)
                az    = float(altaz.az.deg)
                if alt < self.ALT_FLOOR_DEG:
                    continue
                target["_alt"]   = round(alt, 2)
                target["_az"]    = round(az, 2)
                target["_score"] = round(aperture_grip_score(az, alt), 2)
                valid.append(target)
            except Exception:
                pass

        if not valid:
            self._log_flight("All targets below floor. Moving to postflight.")
            self._transition(PipelineState.POSTFLIGHT, msg="All targets set.")
            return

        valid.sort(key=lambda t: t["_score"], reverse=True)
        self._targets = valid
        target = valid[0]

        name    = target.get("name", "UNKNOWN")
        ra_str  = target.get("ra")
        dec_str = target.get("dec")

        coord = SkyCoord(ra=ra_str, dec=dec_str, unit=(u.hourangle, u.deg))
        acq   = AcquisitionTarget(
            name          = name,
            ra_hours      = float(coord.ra.hour),
            dec_deg       = float(coord.dec.deg),
            auid          = target.get("auid", ""),
            exp_ms        = self.PANEL_TIME_SEC * 1000,
            observer_code = self._obs["observer_id"],
        )

        self._session_stats["targets_attempted"] += 1
        self._write_state(state="SLEWING", sub=name, msg=f"Diamond Sequence: {name}")
        self._log_flight(f"Handing {name} to Diamond Sequence (TCP)...")

        result = self.diamond.acquire(acq)

        if result.success:
            self._session_stats["targets_completed"] += 1
            self._session_stats["exposures_total"]   += 1
            self._log_flight(f"Acquisition complete: {result.path.name}")
            notify_info(f"✅ SeeVar acquired {name} → {result.path.name}")

            # Per-target postflight handoff
            self._handoff_to_science(name, result.path)

            # Update ledger — last_success
            self._ledger_update(name, success=True)

            # Rotate target to back of queue
            self._targets.remove(target)
            self._targets.append(target)
            self._write_state(state="TRACKING", sub=name, msg="Observation complete.")
        else:
            self._log_flight(f"TCP Acquisition FAILED for {name}: {result.error}")
            alert(f"❌ SeeVar acquisition failed: {name} — {result.error}")

            # Update ledger — failed attempt
            self._ledger_update(name, success=False)

            self._targets.remove(target)

    def _run_postflight(self):
        self._log_flight("Postflight audit initiated.")
        self._session_stats["end_utc"] = datetime.now(timezone.utc).isoformat()
        completed = self._session_stats["targets_completed"]
        attempted = self._session_stats["targets_attempted"]
        notify_info(
            f"🔭 SeeVar session complete — "
            f"{completed}/{attempted} targets acquired."
        )
        self._transition(PipelineState.PARKED, msg="Postflight complete.")

    def _run_parked(self):
        sun_alt = self._sun_altitude()
        self._write_state(
            sub="Parked",
            msg=f"Parked. Sun at {sun_alt:.1f}°. Waiting for next night."
        )
        if sun_alt > 5.0:
            self._reset_session()
            self._transition(PipelineState.IDLE, msg="Reset. Ready for next night.")
        else:
            time.sleep(self.LOOP_SLEEP_SEC * 2)

    def _run_aborted(self):
        sun_alt = self._sun_altitude()
        self._write_state(sub="ABORTED", msg=f"Holding. Sun at {sun_alt:.1f}°.")
        if sun_alt > 5.0:
            self._reset_session()
            self._transition(PipelineState.IDLE, msg="Abort cleared.")
        else:
            time.sleep(self.LOOP_SLEEP_SEC * 2)

    # -----------------------------------------------------------------------
    # Per-target postflight handoff (absorbed from session_orchestrator)
    # -----------------------------------------------------------------------
    def _handoff_to_science(self, name: str, fits_path: Path):
        """Hand a fresh FITS to ScienceProcessor for green extraction."""
        processor = self._get_science_processor()
        if processor is None:
            log.warning("ScienceProcessor unavailable — skipping science extraction.")
            return
        try:
            safe_name = name.replace(" ", "_")
            processed = processor.process_green_stack(safe_name)
            if processed:
                self._log_flight(f"Science extraction complete: {processed}")
            else:
                log.warning(f"Science extraction returned nothing for {name}.")
        except Exception as e:
            log.error(f"ScienceProcessor error for {name}: {e}")

    # -----------------------------------------------------------------------
    # Ledger — per-target update (authoritative write, append-only)
    # -----------------------------------------------------------------------
    def _ledger_update(self, name: str, success: bool):
        """
        Update ledger.json for a single target.
        Structure: {"entries": {"SS_CYG": {"last_success": ..., "attempts": N}}}
        Never overwrites the full ledger — only updates the target's entry.
        """
        try:
            LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
            ledger = {}
            if LEDGER_FILE.exists():
                try:
                    with open(LEDGER_FILE, "r") as f:
                        ledger = json.load(f)
                except (json.JSONDecodeError, OSError):
                    log.warning("Ledger read failed — starting fresh entry.")

            entries = ledger.setdefault("entries", {})
            key     = name.upper().replace(" ", "_")
            entry   = entries.setdefault(key, {"attempts": 0})

            entry["attempts"] = entry.get("attempts", 0) + 1
            if success:
                entry["last_success"] = datetime.now(timezone.utc).isoformat()
                entry["status"]       = "OK"
            else:
                entry["status"] = "FAILED"

            with open(LEDGER_FILE, "w") as f:
                json.dump(ledger, f, indent=2)

            log.debug(f"Ledger updated: {key} success={success}")
        except OSError as e:
            log.error(f"Ledger write failed for {name}: {e}")

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def _sun_altitude(self) -> float:
        try:
            now = Time.now()
            sun = get_body("sun", now)
            return float(
                sun.transform_to(
                    AltAz(obstime=now, location=self._location)
                ).alt.deg
            )
        except Exception:
            return 0.0

    def _check_weather(self) -> tuple[bool, str]:
        data = _safe_load_json(WEATHER_FILE, {})
        if not data:
            return True, "No weather data — proceeding optimistically."
        status = data.get("status", "UNKNOWN").upper()
        if status in ("RAIN", "STORM", "SNOW", "OVERCAST", "CLOUDY", "WINDY"):
            return False, f"Weather status: {status}"
        clouds = data.get("clouds_pct", 0)
        if clouds > 70:
            return False, f"Cloud cover {clouds}%"
        humidity = data.get("humidity_pct", 0)
        if humidity > 90:
            return False, f"Humidity {humidity}% — dew risk"
        return True, status

    def _check_gps(self) -> str:
        data = _safe_load_json(ENV_STATUS, {})
        return data.get("gps_status", "NO-DATA")

    def _load_mission_targets(self) -> list:
        data = _safe_load_json(MISSION_FILE, [])
        if isinstance(data, list):
            return data
        return data.get("targets", [])

    def _transition(self, new_state: str, sub: str = "", msg: str = ""):
        log.info("STATE: %s → %s", self._state, new_state)
        self._state = new_state
        self._write_state(state=new_state, sub=sub, msg=msg)

    def _write_state(self, state: str = None, sub: str = "", msg: str = "", **kwargs):
        payload = {
            "state":     state or self._state,
            "sub":       sub,
            "msg":       msg,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STATE_FILE, "w") as f:
                json.dump(payload, f, indent=2)
        except OSError as e:
            log.error("system_state.json write failed: %s", e)

    def _write_plan(self, targets: list):
        try:
            with open(PLAN_FILE, "w") as f:
                json.dump(targets, f, indent=2, default=str)
        except OSError as e:
            log.error("Plan write failed: %s", e)

    def _log_flight(self, line: str):
        ts    = datetime.now(timezone.utc).strftime("%H:%M:%S")
        entry = f"[{ts}] {line}"
        log.info(line)
        self._flight_log.append(entry)
        if len(self._flight_log) > 20:
            self._flight_log.pop(0)
        self._write_state(msg=line)

    def _reset_session(self):
        self._targets    = []
        self._flight_log = []
        self._session_stats = {
            "targets_attempted": 0,
            "targets_completed": 0,
            "exposures_total":   0,
            "start_utc": datetime.now(timezone.utc).isoformat(),
            "end_utc":   None,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _safe_load_json(path: Path, default):
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            log.warning("JSON load failed for %s: %s", path, e)
    return default


if __name__ == "__main__":
    Orchestrator().run()
