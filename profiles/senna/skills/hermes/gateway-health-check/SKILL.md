---
name: gateway-health-check
description: Diagnose and verify Hermes gateway health across multiple profiles — launchd status, Discord/Telegram/API-server connectivity, profile resolution, error logs, and multi-bot fleet status. Use when the user asks "are my gateways working", "check the bots", "is Discord connected", or is troubleshooting any gateway connection issue.
---

# Gateway Health Check

Diagnose multi-profile Hermes gateway fleets: launchd status, profile resolution, platform connectivity, and errorlog analysis.

## Key Architecture Facts

- All gateways share ONE Python venv: `~/.hermes/hermes-agent/venv/bin/python` (profile-level hermes-agent dirs are symlinks to root)
- Each gateway is a separate launchd service: `ai.hermes.gateway-<profile>`
- Each uses `--profile <name>` which resolves config from `~/.hermes/profiles/<name>/`
- `HERMES_HOME` env var (set in each launchd service) controls profile config resolution
- **Profile configs are per-profile**: `~/.hermes/profiles/<name>/.env` (secrets) and `~/.hermes/profiles/<name>/config.yaml` (settings)
- Launchd plists live in `~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist`

## Step-by-Step Diagnostic

### 1. List All Gateway Services

```bash
launchctl list | grep hermes
```

Output: `PID  Exit  ServiceName`
- Exit `0` = healthy
- Exit `1` = crashed/errored (restart loop)
- Exit `-15` = killed via SIGTERM (stopped intentionally or failed to start)
- PID `-` = not running

### 2. Inspect Each Failing Gateway

For each service with bad exit codes:

```bash
# Full launchd info including env, paths, plist location
launchctl print gui/$(id -u)/ai.hermes.gateway-<name>

# Check process is actually running
ps aux | grep "gateway run.*<name>" | grep -v grep
```

Key fields to read:
- `program` → Python binary path
- `ProgramArguments` → `--profile <name>` flag
- `environment.HERMES_HOME` → where configs are read from
- `StandardOutPath` / `StandardErrorPath` → log file locations
- `LastExitStatus` → numeric exit code

### 3. Verify Profile Directories Exist

```bash
ls -la ~/.hermes/profiles/<name>/
```

Each profile needs:
- `.env` — API keys, bot tokens
- `config.yaml` — platform config (discord, telegram, api_server, etc.)
- `logs/` — must exist for gateway output

**Common failure**: Launchd service exists but profile directory is empty or missing. The gateway starts, finds no config, and either crashes or starts with no platforms connected.

### 4. Check Logs (Read REAL Files, Don't Tail)

Gateway logs are real files on disk — open them directly:

```bash
# These are the REAL paths (not what plist says — verify with lsof)
cat ~/.hermes/profiles/<name>/logs/gateway.log | tail -50
cat ~/.hermes/profiles/<name>/logs/gateway.error.log | tail -50
cat ~/.hermes/profiles/<name>/logs/errors.log | tail -30
```

**Important**: The log paths in launchd plists may not match where logs actually land. Use `lsof -p <PID>` to find the real file descriptors if logs appear empty.

### 5. Verify Platform Connectivity

Read the gateway.log for connection confirmations:

- **Discord**: Look for `gateway.platforms.discord: Connected to Discord` or `discord connected`
- **Telegram**: Look for `gateway.platforms.telegram: Connected to Telegram` or `telegram connected`
- **API Server**: Look for `api_server connected` and listening address

**Critical: Verify the BOT IDENTITY, not just connection.** The log will say `Connected as <Bot Name>#<tag>` — confirm this matches the expected bot for this profile. If Senna's gateway log says `Connected as Hermes Oracle#6348`, something is wrong.

```bash
grep "Connected as" ~/.hermes/profiles/<name>/logs/gateway.log | tail -5
```

Build a timeline of restarts to detect identity changes:
```bash
grep "Connected as\\|Starting Hermes Gateway\\|Exiting with code" \
  ~/.hermes/profiles/<name>/logs/gateway.log | tail -20
```

If a profile's bot identity changes between restarts, the shared `.env` was overwritten by another profile's setup.

If a platform is configured but NOT connected, the log will show:
- Missing token errors: `telegram is enabled but TELEGRAM_BOT_TOKEN is set to a placeholder`
- Auth failures, flood control, connection refused

