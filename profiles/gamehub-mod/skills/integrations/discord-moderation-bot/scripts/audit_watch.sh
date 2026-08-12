#!/usr/bin/env bash
# audit_watch.sh — silent Discord audit-log watchdog for a Hermes moderation bot.
# Designed as a `no_agent` cron job: it POSTs to Discord itself and stays silent
# when nothing is new (deliver=local so the agent never sees output).
#
# Register:
#   hermes cron create --name audit-watch --no-agent --deliver local \
#     --schedule "0 */6 * * *" --script audit_watch.sh
#
# === FILL THESE IN FOR YOUR SERVER ===
PROFILE_DIR="${PROFILE_DIR:-$HOME/.hermes/profiles/gamehub-mod}"
GUILD=""                 # server ID
AUDIT_CH=""              # digest channel, e.g. #audit-review
ALERT_CH=""              # anomaly-alert channel, e.g. #mod-ops
# Who gets paged on anomalies. Default = owner / senior-mod role,
# NOT the mod-lead/mod role (user preference: owner wants anomaly pings, not the mod team).
ALERT_MENTION="<@&OWNER_ROLE_ID>"
BOT_ID=""                # the bot's user ID
# =====================================

set -euo pipefail

ENV_FILE="$PROFILE_DIR/.env"
STATE_FILE="$PROFILE_DIR/scripts/audit_state.json"

token="$(grep -E '^DISCORD_BOT_TOKEN=' "$ENV_FILE" | head -1 | cut -d= -f2-)"
[ -z "$token" ] && { echo "NO_TOKEN"; exit 1; }

tmp="$(mktemp)"
curl -s -H "Authorization: Bot $token" \
  "https://discord.com/api/v10/guilds/$GUILD/audit-logs?limit=100" -o "$tmp"

TOKEN="$token" python3 - "$tmp" "$STATE_FILE" "$AUDIT_CH" "$ALERT_CH" "$ALERT_MENTION" "$BOT_ID" <<'PY'
import sys, json, os, subprocess, tempfile

tmp, statefile, audit_ch, alert_ch, alert_mention, bot_id = sys.argv[1:7]
with open(tmp) as f:
    data = json.load(f)
entries = data.get("audit_log_entries", [])
if not entries:
    sys.exit(0)

state = {}
if os.path.exists(statefile):
    try:
        state = json.load(open(statefile))
    except Exception:
        state = {}
last = state.get("last_id")
newest = entries[0]["id"]

LABELS = {
    1:"Guild settings updated", 10:"Channel created", 11:"Channel updated",
    12:"Channel deleted", 13:"Channel overwrite added", 14:"Channel overwrite updated",
    15:"Channel overwrite removed",
    20:"Member kicked", 21:"Members pruned", 22:"Member banned",
    23:"Member unbanned", 24:"Member updated", 25:"Member roles updated",
    26:"Member moved", 27:"Member disconnected", 28:"Bot added",
    30:"Role created", 31:"Role updated", 32:"Role deleted",
    40:"Invite created", 41:"Invite updated", 42:"Invite deleted",
    50:"Webhook created", 51:"Webhook updated", 52:"Webhook deleted",
    60:"Emoji created", 61:"Emoji updated", 62:"Emoji deleted",
    72:"Message deleted", 73:"Messages bulk deleted", 74:"Message pinned",
    75:"Message unpinned", 80:"Integration created", 81:"Integration updated",
    82:"Integration deleted",
}
# Action types treated as anomalies worth a human ping.
ANOMALY = {1, 20, 21, 22, 23, 25, 30, 31, 32, 72, 73}

if last is None:
    # First run: baseline only, do not spam.
    json.dump({"last_id": newest}, open(statefile, "w"))
    sys.exit(0)

idx = None
for i, e in enumerate(entries):
    if e["id"] == last:
        idx = i
        break
new = entries if idx is None else entries[:idx]

if not new:
    sys.exit(0)

def post(channel, text):
    pf = tempfile.mktemp(suffix=".json")
    with open(pf, "wb") as f:
        f.write(json.dumps({"content": text}).encode())
    subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bot {os.environ['TOKEN']}",
         "-H", "Content-Type: application/json", "--json", f"@{pf}",
         f"https://discord.com/api/v10/channels/{channel}/messages"],
        capture_output=True)
    os.unlink(pf)

def fmt(e):
    at = e.get("action_type")
    label = LABELS.get(at, f"Action {at}")
    actor = f"<@{e.get('user_id')}>"
    return f"• {label} — by {actor} (entry {e.get('id')})"

lines = [f"\U0001F4CB **Audit log — {len(new)} new event(s)**"]
anomalies = [e for e in new if e.get("action_type") in ANOMALY]
for e in new[:20]:
    lines.append(fmt(e))
if len(new) > 20:
    lines.append(f"\u2026 and {len(new) - 20} more")
post(audit_ch, "\n".join(lines))

if anomalies:
    a_lines = [f"{alert_mention} \u26A0 **Anomaly detected** in audit log:"]
    for e in anomalies[:20]:
        a_lines.append(fmt(e))
    post(alert_ch, "\n".join(a_lines))

json.dump({"last_id": newest}, open(statefile, "w"))
PY
