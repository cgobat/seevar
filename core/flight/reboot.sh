#!/bin/bash
# ==============================================================================
# Script:  /core/flight/reboot.sh
# Purpose: Issue a hard reboot to a Seestar via the local SSC bridge,
#          monitor the network drop/reconnect, and verify API readiness.
# Usage:   ./reboot.sh [IP_ADDRESS]
# ==============================================================================

# Default to the S30 if no IP is provided as an argument
SEESTAR_IP=${1:-"192.168.178.26"}
BRIDGE_URL="http://127.0.0.1:5432/1/command"

echo "[1/4] Sending kill command to $SEESTAR_IP via bridge..."
curl -s -X POST $BRIDGE_URL -d "command=pi_reboot" > /dev/null

echo -n "[2/4] Waiting for Seestar to drop off the network..."
while ping -c 1 -W 1 $SEESTAR_IP &> /dev/null; do
    echo -n "."
    sleep 2
done
echo " [OFFLINE]"

echo -n "[3/4] Waiting for Android OS to boot and reconnect WiFi..."
while ! ping -c 1 -W 1 $SEESTAR_IP &> /dev/null; do
    echo -n "."
    sleep 2
done
echo " [ONLINE]"

echo -n "[4/4] Waiting for Seestar Alpaca daemon to initialize..."
# Loop until the bridge gets a valid response indicating the app is awake
while true; do
    RESPONSE=$(curl -s -X POST $BRIDGE_URL -d "command=get_event_state")
    # If the response contains a JSON bracket, the daemon is talking
    if echo "$RESPONSE" | grep -q "{"; then
        break
    fi
    echo -n "."
    sleep 3
done
echo " [READY]"

echo "✅ Seestar $SEESTAR_IP is fully zeroed out and ready for operations."
