# Service Audit Pattern (Session-Derived)

Session context: 2026-05-09, macOS 15.6. User wanted to verify Hermes gateway + workspace + dashboard were running without port conflicts.

## Starting State

- Gateway (Senna profile): running on 127.0.0.1:8642, PID 75662
- Hermes Workspace (outsourc-e/hermes-workspace at ~/hermes-workspace): NOT running
- workspace-daemon: directory missing from upstream repo, so port 3099 is always absent
- hermes-solar-system (unrelated project): running on 127.0.0.1:5173 and 5174
- API_SERVER_ENABLED=true confirmed in ~/.hermes/profiles/senna/.env (appeared twice on lines 395 and 415 — harmless duplicate)
- Telegram connected (TELEGRAM_BOT_TOKEN present)

## Audit Commands Run

```bash
# 1. Gateway status
hermes gateway status

# 2. All listening ports
lsof -nP -iTCP -sTCP:LISTEN

# 3. Running Vite/workspace processes
ps aux | grep -E 'workspace|pnpm|vite' | grep -v grep

# 4. API server env var
grep API_SERVER_ENABLED ~/.hermes/profiles/senna/.env

# 5. Workspace daemon directory
test -d ~/hermes-workspace/workspace-daemon && echo "EXISTS" || echo "NOT FOUND"

# 6. Workspace package.json for dev command
cat ~/hermes-workspace/package.json | head -30
```

## Key Discovery: Missing Workspace Daemon

The `workspace-daemon/` directory does **not exist** in the upstream repo (outsourc-e/hermes-workspace) as of version 2.3.0. However, `vite.config.ts` references it:

- Line 220: `const workspaceDaemonPort = '3099'`
- Line 221: `const daemonCwd = resolve('workspace-daemon')`

Any dashboard feature depending on the workspace daemon (port 3099) will silently fail because the spawn target doesn't exist. This is an **upstream gap**, not a local configuration issue.

## Port Map Template

| Service | Port | Status | Notes |
|---------|------|--------|-------|
| Gateway | 8642 | ✅/❌ | Check profile alignment |
| Workspace (Vite) | 3000 | ✅/❌ | Default; $PORT env var overrides |
| Workspace Daemon | 3099 | ❌ always | Missing from upstream repo |
| (other Vite projects) | varies | varies | Check cwd to distinguish |

## Duplicate .env Entries

`API_SERVER_ENABLED=true` appeared twice in the Senna .env (lines 395 and 415). The duplicate is harmless — any duplicate env var, the last occurrence wins. Worth cleaning up for clarity but not urgent.

## Presentation Pattern

After completing an audit, present the port map to the user in a structured format:
1. Table of service → port → running? → notes
2. "The Good" — what's correctly configured with no conflicts
3. "The Gap" — what's missing or not running
4. Any one-item readiness note (duplicates, missing dir, etc.)
5. Bottom line summary

This gives the user a clear picture without needing to read the raw terminal output.
