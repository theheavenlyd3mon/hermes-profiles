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

### Multi-Bot Presence in a Shared Chat vs Home-ChannelScoping

A common user-facing confusion: “only one bot responds in this chat.” The fleet may be fully healthy; the other bots may simply be scoped to their own home channels.

Avoid declaring bots down solely from one chat’s silence. Use this presence check across the fleet:

```bash
# 1. Verify each profile is connected with the expected bot identity
for p in ~/.hermes/profiles/*/; do
  name=$(basename "$p")
  last=$(grep "Connected as" "$p/logs/gateway.log" | tail -1 || true)
  chans=$(grep "Channel directory built:" "$p/logs/gateway.log" | tail -1 || true)
  echo "$name: ${last:-no-discord} | ${chans:-no-channel-dir}"
done
```

Cross-check identity and channel count, not just “running.” A profile can be perfectly connected but still not appear in your current thread.

**Compact status table** (useful for user-facing fleet reports):

```
PROFILE     BOT IDENTITY           CHANNELS   LAST SEEN HERE       NOTES
senna       Senna#9675             17         now                  active
code        Hermes Coder#3827      9          occasionally         responds sometimes
creative    Hermes Graphics#8064   9          now                  active in chat
finance     Finance#6348           9          not observed         home-channel scoped
infra       Infra#8657             9          not observed         home-channel scoped
knowledge   Hermes Secretary#9128 10          not observed         home-channel scoped
security    Hermes Architect#6170  9          not observed         home-channel scoped
research    Hermes Researcher#7005 11          not observed         stale allowlist issue possible
```

**Pitfall — silent home—channel scoping**: Profiles with valid Discord connections still only auto**Pitfall —participate in their configured home channel. If you need broad presence here, patch each profile's Discord channel directory/config, not the gateway lifecycle.

**Pitfall — bot in wrong guild entirely**: If the bot is absent from the server's member list (not just silent in one channel), `DISCORD_GUILD_ID` in `.env` points to a different server. The gateway logs look perfectly healthy — `Connected as <Bot>` succeeds. Diagnose by comparing guild IDs against a known-working bot. Full walkthrough: `references/wrong-guild-diagnosis.md`.

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

**Compare tokens across profiles without printing them** — the first 12 chars of the token identify the bot:
```bash
for p in <profileA> <profileB>; do
  echo "$p: $(grep '^DISCORD_BOT_TOKEN=' ~/.hermes/profiles/$p/.env | cut -d= -f2 | cut -c1-12)"
done
```

**Rename a bot without the Developer Portal** — the bot username is PATCHable with its own token (e.g. after a token swap leaves a profile logged in under a misleading app name):
```bash
TOKEN=*** '^DISCORD_BOT_TOKEN=*** ~/.hermes/profiles/<name>/.env | cut -d= -f2)
curl -X PATCH https://discord.com/api/v10/users/@me \
  -H "Authorization: Bot $TOKEN" -H "Content-Type: application/json" \
  -d '{"username": "New Bot Name"}'
```
This renames the bot for EVERY profile sharing that token — check for sharing first with the prefix comparison above.

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

**Important: `gateway.error.log` accumulates across restarts.** Old errors remain at the top; new errors appear at the bottom. Always `tail` the file — don't grep for a pattern and assume it's current. A gateway may have recovered from an old error but hit a new one.

```bash
# Show only the LAST error block (most recent restart)
tail -20 ~/.hermes/profiles/<name>/logs/gateway.error.log
```

In `gateway.error.log`, look for:
- `API_SERVER_KEY is required for the API server` → **Fleet-wide crash (June 2026+)**. A hermes-agent update made `API_SERVER_KEY` mandatory for the api_server platform. All profiles with api_server enabled (explicitly or inherited from root config) will crash without it. See `references/api-server-key-required.md` for the full incident. Fix: generate a key, add to all profiles' `.env`:
  ```bash
  API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
  for p in ~/.hermes/profiles/*/; do
    grep -q '^API_SERVER_KEY=' "$p/.env" 2>/dev/null || echo "API_SERVER_KEY=$API_KEY" >> "$p/.env"
  done
  ```
