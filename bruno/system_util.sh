#!/bin/bash
# Filename: /home/ed/seestar_organizer/bruno/system_util.sh
# Objective: Infrastructure verification and maintenance.

echo "--- Seestar System Utility ---"
if systemctl is-active --quiet seestar.service; then
    echo "[PASS] seestar.service is running."
else
    echo "[FAIL] seestar.service is inactive."
fi

if nc -z 127.0.0.1 5555; then
    echo "[PASS] API Port 5555 is reachable."
else
    echo "[FAIL] API Port 5555 is blocked."
fi
