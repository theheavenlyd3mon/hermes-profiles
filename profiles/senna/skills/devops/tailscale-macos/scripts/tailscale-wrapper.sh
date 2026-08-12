#!/bin/bash
# Wrapper: route the Homebrew `tailscale` CLI to the native Tailscale.app GUI LocalAPI.
# The GUI runs its daemon as IPNExtension and exposes LocalAPI on a TCP port
# (localhost:<port>) instead of the default unix socket the CLI expects.
# Auto-detects that port from the sameuserproof token file so it survives restarts.
# Install to ~/.local/bin/tailscale and ensure ~/.local/bin is FIRST in PATH.

set -euo pipefail

IPN_DIR="$HOME/Library/Group Containers/W5364U7YZB.group.io.tailscale.ipn.macos"
REAL_BIN="/usr/local/bin/tailscale"

PORT=""
if [ -d "$IPN_DIR" ]; then
  for f in "$IPN_DIR"/sameuserproof-*; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    if [[ "$base" =~ sameuserproof-([0-9]+)- ]]; then
      PORT="${BASH_REMATCH[1]}"
      break
    fi
  done
fi

if [ -n "$PORT" ]; then
  export TS_SOCKET="localhost:${PORT}"
else
  echo "tailscale-wrapper: could not find Tailscale GUI LocalAPI port (is the app running?)" >&2
fi

exec "$REAL_BIN" "$@"
