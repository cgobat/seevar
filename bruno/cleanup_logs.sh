#!/bin/bash
# Filename: /home/ed/seestar_organizer/bruno/cleanup_logs.sh
# Version: 1.0.0
# Objective: Manages log rotation and directory cleanup for the Seestar Organizer.

LOG_DIR="/home/ed/seestar_organizer/logs/"
RETENTION_DAYS=7

echo "--- Seestar Log Cleanup Utility ---"

if [ ! -d "$LOG_DIR" ]; then
    echo "[INFO] Log directory does not exist. Creating it now..."
    mkdir -p "$LOG_DIR"
    exit 0
fi

# Count files older than retention period
OLD_FILES=$(find "$LOG_DIR" -type f -mtime +$RETENTION_DAYS | wc -l)

if [ "$OLD_FILES" -gt 0 ]; then
    echo "[INFO] Found $OLD_FILES logs older than $RETENTION_DAYS days. Cleaning up..."
    find "$LOG_DIR" -type f -mtime +$RETENTION_DAYS -delete
    echo "[PASS] Cleanup complete."
else
    echo "[PASS] No old logs found. Storage is optimal."
fi

# Show current storage status of the log directory
du -sh "$LOG_DIR"
