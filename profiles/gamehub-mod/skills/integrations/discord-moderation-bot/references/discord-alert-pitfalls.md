# Discord alert watchdog — pitfalls (from building mod_alert_watchdog.sh)

Condensed failure log from building the near-real-time `#reports` + audit-log alert
cron for The Agentic GameHub. Each item caused a real break; the script bakes in the
fix. Mirror of the pitfall list in SKILL.md, with the exact wrong/right forms.

## 1. Snowflake → timestamp (CRITICAL)
Discord snowflake = `(unix_ms - 1420070400000) << 22 | worker | process | increment`.
To recover a timestamp:
    ts_ms = ((snowflake_id >> 22) + 1420070400000)   # milliseconds
    datetime.fromtimestamp(ts_ms / 1000, tz=utc)
WRONG (yields year 46981 → ValueError → crashes the audit loop on a real ban):
    (snowflake_id >> 22) / 1000 + 1420070400000
The `/1000` must apply to the WHOLE sum, not just the shifted bits.

## 2. Baseline guard (CRITICAL)
On first run with no state file: baseline BOTH cursors to the newest existing
message/audit id, write the state file, and `exit 0` silently. If you instead start
cursors at 0, the next run replays ALL history (we dumped 15 audit events to #mod-ops
on install). Same "100-event burst" failure the digest watchdog warns about.

## 3. #reports read-back blindness
A confidential drop-box (members POST, @everyone DENY READ_MESSAGE_HISTORY) also blocks
the bot from reading it — the @everyone deny overrides the base read grant even for the
bot role. Fix: add a per-channel ALLOW overwrite for VIEW_CHANNEL(10) +
READ_MESSAGE_HISTORY(16) on the bot role. Members still can't read history; bot regains
read-back. VERIFIED: posting a test report → running the watchdog → ping landed in
#mod-ops with both roles mentioned.

## 4. Shell portability
The profile shell resolved to `sh`, not bash, despite `#!/usr/bin/env bash`. `mapfile`
and `for x in "${arr[@]}"` are unavailable → "command not found". Pipe command output
to a temp file and consume with `while IFS= read -r line; do ... done < file`.

## 5. JSON body in post_card
Inline `python3 -c "print(json.dumps(...))"` mangles nested braces (shell expansion).
Write the body with a heredoc to a temp file, then `curl --data @file`. Keep
`allowed_mentions: {parse: ["roles"]}` so role pings actually fire.

## 6. Audit event filter
Alert-worthy types (ban/kick/unban/prune/role-update/bulk-delete): 21, 22, 24, 25, 26,
27, 30, 31. DROP 13/14 (channel create/edit) — pure build noise during setup. Resolve
user_id and target_id to usernames via `GET /users/{id}` so cards read "by Alice on
Bob", not raw IDs.

## 7. Cleanup during testing
Deleting many messages in a tight loop hits Discord rate limits ("You are being rate
limited"). Sleep ~1s between deletes. Post a test report, run the watchdog, confirm the
ping, then delete the test report + the probe card (delete BY ID — does not need read
perms, unlike fetch).
