#!/usr/bin/env bash
# gateway-crash-scan.sh — fleet-wide crash-on-conversation + api-server diagnostic.
# Run: bash ~/.hermes/profiles/senna/skills/hermes/gateway-health-check/scripts/gateway-crash-scan.sh
set -u
HERMES=${HERMES_HOME:-$HOME/.hermes}
for p in "$HERMES"/profiles/*/; do
  name=$(basename "$p")
  log="$p/logs/gateway.error.log"
  glog="$p/logs/gateway.log"
  [ -f "$log" ] || continue
  pid=$(pgrep -f "gateway run.*--profile $name" | head -1)
  conn=$(grep "Connected as" "$glog" 2>/dev/null | tail -1 | sed 's/.*Connected as //')
  imp=$(grep -E "ImportError|cannot import name" "$log" 2>/dev/null | tail -1 | sed -E 's/.*(ImportError|cannot import name)/\1/')
  api=$(grep "API_SERVER_KEY is required" "$log" 2>/dev/null | tail -1)
  mcp=$(grep -c "MCP server .* initial connection failed" "$log" 2>/dev/null)
  echo "=== $name | pid=${pid:-DOWN} | conn=${conn:-none}"
  [ -n "$imp" ] && echo "  IMPORT-CRASH: $imp"
  [ -n "$api" ] && echo "  API_SERVER_KEY: MISSING"
  [ "${mcp:-0}" -gt 0 ] && echo "  MCP warning count: $mcp"
done
