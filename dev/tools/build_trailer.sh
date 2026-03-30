#!/bin/bash
# Filename: ~/seevar/dev/tools/build_trailer.sh
# Version: 1.0.2
# Objective: Robustly normalize and concatenate all SeeVar movie phases.

WORK_DIR="$HOME/seevar/dev/tools"
FINAL_OUT="$WORK_DIR/SeeVar_The_Movie.mp4"
TMP_DIR="$WORK_DIR/tmp_render"

cd "$WORK_DIR" || exit 1
mkdir -p "$TMP_DIR"

# Paths to the four video assets
V1="edfilx.mp4"
V2="Kaspar.mp4"
V3="media/videos/sovereign_flow/1080p60/SovereignCommunicationFlow.mp4"
V4="media/videos/postflight_movie/1080p60/PostflightScienceFlow.mp4"

# Check if the external assets are present
if [ ! -f "$V1" ] || [ ! -f "$V2" ]; then
    echo "[-] Error: Ensure both 'edfilx.mp4' and 'Kaspar.mp4' are in ~/seevar/dev/tools/"
    exit 1
fi

echo "[*] Phase 1: Normalizing videos to 1080p 60fps with stereo audio..."

# 1. edfilx.mp4 (already has audio, just normalize video/audio formats)
echo " -> Processing Intro..."
ffmpeg -y -i "$V1" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60" \
  -c:v libx264 -preset fast -crf 18 -c:a aac -ar 48000 -ac 2 "$TMP_DIR/part1.mp4" </dev/null -loglevel warning

# 2-4. Manim & Preflight videos (no audio, inject silence matching exact video length)
# We use -f lavfi -i anullsrc and -shortest so the silence stops exactly when the video stops.
for i in 2 3 4; do
    eval vid=\$V$i
    echo " -> Processing Part $i..."
    ffmpeg -y -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -i "$vid" \
      -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60" \
      -c:v libx264 -preset fast -crf 18 -c:a aac -shortest "$TMP_DIR/part$i.mp4" </dev/null -loglevel warning
done

echo "[*] Phase 2: Stitching files together..."

# Create the concat list
cat << TXT > "$TMP_DIR/concat_list.txt"
file 'part1.mp4'
file 'part2.mp4'
file 'part3.mp4'
file 'part4.mp4'
TXT

# Concat without re-encoding (extremely fast since they are now identically formatted)
ffmpeg -y -f concat -safe 0 -i "$TMP_DIR/concat_list.txt" -c copy "$FINAL_OUT" -loglevel warning

if [ $? -eq 0 ]; then
    echo "[+] Rendering Complete! Your movie is ready at:"
    echo "$FINAL_OUT"
    echo "You can now safely run: cp $FINAL_OUT /mnt/astronas/"
    # Cleanup temp files
    rm -rf "$TMP_DIR"
else
    echo "[-] FFmpeg encountered an error during concatenation."
fi
