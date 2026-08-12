#!/usr/bin/env bash
# mod_alert_watchdog.sh — recommend-only mod notifier (Hermes = eyes, never hands).
# Watches #reports + the audit log; POSTs a triage card to #mod-ops pinging BOTH mod roles.
# Run as a no_agent cron (deliver=local). First run baselines silently (no history replay).
# Token read from the profile .env (never printed). Shell: POSIX (no mapfile / no pipe-subshell).
set -euo pipefail

PROFILE_ENV="$HOME/.hermes/profiles/gamehub-mod/.env"
STATE="$HOME/.hermes/profiles/gamehub-mod/scripts/.watchdog_state.json"
MOD_OPS="<MOD_OPS_CHANNEL_ID>"      # staff channel the card lands in
REPORTS="<REPORTS_CHANNEL_ID>"       # member drop-box (needs bot READ override, see dropbox ref)
ESPADA_ID="<ESPADA_ROLE_ID>"
HEADCAP_ID="<HEADCAP_ROLE_ID>"

# Ping targets (owner decision: BOTH). allowed_mentions parses roles so pings fire.
PING="<@&$ESPADA_ID> <@&$HEADCAP_ID>"

# --- load env (token + guild only) ---
if [[ -f "$PROFILE_ENV" ]]; then
  while IFS='=' read -r k v; do
    [[ -z "$k" || "$k" == \#* || -z "$v" ]] && continue
    k="${k#"${k%%[![:space:]]*}"}"; k="${k%\"${k##*[![:space:]]}\"}"
    v="${v#\"${v%%[![:space:]]*}\"}"; v="${v%\"${v##*[![:space:]]}\"}"
    v="${v#\"}"; v="${v%\"}"; v="${v#\'}"; v="${v%\'}"
    [[ "$k" == DISCORD_BOT_TOKEN || "$k" == DISCORD_GUILD_ID ]] && export "$k=$v"
  done < "$PROFILE_ENV"
fi
: "${DISCORD_BOT_TOKEN:?DISCORD_BOT_TOKEN missing from profile .env}"
: "${DISCORD_GUILD_ID:?DISCORD_GUILD_ID missing from profile .env}"

API="https://discord.com/api/v10"
AUTH="Authorization: Bot $DISCORD_BOT_TOKEN"
UA="gamehub-mod-watchdog/1.0"

post_card() {
  local content="$1"; local body; body=$(mktemp)
  python3 - <<PY > "$body"
import json
print(json.dumps({"content": r"""$content""", "allowed_mentions": {"parse": ["roles"]}}))
PY
  curl -s -m 25 -X POST -H "$AUTH" -H "Content-Type: application/json" -H "User-Agent: $UA" \
    --data "@$body" "$API/channels/$MOD_OPS/messages" >/dev/null
  rm -f "$body"
}

# --- fresh install: baseline silently, never replay history ---
if [[ ! -f "$STATE" ]]; then
  R_CUR=$(curl -s -m 25 -H "$AUTH" -H "User-Agent: $UA" "$API/channels/$REPORTS/messages?limit=1" \
    | python3 -c "import json,sys;d=json.load(sys.stdin);print(d[0]['id'] if d else 0)" 2>/dev/null || echo 0)
  A_CUR=$(curl -s -m 25 -H "$AUTH" -H "User-Agent: $UA" "$API/guilds/$DISCORD_GUILD_ID/audit-logs?limit=1" \
    | python3 -c "import json,sys;d=json.load(sys.stdin);e=d.get('audit_log_entries',[]);print(e[0]['id'] if e else 0)" 2>/dev/null || echo 0)
  python3 -c "import json;json.dump({'reports':$R_CUR,'audit':$A_CUR},open('$STATE','w'))"
  echo "baselined (reports=$R_CUR audit=$A_CUR); nothing replayed."; exit 0
fi
REPORTS_CURSOR=$(python3 -c "import json;print(json.load(open('$STATE')).get('reports',0))")
AUDIT_CURSOR=$(python3 -c "import json;print(json.load(open('$STATE')).get('audit',0))")

NEW_REPORTS=0
TMP=$(mktemp)
curl -s -m 25 -H "$AUTH" -H "User-Agent: $UA" "$API/channels/$REPORTS/messages?limit=20" | \
  python3 -c "
import json,sys
d=json.load(sys.stdin)
for m in d:
    mid=int(m['id'])
    if mid>int(sys.argv[1]):
        print(f'{mid}|{m[\"author\"].get(\"username\",\"?\")}|{m.get(\"content\",\"\")[:1500]}')
" "$REPORTS_CURSOR" > "$TMP"
while IFS='|' read -r MID AUTHOR BODY; do
  [ -z "$MID" ] && continue
  post_card "🚨 NEW REPORT in #reports — needs a look $PING
Reporter: $AUTHOR
$MID
$BODY"
  [ "$MID" -gt "$REPORTS_CURSOR" ] && REPORTS_CURSOR=$MID
  NEW_REPORTS=$((NEW_REPORTS+1))
done < "$TMP"
rm -f "$TMP"

AUDIT_HITS=0
TMP2=$(mktemp)
curl -s -m 25 -H "$AUTH" -H "User-Agent: $UA" "$API/guilds/$DISCORD_GUILD_ID/audit-logs?limit=50" | \
  python3 -c "
import json,sys,datetime,urllib.request
d=json.load(sys.stdin)
KEEP={21:'MEMBER BANNED',22:'MEMBER UNBANNED',24:'MEMBER KICKED',25:'MEMBER PRUNED',
      26:'MEMBER UNBANNED',27:'BAN ADDED',30:'BULK DELETE',31:'ROLE UPDATED ON MEMBER'}
ALERT={21,22,24,25,26,27,30,31}  # drop routine 12/13/14 (build noise)
def name(uid):
    if not uid: return '?'
    try:
        r=urllib.request.urlopen(urllib.request.Request(
          f'https://discord.com/api/v10/users/{uid}',
          headers={'Authorization':'Bot '+sys.argv[2],'User-Agent':'gh-watchdog'}),timeout=8)
        return json.load(r).get('username','?')
    except Exception: return uid
out=[]
for e in d.get('audit_log_entries',[]):
    eid=int(e['id'])
    if eid>int(sys.argv[1]) and e.get('action_type') in ALERT:
        at=e.get('action_type'); ts=datetime.datetime.utcfromtimestamp((eid>>22)/1000+1420070400000).strftime('%Y-%m-%d %H:%M UTC')
        out.append(f'{eid}|{KEEP.get(at,at)}|by {name(e.get(\"user_id\"))}|on {name(e.get(\"target_id\"))}|{ts}')
print(chr(10).join(out))
" "$AUDIT_CURSOR" "$DISCORD_BOT_TOKEN" > "$TMP2"
while IFS='|' read -r AID REST; do
  [ -z "$AID" ] && continue
  post_card "⚠️ AUDIT EVENT $PING
$AID | $REST"
  [ "$AID" -gt "$AUDIT_CURSOR" ] && AUDIT_CURSOR=$AID
  AUDIT_HITS=$((AUDIT_HITS+1))
done < "$TMP2"
rm -f "$TMP2"

python3 -c "import json;json.dump({'reports':$REPORTS_CURSOR,'audit':$AUDIT_CURSOR},open('$STATE','w'))"
if [ "$NEW_REPORTS" -gt 0 ] || [ "$AUDIT_HITS" -gt 0 ]; then
  echo "alerted: reports=$NEW_REPORTS audit=$AUDIT_HITS"
else
  echo "ok: nothing new"
fi
