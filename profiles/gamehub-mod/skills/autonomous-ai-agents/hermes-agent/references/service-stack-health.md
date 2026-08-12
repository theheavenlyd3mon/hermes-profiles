# Service Stack Health Verification

Use this when checking, restoring, or verifying the full Hermes service stack (gateway, workspace, dashboards) — ensuring all components run on their correct ports with no conflicts.

Derived from a session where the gateway was running but the workspace wasn't, and both needed to be brought up in the right order.

## Quick Port Map (Canonical)

| Service | Port | Default | Notes |
|---------|------|---------|-------|
| Gateway (API Server) | 8642 | `127.0.0.1:8642` | Requires `API_SERVER_ENABLED=true` in profile's `.env` |
| Hermes Workspace (Vite) | 3000 | `0.0.0.0:3000` | Configurable via `$PORT` env var |
| Workspace Daemon | 3099 | `127.0.0.1:3099` | Only if `workspace-daemon/` dir exists in repo — may be absent upstream |
| Other Vite projects | 5173+ | Vite default | Not a conflict unless they overlap with above |

## Full Verification Steps

### 1. Gateway Check

```bash
# Check service status
hermes gateway status

# Check profile alignment — ensure the right profile is running
hermes profile list
hermes --profile senna gateway status

# Check process directly
ps aux | grep -i "hermes gateway" | grep -v grep
```

### 2. Port Conflict Scan

```bash
# Check ALL expected ports at once
lsof -nP -iTCP -sTCP:LISTEN | grep -E '8642|3000|3099|5173|5174'

# Or full port list for complete picture
lsof -nP -iTCP -sTCP:LISTEN
```

### 3. Verify API Server is Enabled

The gateway's OpenAI-compatible HTTP API is required for workspace/dashboard connections.

```bash
# Check Senna profile's .env for the flag
grep API_SERVER_ENABLED ~/.hermes/profiles/senna/.env

# If absent, add it (needs gateway restart to take effect):
echo "API_SERVER_ENABLED=true" >> ~/.hermes/profiles/senna/.env
```

**Important:** `API_SERVER_ENABLED` is snapshotted at gateway process startup. Editing `.env` while the gateway is running has no effect until `hermes gateway restart`.

### 4. Check Workspace Config

```bash
# The workspace's vite.config.ts controls ports
grep -n "port:" ~/hermes-workspace/vite.config.ts

# Defaults to 3000, overridable via $PORT env var:
# port: process.env.PORT ? Number(process.env.PORT) : 3000,
```

### 5. Ordered Startup

**Rule:** start the workspace FIRST, then restart the gateway. Restarting the gateway disconnects Telegram/messaging sessions mid-task, so the workspace should be ready before that happens.

```bash
# Step 1: Start workspace in background
cd ~/hermes-workspace && pnpm dev
# (runs in background — verify via port check, not stdout)

# Step 2: Verify workspace is listening
lsof -nP -iTCP:3000 -sTCP:LISTEN

# Step 3: Restart gateway (will briefly disconnect Telegram)
hermes gateway restart
```

### 6. macOS-Specific Verification

macOS lacks the `timeout` command and `nc` may behave differently. Use Python for reliable port probes:

```bash
# Quick TCP port check (macOS-friendly, no timeout needed)
python3 -c "
import socket
s = socket.socket()
s.settimeout(2)
try:
    s.connect(('127.0.0.1', 3000))
    print('port 3000: OPEN')
    s.close()
except Exception as e:
    print(f'port 3000: {e}')
"
```

This can be extended to check multiple ports:

```bash
python3 -c "
import socket
for port in [8642, 3000, 3099]:
    s = socket.socket()
    s.settimeout(2)
    try:
        s.connect(('127.0.0.1', port))
        print(f'port {port}: OPEN')
        s.close()
    except Exception as e:
        print(f'port {port}: {e}')
"
```

### 7. Background Process Patterns

Vite dev servers started as background processes via `pnpm dev` often produce **no observable stdout** in the process log tool. This is normal. Do NOT treat empty stdout as a failure signal.

**Verification chain when background stdout is empty:**
1. Check `lsof -nP -iTCP:<port> -sTCP:LISTEN` — if Vite is running, the port will show
2. Fall back to Python socket probe (above)
3. Check the process tree: `ps aux | grep vite | grep -v grep`
4. Check for `esbuild` companion processes (Vite uses esbuild as a background service)

## Common Issues

### "Workspace daemon" not running

The workspace daemon (port 3099) is referenced in `vite.config.ts` but the `workspace-daemon/` directory may not exist in the upstream `outsourc-e/hermes-workspace` repo. This is an **upstream gap**, not a local misconfiguration. The main dashboard features still work — the daemon powers specific deep-orchestration features.

### Duplicate env vars

Having `API_SERVER_ENABLED=true` appear twice in `.env` is harmless (last one wins, same value) but can confuse reading. Clean it up if you notice it.

### Gateway restart disconnects current session

When you `hermes gateway restart`, any active Telegram/Discord/Slack session is interrupted. The user will need to send a new message after the gateway comes back up to establish a new session.
