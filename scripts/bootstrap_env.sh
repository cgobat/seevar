#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# PROJECT: Federation Fleet Command
# MODULE:  Environment Guardian
# VERSION: 1.4.17 (Infrastructure Baseline)
# OBJECTIVE: Guarantee .venv integrity and dependencies on boot/install.
# -----------------------------------------------------------------------------
set -e

VENV_DIR="/home/ed/seestar_organizer/.venv"
REQ_PACKAGES=("flask" "toml")

echo "[PRE-FLIGHT] Verifying Environment: $VENV_DIR"

# 1. Ensure the virtual environment exists
if [ ! -f "$VENV_DIR/bin/python3" ]; then
    echo "[PRE-FLIGHT] .venv missing. Rebuilding from active python..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Upgrade pip to prevent legacy installation errors
"$VENV_DIR/bin/python3" -m pip install --upgrade pip -q

# 3. Enforce strictly required packages
for pkg in "${REQ_PACKAGES[@]}";; do
    if ! "$VENV_DIR/bin/python3" -c "import $pkg" 2>/dev/null; then
        echo "[PRE-FLIGHT] Missing module '$pkg'. Forcing installation..."
        "$VENV_DIR/bin/python3" -m pip install "$pkg" -q
    else
        echo "[PRE-FLIGHT] Module '$pkg' verified."
    fi
done

echo "[PRE-FLIGHT] Environment Lock: SECURED."
