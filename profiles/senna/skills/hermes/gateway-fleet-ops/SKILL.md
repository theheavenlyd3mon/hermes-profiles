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

## Pre-Restart Config Validation

Before restarting gateways to pick up config changes, validate that all target
profiles parse cleanly. A malformed `config.yaml` causes the gateway to start
but silently ignore every user override. Catch this before restart to avoid
spinning up broken services.

```bash
# Validate all currently-running profiles' configs
for p in $(hermes gateway list 2>&1 | awk '/running/{print $2}' | sort -u); do
  ruby -e "require 'yaml'; YAML.load_file(\"~/.hermes/profiles/$p/config.yaml\")" 2>/dev/null || echo "BROKEN: $p"
done
```

Ruby ships on macOS and is reliable for this. If unavailable, use:

```bash
python3 -c "import yaml,sys; yaml.safe_load(open('~/.hermes/profiles/$p/config.yaml'))"
```

Note: pyyaml is not preinstalled on all systems. If any profile returns
"BROKEN", inspect `gateway.error.log` and `.corrupt.bak` before restarting.

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

## Recover from Fleet-Wide Error

When ALL gateways are down with the same error (e.g. new mandatory env var after `hermes update`), the individual recovery loop won't help — you need to fix the root cause first.

**Pattern**: Diagnose → Fix env → Restart all → Verify

```bash
# 1. Identify the shared error (tail, not grep — error.log accumulates)
tail -5 ~/.hermes/profiles/senna/logs/gateway.error.log

# 2. Fix the root cause across all profiles
#    Example: missing API_SERVER_KEY (June 2026 incident)
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
for p in ~/.hermes/profiles/*/; do
  grep -q '^API_SERVER_KEY=' "$p/.env" 2>/dev/null || echo "API_SERVER_KEY=$API_KEY" >> "$p/.env"
done

# 3. Restart the fleet
FLEET=$(for dir in ~/.hermes/profiles/*/; do
  profile=$(basename "$dir")
  [ -f "$dir/.env" ] && grep -q '^DISCORD_BOT_TOKEN=' "$dir/.env" 2>/dev/null && echo "$profile"
done)
for p in $FLEET; do
  hermes --profile "$p" gateway restart 2>&1
done

# 4. Verify (5s settle, check actual processes not launchctl exit codes)
sleep 5
ps aux | grep "hermes_cli.main.*gateway" | grep -v grep | wc -l
```

**Don't trust `launchctl list` exit codes alone** — after a crash-restart cycle, launchctl may show stale exit codes (exit=-15 or exit=1) even when the process is now running. Always verify with `ps aux` or check `gateway.log` for `Connected as`.

See `gateway-health-check` skill's `references/api-server-key-required.md` for the full API_SERVER_KEY incident.

## api_server Port Conflict Resolution

Multiple profiles with `platforms.api_server.enabled: true` and no explicit `port:` override will fight for the default `127.0.0.1:8643`. Only one can bind; the rest enter reconnect loops. Two remediation strategies exist.

**Strategy A — Single owner (lowest maintenance):** disable `api_server` on every profile except one owner. The bot-only profiles don't need loopback API access. Example: enable only on `security` or `senna`. After changes, restart each profile and verify with `tail gateway.log`.

**Strategy B — Multi-owner with unique ports:** give each profile its own port via an explicit `port:` override in `platforms.api_server` **and** ensure `platforms:` is not duplicated in the config file. Duplicate `platforms:` sections in the same file cause later sections to be ignored by config parsers, so the effective config may not change even though the file looks patched. Always verify the file has exactly one `platforms:` block before restarting.

Example unique-port block:
```yaml
platforms:
  api_server:
    enabled: true
    port: 8645            # outside the default 8643
    extra:
      host: 127.0.0.1
      port: 8645          # extra should match the api_server port
```

Anti-pattern caused by broad edits: a prior fix appended a second `platforms:` block at the end of a file, creating duplicates. The gateway honored the first block and ignored the later changed snippet. **Rule:** never append a duplicate `platforms:` block; modify the existing one in place.

## Profile Config Safety

- Do not do bulk appends to config.yaml. Use targeted read → patch → verify.
- When setting `enabled: false`, prefer changing the existing block over adding a new block elsewhere in the file.
- Before fleet restart, run `ruby -e "require 'yaml'; YAML.load_file('...')"` for every target profile, or at least for the one changed, to confirm parse success.
- **Never bulk-overwrite profile configs from a single source without diffing first.** Before syncing all profile `config.yaml` files from one canonical source, diff every profile against the source and preserve unique per-profile deltas, or explicitly ask the user before discarding them. Blind overwrites are config-destroy operations, not syncs. See `references/profile-config-sync.md`.

## Fleet Config Health Check

When reviewing fleet health, check these minimum requirements per Discord profile:

```bash
for p in <profile1> <profile2> ...; do
  echo "--- $p ---"
  echo "  model: $(grep -A3 '^model:' ~/.hermes/profiles/$p/config.yaml 2>/dev/null | grep 'default:' | head -1)"
  echo "  provider: $(grep 'provider:' ~/.hermes/profiles/$p/config.yaml 2>/dev/null | head -1)"
  echo "  api_server: $(grep -A3 'api_server' ~/.hermes/profiles/$p/config.yaml 2>/dev/null | grep 'enabled' | head -1)"
  echo "  DISCORD_TOKEN: $([ -f ~/.hermes/profiles/$p/.env ] && grep -q '^DISCORD_BOT_TOKEN=' ~/.hermes/profiles/$p/.env 2>/dev/null && echo '✓ present' || echo '✗ missing')"
  echo "  API_SERVER_KEY: $([ -f ~/.hermes/profiles/$p/.env ] && grep -q '^API_SERVER_KEY=' ~/.hermes/profiles/$p/.env 2>/dev/null && echo '✓ present' || echo '✗ MISSING')"
  echo "  .env: $([ -L ~/.hermes/profiles/$p/.env ] && echo 'SYMLINK' || echo 'OWN FILE')"
done
```

