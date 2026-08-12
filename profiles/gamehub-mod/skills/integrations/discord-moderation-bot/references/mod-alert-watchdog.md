# Mod-alert watchdog (recommend-only enforcement notifier)

Architecture: **Gamehub-mod is the analyst + notifier, never the enforcer.** The
enforcement hands belong to enforcement-bot (or a human mod). This watchdog watches `#reports`
+ the audit log and POSTs a triage card to `#mod-ops` pinging BOTH mod roles. It never
kicks or bans.

## Enforcement ladder (decided 2026-07-13 — RECOMMEND-ONLY)
- **Tier 0 (soft):** minor slip (off-topic, mild flame) → bot deletes + friendly note. No ping.
- **Tier 1 (Muted):** repeat/spam, clear single break → bot applies `Muted` (MAX self-action), logs to #mod-ops. Ping AFTER.
- **Tier 2 (recommend ban):** harassment, IP theft, raid pattern → bot writes triage card + evidence in #mod-ops, pings mods, waits for human.
- **Tier 3 (auto-ban carve-out):** unambiguous automation (mass-join + identical spam + captcha-bypassed) → enforcement-bot bans + dumps evidence to #mod-ops; Hermes pings mods. Hermes itself never bans.

**Ping targets (owner current decision):** BOTH mod-lead `<@mod-role>` and Head
Captain `<@mod-role>`. Use `allowed_mentions: {parse: ["roles"]}` so the
mention actually fires and the bot never pings `@everyone`. Owner changes targets if needed.

**Layer split:** enforcement-bot = hands (mute/kick/ban per rules you configure; can defer to
#mod-ops). Hermes = eyes (triage, log, ping). Keeps the charter intact — no bot-initiated
ban without human go-ahead.

## Watchdog pitfalls (learned the hard way)
1. **BASELINE FIRST.** On a fresh/empty state file, set the cursor to "now" (newest message
   ID) and `exit 0` silently. If the cursor starts at `0`, the first run replays the ENTIRE
   history — this bot dumped 15 stale audit events into #mod-ops on its first real run
   before the guard existed.
2. **POST Discord JSON via a temp file:** `--data @/tmp/body.json` built with a quoted
   Python heredoc. Do NOT build it inline with `--data "$(python3 -c "...")"` — the shell
   mangles the dict braces (`{`/`}`) and you get a `SyntaxError` + a broken empty POST.
3. **Use POSIX `while IFS='|' read -r ...; do ...; done < file`.** NOT `mapfile` (absent in
   some `/bin/sh` setups — `mapfile: command not found`), and NOT `... | while read` (the
   pipeline is a subshell, so cursor-variable updates don't persist → it re-alerts the same
   item forever). Redirect into a temp file, then read from the file.
4. **`#reports` blinds the bot** unless you add the explicit bot-role READ override (see
   `report-channel-dropbox.md` caveat). The watchdog otherwise fetches 0 reports.
5. **Filter audit to security-relevant action types only** (member ban/unban/kick/prune,
   role-update-on-member, bulk-delete). Routine channel/role CREATE (13/14/12) is build
   noise — drop it. Resolve user/target IDs to names + add a timestamp so cards are readable.

## Register as cron
`no_agent=true` + `deliver=local` + silent-when-idle (watchdog pattern; Discord stays clean
between events). Test: delete the state file (forces baseline, no post), post a real test
report to `#reports`, run once (should ping #mod-ops), then delete the test message + the
probe card from #mod-ops so the channel stays clean.

See `scripts/mod_alert_watchdog.sh` (fill in the GUILD / channel / role IDs; token read from
the profile `.env`, never printed).