**Quick channel directory check**: The gateway prints a log line showing how many Discord channels it can see. This confirms the bot has proper visibility:

```bash
grep "Channel directory built:" ~/.hermes/profiles/<name>/logs/gateway.log | tail -1
# Output: "Channel directory built: 12 target(s)"
# Low count (< 5) = bot may lack channel visibility permissions
```

### 6. Detect Cross-Profile Token Conflicts (.env Symlink Problem)

The most common multi-bot failure: **all profiles share the same Discord token** because their `.env` files are symlinked to `~/.hermes/.env` (the default).

```bash
# Check ALL profiles for .env symlinks vs own files
for p in ~/.hermes/profiles/*/; do
  name=$(basename "$p")
  envf="${p}.env"
  if [ -L "$envf" ]; then
    echo "$name: SYMLINK -> $(readlink "$envf")  ⚠️  SHARED"
  elif [ -f "$envf" ]; then
    echo "$name: OWN FILE  ✓"
  else
    echo "$name: NO .env  ✗"
  fi
done
```

**Each profile that needs its own bot MUST have its own `.env` file**, not a symlink to the shared one. Profiles sharing a `.env` all connect as the same bot — only one will succeed.

**To fix:** Create a standalone `.env` for the target profile with its unique bot token:

```bash
# Remove symlink
rm ~/.hermes/profiles/<name>/.env

# Create independent .env with just the essentials for this bot
cat > ~/.hermes/profiles/<name>/.env << 'EOF'
DISCORD_BOT_TOKEN=<unique-token-for-this-bot>
DISCORD_ALLOWED_USERS=<your-discord-user-id>
EOF

# Restart the gateway
launchctl kickstart gui/$(id -u)/ai.hermes.gateway-<name>
```

**Signs of a token conflict:**
- Gateway log says `Connected as Hermes <ProfileB>#1234` but this is `<ProfileA>`'s gateway
- A bot that was correctly connected as BotA yesterday is now appearing as BotB
- Discord reports `WebSocket closed with 4004` (authentication failed) — the token in the shared .env was overwritten
- Two gateways start successfully but only one bot appears online in Discord

**Quick identity timeline** — reconstruct when a profile started logging in as the wrong bot:

```bash
grep "Connected as" ~/.hermes/profiles/<name>/logs/gateway.log | tail -10
```

### 7. API Server Port Conflict Resolution

When multiple profiles expose API servers (for workspace/dashboard connectivity), port conflicts cause silent fallback — gateways bind to a different port than configured. The workspace may stop working after a restart order changes.

#### The Env Var Trap

The api_server is controlled by TWO independent mechanisms. Setting only the config is not enough:

1. **Config toggle** — `platforms.api_server.enabled: false` (or explicit port)
2. **Env var** — `API_SERVER_ENABLED=true` in the profile's `.env`

**If `API_SERVER_ENABLED=true` is set in .env, the api_server starts regardless of what config.yaml says.** The env var overrides the config.

```bash
# Check ALL profiles for the env var
for p in ~/.hermes/profiles/*/; do
  name=$(basename "$p")
  val=$(grep "API_SERVER_ENABLED" "$p.env" 2>/dev/null || echo "not set")
  echo "$name: $val"
done

# Remove from a profile (keeping only on coordinator)
sed -i '' '/^API_SERVER_ENABLED=/d' ~/.hermes/profiles/<name>/.env
```

**Diagnostic: find what port each gateway is actually on vs. what its config says**

```bash
# 1. List all running gateways and their actual listening ports
lsof -iTCP -sTCP:LISTEN -n -P 2>/dev/null | grep -E '864[0-9]|865[0-9]'

# 2. Match a PID to its profile
ps aux | grep 'gateway run' | grep -v grep | grep -oP '--profile \K\S+'

# 3. Check each profile's effective config for its api_server port
# Profile's own config:
grep -A3 'api_server' ~/.hermes/profiles/<name>/config.yaml 2>/dev/null
# Profile's home config (if it has one):
grep -A3 'api_server' ~/.hermes/profiles/<name>/home/.hermes/config.yaml 2>/dev/null
# Default config (fallback if none of the above):
grep -A3 'api_server' ~/.hermes/config.yaml 2>/dev/null
```

**Config inheritance chain** — The effective api_server config is resolved from (first match wins):
1. `~/.hermes/profiles/<name>/config.yaml` — profile's own explicit config
2. `~/.hermes/profiles/<name>/home/.hermes/config.yaml` — profile's HERMES_HOME config
3. `~/.hermes/config.yaml` — default/root config (all profiles inherit from this if they lack their own)

