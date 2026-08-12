#!/usr/bin/env bash
# Discord REST introspection via curl.
# WHY curl (not Python urllib): Discord's Cloudflare WAF returns HTTP 403
# Error 1010 ("Access denied based on browser signature") to urllib's TLS
# stack even with a valid token. curl passes cleanly. See
# references/discord-api-introspection.md.
#
# Usage:
#   bash scripts/discord_introspect.sh [profile_env_path] [guild_id]
# guild_id is auto-detected from the first guild the bot is in if omitted.
set -euo pipefail

PROFILE_ENV="${1:-$HOME/.hermes/profiles/gamehub-mod/.env}"
TOKEN="$(grep -E '^DISCORD_BOT_TOKEN=' "$PROFILE_ENV" | head -1 | cut -d= -f2-)"
[ -z "$TOKEN" ] && { echo "no DISCORD_BOT_TOKEN in $PROFILE_ENV" >&2; exit 1; }

API="https://discord.com/api/v10"
hdr=(-H "Authorization: Bot $TOKEN" -H "Accept: application/json")

echo "=== BOT SELF (token check) ==="
curl -s -m 20 "${hdr[@]}" "$API/users/@me" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(' ',d.get('id'),d.get('username'))"

echo "=== GUILDS ==="
curl -s -m 20 "${hdr[@]}" "$API/users/@me/guilds" \
  | python3 -c "import sys,json;[print(' ',g['id'],g['name']) for g in json.load(sys.stdin)]"

G="${2:-$(curl -s -m 20 "${hdr[@]}" "$API/users/@me/guilds" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)[0]['id'])")}"
echo "=== CHANNELS (guild $G) ==="
curl -s -m 20 "${hdr[@]}" "$API/guilds/$G/channels" \
  | python3 -c "import sys,json;[print(' ',c['type'],c['id'],c.get('name','?')) for c in json.load(sys.stdin)]"
echo "=== ROLES (guild $G) ==="
curl -s -m 20 "${hdr[@]}" "$API/guilds/$G/roles" \
  | python3 -c "import sys,json;[print(' ',r['id'],r['name']) for r in json.load(sys.stdin)]"
