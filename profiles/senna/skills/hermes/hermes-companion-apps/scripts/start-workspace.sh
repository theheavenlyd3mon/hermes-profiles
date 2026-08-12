#!/bin/bash
# start-workspace.sh — starts dashboard + workspace for a given profile
# Usage: ./start-workspace.sh [profile-name] [gateway-port]
#
# Prerequisites:
#   - Hermes Agent installed with gateway configured for the profile
#   - hermes-workspace cloned and dependencies installed (pnpm install)
#   - .env configured in ~/hermes-workspace/

set -euo pipefail

PROFILE="${1:-senna}"
GATEWAY_PORT="${2:-8642}"
WORKSPACE_DIR="${HERMES_WORKSPACE_DIR:-$HOME/hermes-workspace}"
DASHBOARD_PORT="${HERMES_DASHBOARD_PORT:-9119}"
WORKSPACE_PORT="${PORT:-3000}"

echo "=== Hermes Workspace Startup ==="
echo "Profile:      $PROFILE"
echo "Gateway port: $GATEWAY_PORT"
echo "Workspace:    $WORKSPACE_DIR"
echo ""

# 1. Check gateway is running
echo "[1/3] Checking gateway on :$GATEWAY_PORT..."
if lsof -i :$GATEWAY_PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "  ✓ Gateway is listening"
else
  echo "  ✗ Gateway not running. Starting..."
  hermes --profile "$PROFILE" gateway start
  sleep 3
  if lsof -i :$GATEWAY_PORT -sTCP:LISTEN >/dev/null 2>&1; then
    echo "  ✓ Gateway started"
  else
    echo "  ✗ Gateway failed to start. Run: hermes --profile $PROFILE gateway start"
    exit 1
  fi
fi

# 2. Start dashboard (background)
echo "[2/3] Starting dashboard on :$DASHBOARD_PORT..."
if lsof -i :$DASHBOARD_PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "  ✓ Dashboard already running"
else
  hermes --profile "$PROFILE" dashboard --port "$DASHBOARD_PORT" --no-open --skip-build &
  DASHBOARD_PID=$!
  sleep 3
  if lsof -i :$DASHBOARD_PORT -sTCP:LISTEN >/dev/null 2>&1; then
    echo "  ✓ Dashboard started (PID: $DASHBOARD_PID)"
  else
    echo "  ⚠ Dashboard may still be starting..."
  fi
fi

# 3. Start workspace (foreground)
echo "[3/3] Starting workspace on :$WORKSPACE_PORT..."
echo ""
echo "=== URLs ==="
echo "  Workspace: http://127.0.0.1:$WORKSPACE_PORT"
echo "  Dashboard: http://127.0.0.1:$DASHBOARD_PORT"
echo "  Gateway:   http://127.0.0.1:$GATEWAY_PORT"
echo ""
echo "Press Ctrl+C to stop."
echo ""

cd "$WORKSPACE_DIR"
HERMES_API_URL="http://127.0.0.1:$GATEWAY_PORT" exec pnpm dev
