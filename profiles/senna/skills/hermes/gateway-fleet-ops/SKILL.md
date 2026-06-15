---
name: gateway-fleet-ops
description: Start, verify, and recover the Discord gateway fleet. Operational runbook — not diagnostic. Use when user says "start the gateways", "restart the bots", "gateways are down", or after hermes update.
tags: [gateway, discord, fleet, launchd, recovery, operations]
metadata:
  hermes:
    related_skills: [gateway-health-check, hermes-agent]
---

# Gateway Fleet Ops

Operational runbook for the Discord gateway fleet. Diagnostic deep-dives → `gateway-health-check`.

```
IDENTITY: Operational.Runbook. FleetStart|FleetVerify|FleetRecover.
START_LOOP: DiscoverFleet→InstallMissing→StartAll→Wait3s→Verify→FixOrReport
RECOVER: CheckList→DiagnoseDown→InstallMissing→RestartDown→Verify
VERIFY_GATE: AllExpectedRunning→Report|AnyDown→Diagnose→Retry→Escalate
```

## Fleet Composition — Dynamic Discovery

**DO NOT hardcode the fleet list.** The team changes — SOUL.md is the source
of truth, and which profiles have Discord tokens determines which gateways
can run. Always discover at runtime.

```bash
# Discover which profiles have Discord bot tokens
for dir in ~/.hermes/profiles/*/; do
  profile=$(basename "$dir")
  if [ -f "$dir/.env" ] && grep -q '^DISCORD_BOT_TOKEN=' "$dir/.env" 2>/dev/null; then
    echo "$profile"
  fi
done
```

To check which are actually running:
```bash
hermes gateway list
```

The gap between "has token" and "is running" is what needs attention.

## Start All

```bash
# 1. Discover profiles with Discord tokens
FLEET=$(for dir in ~/.hermes/profiles/*/; do
  profile=$(basename "$dir")
  [ -f "$dir/.env" ] && grep -q '^DISCORD_BOT_TOKEN=' "$dir/.env" 2>/dev/null && echo "$profile"
done)

# 2. Install any missing launchd plists
for p in $FLEET; do
  plist="$HOME/Library/LaunchAgents/ai.hermes.gateway-$p.plist"
  [ -f "$plist" ] || hermes --profile "$p" gateway install 2>&1
done

# 3. Start every profile
for p in $FLEET; do
  hermes --profile "$p" gateway start 2>&1
done

# 4. Verify after 3s settle
sleep 3 && hermes gateway list
```

## Verify

`hermes gateway list` — all profiles with Discord tokens should show PID, not "not running".

If any are down, check:
1. Plist exists? `ls ~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist`
2. Logs? `tail -20 ~/.hermes/profiles/<name>/logs/gateway.error.log`
3. Token? `grep DISCORD_BOT_TOKEN ~/.hermes/profiles/<name>/.env | head -1`

## Recover Down Gateways

```bash
# Discover fleet, then recover any that are down
FLEET=$(for dir in ~/.hermes/profiles/*/; do
  profile=$(basename "$dir")
  [ -f "$dir/.env" ] && grep -q '^DISCORD_BOT_TOKEN=' "$dir/.env" 2>/dev/null && echo "$profile"
done)

for p in $FLEET; do
  status=$(hermes gateway list 2>&1 | grep "^  .*$p")
  echo "$status" | grep -q "not running" && {
    echo "Recovering $p..."
    hermes --profile "$p" gateway install 2>&1
    hermes --profile "$p" gateway start 2>&1
  }
done
sleep 3 && hermes gateway list
```

## Post-Update Restart

After `hermes update`, restart all to pick up new code:

```bash
FLEET=$(for dir in ~/.hermes/profiles/*/; do
  profile=$(basename "$dir")
  [ -f "$dir/.env" ] && grep -q '^DISCORD_BOT_TOKEN=*** "$dir/.env" 2>/dev/null && echo "$profile"
done)

for p in $FLEET; do
  hermes --profile "$p" gateway restart 2>&1
done
sleep 3 && hermes gateway list
```

## Resource Management

When the user asks "what's running" or their Mac is hot/slow, check the
fleet's resource footprint:

```bash
ps -eo pid,pcpu,pmem,rss,etime,args | grep "hermes_cli.main.*gateway" | grep -v grep | sort -k2 -rn
```

Columns: PID, %CPU, %MEM, RSS (KB), elapsed time, full command.

**Identify unused gateways.** The user may not need all 8 running. Check
which Discord bots are actually receiving messages before assuming a pattern.
Kill-and-ask is fine — the user knows which they use.

**Kill selectively:**

```bash
# Kill one gateway by profile name
pkill -f "hermes_cli.main --profile foreman gateway"

# Kill multiple
for p in foreman designer architect; do
  pkill -f "hermes_cli.main --profile $p gateway"
done
```

**Kill all non-senna gateways** (nuclear option):

```bash
ps -eo pid,args | grep "hermes_cli.main.*gateway" | grep -v senna | grep -v grep | awk '{print $1}' | xargs kill 2>/dev/null
```

