#!/usr/bin/env bash
# plan_gate.sh — pre-assembly gate: verifies the taste contract carries real
# craft decisions (named entries, not vibes) and the engine choice is logged,
# BEFORE any timeline work. Exists because "wrote a contract" was checkable
# but "wrote an empty contract" was not — an agent can satisfy
# [taste-contract] formally while skipping the whole craft layer; this gate
# closes that hole ([taste-contract], [hyperframes-handoff]).
# Checks: contract section + required fields → Motion plan cites the approved
# palette (craft/motion-recipes.md) or declares freestyle/none → Direction
# entry (pick or logged skip reason) → Engine Decision entry with Chosen line.
# Exit: 0 = pass (assembly may start); 2 = at least one hard miss.
#
# Usage: plan_gate.sh <videos_dir>/edit/project.md
set -uo pipefail

PROJECT="${1:?usage: plan_gate.sh <videos_dir>/edit/project.md}"
[ -f "$PROJECT" ] || { echo "ERROR: $PROJECT not found — no project log, no timeline work"; exit 2; }
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECIPES="$DIR/../craft/motion-recipes.md"
FAIL=0

echo "===================== PLAN GATE ====================="
echo "PROJECT LOG  : $PROJECT"
echo "RUN AT       : $(date '+%Y-%m-%d %H:%M:%S')"

# -- 1. taste contract section + required fields -----------------------------
CONTRACT="$(awk '/^#+ *Taste Contract/{f=1;next} f&&/^## /{f=0} f' "$PROJECT")"
if [ -z "$CONTRACT" ]; then
  echo "contract     : ** MISSING ** — no '## Taste Contract' section"
  FAIL=1
else
  echo "contract     : found"
  for FIELD in "Design read" "Dials" "Signature device" "Text treatment" "Motion plan" "Opening" "Transitions" "Body treatment" "Ending" "Sound" "Anti-patterns"; do
    if grep -qi "$FIELD" <<<"$CONTRACT"; then
      echo "  field      : ok — $FIELD"
    else
      echo "  field      : ** MISSING ** — $FIELD"
      FAIL=1
    fi
  done
fi

# -- 2. Motion plan cites the approved palette --------------------------------
# Scope the match to the Motion plan LINE only: matching the whole contract
# gave false passes (e.g. "ambient" inside "natural ambient audio").
if [ -n "$CONTRACT" ]; then
  MPLAN="$(grep -iA1 'Motion plan' <<<"$CONTRACT")"
  HIT=""
  if [ -f "$RECIPES" ] && [ -n "$MPLAN" ]; then
    while IFS= read -r NAME; do
      [ -n "$NAME" ] || continue
      if grep -qiF "$NAME" <<<"$MPLAN"; then HIT="$NAME"; break; fi
    done < <(grep -oE '^\| \*\*[^*]+\*\*' "$RECIPES" | sed 's/^| \*\*//; s/\*\*$//')
  fi
  if [ -z "$HIT" ] && [ -n "$MPLAN" ]; then
    for P in snap ui gentle lively ambient; do
      if grep -qiE "\`${P}\`|preset[^a-zA-Z]*${P}" <<<"$MPLAN"; then HIT="preset \`$P\`"; break; fi
    done
  fi
  if [ -n "$HIT" ]; then
    echo "motion plan  : ok — cites approved palette ($HIT)"
  elif grep -qi 'freestyle' <<<"$MPLAN"; then
    echo "motion plan  : ok — declared freestyle (the written reason lives in the contract)"
  else
    echo "motion plan  : ** FAIL ** — names no recipe/preset from craft/motion-recipes.md and declares no freestyle (unread palette = unplanned motion; [design-floor] forbids 'no motion' as a taste choice)"
    FAIL=1
  fi
fi

