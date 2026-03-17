#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/preflight/weather.py
Version: 1.5.1
Objective: Dual-source weather consensus daemon.
           Source 1 — open-meteo   : precipitation, wind, humidity (hard aborts)
           Source 2 — Clear Outside: per-layer clouds, fog (photometry aborts)
           Feeds status, clouds_pct, humidity_pct to the Orchestrator via
           data/weather_state.json.
"""

import json
import time
import logging
import requests
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Sovereign Paths & Imports
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.utils.env_loader import DATA_DIR
from core.flight.vault_manager import VaultManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("WeatherSentinel")


def _load_thresholds() -> dict:
    """Load weather veto thresholds from config.toml [weather] section.
    Falls back to safe defaults if section or key is missing."""
    defaults = {
        "precip_limit":    0.5,
        "wind_limit":      30.0,
        "humidity_limit":  90.0,
        "low_cloud_limit": 30.0,
        "mid_cloud_limit": 50.0,
        "high_cloud_warn": 70.0,
        "fog_abort":       True,
    }
    try:
        import tomllib
        from core.utils.env_loader import CONFIG_PATH
        with open(CONFIG_PATH, "rb") as f:
            config = tomllib.load(f)
        w = config.get("weather", {})
        return {
            "precip_limit":    float(w.get("max_precip_mm",      defaults["precip_limit"])),
            "wind_limit":      float(w.get("max_wind_kmh",        defaults["wind_limit"])),
            "humidity_limit":  float(w.get("max_humidity_pct",    defaults["humidity_limit"])),
            "low_cloud_limit": float(w.get("max_cloud_low_pct",   defaults["low_cloud_limit"])),
            "mid_cloud_limit": float(w.get("max_cloud_mid_pct",   defaults["mid_cloud_limit"])),
            "high_cloud_warn": float(w.get("max_cloud_high_pct",  defaults["high_cloud_warn"])),
            "fog_abort":       bool(w.get("fog_abort",            defaults["fog_abort"])),
        }
    except Exception as e:
        log.warning("Could not load weather thresholds from config.toml: %s — using defaults", e)
        return defaults


class WeatherSentinel:
    def __init__(self):
        self.weather_state_file = DATA_DIR / "weather_state.json"
        self.vault = VaultManager()
        self.t = _load_thresholds()
        log.info(
            "Thresholds — precip:%.1fmm wind:%.0fkm/h hum:%.0f%% "
            "low:%.0f%% mid:%.0f%% high:%.0f%% fog_abort:%s",
            self.t["precip_limit"], self.t["wind_limit"], self.t["humidity_limit"],
            self.t["low_cloud_limit"], self.t["mid_cloud_limit"],
            self.t["high_cloud_warn"], self.t["fog_abort"]
        )

    def get_coordinates(self) -> tuple[float, float]:
        """Fetches coordinates from VaultManager — respects live GPS RAM override."""
        cfg = self.vault.get_observer_config()
        return float(cfg.get("lat", 0.0)), float(cfg.get("lon", 0.0))

    # -------------------------------------------------------------------------
    # SOURCE 1 — open-meteo
    # -------------------------------------------------------------------------

    def fetch_open_meteo(self, lat: float, lon: float) -> dict:
        """
        Fetches precipitation, wind, humidity for the next 12 hours.
        No API key required.
        """
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=precipitation,cloud_cover,relative_humidity_2m,wind_speed_10m"
        )
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json().get("hourly", {})

            precip   = max(data.get("precipitation",         [0])[:12]) if data.get("precipitation")         else 0
            clouds   = max(data.get("cloud_cover",           [0])[:12]) if data.get("cloud_cover")           else 0
            humidity = max(data.get("relative_humidity_2m",  [0])[:12]) if data.get("relative_humidity_2m")  else 0
            wind     = max(data.get("wind_speed_10m",        [0])[:12]) if data.get("wind_speed_10m")        else 0

            return {"precip": precip, "clouds": clouds, "humidity": humidity, "wind": wind}
        except Exception as e:
            log.warning("open-meteo fetch failed: %s", e)
            return {}

    # -------------------------------------------------------------------------
    # SOURCE 2 — Clear Outside
    # -------------------------------------------------------------------------

    def fetch_clear_outside(self, lat: float, lon: float) -> dict:
        """
        Fetches per-layer cloud data and fog from Clear Outside.
        Returns worst values over the next 3 hours.
        """
        try:
            from clear_outside_apy import ClearOutsideAPY
            api = ClearOutsideAPY(str(round(lat, 2)), str(round(lon, 2)), view="current")
            api.update()
            data = api.pull()

            hours = data.get("forecast", {}).get("day-0", {}).get("hours", {})
            if not hours:
                log.warning("Clear Outside returned no hourly data.")
                return {}

            # Worst of next 3 hours
            sample = list(hours.values())[:3]
            low  = max(int(h.get("low-clouds",  0)) for h in sample)
            mid  = max(int(h.get("mid-clouds",  0)) for h in sample)
            high = max(int(h.get("high-clouds", 0)) for h in sample)
            fog  = max(int(h.get("fog",         0)) for h in sample)

            log.info(
                "Clear Outside — low: %d%% mid: %d%% high: %d%% fog: %d",
                low, mid, high, fog
            )
            return {"low": low, "mid": mid, "high": high, "fog": fog}

        except ImportError:
            log.warning("clear-outside-apy not installed — skipping Clear Outside source.")
            return {}
        except Exception as e:
            log.warning("Clear Outside fetch failed: %s", e)
            return {}

    # -------------------------------------------------------------------------
    # CONSENSUS
    # -------------------------------------------------------------------------

    def get_consensus(self):
        """
        Builds dual-source consensus and writes weather_state.json.
        Priority order:
          1. Fog (Clear Outside)    → FOGGY — hard abort
          2. Rain (open-meteo)      → RAIN  — hard abort
          3. Low cloud (CO)         → CLOUDY
          4. Mid cloud (CO)         → CLOUDY
          5. Humidity (OM)          → HUMID
          6. Wind (OM)              → WINDY
          7. High cloud only (CO)   → HAZY  — warning, still observable
          8. All clear              → CLEAR
        """
        lat, lon = self.get_coordinates()
        if lat == 0.0 and lon == 0.0:
            log.error("Coordinates are 0.0 (Null Island). Cannot fetch weather.")
            return

        log.info("Fetching dual-source weather for %.4f, %.4f...", lat, lon)

        om = self.fetch_open_meteo(lat, lon)
        co = self.fetch_clear_outside(lat, lon)

        clouds_pct   = om.get("clouds",   0)
        humidity_pct = om.get("humidity", 0)

        # Consensus decision — ordered by severity
        # Thresholds loaded from config.toml [weather] — tunable without code changes
        # HUMID and HAZY are warnings only — observatory still opens
        # Dew heater should activate on HUMID
        t = self.t
        if t["fog_abort"] and co.get("fog", 0) > 0:
            status, icon = "FOGGY",  "🌫️"
        elif om.get("precip", 0) > t["precip_limit"]:
            status, icon = "RAIN",   "🌧️"
        elif co.get("low", 0) > t["low_cloud_limit"]:
            status, icon = "CLOUDY", "☁️"
        elif co.get("mid", 0) > t["mid_cloud_limit"]:
            status, icon = "CLOUDY", "☁️"
        elif om.get("wind", 0) > t["wind_limit"]:
            status, icon = "WINDY",  "💨"
        elif co.get("high", 0) > t["high_cloud_warn"]:
            status, icon = "HAZY",   "🌤️"
        elif humidity_pct > t["humidity_limit"]:
            status, icon = "HUMID",  "💧"  # Warning only — activate dew heater
        else:
            status, icon = "CLEAR",  "✨"

        state = {
            "_objective": "Dual-source weather consensus. Read by dashboard.py and orchestrator.py.",
            "status":       status,
            "icon":         icon,
            "clouds_pct":   int(clouds_pct),
            "humidity_pct": int(humidity_pct),
            "low_cloud":    co.get("low",  0),
            "mid_cloud":    co.get("mid",  0),
            "high_cloud":   co.get("high", 0),
            "fog":          co.get("fog",  0),
            "last_update":  time.time(),
        }

        try:
            self.weather_state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.weather_state_file, "w") as f:
                json.dump(state, f, indent=4)
            log.info(
                "Consensus: %s %s — low:%d%% mid:%d%% high:%d%% fog:%d hum:%d%%",
                status, icon,
                co.get("low", 0), co.get("mid", 0),
                co.get("high", 0), co.get("fog", 0),
                humidity_pct,
            )
        except OSError as e:
            log.error("Failed to write weather_state.json: %s", e)


if __name__ == "__main__":
    log.info("WeatherSentinel v1.5.0 starting...")
    sentinel = WeatherSentinel()
    while True:
        sentinel.get_consensus()
        time.sleep(600)
