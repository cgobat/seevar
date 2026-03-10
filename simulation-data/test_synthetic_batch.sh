#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

PLAN_FILE="$1"

if [ -z "$PLAN_FILE" ]; then
    echo "Usage: ./test_synthetic_batch.sh <absolute_path_to_tonights_plan.json>"
    exit 1
fi

if [ ! -f "$PLAN_FILE" ]; then
    echo "Error: Roster file not found at $PLAN_FILE"
    exit 1
fi

echo "Extracting 5 random targets from $PLAN_FILE..."

# Parse the JSON for target names, shuffle them, take 5, and loop through them safely
jq -r '.targets[].name' "$PLAN_FILE" | shuf -n 5 | while read -r TARGET; do
    echo "----------------------------------------"
    echo "Starting simulation for: $TARGET"
    python3 synthetic_fits_generator.py --target "$TARGET" --plan "$PLAN_FILE"
done

echo "----------------------------------------"
echo "Batch generation complete. Check data/local_buffer/ for the .fit files."
