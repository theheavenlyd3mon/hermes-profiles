#!/usr/bin/env bash
# scene_gate.sh — the gate BETWEEN the scene loop and the master render.
# plan_gate.sh guards the start of assembly; review_gate.sh guards delivery;
# this guards the one seam that used to rely on discipline alone: a master
# may only be rendered after every Scene Ledger row is LOCKED on per-scene
# evidence. Field accident: a monolithic composition shipped with all rows
# marked LOCKED retroactively from the master render, every scene file still
# an empty template — the skipped scene-loop [hyperframes-handoff] forbids.
# Run it BEFORE assembling the master and paste the verbatim block into
# project.md; review_gate.sh gate 5 re-runs the same check at delivery, so
# skipping it here cannot survive to the verdict.
# Exit: 0 = gate passes; 2 = scene loop incomplete, no master render.
#
# Usage: scene_gate.sh <videos_dir>/edit/project.md
set -uo pipefail

PROJECT="${1:?usage: scene_gate.sh <videos_dir>/edit/project.md}"
[ -f "$PROJECT" ] || { echo "ERROR: $PROJECT not found" >&2; exit 1; }
RC=0

echo "==================== SCENE GATE ====================="
echo "PROJECT LOG  : $PROJECT"
echo "RUN AT       : $(date '+%Y-%m-%d %H:%M:%S')"

if ! grep -qi 'scene ledger' "$PROJECT"; then
  # No ledger at all: multi-scene pieces REQUIRE one (review/project-log.md
  # § Scene Ledger); only single-scene loops and user-granted mechanical
  # jobs may skip. This script cannot count scenes, so it warns, not fails.
  echo "LEDGER       : none found — REQUIRED for multi-scene pieces; only single-scene loops and user-granted mechanical jobs may skip (review/project-log.md § Scene Ledger)"
  echo "SCENE GATE   : PASS (no ledger to check — if this piece is multi-scene, that is itself a plan defect)"
  exit 0
fi

# only count real ledger rows: the LAST cell is the status word (prose that
# merely mentions a status mid-sentence must not trip the gate)
N_LOCK="$(grep -cE "^\|.*\|[[:space:]]*\*{0,2}LOCKED\*{0,2}[[:space:]]*\|?[[:space:]]*$" "$PROJECT")"
N_OPEN="$(grep -cE "^\|.*\|[[:space:]]*\*{0,2}(DRAFT|INVALIDATED)\*{0,2}[[:space:]]*\|?[[:space:]]*$" "$PROJECT")"
N_VER="$(grep -cE "^\|.*\|[[:space:]]*\*{0,2}VERIFIED\*{0,2}[[:space:]]*\|?[[:space:]]*$" "$PROJECT")"
if [ "$N_OPEN" -gt 0 ]; then
  echo "LEDGER       : ** FAIL ** $N_OPEN row(s) still DRAFT/INVALIDATED — a decorative ledger is a skipped scene-loop ([hyperframes-handoff]; scene-review.md six checks per row, then LOCKED)"
  RC=2
elif [ "$N_VER" -gt 0 ]; then
  echo "LEDGER       : ** FAIL ** $N_VER row(s) VERIFIED but never LOCKED — lock the row before the master, or the master ships unverified scenes"
  RC=2
else
  echo "LEDGER       : ok — $N_LOCK row(s) LOCKED"
fi

# every scene file must carry at least one REAL iteration entry
# ("## iter 1 — ..."). An empty template's "## Iteration log" placeholder
# header must not satisfy this gate — a LOCKED scene with no logged
# render+check round is an unverified scene (project-log.md § One file
# per scene).
SCDIR="$(dirname "$PROJECT")/scenes"
NSC="$(ls "$SCDIR"/*.md 2>/dev/null | wc -l | tr -d ' ')"
if [ "$NSC" -gt 0 ]; then
  NITER="$(grep -l -E '^#{1,3}[[:space:]]*iter[[:space:]]+[0-9]+' "$SCDIR"/*.md 2>/dev/null | wc -l | tr -d ' ')"
  if [ "$NITER" -lt "$NSC" ]; then
    echo "SCENE LOG    : ** FAIL ** $NITER/$NSC scene files have an iteration entry — a LOCKED scene with no logged render+check round is an unverified scene (project-log.md § One file per scene)"
    RC=2
  else
    echo "SCENE LOG    : ok — $NSC scene file(s), all with iteration entries"
  fi
else
  echo "SCENE LOG    : ** FAIL ** no edit/scenes/*.md files — the scene loop never started (one file per scene, review/project-log.md)"
  RC=2
fi

if [ "$RC" -ne 0 ]; then
  echo "SCENE GATE   : FAIL — finish the scene loop (render each scene, six checks, LOCK the row) before ANY master render"
  exit 2
fi
echo "SCENE GATE   : PASS — master render may start; paste this block into project.md"
