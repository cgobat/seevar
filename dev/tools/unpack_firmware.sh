#!/bin/bash
# Filename: ~/seevar/dev/tools/unpack_firmware.sh
# Version: 1.0.0
# Objective: Download the Seestar iOS application, extract the embedded firmware archive (zwo_iscope_update.tar.bz2), and unpack the Linux filesystem for static analysis.

WORK_DIR="$HOME/seevar/dev/firmware_analysis"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR" || exit 1

echo "[*] Setting up workspace in $WORK_DIR..."

# The firmware is bundled inside the iOS App (IPA file).
# IPA files are just ZIP archives. We need to download a decrypted IPA.
# Since we cannot script an Apple App Store download directly, we will pause and ask the user to provide it.
if [ ! -f "Seestar.ipa" ]; then
    echo "================================================================="
    echo "[!] ACTION REQUIRED: Decrypted Seestar IPA not found."
    echo ""
    echo "To proceed, you must obtain the Seestar iOS app bundle:"
    echo "1. Download the Seestar IPA (using a tool like ipatool or a jailbroken iPhone)."
    echo "2. Rename the file to 'Seestar.ipa'."
    echo "3. Place it in: $WORK_DIR/"
    echo "4. Re-run this script."
    echo "================================================================="
    exit 1
fi

echo "[*] Extracting Seestar.ipa..."
unzip -q Seestar.ipa -d ios_payload

echo "[*] Locating zwo_iscope_update.tar.bz2..."
FIRMWARE_ARCHIVE=$(find ios_payload -name "zwo_iscope_update.tar.bz2")

if [ -z "$FIRMWARE_ARCHIVE" ]; then
    echo "[-] Error: Could not find the firmware archive inside the IPA."
    exit 1
fi

echo "[+] Found firmware archive at: $FIRMWARE_ARCHIVE"
echo "[*] Extracting Linux filesystem (This may take a moment)..."

mkdir -p rootfs
tar -xjf "$FIRMWARE_ARCHIVE" -C rootfs/

echo "[+] Extraction complete!"
echo "[*] The zwoair_imager binary should be located at: rootfs/usr/bin/zwoair_imager"
echo ""
echo "Next Steps: Run 'strings rootfs/usr/bin/zwoair_imager | grep -i method' to hunt for hidden JSON-RPC commands."

# Cleanup the unpacked iOS payload to save space
rm -rf ios_payload