- `Gateway runtime lock is already held` → duplicate gateway instances
- `No user allowlists configured` → **all messages silently denied.** The bot appears online in the member list, the user types, nothing happens. Log shows `Discord messages are being denied because no allowlist is configured` and `Unauthorized slash attempt: ... reason='user not in DISCORD_ALLOWED_USERS'`. This is NOT a connection problem — the gateway is healthy. Fix: add `DISCORD_ALLOWED_USERS=<discord_user_id>` to the profile's `.env`, then restart. Full diagnostic: `references/allowlist-silent-denial.md`.
- Model 404 errors → wrong model name in config
- `Flood control exceeded` → Telegram rate limiting on command registration
- `WebSocket closed with 4004` → Discord authentication failed — usually token contention between multiple gateway instances sharing the same bot token. See `references/gateway-crash-loop-diagnostic-2026-05-27.md` for a full case study.
- `RuntimeError: Provider 'X' is set in config.yaml but no API key was found` → Profile's `.env` is missing the API key for its configured provider. See `references/wrong-model-discord-error.md` for full case study. Fix: add key to profile `.env` or switch provider.
- Session summarization 401 → OpenAI key missing (non-fatal, just can't summarize old sessions)
- MCP server `Connection closed` / `parked` on every gateway start **after a `hermes update`** → the update swapped the venv and pip-installed MCP server binaries were left behind in the old one. Confirm: `ls ~/.hermes/hermes-agent/venv/bin/ | grep <server>` finds nothing, but a `~/.hermes/hermes-agent/venv.stale.*/bin/<server>` still exists. Get the PyPI package name from the stale venv's `site-packages/*/METADATA`, then `~/.hermes/hermes-agent/venv/bin/pip install <package>`. MCP keepalive `degraded → connected` cycles without full failure are cosmetic — only act if the server's tools actually error.

## Path Resolution Gotcha

Profile configs may live in nested paths due to symlinks. Use Python to find real files:

```python
import os, glob
for f in glob.glob(os.path.expanduser("~/.hermes/profiles/*/config.yaml")):
    print(f, "->", os.path.realpath(f))
```

The `find` and `ls` commands may report paths that include repeated segments like `profiles/senna/home/.hermes/profiles/senna/home/.hermes` — this is normal for symlinked Hermes home directories. Use Python's `os.path.realpath()` or `glob.glob()` to resolve the actual location.

**Don't trust launchctl exit codes alone.** After a crash-restart cycle, launchctl may show stale exit codes (exit=-15 or exit=1) even when the process recovered and is now running. Always cross-check with:
```bash
ps aux | grep "hermes_cli.main.*gateway" | grep -v grep
```
Or check `gateway.log` for the latest `Connected as` line. The launchctl exit code reflects the last time launchd noticed a state change — if the gateway stabilized after the initial failures, the exit code may never update.

### Model Inventory Per Profile

When reporting fleet status, include each profile's configured model and provider:

```bash
for p in ~/.hermes/profiles/*/; do
  name=$(basename "$p")
  cfg="${p}config.yaml"
  if [ -f "$cfg" ]; then
    model=$(grep -A2 "^model:" "$cfg" | grep "default:" | awk '{print $2}')
    provider=$(grep -A2 "^model:" "$cfg" | grep "provider:" | awk '{print $2}')
    echo "$name: ${model:-unset} (${provider:-unset})"
  fi
done
```

Include this in the Quick Health Summary table as a MODEL column.

### Quick Health Summary Format

When reporting status, use this compact format that includes bot identity verification (the #tag from Discord connect):

```
PROFILE     PID     EXIT  BOT IDENTITY           MODEL                          PLATFORMS        NOTES
senna       42235   1     Oracle#6348    ⚠️       tencent/hy3:free (nous)        api,discord     Wrong bot — .env symlink conflict
researcher  27543   0     Researcher#7005 ✓      tencent/hy3:free (nous)        api,discord     OK
code        88782   0     Coder#3827 ✓           stepfun/step-3.7-flash (nous)  api,discord     OK
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
4. **401 Unauthorized / "Improper token has been passed"** — the token in `.env` is revoked or reset. The gateway retries endlessly (60s → 120s → 240s backoff) but never connects. Fix: user resets token in Discord Developer Portal → paste into `.env` → **restart the gateway** (it caches the token in memory at startup). See the restart-targeting pitfall below.

### Stale Launchd Services
Remove plists for profiles that no longer exist:
```bash
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<old>.plist
rm ~/Library/LaunchAgents/ai.hermes.gateway-<old>.plist
```

## Crash-on-Conversation: connected but dies on first reply

A fleet can be **fully running and logged into Discord** yet crash the instant a real
message arrives. User-facing symptom: bot is present in the channel (may send a
session-reset notice), then replies `unexpected error` / `try /reset`. This is NOT a
connection/token problem and NOT "bots are down" — it is **stale in-memory code** from a
`hermes-agent` update that was never followed by a fleet restart.

Mechanism: the update added new symbols (e.g. `reset_conversation_context`,
`TELEGRAM_RICH_MESSAGES_HINT`) to source. Running gateways still import the pre-update
bytecode. Login code is unchanged (so they connect), but `run_conversation` does
`from agent.portal_tags import reset_conversation_context` → `ImportError` → the reply
dies. The symbols exist on disk in the new code; only the *running process* has the stale
copy. Single `hermes_cli/main.py` on disk — this is NOT the dual-tree failure (step 8).

**Distinguish from "down":** `ps` shows live gateway PIDs AND `gateway.log` shows a recent
`Connected as <Bot>#<tag>` → not an auth/token issue. The crash shows in `gateway.error.log`
as an `ImportError` / `cannot import name` nested inside `run_conversation` / `run_sync`.

Full signatures, reproduction recipe, and confirmation one-liner:
`references/crash-on-conversation-import-errors.md`.

**Fix:** `find ~/.hermes/hermes-agent -name __pycache__ -type d -exec rm -rf {} +`, then
restart the fleet (every Discord profile) so each gateway re-imports current code. This is
the same trigger class as the `API_SERVER_KEY` incident — **a `hermes update` without a
fleet restart leaves gateways serving stale code.** Full one-pass diagnostic
(import crashes + API_SERVER_KEY + MCP warnings): `bash scripts/gateway-crash-scan.sh`.

## Diagnostic Pitfalls (easy to misread)

**`hermes gateway restart` may silently restart the WRONG profile — always verify the target PID changed (2026-07-20).** When restarting a *specific other* profile's gateway, both `hermes --profile <p> gateway restart` and `HERMES_PROFILE=<p> hermes gateway restart` were observed to restart a *different* profile (the current/default one) while the intended target's PID never budged. In this session two restarts bumped senna's PID; novel stayed at PID 18712 the whole time, still holding the stale in-memory token, still 401ing. **The reliable way to restart one specific profile is launchctl by exact service name:**
```bash
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway-<name>
```
**Always verify the restart hit the right target:** capture PID before (`launchctl list | grep <name>`), restart, then confirm the PID changed AND `tail gateway.log` shows a fresh `Connected as <Bot>`. If the PID is unchanged, the command targeted the wrong service — use the launchctl form above. This also applies after a token swap: the gateway caches the token at startup, so an unchanged PID means the new token was never loaded.

**Restart guard activates mid-session in TUI after ~4 restarts (2026-07-20).** The
`gateway-fleet-restart` skill documents the guard for gateway-backed sessions only
(pitfall #4). In practice, the guard also activates in TUI sessions after a threshold
of ~4 successful `hermes --profile <p> gateway restart` calls in one session. Both
`hermes --profile <p> gateway restart` AND `launchctl kickstart -k` are blocked once
it triggers. Strategy: restart as many profiles as possible in the first batch (they
succeed before the guard arms), then hand the remaining profiles to the user's host
shell with the `launchctl kickstart -k` loop. Do NOT retry blocked calls — they
re-block identically.

**`ps` false-negative on `--replace`.** The running command is
`... -m hermes_cli.main gateway run --replace` — it does NOT contain the literal string
`hermes_cli.main.*gateway` in a form grep reliably matches with `awk` field splitting, and
a too-specific grep (`gateway run.*<name>`) can return zero even when the process is alive.
Two reliable checks: (1) `pgrep -f "gateway run --replace"` for live PIDs; (2) read
`gateway-exit-diag.log` for the most recent `gateway.start` pid. If `ps` says zero but
launchctl shows a PID, the process is alive — trust the PID.

**Error-log noise + tail discipline.** `gateway.error.log` is append-only across months of
restart cycles (Senna's was 51k lines / 6.4 MB). `grep` for a pattern and you'll surface a
decades-old error. Two rules: (1) always `tail` the file to read the *most recent* state;
(2) the user's own blocked tool calls and benign WARNINGs (MCP retries, liveness probes)
pile onto the tail — read the tail for the gateway's own errors, not the agent's chatter.
The single most informative line is usually an `ImportError` or `cannot import name`.

**Archiving a profile does NOT stop its gateway — zombie processes survive (2026-07-27).** Moving `~/.hermes/profiles/<name>/` to an archive dir leaves the launchd service and the running process alive. The zombie keeps old code in memory, and launchd recreates an empty `state/` dir so the profile looks half-alive. When archiving a profile, also:
```bash
launchctl bootout gui/$(id -u)/ai.hermes.gateway-<name>
rm ~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist
```
**Verify the kill with `ps`, not `launchctl list`** — launchctl's table can be stale right after bootout. `ps -p <pid> -o pid,args | grep "gateway run"` returning nothing is the source of truth.

**Verify a fleet restart by process start time, not by "Connected as" alone.** After a restart loop, audit actual start times — profiles the loop silently missed (wrong-target bug above) stand out immediately:
```bash
ps aux | grep 'gateway run --replace' | grep -v grep | awk '{print $2, $9, $NF}' | sort
```
Any gateway whose start time predates the restart window is still on old code.

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
# 0. Clear stale bytecode FIRST (prevents ImportError crashes after restart)
find ~/.hermes/hermes-agent -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null

# 1. Restart every Discord gateway:
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