# -- 2b. design floor: the contract must not legislate craft away ------------
# Case study: a contract saying "no BGM, no text overlays, no
# decorative transitions" produced a compliant but design-free deliverable.
if [ -n "$CONTRACT" ]; then
  VIOL="$(grep -oiE 'no (text|title|overlay|motion|animation|graphic|transition)[a-z ]*' <<<"$CONTRACT" | head -3 | tr '\n' ';')"
  if [ -n "$VIOL" ] && ! grep -qiE 'user (asked|requested)|raw cut|用户要求' <<<"$CONTRACT"; then
    echo "design floor : ** FAIL ** — contract removes a required design class ($VIOL) with no user request on record ([design-floor])"
    FAIL=1
  else
    echo "design floor : ok — no blanket craft removal detected"
  fi
  # the four mandatory slots must carry an actual decision, not a shrug
  for SLOT in Opening Transitions Body Ending; do
    LINE="$(grep -i "^\*\*${SLOT}" <<<"$CONTRACT" | head -1)"
    if [ -z "$LINE" ]; then
      echo "  slot       : ** FAIL ** ${SLOT} — not declared ([design-floor]; default picks in art-direction.md § Default kit)"
      FAIL=1
    elif grep -qiE ':[[:space:]]*(none|n/a|tbd|无|没有|不做)|plain cut only' <<<"$LINE"; then
      echo "  slot       : ** FAIL ** ${SLOT} — declared empty; low dials mean restrained design, never absent"
      FAIL=1
    else
      echo "  slot       : ok — ${SLOT}"
    fi
  done
  # scene ledger: multi-scene pieces plan scene-by-scene (project-log.md § Scene Ledger)
  if grep -qi 'scene ledger' "$PROJECT"; then
    LROWS="$(grep -cE '^\|.*(DRAFT|VERIFIED|LOCKED|INVALIDATED)' "$PROJECT")"
    if [ "$LROWS" -ge 1 ]; then
      echo "  ledger     : ok — Scene Ledger present ($LROWS status rows)"
      # per-scene DESIGN: each BODY row must name devices (opening/ending rows
      # are governed by the design-floor slot checks, not here)
      DEVROWS=0; BODYROWS=0; SROWS=0
      while IFS= read -r ROW; do
        grep -qE '^\|[[:space:]]*G-' <<<"$ROW" && continue
        SROWS=$((SROWS+1))
        grep -qiE '\|[^|]*(opening|ending|title card|end card|开场|片尾|收尾)[^|]*\|' <<<"$ROW" && continue
        BODYROWS=$((BODYROWS+1))
        HIT=""
        if [ -f "$RECIPES" ]; then
          while IFS= read -r NAME; do
            [ -n "$NAME" ] || continue
            grep -qiF "$NAME" <<<"$ROW" && { HIT=1; break; }
          done < <(grep -oE '^\| \*\*[^*]+\*\*' "$RECIPES" | sed 's/^| \*\*//; s/\*\*$//')
        fi
        [ -z "$HIT" ] && grep -qiE 'freeze|badge|label|mask|reframe|push-?in|speed.?ramp|pip|polaroid|split|ticker|count-?up|odometer|doodle|sticker|wipe|dissolve|insert|定格|徽章|相纸|贴纸' <<<"$ROW" && HIT=1
        [ -n "$HIT" ] && DEVROWS=$((DEVROWS+1))
      done < <(grep -E '^\|.*(DRAFT|VERIFIED|LOCKED|INVALIDATED)' "$PROJECT")
      if [ "$DEVROWS" -lt "$BODYROWS" ]; then
        echo "               ** FAIL ** only $DEVROWS/$BODYROWS body rows name a device — the device cell IS the per-scene design; rows with just a time box produce one-badge-per-scene bodies (project-log.md § Scene Ledger)"
        FAIL=1
      else
        echo "               ok — all $BODYROWS body rows carry per-scene devices"
      fi
      # one file per scene: detail + iteration log live there, not in the table
      SCDIR="$(dirname "$PROJECT")/scenes"
      NSC="$(ls "$SCDIR"/*.md 2>/dev/null | wc -l | tr -d ' ')"
      NDESIGN="$(grep -l -i 'design' "$SCDIR"/*.md 2>/dev/null | wc -l | tr -d ' ')"
      if [ "$NSC" -lt "$SROWS" ]; then
        echo "               ** FAIL ** $NSC scene file(s) in edit/scenes/ for $SROWS scene rows — one file per scene, created at plan time with its Design block (project-log.md § One file per scene)"
        FAIL=1
      elif [ "$NDESIGN" -lt "$SROWS" ]; then
        echo "               ** FAIL ** $NDESIGN/$SROWS scene files carry a Design block — an empty scene file is a skipped per-scene design"
        FAIL=1
      else
        echo "               ok — $NSC scene files with Design blocks in edit/scenes/"
      fi
    else
      echo "  ledger     : ** FAIL ** Scene Ledger heading exists but no rows carry a status (DRAFT/VERIFIED/LOCKED) — an empty ledger is a skipped plan"
      FAIL=1
    fi
  else
    echo "  ledger     : WARN — no Scene Ledger; required for multi-scene pieces before assembly (review/project-log.md § Scene Ledger)"
  fi
  # the sound plan must exist and silence must carry a quoted user approval
  SNDLINE="$(grep -iA1 '^\*\*Sound' <<<"$CONTRACT")"
  if [ -n "$SNDLINE" ]; then
    if grep -qiE 'silen|no (audio|bgm|sound)|无声|静音' <<<"$SNDLINE" && ! grep -qiE 'user (asked|approved|requested|specified)|用户(要求|批准|指定)' <<<"$SNDLINE"; then
      echo "               ** FAIL ** sound plan declares silence without a quoted user approval ([audio-preserved])"
      FAIL=1
    else
      echo "               ok — sound plan declared"
    fi
  fi
  # the ending must be a designed close, not a bare freeze/hold
  ENDLINE="$(grep -iA1 '^\*\*Ending' <<<"$CONTRACT")"
  if [ -n "$ENDLINE" ]; then
    if grep -qiE 'card|bookend|lockup|credits|logo|ticker|polaroid|closing (text|line)|收尾卡|呼应|片尾卡|拍立得|落款' <<<"$ENDLINE"; then
      echo "               ok — ending is a designed close"
    elif grep -qiE 'freeze|held? frame|hold|定格|冻帧' <<<"$ENDLINE"; then
      echo "               ** FAIL ** ending is only a freeze/hold — needs a designed closing card (art-direction.md § Default kit · Ending)"
      FAIL=1
    else
      echo "               WARN — ending names no card/bookend/lockup; confirm it is a designed close, not a bare stop"
    fi
  fi
  # the body must name library material — and enough of it (richness floor: ≥3 device families)
  # counted across the Body line AND the ledger rows: per-scene design puts the
  # devices in the rows and leaves the Body line as a pointer.
  BODY="$(grep -iA1 '^\*\*Body' <<<"$CONTRACT" | sed -n '1p;2{/^\*\*/!p;}')"
  BODY="$BODY
