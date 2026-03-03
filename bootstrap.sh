#!/bin/bash
# S30-PRO Federation: Infrastructure Bootstrap
# Version: 2.5.0 (Resurrection Grade)
# Objective: Rebuilds the RAID1 directory structure and initializes the Register.

echo "🏗️  Phase 1: Hardening RAID1 Directory Structure..."
mkdir -p ~/seestar_organizer/{core/preflight,core/flight,core/postflight,data,utils,logic,logs/archive}
echo "✅ Directories Secured."

echo "🔑 Phase 2: Enforcing Execution Permissions..."
chmod +x ~/seestar_organizer/core/fed-mission
chmod +x ~/seestar_organizer/utils/generate_manifest.py
echo "✅ Permissions Set."

echo "📖 Phase 3: Opening the Master Register..."
if [ -f "~/seestar_organizer/data/targets.json" ]; then
    python3 ~/seestar_organizer/utils/init_ledger.py
    echo "✅ Ledger Initialized from Master Catalog."
else
    echo "⚠️  Warning: targets.json missing. Register cannot be opened."
fi

echo "🛰️  Phase 4: Running Boot Audit..."
# Ensures all 6 JSON pillars exist
python3 ~/seestar_organizer/utils/generate_manifest.py

echo "🏁 Bootstrap Complete. Federation Engine is ONLINE."
