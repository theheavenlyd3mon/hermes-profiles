# Audit-Log Watch Digest (Hermes `no_agent` cron → Discord)

## Why this pattern
The installed Hermes Discord tool has no scheduler and **no send action**. To make
the bot push periodic digests/alerts into a staff channel, combine:
- a `no_agent` cron job (the script's stdout is delivered verbatim, or — with
  `deliver=local` — the script POSTs to Discord itself and stays silent), and
- a bash script that reads the bot token from the profile `.env`, calls the Discord
  REST API with `curl`, and diffs a state file.

## Registration
```bash
hermes cron create \
  --name audit-watch \
  --no-agent \
  --deliver local \
  --schedule "0 */6 * * *" \
  --script audit_watch.sh
```
- `deliver=local` → the agent never sees output; the script POSTs to Discord directly.
- `no_agent=true` → no LLM; the script IS the job (watchdog pattern). Silent when
  nothing is new, so Discord stays clean between events.

## Behavior contract (from the working build)
- Pull recent audit-log entries (`GET /guilds/{id}/audit-logs?limit=100`).
- **First run**: write baseline `last_id`, post nothing (avoids a 100-event spam burst).
- **Subsequent runs**: diff against `last_id`; **silent if nothing new**.
- New entries → concise summary POSTed to the digest channel (e.g. `#audit-review`).
- Anomalies (role/permission changes, mass deletes, bans, unexpected bot actions)
  → second POST to the alert channel, **mentioning the senior-mod / owner role,
  NOT the mod-lead/mod role** (user preference: owner wants anomaly pings, not the
  mod team).
- Persist a state file (e.g. `~/.hermes/profiles/<profile>/scripts/audit_state.json`).

## Token handling (IMPORTANT)
Read the token at runtime from the profile `.env`:
```bash
token="$(grep -E '^DISCORD_BOT_TOKEN=' "$PROFILE_DIR/.env" | head -1 | cut -d= -f2-)"
```
Never hardcode or commit the token. The `.env` is locked to direct reads, but the
terminal/heredoc can reach it.

## POSTing
```bash
curl -s -H "Authorization: Bot $token" -H "Content-Type: application/json" \
  --json @body.json "https://discord.com/api/v10/channels/<channel_id>/messages"
```
(body.json: `{"content":"..."}`). Use `urllib`? **NO** — Discord's Cloudflare WAF
403s Python's TLS stack (Error 1010). Use `curl`.

## Testing (do this before trusting it)
1. Force a baseline reset: `echo '{"last_id":"0"}' > audit_state.json`, then run the
   script → expect a digest POST (verifies the post path end-to-end).
2. Delete the test message afterward (the bot has `MANAGE_MESSAGES`) so staff
   channels stay clean.
3. Reset the baseline to the real latest `last_id` so production runs stay silent.

## Template
`scripts/audit_watch.sh` — fill in `GUILD` / channel / role IDs + the alert mention.
