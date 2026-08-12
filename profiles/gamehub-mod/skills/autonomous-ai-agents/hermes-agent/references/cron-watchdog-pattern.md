# Cron Watchdog Pattern: Auto-Starting Dependent Services

This reference documents how to use Hermes cron jobs as lightweight service watchdogs — checking if a required service is up and starting dependent services when the primary is healthy.

## Use Case

You want Service B (e.g., a web dashboard) to start automatically whenever Service A (e.g., the Hermes gateway) is running. You don't want to remember a manual startup sequence.

## Pattern: Cron-Based Watchdog

The approach: a cron job that runs frequently (every 60 seconds), checks two conditions, and acts when both are met.

**Checklist pattern:**
1. Is Service A listening on its port? (gateway → port 8642)
2. Is Service B NOT already running? (workspace → port 3000)
3. If both conditions true → start Service B

## Implementation

Create a cron job with a prompt that uses terminal checks:

```bash
hermes cron create "* * * * *" \
  --name "watchdog-workspace" \
  "Check if the Hermes gateway is healthy (port 8642) and the workspace dashboard (port 3000) is NOT already running. If the gateway is up and the workspace is down, start the workspace dashboard by running 'cd ~/hermes-workspace && pnpm dev' in the background. Do NOT report success — only report if there were errors starting the workspace."
```

Key design choices:
- **Every 60 seconds** is fine — the check is cheap (a port probe)
- **Silent success** — only report errors, so the user isn't spammed
- **The gate check is explicit** — never start the dependent if the primary isn't healthy

## Port Health Checks (macOS)

```bash
# Python socket check (most reliable on macOS)
python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',8642)); s.close(); print('ok')"

# lsof check
lsof -nP -iTCP:8642 -sTCP:LISTEN 2>/dev/null
```

## Hermes Dashboard Architecture (Two Tiers)

When automating dashboard startup, know the two separate UIs:

| Dashboard | Command | Port | Type | Status |
|-----------|---------|------|------|--------|
| Built-in | `hermes dashboard` | 9119 | Python static server | Usually running |
| Workspace | `cd ~/hermes-workspace && pnpm dev` | 3000 | Vite/React dev server | Manual start |

The built-in `hermes dashboard` (port 9119) is a lightweight web UI for config, API keys, and sessions. It's started by `hermes dashboard --no-open` and usually left running.

The Hermes Workspace (`~/hermes-workspace/`) is a full Vite/React/TanStack application that proxies API calls to the gateway. It can auto-start the gateway on dev server launch (built into vite.config.ts), but we want the reverse: gateway → workspace.

## Full Service Health Sweep

When verifying all services after a gateway restart or system wake:

```bash
#!/bin/bash
echo "Gateway (8642):" $(python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',8642)); s.close(); print('✓')" 2>/dev/null || echo "✗")
echo "Dashboard (9119):" $(python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',9119)); s.close(); print('✓')" 2>/dev/null || echo "✗")
echo "Workspace (3000):" $(python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',3000)); s.close(); print('✓')" 2>/dev/null || echo "✗")
echo "WebUI (8787):" $(python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',8787)); s.close(); print('✓')" 2>/dev/null || echo "✗")
```

## Pitfalls

- **Don't start the workspace if the gateway isn't healthy** — the Vite dev server will start but won't connect properly, and the workspace tries to auto-start its own gateway, causing a conflict
- **Background processes on macOS** — `pnpm dev` backgrounded with `&` may not survive terminal closure. Use `nohup` or consider a launchd plist for persistence
- **Port conflict** — if something else is already on port 3000, Vite's `strictPort: false` will pick a different port (3001, 3002...), so the watchdog's port probe on 3000 will miss it