$(grep -E '^\|.*(DRAFT|VERIFIED|LOCKED|INVALIDATED)' "$PROJECT" 2>/dev/null)"
  if [ -n "$BODY" ]; then
    BCOUNT=0; BNAMES=""
    if [ -f "$RECIPES" ]; then
      while IFS= read -r NAME; do
        [ -n "$NAME" ] || continue
        if grep -qiF "$NAME" <<<"$BODY"; then BCOUNT=$((BCOUNT+1)); BNAMES="$BNAMES$NAME · "; fi
      done < <(grep -oE '^\| \*\*[^*]+\*\*' "$RECIPES" | sed 's/^| \*\*//; s/\*\*$//')
    fi
    for KWPAIR in "camera (rig|push|move)|push-?in:camera move" "pip|picture-in-picture:PiP" "b-?roll:B-roll" "speed ramp:speed ramp" "freeze|定格:freeze emphasis" "track(ing|ed)|跟随:tracking element" "split-?screen|分屏:split screen" "look:|looks/:look"; do
      KW="${KWPAIR%%:*}"; LABEL="${KWPAIR##*:}"
      if grep -qiE "$KW" <<<"$BODY"; then BCOUNT=$((BCOUNT+1)); BNAMES="$BNAMES$LABEL · "; fi
    done
    if [ "$BCOUNT" -eq 0 ]; then
      echo "               ** FAIL ** body names no recipe/look/camera move — a bare clip chain between a nice open and close is a skipped edit (art-direction.md § Default kit · Body)"
      FAIL=1
    elif [ "$BCOUNT" -lt 3 ]; then
      echo "               ** FAIL ** body names only $BCOUNT device family(ies) (${BNAMES%% · }) — richness floor needs ≥3 distinct BODY devices; badges/title/closing card don't count (art-direction.md § Richness floor)"
      FAIL=1
    else
      echo "               ok — body cites $BCOUNT device families (${BNAMES%% · })"
    fi
  fi
  # motivated transitions: hard-cut spine is legal, but ≥2 match/mask links are the floor
  TRLINE="$(grep -iA1 '^\*\*Transitions' <<<"$CONTRACT")"
  if [ -n "$TRLINE" ] && ! grep -qiE 'match|motivated|mask|occlu|action link|object link|whip|遮挡|匹配|推门' <<<"$TRLINE"; then
    echo "               WARN — transitions plan names no motivated/match cut; richness floor asks ≥2 action/object/mask links (craft/transitions.md)"
  fi
  if grep -qiE 'signature device[^a-zA-Z]*(none|n/a|无)' <<<"$CONTRACT"; then
    echo "               WARN: signature device declared none — review §D concept row will likely cap the verdict"
  fi
