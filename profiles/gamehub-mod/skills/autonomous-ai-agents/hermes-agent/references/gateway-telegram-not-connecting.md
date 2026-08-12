# Telegram Not Connecting — Gateway Running but 1 Platform Only

## Symptoms

- `hermes gateway status` shows PID running
- Gateway log says `Gateway running with 1 platform(s)` — no Telegram
- `grep TELEGRAM_BOT_TOKEN ~/.hermes/.env` shows the token is set
- Root `.env` has `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `TELEGRAM_HOME_CHANNEL` uncommented

## Root Cause

The gateway loads `.env` from `HERMES_HOME`, not from the root `~/.hermes/.env`.

When `hermes gateway start` runs under a profile (e.g. Senna), `HERMES_HOME` is set to
`~/.hermes/profiles/senna/`. So `get_hermes_home() / ".env"` resolves to:

```
~/.hermes/profiles/senna/.env   ← gateway reads this
```

NOT:

```
~/.hermes/.env                   ← root (not read by gateway)
```

If the profile `.env` is a **different file** (not a symlink) and doesn't have the
Telegram vars, the gateway will never connect Telegram — even if the root `.env` is
fully configured.

## Diagnosis Flow

### 1. Check how many platforms the gateway actually loaded

```bash
grep "platform(s)" ~/.hermes/profiles/senna/logs/gateway.log
# Expected: "Gateway running with 2 platform(s)"
# Bad: "Gateway running with 1 platform(s)" (api_server only)
```

### 2. Check if Telegram is trying to connect at all

```bash
grep -i "telegram" ~/.hermes/profiles/senna/logs/gateway.log
# If Telegram never appears → gateway can't see the env vars
# If "Failed to connect" → network issue (different problem)
```

### 3. Which `.env` does the gateway actually load?

Check the launchd plist for HERMES_HOME:

```bash
cat ~/Library/LaunchAgents/ai.hermes.gateway-*.plist | grep HERMES_HOME
```

Then verify that `.env` has the Telegram vars:

```bash
HERMES_HOME_PATH=$(cat ~/Library/LaunchAgents/ai.hermes.gateway-senna.plist | grep HERMES_HOME | sed 's/.*<string>//;s/<\/string>//')
grep "^TELEGRAM" "$HERMES_HOME_PATH/.env"
```

Or more directly:

```bash
grep "^TELEGRAM" ~/.hermes/profiles/senna/.env      # if known
grep "^TELEGRAM" ~/.hermes/.env                       # root (may not be loaded by gateway)
```

### 4. Compare root `.env` vs profile `.env`

```bash
diff <(grep "^TELEGRAM" ~/.hermes/.env) <(grep "^TELEGRAM" ~/.hermes/profiles/senna/.env) 2>&1
# Or a full diff to see all divergences:
diff ~/.hermes/.env ~/.hermes/profiles/senna/.env 2>&1 | head -50
```

## Fix Options

### Option A — Add Telegram vars to profile `.env` (targeted)

Insert the active vars into the profile `.env` that the gateway reads:

```bash
sed -i '' '/^# Telegram Bot Token/a\
TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN_PLACEHOLDER' ~/.hermes/profiles/senna/.env
sed -i '' '/^# TELEGRAM_HOME_CHANNEL=/i\
TELEGRAM_ALLOWED_USERS=6494314827' ~/.hermes/profiles/senna/.env
```

Then restart: `hermes gateway restart`

**Watch out:** sed `a` (append) puts the text ON THE SAME LINE as the target. Use `i` (insert before) instead if placement matters, or insert after a blank line.

### Option B — Symlink profile `.env` to root (if both files should match)

This only works if the profile `.env` isn't needed for profile-specific overrides:

```bash
rm ~/.hermes/profiles/senna/.env
ln -s ~/.hermes/.env ~/.hermes/profiles/senna/.env
```

Not recommended if the profile `.env` has diverged significantly (different keys, different
comment states, different path vars) — the symlink would introduce those differences into
the gateway's view too.

### Option C — Make Senna the default profile (long-term fix)

If Senna is your primary profile:

```bash
hermes profile use senna
hermes gateway stop          # stops old default gateway
hermes gateway start         # starts senna gateway (now the default)
```

Now `hermes gateway start` (no `--profile` flag) runs the right one. No need to manage
two `.env` files.

## Verification

After fixing, check:

```bash
# 1. Logs show Telegram connected
grep -i "telegram.*connected" ~/.hermes/profiles/senna/logs/gateway.log

# 2. Gateway now shows 2 platforms
grep "platform(s)" ~/.hermes/profiles/senna/logs/gateway.log

# 3. Send a test message from Telegram to the bot
```

## Additional macOS Quirk: `~` Path Resolution

When using the terminal tool on macOS within a Hermes profile session, `~` may resolve
through `HERMES_HOME` rather than the actual home directory. This causes:

```bash
cat ~/.hermes/.env          # → empty (resolves to ~/.hermes/profiles/senna/home/.hermes/.env which doesn't exist)
cat ~/.hermes/.env  # → works (absolute path)
```

Always use absolute paths (`~/.hermes/.env`) when verifying file contents
from within a profile's terminal tool. Use `ls -la` to confirm existence, not just `cat`.
