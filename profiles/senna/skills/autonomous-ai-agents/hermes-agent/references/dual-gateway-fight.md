# Dual Gateway Fight: Two Launchd Plists Competing for Port 8642

A specific failure mode on macOS where two Hermes launchd services run simultaneously, creating an infinite restart loop.

## Symptoms

- Telegram sends "gateway shutting down" notifications every 2-10 seconds
- `hermes gateway status` shows a running process with recent PID
- `ps aux | grep hermes.*gateway` shows **two** gateway processes
- Gateway log (`~/.hermes/profiles/<name>/logs/gateway.log`) shows repeated cycles of:
  ```
  Gateway running with 2 platform(s)
  Received SIGTERM — initiating shutdown
  Starting Hermes Gateway...
  Received SIGTERM — initiating shutdown
  ```
  repeating within seconds
- The API server on port 8642 keeps restarting (briefly available, then disappears)

## Root Cause

Two launchd plist files exist:
1. `~/Library/LaunchAgents/ai.hermes.gateway.plist` — old default profile gateway (no `--profile` flag, `HERMES_HOME=~/.hermes`)
2. `~/Library/LaunchAgents/ai.hermes.gateway-senna.plist` — Senna (or other named) profile gateway (`--profile senna`, `HERMES_HOME=~/.hermes/profiles/senna`)

Both plists have:
- `KeepAlive` → `SuccessfulExit` = `false` (restart on any exit code)
- `RunAtLoad` = `true` (starts on login)
- Gateway `--replace` flag (SIGTERMs any existing gateway on startup)

**The fight:**
1. Default gateway starts (no profile) → takes port 8642
2. Senna gateway starts (--profile senna --replace) → SIGTERMs default
3. Default launchd sees exit code 1 → restarts default gateway
4. Senna gateway now has port 8642
5. Default gateway starts with --replace → SIGTERMs Senna
6. Senna launchd sees exit code 1 → restarts Senna gateway
7. GOTO 1 — infinite loop

## Diagnosis

```bash
# 1. List all Hermes launchd plists
ls -la ~/Library/LaunchAgents/*hermes*

# 2. Check how many gateways are currently running
ps aux | grep "hermes.*gateway" | grep -v grep

# 3. Check launchd service list
launchctl list | grep hermes

# 4. Check the gateway log for SIGTERM cycles
tail -100 ~/.hermes/profiles/<profile>/logs/gateway.log | grep -E "SIGTERM|Starting|running with"

# 5. Check the OLD (default) gateway log too
tail -50 ~/.hermes/logs/gateway.log | grep -E "SIGTERM|Starting|running with"
```

## Fix

### 1. Stop and unload the OLD/duplicate plist

```bash
launchctl bootout gui/$(id -u)/ai.hermes.gateway     # stop the service
rm ~/Library/LaunchAgents/ai.hermes.gateway.plist     # remove plist so it can't restart
```

### 2. Verify only the correct one remains

```bash
launchctl list | grep hermes          # should show only one (e.g. ai.hermes.gateway-senna)
ps aux | grep "hermes.*gateway"       # should show one process
```

### 3. Confirm the surviving gateway is stable

Check the profile's gateway log — after 30 seconds, there should be NO new SIGTERM lines. The log should show a single clean startup sequence ending with "Gateway running with 2 platform(s)" and then only periodic cron ticker messages.

```bash
tail -20 ~/.hermes/profiles/<profile>/logs/gateway.log
# Expected: no SIGTERM lines, just "Press Ctrl+C to stop" and "Cron ticker started"
```

## Prevention

- When consolidating profiles (moving default to Senna, etc.), always check for stale plists
- After `hermes profile use <name>`, verify only one launchd plist exists
- If you see two `ai.hermes.gateway*` plist files, the old default is orphaned — remove it

## Side Effects

During the fight, the constant restarting triggers Telegram's flood control on the `set_my_commands` call. The error log shows:

```
telegram.error.RetryAfter: Flood control exceeded. Retry in 1405 seconds
```

This is harmless and resolves on its own after about 20 minutes once the gateway stays up. The command menu registration is cosmetic — it sets the bot's slash-command hints.