fi

# -- 3. Direction entry (pick or logged skip reason) --------------------------
if grep -qE '^#+ *Direction' "$PROJECT"; then
  echo "direction    : ok — entry present"
else
  echo "direction    : ** MISSING ** — no '## Direction' entry (the three-direction pick, or the skip reason)"
  FAIL=1
fi

# -- 4. Engine Decision entry --------------------------------------------------
ENGINE="$(awk '/^#+ *Decision[^a-zA-Z]*Engine/{f=1;next} f&&/^## /{f=0} f' "$PROJECT")"
if [ -z "$ENGINE" ]; then
  echo "engine       : ** MISSING ** — no '## Decision — Engine' entry"
  FAIL=1
elif ! grep -qi 'Chosen' <<<"$ENGINE"; then
  echo "engine       : ** FAIL ** — Engine decision has no 'Chosen:' line"
  FAIL=1
else
  CHOSEN="$(grep -i 'Chosen' <<<"$ENGINE" | head -1)"
  echo "engine       : ok — ${CHOSEN}"
  if grep -qi 'ffmpeg' <<<"$CHOSEN" && ! grep -qi 'hyperframes' <<<"$CHOSEN"; then
    # mechanical exemption is user-granted only; an agent calling its own vlog
    # "mechanical" is the exact bypass seen in the field
    if grep -qiE 'user (asked|requested|specified)|用户(要求|指定)' <<<"$ENGINE"; then
      echo "               note: FFmpeg-only with a USER-GRANTED mechanical exemption — final review re-checks it"
    else
      echo "               ** FAIL ** FFmpeg-only assembly, no user-granted mechanical exemption on record — designed deliverables (vlog/montage/intro/promo/recap) route to HyperFrames ([hyperframes-handoff])"
      FAIL=1
    fi
  fi
fi

echo "==================== GATE SUMMARY ===================="
if [ "$FAIL" -ne 0 ]; then
  echo "GATE VERDICT : FAIL — complete the plan in project.md, then re-run; no assembly before this passes"
  exit 2
fi
echo "GATE VERDICT : PASS — assembly may start; paste this block into project.md"
