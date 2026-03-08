#!/bin/bash
# 🛰️ S30-PRO Federation: Sovereign Snapshot Utility
# Version: 1.2.0
# Objective: Point-in-time code and logic backup to NAS with symlink rotation.

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BASE_DEST="/mnt/astronas/backup"
SNAPSHOT_DEST="$BASE_DEST/federation_$TIMESTAMP"
SOURCE_DIR="/home/ed/seestar_organizer"

echo "📦 Initiating Sovereign Snapshot: federation_$TIMESTAMP..."
mkdir -p "$SNAPSHOT_DEST"

# Sync logic, code, and dialects (Excluding heavy binaries and virtualenvs)
rsync -av --delete \
  --exclude='venv/' \
  --exclude='.venv/' \
  --exclude='__pycache__/' \
  --exclude='data/' \
  --exclude='logs/*.log' \
  --exclude='.git/' \
  --exclude='s30_storage/' \
  --exclude='images/' \
  "$SOURCE_DIR/" "$SNAPSHOT_DEST/"

# Maintenance: Update latest pointer and remove backups older than 30 days
ln -sfn "$SNAPSHOT_DEST" "$BASE_DEST/latest"
find "$BASE_DEST" -maxdepth 1 -name "federation_*" -type d -mtime +30 -exec rm -rf {} +

echo "✅ Federation Snapshot secured at: $SNAPSHOT_DEST"
echo "🔗 'latest' pointer updated."
