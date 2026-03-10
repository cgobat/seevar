#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

PLAN_FILE="$1"

if [ -z "$PLAN_FILE" ]; then
    echo "Usage: ./generate_all_targets.sh <path_to_tonights_plan.json>"
    exit 1
fi

if [ ! -f "$PLAN_FILE" ]; then
    echo "Error: Roster file not found at $PLAN_FILE"
    exit 1
fi

TOTAL_TARGETS=$(jq '.targets | length' "$PLAN_FILE")
echo "Starting full batch generation for $TOTAL_TARGETS targets from $PLAN_FILE..."

COUNT=1
jq -r '.targets[].name' "$PLAN_FILE" | while read -r TARGET; do
    echo "----------------------------------------"
    echo "Processing [$COUNT/$TOTAL_TARGETS]: $TARGET"
    python3 synthetic_fits_generator.py --target "$TARGET" --plan "$PLAN_FILE"
    COUNT=$((COUNT + 1))
done

echo "----------------------------------------"
echo "Full batch generation complete. Check data/local_buffer/ for the .fit files."
