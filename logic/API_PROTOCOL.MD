# 📡 SEESTAR S30-PRO HARDWARE PROTOCOL

> **Objective:** Definitive ZWO JSON-RPC method mapping for SeeVar.
> **Version:** 3.0.0 (Sovereign TCP / Praw revision)
> **Path:** `logic/API_PROTOCOL.MD`

All science acquisition goes via **direct TCP to the S30-Pro**.
The Alpaca bridge (`127.0.0.1:5432`) is a health-check and scheduler
toggle only — it is not the capture path. See `ALPACA_BRIDGE.MD`.

## Port Architecture

| Port | Host | Protocol | Purpose |
|------|------|----------|---------|
| `4700` | `192.168.178.55` | JSON-RPC over TCP (`\r\n`) | All sovereign control |
| `4801` | `192.168.178.55` | Binary frame stream | Science capture (preview frames) |
| `4800` | `192.168.178.55` | Binary frame stream | ZIP stacks — not used for science |
| `5432` | `127.0.0.1` | HTTP (Alpaca) | Bridge health-check only |

**Port 5555 does not exist. Port 4720 does not exist. Do not use either.**

## JSON-RPC Wire Format (port 4700)

All messages are newline-terminated JSON, sent as UTF-8:

```python
msg = {"id": <int>, "method": "<method>", "params": <value>}
wire = (json.dumps(msg) + "\r\n").encode("utf-8")
```

`id` is an auto-incrementing integer per session (start at 10000,
mirrors seestar_alp convention). `params` is omitted when not required.

## Confirmed Methods

### Session control
| Method | Params | Effect |
|--------|--------|--------|
| `get_device_state` | — | Health probe. Any valid response = device alive. |
| `iscope_stop_view` | — | Abort all active camera/mount operations. |
| `iscope_start_view` | `{"mode": "star"}` | Begin continuous exposure stream. |

### Mount
| Method | Params | Effect |
|--------|--------|--------|
| `scope_sync` | `[ra_hours, dec_deg]` | Sync mount pointing model. |
| `scope_goto` | `[ra_hours, dec_deg]` | Slew to coordinates. |
| `scope_park` | — | Park mount. |
| `set_user_location` | `{"lat": float, "lon": float, "force": true}` | Push GPS fix to mount. |

### Camera
| Method | Params | Effect |
|--------|--------|--------|
| `set_control_value` | `["gain", 80]` | Set sensor gain. |
| `set_setting` | `{"exp_ms": {"stack_l": ms}}` | Set exposure time (ms). |
| `start_solve` | — | Trigger plate solve / centering. |
| `start_auto_focuse` | — | Trigger autofocus. Note firmware typo — one `s`. |

## Unconfirmed / Removed Methods

These methods appear in older docs or seestar_alp source but are
**not confirmed** on the S30-Pro firmware. Do not use:

| Method | Status |
|--------|--------|
| `start_exposure` | ❌ Not confirmed — do not use |
| `get_last_frame` | ❌ Not confirmed |
| `get_stacked_img` | ❌ Not confirmed |
| `method_sync` | ❌ Removed from seestar_alp |
| `iscope_get_app_state` | ❌ Not confirmed — use `get_device_state` |

## Binary Frame Protocol (port 4801)

Frames arrive as a continuous stream of `[80-byte header][payload]` pairs.

```
Header format (big-endian, first 20 bytes used):
  fmt = ">HHHIHHBBHH"
  fields: _s1, _s2, _s3, size, _s5, _s6, code, frame_id, width, height

Frame IDs:
  21  Preview  — raw uint16 Bayer GRBG  ← science target
  23  Stack    — ZIP containing raw_data (not used for science)

Payload size < 1000 bytes = heartbeat packet, skip (no payload to read).
```

Science capture reads frame_id 21 only. Expected payload:
`width × height × 2 bytes` (uint16, big-endian).

Sensor: IMX585, 2160 × 3840 px, GRBG Bayer, 3.74″/px.

## Sovereign Acquisition Sequence

The complete capture sequence executed by `DiamondSequence.acquire()`:

```
1. iscope_stop_view          — clear any active session
2. scope_sync [ra, dec]      — point mount
3. sleep(SETTLE_SECONDS=8)   — post-slew settle
4. iscope_start_view         — begin ContinuousExposure
5. sleep(2.0)                — allow first frame to arrive
6. port 4801: read frames until frame_id == 21
7. iscope_stop_view          — end session
8. reshape uint16 array -> write_fits()
```

Implementation: `core/flight/pilot.py` — `DiamondSequence`, `ControlSocket`,
`ImageSocket`.

## Error Codes

Observed on the JSON-RPC control channel (port 4700):

| Code | Meaning | Resolution |
|------|---------|------------|
| `103` | Method not found | Malformed JSON payload or unrecognised method name |
| `1031` | Not connected | Device dropped connection — reconnect and retry |
| `0 bytes` | Silent failure / session lock | SSC UI may be holding control authority — send `iscope_stop_view` first |
