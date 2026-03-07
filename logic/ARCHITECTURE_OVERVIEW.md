# 🏛️ SEESTAR S30-PRO: SOVEREIGN ARCHITECTURE

> **Objective:** High-precision AAVSO Photometry via direct hardware control.
> **Version:** 2.0.0 (Sovereignty Release)

---

## 🛰️ 1. THE FLIGHT HANGAR (`core/flight/`)
*The active "Cockpit" where hardware meets command.*

- **`pilot.py`**: The actual pilot. Communicates via Port 5555 (Alpaca Bridge). Handles Slewing, Plate-solving (with 207-recovery), and triggering single RAW frames (`stack=False`).
- **`session_orchestrator.py`**: The Commanding Officer. The single entry point. It initiates the Pilot and, upon mission completion, hands the data to the Science Processor.

## 📦 2. THE POSTFLIGHT BAY (`core/postflight/`)
*The "Cargo & Science" area. No consumer-grade syncing allowed.*

- **`librarian.py`**: The RAID1 Guard. It receives binary streams directly from the Pilot, audits them for FITS integrity, and vaults them to `data/local_buffer` on the RAID1.
- **`science_processor.py`**: The Scientist. Leverages `pysiril` to extract the Green Channel (G1+G2) without interpolation, creating monochrome "Diamonds" for photometry.

## 🧪 3. THE DATA VAULT (`data/`)
*Structured to prevent SD-card grinding.*

- **`data/local_buffer/`**: (RAID1) Stores the raw and processed FITS files.
- **`data/qc/`**: (SD Card) Stores tiny, daily-rotated JSON ledgers of the night's success/failure rates.
- **`/mnt/astronas/`**: The final destination. Monthly AAVSO-ready archives are synced here when "Home" status is detected.

## 🤖 4. THE LOGIC BOARD (`logic/`)
*The Library of Information and Protocols.*

- **`STATE_MACHINE.md`**: The deterministic flow of hardware transitions.
- **`api_protocol.md`**: The Rosetta Stone for ZWO JSON-RPC methods.
- **`ARCHITECTURE_OVERVIEW.md`**: This document.
