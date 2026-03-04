# 📡 Seestar S30 (Wilhelmina) Communication Protocol & API Guide

**Version:** 1.1 (Includes Goto & Action Form Mapping)
**Firmware Target:** v3.13.5
**Device:** ZWO Seestar S30

---

## 🏗️ 1. The Dual-Wield Architecture
The Seestar ALP bridge operates on two distinct control planes. Mixing them for automated workflows can cause session locks.

* **Port 5432 (SSC Web Wrapper / "The Muscles"):** * Primary Authority for state initialization and movement.
  * Use for reliable, heavy-lifting commands: `scope_park`, `scope_move_to_horizon`, `grab_control`, and `goto` slews.
  * *Warning:* Active sessions here may block motor commands on Port 5555.
* **Port 5555 (Alpaca Bridge / "The Eyes"):** * ASCOM-compliant telemetry and JSON-RPC tunneling.
  * Use for high-frequency polling, coordinate reads, and hardware vitals.

---

## 🎯 2. The "Muscle" Commands (Port 5432)
Instead of raw JSON-RPC, the SSC bridge provides standard HTTP form endpoints to command the mount. 

### A. The Target Slew (Goto)
To command Wilhelmina to move to a specific coordinate, send an HTTP `POST` request.
* **Endpoint:** `http://127.0.0.1:5432/1/goto`
* **Content-Type:** `application/x-www-form-urlencoded`
* **Required Form Data:**
  * `targetName`: String identifier (e.g., "CH Cyg").
  * `searchFor`: Catalog type. Use `VS` for AAVSO Variable Stars, `DS` for Simbad Deep Sky.
  * `ra`: Right Ascension (Decimal degrees or HMS).
  * `dec`: Declination (Decimal degrees or DMS).

### B. Standard Actions (Park, Focus, Filter)
To execute discrete hardware actions, send an HTTP `POST` request.
* **Endpoint:** `http://127.0.0.1:5432/1/command`
* **Content-Type:** `application/x-www-form-urlencoded`
* **Required Form Data:**
  * `command`: The specific action string.
* **Key Action Strings:**
  * `scope_move_to_horizon` (Unpark)
  * `scope_park`
  * `set_eq_mode` (Crucial for tracking)
  * `grab_control` / `release_control` (Session arbitration)
  * `start_solve` (Plate solve)

---

## 🔑 3. The JSON-RPC "Master Key" (Port 5555)
To access internal Seestar hardware data that isn't exposed as a standard Alpaca property, tunnel a JSON-RPC request through the Alpaca `action` endpoint using the `method_sync` wrapper.

**Request Structure:**
* **Method:** `PUT`
* **URL:** `http://127.0.0.1:5555/api/v1/telescope/1/action`
* **Body:**
  * `Action=method_sync`
  * `Parameters={"method":"<TARGET_METHOD>"}`
  * `ClientID=1`
  * `ClientTransactionID=<INCREMENTING_INT>`

> ⚠️ **Crucial Syntax Note:** For top-level state queries (like `get_device_state`), omit the empty `"params": {}` block. For queries like `scope_get_horiz_coord`, the empty `"params": {}` block is strictly required.

---

## 📊 4. Critical Telemetry Targets (Port 5555)

### A. Hardware Vitals (`get_device_state`)
Run via `method_sync` (No params block).
* **Leveling / Offsets:** `result.balance_sensor.data` (contains `x`, `y`, `angle`)
* **Compass / Heading:** `result.compass_sensor.data.direction`
* **Battery Level:** `result.pi_status.battery_capacity`
* **Storage Check:** `result.storage.storage_volume[0]` (contains `used_percent`, `free_mb`)

### B. Mount & App State (`iscope_get_app_state`)
Run via `method_sync` (With params block).
* **Coordinates:** `result.View.target_ra_dec`
* **Focus Position:** `result.FocuserMove.position`

### C. Live Position (`scope_get_horiz_coord`)
Run via `method_sync` (With empty `"params": {}` block). Returns live `[Altitude, Azimuth]`.

---

## 🚧 5. Known Limitations & Error Codes

| Code | Meaning | Resolution / Cause |
| :--- | :--- | :--- |
| **103** | Method Not Found | The JSON payload in `Parameters` is malformed, uses the wrong vocabulary, or breaks the `params: {}` rule. |
| **1031** | Not Connected | The Alpaca driver state dropped. Send a `Connected=true` PUT request to re-establish. |
| **0 Bytes** | Silent Failure / Lock | Often indicates a "Control Authority" lock. The SSC UI (5432) is holding the session hostage. |
