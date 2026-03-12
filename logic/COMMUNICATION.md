# 📡 COMMUNICATION PROTOCOL

> **Status:** RETIRED
> **Replaced by:** `API_PROTOCOL.MD` (wire protocol, confirmed methods,
> error codes) and `ALPACA_BRIDGE.MD` (bridge role and health-check).
> **Version:** 2.0.0 (Praw)
> **Path:** `logic/COMMUNICATION.md`

This document previously described the Alpaca/port-5555 communication
architecture. That architecture is superseded. All science acquisition
now goes via direct TCP to the S30-Pro on port 4700 (control) and
port 4801 (frame stream).

See `API_PROTOCOL.MD` for the authoritative protocol reference.
