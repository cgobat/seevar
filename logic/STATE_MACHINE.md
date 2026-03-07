# 🤖 S30-PRO SOVEREIGNTY: THE STATE MACHINE

> **Objective:** Deterministic control over hardware transitions via JSON-RPC.
> **Version:** 2.0.0 (The "Diamond" Revision)

---

## 🏗️ PHASE 1: INITIALIZATION (IDLE → READY)
Before science begins, we force a "Clean Slate."

| Action | JSON-RPC Method | Expected Value | Failure / Recovery |
| :--- | :--- | :--- | :--- |
| **Kill UI/App** | `iscope_stop_view` | `{"result": 0}` | Mandatory to break ZWO Stacking locks. |
| **Set Gain** | `set_control_value` | `["gain", 80]` | Fixes sensitivity for Photometry. |
| **Shutter** | `set_setting` | `{"exp_ms": {...}}` | Pre-sets timing for the `start_exposure` call. |

---

## 🔭 PHASE 2: NAVIGATION (QUEUED → TRACKING)
We don't trust the mount; we verify the sky.

### 1. The Slew
- **Command**: `scope_goto` with `[ra, dec]`
- **Progression**: Poll `get_event_state`.
- **Requirement**: `is_slewing` must transition `True -> False`.

### 2. The Solve (Entering the Cave)
- **Command**: `start_solve`
- **Demand**: Poll `get_solve_result` until `code` is returned.
- **Outcome 0**: Success. Transition to **INTEGRATING**.
- **Outcome 207**: "Fail to operate." **Recovery**: Offset mount by 0.5° and retry.
- **Outcome 400/500**: Bridge Error. **Recovery**: Restart Alpaca Service.

---

## 📸 PHASE 3: SCIENCE (INTEGRATING → VERIFYING)
Bypassing the consumer stacker to get pure RAW data.

| Step | Command / Polling | Success Condition |
| :--- | :--- | :--- |
| **Trigger** | `start_exposure` | `["light", false]` (Single Frame Mode) |
| **Monitor** | `get_exp_status` | Status transitions from `Exposing` to `Idle`. |
| **Check** | `get_view_state` | `new_image: true` must appear. |

---

## 📉 PHASE 4: HARVEST (VERIFYING → COMPLETED)
Moving the "Diamond" from the telescope to the Pi.

1. **Pull**: Execute `get_stacked_img` to pull the binary FITS data.
2. **Log**: Record the midpoint UTC timestamp (AAVSO requirement).
3. **Clean**: Once file is verified in `local_buffer/`, proceed to next iteration.

---

## ⚠️ CRITICAL VETO LOGIC (ANY STATE)
If these conditions occur, the machine must transition to **PARKING** immediately:
- **`get_device_state` (battery)**: `< 10%`.
- **`get_device_state` (temp)**: `> 55.0C`.
- **Heartbeat Lost**: No response from Alpaca Port 5555 for > 10 seconds.