**Common scenario: config says 8642, process is on 8643**

This happens when two gateways both target port 8642. The first one to start binds successfully. The second starts on 8643 (the next available port). The gateway logs this silently — no error, just a different port.

**Resolution — assign explicit unique ports**

For each profile that needs an API server, set an explicit port. Don't rely on inheritance or auto-fallback.

Then update the workspace .env:
```
# ~/hermes-workspace/.env
HERMES_API_URL=http://127.0.0.1:8643   # points to the coordinator profile
HERMES_DASHBOARD_URL=http://127.0.0.1:9119
```

**One-liner to verify:**
```bash
for url in 8642 8643 8644 8645; do
  resp=$(curl -s --connect-timeout 1 "http://127.0.0.1:$url/health" 2>/dev/null)
  if [ "$resp" != "" ]; then echo ":$url responding"; fi
done
```

**Best practice:** Only coordinator and implementer profiles need api_server. Discord-only profiles communicate through the gateway's platform adapter — no HTTP port needed.

### 8. Detect Dual hermes-agent Source Trees

A common post-migration problem: the original `~/.hermes/hermes-agent/` checkout remains while a profile also has its own `~/.hermes/profiles/<name>/hermes-agent/`. Gateway processes may use EITHER venv depending on how they were launched, causing code version mismatches across profiles.

```bash
# Show which Python binary each running gateway uses
ps aux | grep 'gateway run' | grep -v grep | awk '{print $NF, $(NF-1), $(NF-2)}'

# Check if two separate checkouts exist
diff <(cd ~/.hermes/hermes-agent && git log --oneline -1) \
     <(cd ~/.hermes/profiles/senna/hermes-agent && git log --oneline -1) 2>&1
```

**Signs of mixed venv usage:**
- `senna` gateway uses `~/.hermes/hermes-agent/venv/bin/python`
- `coder` gateway uses `~/.hermes/profiles/senna/hermes-agent/venv/bin/python`
- Different git commits in each checkout

**Why it matters:** One profile may run newer code with different tool schemas, adapter behavior, or bug fixes. Subtle incompatibilities between versions cause hard-to-diagnose failures (e.g., Discord adapter changes, tool schema mismatches).

**Resolution:** Consolidate to one hermes-agent checkout. Root (`~/.hermes/hermes-agent/`) is the canonical install — the CLI depends on it. Profile-level copies should be **symlinks to root**, not separate checkouts. NEVER remove root. See `hermes-directory-cleanup` skill's `references/hermes-agent-is-cli-backbone.md`.

### 9. Analyze Gateway Exit Diagnostics

Senna's profile logs a structured JSON restart history at `logs/gateway-exit-diag.log`. Each line is a JSON object with `tag`, `pid`, `success`, and `ts` fields. Useful for detecting crash-loop patterns:

```bash
# Count restarts in the last N hours
grep 'gateway.start' ~/.hermes/profiles/<name>/logs/gateway-exit-diag.log | \
  python3 -c "import sys,json; starts=[json.loads(l) for l in sys.stdin]; print(f'{len(starts)} starts')"

# Show restart/failure timeline
grep -E 'gateway\.(start|exit_nonzero)' ~/.hermes/profiles/<name>/logs/gateway-exit-diag.log | \
  python3 -c "
import sys,json
for l in sys.stdin:
    d = json.loads(l)
    tag = d['tag'].split('.')[-1]
    print(f\"{d['ts']}  {tag:12s}  pid={d.get('pid','')}  ok={d.get('success','')}\")"
```

**Rapid restart pattern** (gateway.start every 2-5 minutes with exit_nonzero in between) indicates fighting gateways or persistent auth failures. If the pattern stops after a few hours, the competing process likely died and the surviving gateway stabilized.

### 10. Check for Common Errors

