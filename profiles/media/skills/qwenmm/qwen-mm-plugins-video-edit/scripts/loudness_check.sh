#!/usr/bin/env bash
# loudness_check.sh — objective audio evidence for final review.
# Checks: (1) audio stream presence  (2) integrated loudness / true peak / LRA
#         (3) full-track-silence heuristic.
# Exit codes: 0 = audio present & measured; 2 = NO audio stream (fails the
# [audio-preserved] rule for footage/narration deliverables unless approved).
#
# Usage: loudness_check.sh INPUT.mp4
set -uo pipefail

IN="${1:?usage: loudness_check.sh INPUT}"
[ -f "$IN" ] || { echo "ERROR: $IN not found" >&2; exit 1; }

ASTREAMS=$(ffprobe -v error -select_streams a -show_entries stream=index,codec_name,channels,sample_rate -of csv=p=0 "$IN")
if [ -z "$ASTREAMS" ]; then
  echo "AUDIO STREAM : ABSENT"
  echo "VERDICT      : FAIL — no audio stream ([audio-preserved]: needs explicit approval)"
  exit 2
fi
echo "AUDIO STREAM : present ($ASTREAMS)"

# EBU R128 measurement (loudnorm print_format json on a null mux)
STATS=$(ffmpeg -hide_banner -nostats -i "$IN" -map a:0 \
  -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | \
  sed -n '/{/,/}/p')

# Require at least one digit in the capture: ffmpeg prints "-inf" for silent
# tracks, and a bare "-" used to reach float() and crash the advisory.
II=$(echo "$STATS"   | sed -n 's/.*"input_i"[^-0-9]*\(-\{0,1\}[0-9][0-9.]*\).*/\1/p')
TP=$(echo "$STATS"   | sed -n 's/.*"input_tp"[^-0-9]*\(-\{0,1\}[0-9][0-9.]*\).*/\1/p')
LRA=$(echo "$STATS"  | sed -n 's/.*"input_lra"[^-0-9]*\(-\{0,1\}[0-9][0-9.]*\).*/\1/p')
THR=$(echo "$STATS"  | sed -n 's/.*"input_thresh"[^-0-9]*\(-\{0,1\}[0-9][0-9.]*\).*/\1/p')

# "-inf" integrated (fully digital-silent stream) reads as missing above — catch it
grep -q '"input_i"[^0-9-]*-inf' <<<"$STATS" && { 
  echo "INTEGRATED   : -inf LUFS  (digital silence)"
  echo "VERDICT      : FAIL — track is digitally silent"; exit 2; }

echo "INTEGRATED   : ${II:-?} LUFS   (platform target -14, podcasts -16)"
echo "TRUE PEAK    : ${TP:-?} dBTP   (keep <= -1.0 ~ -1.5)"
echo "LRA          : ${LRA:-?} LU     (dialogue-led 6-12 typical)"

# Full-silence heuristic: integrated below -50 LUFS means effectively silent
if [ -n "${II:-}" ]; then
  SILENT=$(python3 -c "print('yes' if float('$II') < -50 else 'no')")
  if [ "$SILENT" = "yes" ]; then
    echo "VERDICT      : FAIL — track is effectively silent (I=${II} LUFS)"
    exit 2
  fi
fi

# Loud/quiet advisory (not a failure)
if [ -n "${II:-}" ]; then
  python3 - "$II" "${TP:-}" <<'EOF'
import sys
def num(v, d=0.0):
    try: return float(v)
    except (TypeError, ValueError): return d
i = num(sys.argv[1]); tp = num(sys.argv[2] if len(sys.argv) > 2 else None)
notes = []
if i > -10:  notes.append(f"hot mix ({i} LUFS > -10): platforms will turn it down")
if i < -24:  notes.append(f"quiet mix ({i} LUFS < -24): viewers will crank volume")
if tp > -1.0: notes.append(f"true peak {tp} dBTP > -1.0: clipping risk after lossy encode")
print("ADVISORY     : " + ("; ".join(notes) if notes else "levels look reasonable"))
EOF
fi
echo "VERDICT      : PASS — audio present and measured"
