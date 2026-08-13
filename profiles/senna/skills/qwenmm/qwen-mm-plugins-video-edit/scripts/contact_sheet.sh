#!/usr/bin/env bash
# contact_sheet.sh — extract frames at a fixed interval and tile them into one
# JPG for final-review evidence. Columns fixed at 5; rows derived from duration.
#
# Usage: contact_sheet.sh INPUT.mp4 OUTPUT.jpg [FPS] [TILE_W]
#   FPS    sampling rate, default 1 (one frame per second)
#   TILE_W per-tile width px, default 320 (height auto, aspect kept)
set -euo pipefail

IN="${1:?usage: contact_sheet.sh INPUT OUTPUT [FPS] [TILE_W]}"
OUT="${2:?missing OUTPUT}"
FPS="${3:-1}"
TILE_W="${4:-320}"

[ -f "$IN" ] || { echo "ERROR: $IN not found" >&2; exit 1; }

DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$IN")
N=$(python3 -c "import math; print(max(1, math.ceil(float('$DUR') * float('$FPS'))))")
COLS=5
ROWS=$(python3 -c "import math; print(max(1, math.ceil($N / $COLS)))")

# NOTE: no drawtext (some ffmpeg builds lack the filter); frame order is
# row-major so frame k sits at t = k/FPS — annotate mentally or in the report.
ffmpeg -y -v error -i "$IN" \
  -vf "fps=${FPS},scale=${TILE_W}:-2,tile=${COLS}x${ROWS}:margin=4:padding=4:color=0x101014" \
  -frames:v 1 -q:v 3 "$OUT"

echo "contact sheet: $OUT  (${N} frames @ ${FPS}fps, ${COLS}x${ROWS}, src ${DUR%.*}s)"