In `gateway.error.log`, look for:
- `Gateway runtime lock is already held` → duplicate gateway instances
- `No user allowlists configured` → all unauthorized users denied (not a crash, but means no one can talk to the bot)
- Model 404 errors → wrong model name in config
- `Flood control exceeded` → Telegram rate limiting on command registration
- `WebSocket closed with 4004` → Discord authentication failed — usually token contention between multiple gateway instances sharing the same bot token. See `references/gateway-crash-loop-diagnostic-2026-05-27.md` for a full case study.
- `RuntimeError: Provider 'X' is set in config.yaml but no API key was found` → Profile's `.env` is missing the API key for its configured provider. See `references/wrong-model-discord-error.md` for full case study. Fix: add key to profile `.env` or switch provider.
- Session summarization 401 → OpenAI key missing (non-fatal, just can't summarize old sessions)

## Path Resolution Gotcha

Profile configs may live in nested paths due to symlinks. Use Python to find real files:

```python
import os, glob
for f in glob.glob(os.path.expanduser("~/.hermes/profiles/*/config.yaml")):
    print(f, "->", os.path.realpath(f))
```

The `find` and `ls` commands may report paths that include repeated segments like `profiles/senna/home/.hermes/profiles/senna/home/.hermes` — this is normal for symlinked Hermes home directories. Use Python's `os.path.realpath()` or `glob.glob()` to resolve the actual location.

## Quick Health Summary Format

When reporting status, use this compact format that includes bot identity verification (the #tag from Discord connect):

```
PROFILE     PID     EXIT  BOT IDENTITY           PLATFORMS        NOTES
senna       42235   1     Oracle#6348    ⚠️       api,discord     Wrong bot — .env symlink conflict
researcher  27543   0     Researcher#7005 ✓      api,discord     OK
secretary   27708   -15   -                      -                Killed, no profile
architect   31922   0     -                       api              Discord not configured
```

**BOT IDENTITY column notes:**
- ✓ = logged in as the expected bot for this profile
- ⚠️ = wrong identity (likely shared .env problem)
- - = no Discord platform configured

## Fixing Common Problems

### Missing API Key (Provider Mismatch)

The most common "wrong model" error on Discord. The gateway log shows:

```
RuntimeError: Provider 'deepseek' is set in config.yaml but no API key was found.
Set the DEEPSEEK_API_KEY environment variable, or switch to a different provider with `hermes model`.
```

**Root cause**: The profile's `config.yaml` references a provider (e.g. `deepseek`, `openrouter`) but the profile's `.env` file doesn't have the corresponding API key. **Profiles do NOT inherit from root `~/.hermes/.env`** — each needs its own keys.

**Diagnostic:**
```bash
# 1. Check what provider the profile uses
grep -A3 "^model:" ~/.hermes/profiles/<name>/config.yaml

# 2. Check what keys exist in the profile's .env
grep "API_KEY" ~/.hermes/profiles/<name>/.env | sed 's/=.*/=***/'

# 3. Check if root .env has the key (doesn't help the profile, but confirms it exists)
grep "API_KEY" ~/.hermes/.env | sed 's/=.*/=***/'
```

**Fix options:**
1. Copy the key from root `.env` to the profile's `.env` (keep provider, just add key)
2. Switch the profile to a provider whose key IS in its `.env` (e.g. switch to xiaomi if XIAOMI_API_KEY exists)

After fixing, restart the gateway:
```bash
kill $(ps aux | grep "profile <name>.*gateway" | grep -v grep | awk '{print $2}')
```

### Missing Profile Directory
Create with `hermes setup` or copy from a working profile and edit `.env`/`config.yaml`.

### Gateway Crash Loop (exit=1)
Check `gateway.error.log` — usually a missing config file or wrong model name.

**If both logs are empty**: The gateway is crashing before it can write anything (Python import error, missing module, bad .env parse). Run it manually in foreground to see the real error:

```bash
# Stop the launchd agent first
launchctl bootout gui/$(id -u)/ai.hermes.gateway-<name> 2>/dev/null
sleep 1

# Run manually — stderr goes to your terminal
HERMES_HOME=~/.hermes/profiles/<name> \
  ~/.hermes/hermes-agent/venv/bin/python \
  -m hermes_cli.main --profile <name> gateway run --replace 2>&1 | head -50
```

If it runs fine manually but crashes under launchd, the issue is in the plist (wrong WorkingDirectory, missing env vars, bad paths). Compare with a working profile's plist.

Note: `exit=256` in launchd means the same as exit=1 (the process exited with code 1, which launchd stores as 256 = 1<<8).

### OnDemand Flag (Auto-Restart Behavior)

Launchd services have an `OnDemand` flag that controls restart behavior:

```bash
launchctl print gui/$(id -u)/ai.hermes.gateway-<profile> | grep OnDemand
```

- **OnDemand=true**: Launchd restarts the process automatically if it crashes. Standard for coordinator profiles.
- **OnDemand=false**: The service runs once. If it exits (even cleanly), it stays dead. Must be manually kickstarted.

**Check which profiles have which:**
```bash
for s in senna researcher secretary coder architect foreman oracle; do
  if [ -f ~/Library/LaunchAgents/ai.hermes.gateway-$s.plist ]; then
    on=$(grep -A1 'KeepAlive\|OnDemand' ~/Library/LaunchAgents/ai.hermes.gateway-$s.plist | head -2)
    echo "$s: $on"
  fi
done
```

### The `hermes config set` Duplicate Key Problem

When using `hermes config set` to modify a nested key that already exists in config.yaml, the tool **appends** a new section at the end of the file rather than modifying the existing key in place. This creates duplicate YAML keys.

Common scenario — setting `platforms.api_server.enabled: false` on a profile that has `platforms: {}`:

```yaml
# Result: TWO platforms sections!
  platforms: {}                     # Original (under tui: section, middle of file)
  ...
platforms:                          # Appended (root level, end of file)
  api_server:
    enabled: false
```

**Detection:**
```bash
grep -n "^platforms:" ~/.hermes/profiles/<name>/config.yaml | wc -l
# If > 1, you have duplicates
```

**Fix:** Use `patch` to merge the two sections, or remove the duplicate and edit the original in-place.

**Prevention:** Prefer direct `patch` (find-and-replace) for modifying existing config keys. Reserve `hermes config set` for keys you're certain don't exist yet.

### Discord/Telegram Not Connecting
1. Verify `.env` has the real bot token (not placeholder)
2. Verify `config.yaml` has the platform enabled under `platforms:`
3. Check gateway.log for connection errors

### Stale Launchd Services
Remove plists for profiles that no longer exist:
```bash
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<old>.plist
rm ~/Library/LaunchAgents/ai.hermes.gateway-<old>.plist
```

## Fleet Management (Start / Restart After Update)

### Key Commands

```bash
# List all profiles and gateway status
hermes gateway list

# Start/restart ONE profile's gateway (launchd service)
hermes --profile <name> gateway start
hermes --profile <name> gateway restart

# Install a profile's gateway as a launchd service (persists across reboots)
hermes --profile <name> gateway install

# --all flag: kills ALL stale gateway processes across all profiles, then starts current profile
hermes gateway start --all
```

**Important**: `hermes gateway start --all` only starts the *current profile's* gateway after killing stale processes. It does NOT start every profile's gateway. You need a loop for full fleet restart.

### Pre-Flight: Ensure All Profiles Are Installed

`hermes gateway list` shows "not running" whether a service is stopped OR never installed as a launchd agent. Before starting a fleet, verify plists exist:

```bash
# Check which profiles have launchd plists
for p in senna architect coder designer foreman oracle researcher secretary; do
  plist="$HOME/Library/LaunchAgents/ai.hermes.gateway-$p.plist"
  if [ -f "$plist" ]; then echo "$p: installed ✓"; else echo "$p: MISSING plist ✗"; fi
done
```

If any are missing, install them first — `gateway start` will fail silently or error without a plist:

```bash
hermes --profile <name> gateway install
```

### Post-Update Fleet Restart

After `hermes update`, all gateway processes should be restarted to pick up the new code:

```bash
# One-liner — restart every Discord gateway:
for p in senna architect coder designer foreman oracle researcher secretary; do
  echo "Restarting $p..."
  hermes --profile "$p" gateway restart
done
```

Add to ~/.zshrc as an alias for repeated use:

```bash
alias hermes-fleet='for p in senna architect coder designer foreman oracle researcher secretary; do
  echo "Restarting $p..."
  ~/.hermes/profiles/senna/home/.local/bin/hermes --profile "$p" gateway restart
done'
```

### Full Update + Restart Workflow

```
1. hermes update                    # update hermes-agent
2. hermes-fleet                     # restart all Discord gateways (or use loop above)
3. hermes gateway list              # verify all expected gateways are running
```

### Launchd Auto-Start Behavior

Each installed gateway is a launchd service (`ai.hermes.gateway-<profile>`). They auto-start on user login — no manual intervention needed after a reboot. Manual restart is only required after an update that changes hermes-agent code.

To install a new profile's gateway as a persistent service:
```bash
hermes --profile <name> gateway install
```
