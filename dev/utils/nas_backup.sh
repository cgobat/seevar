#!/bin/bash
# 🛰️ SeeVar: Sovereign Snapshot Utility
# Version: 1.3.2
# Objective: Backup SeeVar code and logic to dynamically defined NAS targets.
#            SMB/CIFS-safe: avoids symlinks and permission sync errors.

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Dynamically find the SeeVar root directory
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Extract the NAS primary_dir dynamically from config.toml
NAS_DIR=$(grep 'primary_dir' "$SOURCE_DIR/config.toml" | cut -d '"' -f 2 || echo "/mnt/astronas/")
BASE_DEST="${NAS_DIR}backup"
SNAPSHOT_DEST="$BASE_DEST/seevar_$TIMESTAMP"

echo "📦 Initiating SeeVar Snapshot from $SOURCE_DIR..."
mkdir -p "$SNAPSHOT_DEST"

# Use -rtv instead of -av to prevent SMB ownership/permission transfer errors
rsync -rtv --delete \
  --exclude='.venv/' \
  --exclude='__pycache__/' \
  --exclude='data/' \
  --exclude='logs/*.log' \
  --exclude='.git/' \
  "$SOURCE_DIR/" "$SNAPSHOT_DEST/"

# SMB mounts often reject symlinks. Write a pointer file instead.
echo "$SNAPSHOT_DEST" > "$BASE_DEST/seevar_latest_pointer.txt"

find "$BASE_DEST" -maxdepth 1 -name "seevar_*" -type d -mtime +30 -exec rm -rf {} +

echo "✅ SeeVar Snapshot secured at: $SNAPSHOT_DEST"
