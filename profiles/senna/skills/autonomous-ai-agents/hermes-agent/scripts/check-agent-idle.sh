#!/usr/bin/env bash
# check-agent-idle.sh — Pre-flight readiness check before issuing /new
#
# Tests three things:
#   1. SQLite lock status on state.db and lcm.db
#   2. Recent write activity to those DBs (within last 5 seconds)
#   3. Unexpected Hermes background processes beyond gateway + active session
#
# Returns 0 if safe to issue /new, 1 if busy (with diagnostic output).
#
# Usage:
#   bash ~/.hermes/profiles/senna/skills/.../hermes-agent/scripts/check-agent-idle.sh
#
# Recommended alias:
#   alias hermes-ready='bash ~/.hermes/profiles/senna/skills/autonomous-ai-agents/hermes-agent/scripts/check-agent-idle.sh'

set -euo pipefail

PROFILE_DIR="${HERMES_HOME:-$HOME/.hermes/profiles/senna}"
STATE_DB="$PROFILE_DIR/state.db"
LCM_DB="${LCM_DB:-$PROFILE_DIR/lcm.db}"
WARNINGS=()
BUSY=false

echo "── Hermes pre-flight check ──"

# --- 1. SQLite lock check (state.db) ---
if [ -f "$STATE_DB" ]; then
  if sqlite3 "$STATE_DB" "PRAGMA busy_timeout=200; SELECT 1;" 2>/dev/null | grep -q 1; then
    echo "  ✓  state.db — responsive"
  else
    echo "  ⚠  state.db — unresponsive (locked or busy)"
    WARNINGS+=("state.db locked")
    BUSY=true
  fi

  # Check for recent writes (within 5 seconds)
  LAST_MOD=$(stat -f "%m" "$STATE_DB" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  AGE=$((NOW - LAST_MOD))
  if [ "$AGE" -le 5 ]; then
    echo "  ⚠  state.db — modified $AGE seconds ago (still settling)"
    WARNINGS+=("state.db recently written")
    BUSY=true
  fi
else
  echo "  -  state.db — not found at $STATE_DB"
fi

# --- 2. SQLite lock check (lcm.db) ---
if [ -f "$LCM_DB" ]; then
  if sqlite3 "$LCM_DB" "PRAGMA busy_timeout=200; SELECT 1;" 2>/dev/null | grep -q 1; then
    echo "  ✓  lcm.db — responsive"
  else
    echo "  ⚠  lcm.db — unresponsive (locked or busy)"
    WARNINGS+=("lcm.db locked")
    BUSY=true
  fi

  LAST_MOD=$(stat -f "%m" "$LCM_DB" 2>/dev/null || echo 0)
  AGE=$((NOW - LAST_MOD))
  if [ "$AGE" -le 5 ]; then
    echo "  ⚠  lcm.db — modified $AGE seconds ago (still settling)"
    WARNINGS+=("lcm.db recently written")
    BUSY=true
  fi
else
  echo "  -  lcm.db — not found at $LCM_DB"
fi

# --- 3. Check for WAL files (pending checkpoint) ---
for DB in "$STATE_DB" "$LCM_DB"; do
  if [ -f "${DB}-wal" ] && [ -s "${DB}-wal" ]; then
    WAL_SIZE=$(stat -f "%z" "${DB}-wal" 2>/dev/null || echo 0)
    if [ "$WAL_SIZE" -gt 4096 ]; then
      echo "  ⚠  $(basename "$DB")-wal — pending checkpoint ($WAL_SIZE bytes)"
      WARNINGS+=("$(basename "$DB")-wal pending")
      BUSY=true
    fi
  fi
done

# --- 4. Unexpected Hermes background processes ---
# Count Hermes-related PIDs excluding gateway (PID from env or live check)
CURRENT_PID=$$
ACTIVE_PIDS=$(ps aux | grep -i "[h]ermes" | awk '{print $2}' | grep -v "^$CURRENT_PID$" || true)
GATEWAY_PID=$(hermes gateway status 2>/dev/null | grep -oE 'PID [0-9]+' | grep -oE '[0-9]+' || echo "")

EXTRA_PIDS=0
for PID in $ACTIVE_PIDS; do
  if [ "$PID" != "$GATEWAY_PID" ]; then
    EXTRA_PIDS=$((EXTRA_PIDS + 1))
  fi
done

if [ "$EXTRA_PIDS" -gt 0 ]; then
  echo "  ⚠  $EXTRA_PIDS extra Hermes process(es) running (beyond current + gateway)"
  WARNINGS+=("unexpected processes")
  BUSY=true
fi

# --- Result ---
echo ""
if $BUSY; then
  echo "✗  System busy — wait a moment, then check again."
  echo "   Recommended: use '/clear' instead of '/new' in TUI."
  exit 1
else
  echo "✓  System idle — safe to issue /new"
  exit 0
fi
