#!/usr/bin/env bash
# black_check.sh — objective black-gap evidence for final review.
# Detects black segments (unfilled timeline gaps, bad xfade offsets, missing
# clips) that read as broken transitions in the deliverable.
# Head/tail black inside the first/last GRACE seconds is reported as ADVISORY
# (intentional fade-in/out is a design choice); interior black is a FAIL.
# Exit codes: 0 = no interior black; 2 = interior black gap(s) found.
#
# Usage: black_check.sh INPUT.mp4 [MIN_DUR] [PIX_TH]
#   MIN_DUR  minimum black duration to flag, seconds (default 0.1)
#   PIX_TH   blackdetect luma threshold 0-1 (default 0.10)
set -uo pipefail

IN="${1:?usage: black_check.sh INPUT [MIN_DUR] [PIX_TH]}"
MIN_DUR="${2:-0.1}"
PIX_TH="${3:-0.10}"
GRACE=0.5
[ -f "$IN" ] || { echo "ERROR: $IN not found" >&2; exit 1; }

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
echo "DURATION     : ${DUR}s   (min flagged black: ${MIN_DUR}s, luma th: ${PIX_TH})"

SEGS=$(ffmpeg -hide_banner -nostats -i "$IN" \
  -vf "blackdetect=d=${MIN_DUR}:pix_th=${PIX_TH}" -an -f null - 2>&1 | \
  grep -o 'black_start:[0-9.]* black_end:[0-9.]* black_duration:[0-9.]*' || true)

if [ -z "$SEGS" ]; then
  echo "BLACK GAPS   : none"
  echo "VERDICT      : PASS — no black segments >= ${MIN_DUR}s"
  exit 0
fi

FAILS=0
while read -r LINE; do
  S=$(echo "$LINE" | sed 's/.*black_start:\([0-9.]*\).*/\1/')
  E=$(echo "$LINE" | sed 's/.*black_end:\([0-9.]*\).*/\1/')
  D=$(echo "$LINE" | sed 's/.*black_duration:\([0-9.]*\).*/\1/')
  KIND=$(python3 -c "
s,e,d,dur,g=float('$S'),float('$E'),float('$D'),float('$DUR'),float('$GRACE')
print('head' if s < g else 'tail' if e > dur-g else 'interior')")
  if [ "$KIND" = "interior" ]; then
    echo "BLACK GAP    : ${S}s -> ${E}s  (${D}s)  INTERIOR — broken transition / timeline gap"
    FAILS=$((FAILS+1))
  else
    echo "BLACK GAP    : ${S}s -> ${E}s  (${D}s)  ${KIND} — advisory (fade-in/out is legitimate if declared)"
  fi
done <<< "$SEGS"

if [ "$FAILS" -gt 0 ]; then
  echo "VERDICT      : FAIL — ${FAILS} interior black gap(s); inspect the timeline at those timestamps"
  echo "HINT         : common causes — clip data-start/data-duration gap (HyperFrames),"
  echo "               xfade offset != A_duration - fade_duration (FFmpeg),"
  echo "               a missing/failed asset rendering as black."
  exit 2
fi
echo "VERDICT      : PASS — only head/tail black (verify it is a declared fade)"
