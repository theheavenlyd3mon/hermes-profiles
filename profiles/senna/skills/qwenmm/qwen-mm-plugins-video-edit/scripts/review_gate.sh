#!/usr/bin/env bash
# review_gate.sh — ONE command that runs every hard technical gate for final
# review. Exists so the gates cannot be individually "forgotten": the review
# verdict must paste this script's verbatim output; a verdict without a
# REVIEW GATE block is void ([review-independence]).
# Runs: ffprobe summary → loudness_check → black_check → plan_gate re-run
# (gate 4 re-validates the plan against the nearest project.md, so skipping
# plan_gate during planning cannot survive to delivery).
# Exit: 0 = all gates pass; 2 = at least one hard gate failed.
#
# Usage: review_gate.sh FINAL.mp4
set -uo pipefail

IN="${1:?usage: review_gate.sh FINAL.mp4}"
[ -f "$IN" ] || { echo "ERROR: $IN not found" >&2; exit 1; }
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FAIL=0

echo "==================== REVIEW GATE ===================="
echo "FILE         : $IN"
echo "SHA1(head)   : $(head -c 1048576 "$IN" | shasum | cut -c1-12)  (identity of the reviewed bytes)"
echo "RUN AT       : $(date '+%Y-%m-%d %H:%M:%S')"

echo "---------------- gate 1/5: ffprobe ------------------"
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate \
  -of default=nw=1 "$IN" || FAIL=1

echo "---------------- gate 2/5: loudness -----------------"
bash "$DIR/loudness_check.sh" "$IN"; RC_L=$?
[ "$RC_L" -ge 2 ] && FAIL=1

echo "---------------- gate 3/5: black gaps ---------------"
bash "$DIR/black_check.sh" "$IN"; RC_B=$?
[ "$RC_B" -ge 2 ] && FAIL=1

# gate 4: the PLAN must have passed before this output existed. Without this
# check plan_gate.sh is bypassable by simply never running it — which is
# exactly how empty taste contracts reached delivery.
echo "---------------- gate 4/5: plan gate ----------------"
PROJECT=""
for CAND in "$(dirname "$IN")/project.md" "$(dirname "$IN")/../project.md" \
            "$(dirname "$IN")/edit/project.md"; do
  [ -f "$CAND" ] && { PROJECT="$CAND"; break; }
done
if [ -z "$PROJECT" ]; then
  echo "** FAIL ** no project.md found near the output — no plan, no delivery"
  RC_P=2
else
  echo "PROJECT LOG  : $PROJECT"
  PLAN_OUT="$(bash "$DIR/plan_gate.sh" "$PROJECT" 2>&1)"; RC_P=$?
  # echo every check line (skip plan_gate's own banner/summary decoration)
  grep -vE '^=+|^PLAN GATE|^RUN AT|^PROJECT LOG' <<<"$PLAN_OUT" | sed 's/^/  /'
fi

echo "---------------- gate 5/5: scene ledger --------------"
# Single source of truth: scene_gate.sh (the pre-master gate). Re-running it
# here means skipping it before the master render cannot survive to delivery.
RC_LED=0
if [ -n "$PROJECT" ]; then
  SG_OUT="$(bash "$DIR/scene_gate.sh" "$PROJECT" 2>&1)"; RC_LED=$?
  grep -vE '^=+|^SCENE GATE|^RUN AT|^PROJECT LOG' <<<"$SG_OUT" | sed 's/^/  /'
else
  echo "LEDGER       : skipped — no project.md (already failed gate 4)"
fi
[ "$RC_P" -ge 2 ] && FAIL=1
[ "$RC_LED" -ge 2 ] && FAIL=1

echo "==================== GATE SUMMARY ===================="
echo "loudness     : exit $RC_L $( [ "$RC_L" -ge 2 ] && echo '** FAIL **' || echo 'ok' )"
echo "black gaps   : exit $RC_B $( [ "$RC_B" -ge 2 ] && echo '** FAIL **' || echo 'ok' )"
echo "plan gate    : exit $RC_P $( [ "$RC_P" -ge 2 ] && echo '** FAIL **' || echo 'ok' )"
echo "scene ledger : exit $RC_LED $( [ "$RC_LED" -ge 2 ] && echo '** FAIL **' || echo 'ok' )"
echo "REMINDER     : technical only. The verdict still needs the Engine line"
echo "               (matches project.md) and the Appeal rubric scored on the"
echo "               SEVEN VERBATIM rows of final-review.md §D:"
echo "               concept(veto) · contract · rhythm · restraint · craft ·"
echo "               sound · typography&motion. Invented rows = void review."
echo "               [design-floor]: no opening treatment / no animated text"
echo "               / no deliberate ending = fails §D regardless of gates."
echo "               Device ledger: every contract-declared device needs a"
echo "               render timestamp in the verdict — a declared device with"
echo "               no timestamp = verdict FAIL ('PASS with notes' is illegal)."
if [ "$FAIL" -ne 0 ]; then
  echo "GATE VERDICT : FAIL — fix and re-run on the NEW file (review invalidation rule)"
  exit 2
fi
echo "GATE VERDICT : PASS — paste this whole block into the review verdict / project.md"
