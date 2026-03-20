#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: core/flight/neutralizer.py
Version: 3.0.1
Objective: Hardware reset — stops any active S30-Pro session and verifies idle state before handing control to the pilot.
"""

import json
import logging
import socket
import sys
import time

import requests

from core.flight.pilot import SEESTAR_HOST

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger("Neutralizer")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
S30_HOST        = SEESTAR_HOST  # Dynamically sourced from pilot.py / config.toml
S30_PORT        = 4700          # sovereign JSON-RPC control
ALPACA_URL      = "http://127.0.0.1:5432/api/v1/telescope/1"
SOCK_TIMEOUT    = 5             # seconds per RPC call
HEARTBEAT_MAX   = 180           # seconds to wait for engine pulse
STATE_TIMEOUT   = 60            # seconds to verify idle state
POLL_INTERVAL   = 5             # seconds between polls


# ---------------------------------------------------------------------------
# Sovereign TCP JSON-RPC (port 4700)
# ---------------------------------------------------------------------------
def _sovereign_rpc(method: str, params=None) -> dict | None:
    payload = {"method": method}
    if params is not None: payload["params"] = params

    try:
        with socket.create_connection((S30_HOST, S30_PORT), timeout=SOCK_TIMEOUT) as sock:
            sock.sendall((json.dumps(payload) + "\r\n").encode())
            raw = b""
            while not raw.endswith(b"\n"):
                chunk = sock.recv(4096)
                if not chunk: break
                raw += chunk
            return json.loads(raw.decode().strip())
    except (socket.timeout, ConnectionRefusedError) as e:
        logger.warning(f"RPC {method} failed: {e}")
        return None
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"RPC {method} error: {e}")
        return None

# ---------------------------------------------------------------------------
# State verification via get_device_state
# ---------------------------------------------------------------------------
def _device_is_idle() -> bool:
    resp = _sovereign_rpc("get_device_state")
    if resp is None: return False

    result = resp.get("result", resp)
    if isinstance(result, dict):
        is_parked   = result.get("parked", False)
        app_status  = str(result.get("state", "unknown")).lower()
        return is_parked and app_status == "idle"

    logger.warning(f"Unexpected get_device_state shape: {resp}")
    return False

# ---------------------------------------------------------------------------
# Main sequence
# ---------------------------------------------------------------------------
def enforce_zero_state() -> bool:
    logger.info("STEP 1: Disabling SSC scheduler...")
    try:
        requests.post(
            f"{ALPACA_URL}/action",
            json={"Action": "schedule", "Parameters": json.dumps({"state": "stop"}), "ClientID": 42, "ClientTransactionID": int(time.time())},
            timeout=3,
        )
    except requests.RequestException as e:
        logger.debug(f"Scheduler toggle skipped (bridge may not be running): {e}")

    logger.info("STEP 2: Issuing iscope_stop_view + scope_park...")
    _sovereign_rpc("iscope_stop_view")
    time.sleep(1)
    _sovereign_rpc("scope_park")

    logger.info(f"STEP 3: Waiting for device heartbeat (max {HEARTBEAT_MAX}s)...")
    start, alive = time.time(), False

    while (time.time() - start) < HEARTBEAT_MAX:
        resp = _sovereign_rpc("get_device_state")
        if resp is not None:
            logger.info(f"Heartbeat detected after {int(time.time() - start)}s.")
            alive = True
            break
        time.sleep(POLL_INTERVAL)

    if not alive:
        logger.error("Flatline: device did not respond within timeout.")
        return False

    logger.info(f"STEP 4: Verifying zero-state (max {STATE_TIMEOUT}s)...")
    deadline = time.time() + STATE_TIMEOUT

    while time.time() < deadline:
        if _device_is_idle():
            logger.info("Zero-state SECURED — mount parked and idle.")
            return True
        time.sleep(POLL_INTERVAL)

    logger.warning("Zero-state verification timed out. Device alive but state unconfirmed.")
    return True

if __name__ == "__main__":
    sys.exit(0 if enforce_zero_state() else 1)
