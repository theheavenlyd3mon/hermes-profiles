# Gateway Consolidation Walkthrough

Session: 2026-05-11. User had two gateways (default + senna), Telegram configured only under Senna.

## Before State

- **Default profile gateway** (PID 10925) — running since Friday. Useless — Telegram keys were commented out in root `.env`.
- **Senna profile gateway** — stopped. Had real Telegram bot token and user allowlist in its profile `.env`.
- Telegram keys lived ONLY in `~/.hermes/profiles/senna/.env`, not in root.
- `hermes gateway status` showed `default` gateway as running with no Telegram capability.

## Streamlining Steps

### Step 1: Move Telegram keys to root `.env`

**Before (root .env):**
```
# TELEGRAM_BOT_TOKEN=
# TELEGRAM_ALLOWED_USERS=
```

**After (root .env):**
```
TELEGRAM_BOT_TOKEN=<actual-token>
TELEGRAM_ALLOWED_USERS=6494314827
TELEGRAM_HOME_CHANNEL=6494314827
```

Used `patch` tool to replace commented-out lines with active values. Token came from Senna's `.env`.

### Step 2: Remove active Telegram keys from Senna `.env`

```bash
sed -i '' '/^TELEGRAM_BOT_TOKEN=/d' ~/.hermes/profiles/senna/.env
sed -i '' '/^TELEGRAM_ALLOWED_USERS=/d' ~/.hermes/profiles/senna/.env
sed -i '' '/^TELEGRAM_HOME_CHANNEL=/d' ~/.hermes/profiles/senna/.env
```

After removal, only commented placeholder lines remain in Senna's `.env`. The profile inherits from root — same principle as the plugins symlink.

### Step 3: Set Senna as sticky default profile

```bash
hermes profile use senna
# Output: Switched to: senna
```

Verifiable with `hermes profile list` — Senna now has ◆ marker.

### Step 4: Stop the old default gateway

```bash
hermes --profile default gateway stop
# Output: ✓ Service stopped
```

### Step 5: Start Senna gateway

```bash
hermes gateway start
# Output: ✓ Service started
```

Because Senna is now the default profile, `hermes gateway start` (no `--profile` flag) runs the right one.

## After State

- One gateway process (Senna, PID 97214)
- Telegram keys in root `.env` (single source of truth)
- Senna `.env` has only comments for Telegram (inherits from root)
- `hermes profile list` shows Senna as default (◆)
- `hermes gateway status` shows Senna gateway loaded and running
- API server on port 8642, health check responds `{"status": "ok"}`
- Channel directory shows 1 Telegram DM connected

## Verification Commands

```bash
hermes gateway status                    # running, correct profile
hermes profile list                      # Senna marked as default
grep "^TELEGRAM" ~/.hermes/.env              # active keys in root
grep "TELEGRAM" ~/.hermes/profiles/senna/.env  # comments only in profile
lsof -nP -iTCP:8642 -sTCP:LISTEN         # gateway API server listening
curl -s http://127.0.0.1:8642/health     # should return {"status":"ok"}
```

## Notes

- The old default gateway (launchd plist at `~/Library/LaunchAgents/ai.hermes.gateway.plist`) is now unloaded. Its definition file still exists on disk but launchd won't start it.
- If a future Hermes update resets the default profile, re-run `hermes profile use senna`.
- This pattern mirrors the plugins symlink approach: canonical config in root, profiles inherit.
