#!/bin/bash
# Filename: core/utils/reconnect_all.sh
# Objective: Force-mount S30 storage and wait for API readiness.

S30_IP="192.168.178.26"
MOUNT_POINT="$HOME/seestar_organizer/s30_storage"

echo "🔄 Step 1: Refreshing Samba Mount..."
sudo mount -a
if [ -d "$MOUNT_POINT/MyWorks" ]; then
    echo "✅ Mount Successful: MyWorks is visible."
else
    echo "⚠️ Mount Failed: Drive still not reachable."
fi

echo "📡 Step 2: Waiting for SSC Bridge on $S30_IP..."
for port in 80 5555 8080; do
    if nc -zv $S30_IP $port 2>/dev/null; then
        echo "✅ FOUND! Williamina is listening on port $port."
        exit 0
    fi
done

echo "❌ Failure: No open ports found. Is Guest Mode active in the Seestar App?"
