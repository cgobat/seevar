# 📡 SEESTAR S30-PRO HARDWARE PROTOCOL

> **Objective:** Definitive ZWO JSON-RPC method mapping.
> **Version:** 2.0.0

## 🛠️ Core Methods (via Alpaca Action)

### Camera Control
- `start_exposure`: `["light", false]` -> Triggers single frame.
- `set_setting`: `{"exp_ms": {"stack_l": ms}}` -> Sets exposure time.
- `set_control_value`: `["gain", 80]` -> Sets sensor gain.
- `iscope_stop_view`: Aborts all current camera actions.

### Navigation & Mount
- `scope_goto`: `[ra, dec]` -> Slew to coordinates.
- `start_solve`: Triggers plate solving/centering.
- `get_solve_result`: Poll for `code: 0` (Success).
- `scope_set_track_state`: `{"tracking": true}` -> Toggle sidereal tracking.

## ⚠️ Port Architecture
- **Port 5555**: Control Port (Alpaca / JSON-RPC). **Use this for everything.**
- **Port 4720**: Video Stream (Preview only). **Ignore for Science.**