**Stop permanently (don't just kill — launchd will respawn):**

The correct sequence is `stop` first, then `uninstall`. Reverse order fails
because the process is still supervised while the plist exists, and
`launchctl unload` errors on newer macOS (returns "Input/output error").

```bash
# Step 1: Stop the running process
hermes --profile <name> gateway stop

# Step 2: Remove the launchd plist so it won't respawn
hermes --profile <name> gateway uninstall
```

Do NOT use `launchctl unload` or `rm` on the plist directly — those fail
silently or error on macOS 15+. The `hermes gateway` subcommands handle
both the launchd bootout and plist removal correctly.

To restart later: `hermes --profile <name> gateway install && hermes --profile <name> gateway start`

**Memory footprint** of idle gateways: ~40-60MB RSS each. Eight gateways
= ~400MB. Not huge, but on a 16GB machine with swap pressure, every bit
counts. Senna's gateway is the heaviest (~450MB) because it handles the
main session plus LSP servers (bash-language-server, yaml-language-server).

## Pitfalls

- `hermes gateway start --all` only starts the CURRENT profile after killing stale processes. Does NOT start every profile. Use the discovery loop.
- `gateway start` without a plist will error silently. Always install first if plist missing.
- Each profile needs its own `.env` with its own `DISCORD_BOT_TOKEN`. Symlinked `.env` = all bots connect as same identity = only one wins.
- **`.env` may show `REPLACE_ME` placeholder tokens**: After profile migration, the `.env` files may contain `DISCORD_BOT_TOKEN=REPLACE_ME` (10 chars) instead of real tokens (70+ chars). The gateways still work because they load tokens through an internal mechanism (launchd environment or keychain), not by reading `.env` directly. The fleet discovery script (`grep -q '^DISCORD_BOT_TOKEN='`) still matches `REPLACE_ME` lines, so discovery works. But direct token extraction for API calls (curl, Python urllib) will fail with 401. **Don't trust `.env` token values for API calls** — use the gateway's own connection status or the `discord_admin` platform tool instead.
- After recovery, verify bot identity in logs: `grep "Connected as" ~/.hermes/profiles/<name>/logs/gateway.log | tail -1`
- `exit=256` in launchd = exit code 1 (crash). Check `gateway.error.log`.
- **Profile CLI wrapper breakage after update**: The wrapper at `profiles/<name>/home/.local/bin/hermes` hardcodes the venv path. If `hermes update` rebuilds or moves the venv, the wrapper breaks silently — `hermes` commands return "No such file or directory" (exit 126). Fix: rewrite the wrapper to point to `~/.hermes/hermes-agent/venv/bin/hermes`. See `hermes-maintenance` skill for the full repair procedure.
- Deep diagnostics (crash loops, port conflicts, token collisions, dual source trees) → load `gateway-health-check` skill.
- **SOUL.md is the source of truth for team composition, not this skill.** The team changes — profiles get added, renamed, or retired. Never hardcode a profile list from this skill into commands. Always discover from SOUL.md + token presence. If the user says "we changed the team", check SOUL.md first.
- **Old→new profile renames (as of June 2026):** architect→security, foreman→infra, oracle→finance, designer→creative, coder→code, researcher→research. Some old names may still have tokens/launchd plists — clean them up if the user confirms. **Token reuse caveat:** when a new profile reuses an old profile's bot token, the bot retains the old display name and all old channel memberships. Gateway restart doesn't fix this — the identity lives on Discord's side. Verify with `curl -s https://discord.com/api/v10/users/@me -H 'Authorization: Bot <token>'` after any token swap. If the username doesn't match the new profile, the user needs to rename the bot in Discord Developer Portal or create a fresh token.
- **Reused bot tokens keep old channel access.** When a profile is renamed and reuses the old bot token (e.g., architect's token → security profile), the bot retains Discord channel memberships from before the rename. It will appear active in BOTH old channels (e.g., #architecture) and new channels (e.g., #security-ops). After profile renames, explicitly remove the bot from old channels or archive those channels. Don't assume the bot only shows up where you expect — check `send_message(action='list')` to see the full channel list. This is a Phase 8 (Update Discord) step in migrations, not a gateway config issue. **The user must do channel cleanup manually** — there is no `hermes discord` CLI command, and `discord_admin` is only available inside gateway sessions.
- **Not all profiles need Discord gateways.** Some are CLI-only workers (ue5, mlops, homelab, etc.). Only profiles with `DISCORD_BOT_TOKEN` in their `.env` can run gateways. Ask the user which should be online — don't assume all 20+ need to be running.
- **Stopping gateways permanently requires TWO commands in order:** `stop` then `uninstall`. Running only `uninstall` removes the plist but the process keeps running (until killed). Running only `stop` kills the process but launchd respawns it from the still-loaded plist. On macOS 15+, `launchctl unload` and `launchctl bootout` return I/O errors — always use the `hermes gateway` subcommands instead.
- **Cron delivery uses default profile's Discord client, not the job's profile.** When a cron job has `profile: oracle` and `deliver: discord:<channel_id>`, the message appears from Senna's bot, not Oracle's. Fix: set `deliver: local` + add DELIVERY OVERRIDE in the prompt to use `send_message` explicitly. See `cron-pipeline` skill for full pattern and override template.