Also verify bot identities match expected profiles:
```bash
for p in senna creative security; do
  echo "$p: $(grep 'Connected as' ~/.hermes/profiles/$p/logs/gateway.log 2>/dev/null | tail -1 | awk -F'Connected as ' '{print $NF}')"
done
```

## Restart Fleet (ordered, running-only)

Use when the user says "restart the fleet", "restart gateways", or after config/profile changes that require gateway reload. Default: restart only currently running gateways. `full=true`: restart all profiles with Discord tokens regardless of state.

```bash
# 1. Discover running gateways
hermes gateway list

# 2. Optional: validate configs
ruby -e "require 'yaml'; YAML.load_file('$HOME/.hermes/profiles/<profile>/config.yaml')"

# 3. Restart each running gateway in order (one per terminal call, timeout=300)
hermes --profile <profile> gateway restart

# 4. Settle
sleep 3..6

# 5. Verify all are back online
hermes gateway list
```

Constraints:
- Do not restart the whole fleet if the user only asks for "running" ones unless explicitly directed.
- Do not use `gateway stop` + `gateway start` pairs when `gateway restart` is available.
- Do not leave a partially-restarted fleet without verification output.
- Do not modify `.env` tokens or SOUL.md here; that belongs in migration/setup skills.

Verification gate — output must include:
- per-profile restart result
- final `gateway list` table showing PID for every restarted profile
- explicit flag if any profile failed to come back online

## Pitfalls

- **Terminal foreground timeout vs the gateway drain window**: `hermes --profile <p> gateway restart` drains in-flight runs BEFORE killing the old process. The drain window is the profile's `gateway_timeout` (default 180s). The terminal tool foreground timeout defaults to 60s and caps at 600s. Running many restarts in one `for` loop with the default 60s timeout WILL time out partway through and abort the loop. (Happened: loop died on `gamehub-mod`'s drain, leaving infra/knowledge/research/security untouched.) **Fix:** restart one profile per terminal call with `timeout=300`, OR run each in background with `notify_on_complete=true`. Never batch more than ~2 restarts in a single foreground command.
- **Restart the CURRENT session's gateway LAST (or skip it)**: If operating inside a gateway-backed session (e.g. `senna`), restarting it mid-run drops your own live connection. Restart every *other* running profile first, then `senna` last — or leave it and let the user restart separately.
- **A gateway that "won't come back" is almost always AUTH, not restart mechanics**: `gateway restart` = stop (drain) + start. If the START phase can't authenticate, the process exits non-zero. Looping `restart` just reproduces the failure — diagnose first: read `tail -40 ~/.hermes/profiles/<p>/logs/gateway.log` and `.../logs/gateway-exit-diag.log`. "Connected as <bot>" = good; `asyncio.run.returned success=False` with NO "connected" line = start failed to auth. Check token mechanism: `grep access_token_env ~/.hermes/profiles/<p>/config.yaml`. Resolution: put `<VAR>=value` in `~/.hermes/profiles/<p>/.env` (Hermes loads `.env` at gateway start), export it in the launch shell, or create a LaunchAgent plist that sets it.
- **Restarting gateways from INSIDE a gateway-backed agent session is blocked on ALL paths**: Every agent-initiated gateway lifecycle command is refused by a Hermes safety guard — `gateway restart`, `launchctl kickstart -k`, and one-shot `no_agent` cron jobs all fail. The guard's directive is the fix: **run the restart from a shell that is NOT the agent's gateway session** — the user's normal Terminal.app on the host. Give the user the exact command; do not loop through agent paths.
- **`API_SERVER_KEY` is mandatory (June 2026+)**: After a hermes-agent update, the api_server platform requires `API_SERVER_KEY` in each profile's `.env`. Without it, the gateway crashes and restarts in a loop. Affects ALL profiles — even those without explicit api_server config inherit it from root `~/.hermes/config.yaml`. Fleet-wide symptom: all gateways down, all error logs show the same `API_SERVER_KEY is required` message. Fix: generate one random key, add to all profiles' `.env`, restart fleet. See `gateway-health-check` skill's `references/api-server-key-required.md`.
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
- **Corrupted config.yaml — gateway runs but ignores ALL user overrides silently.** A malformed YAML block (commonly in the `providers:` or `fallback_providers:` section after manual edits) causes the config parser to fail. The gateway starts but falls back to defaults, logging: `Failed to parse config.yaml: mapping values are not allowed here — Falling back to default config — every user override is being IGNORED`. A timestamped `.corrupt` backup is saved automatically (e.g. `config.yaml.corrupt.20260630-094625.bak`). **Symptoms:** gateway appears healthy (running, bot connected), but uses wrong model, wrong provider, or missing platform config. **Detection:** check `gateway.error.log` for the parse failure message. **Fix:** compare the `.corrupt.bak` with the current file, identify the indentation error (often `name: <string>` where `custom:name:` was intended in a providers block), and patch the YAML.
