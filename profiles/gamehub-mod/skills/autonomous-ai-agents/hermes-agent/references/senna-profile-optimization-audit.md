# Senna Profile Optimization Audit Notes

Session-derived reference for optimizing a Hermes install without changing services or deleting data first.

## User-specific baseline discovered

- Canonical/default profile: `senna` (`~/.hermes/active_profile` contains `senna`).
- Senna config path: `~/.hermes/profiles/senna/config.yaml`.
- Senna env path: `~/.hermes/profiles/senna/.env`.
- Senna has `API_SERVER_ENABLED=true` in `.env`.
- Senna gateway was stopped during audit; Hermes also reported a `default` gateway PID, but port `8642` was not listening. Treat this as possible stale gateway state until verified.
- No MCP servers were configured via `hermes mcp list`, even though GBrain/Icarus exist on disk.

## Read-only audit command set

Use before optimizing or cleaning up:

```bash
hermes profile list
hermes status --all
hermes config
hermes tools list
hermes plugins list
hermes mcp list
hermes cron list --all
hermes sessions stats

du -sh ~/.hermes
du -sh ~/.hermes/* 2>/dev/null | sort -h
du -sh ~/.hermes/profiles/* 2>/dev/null | sort -h

du -sh ~/.hermes/profiles/senna/* ~/.hermes/profiles/senna/.[!.]* 2>/dev/null | sort -h
find ~/.hermes/profiles/senna -type f -size +50M -print 2>/dev/null | sort
find ~/.hermes/profiles/senna -type d -name node_modules -prune -print 2>/dev/null | sort
find ~/.hermes/profiles/senna -type d -name .git -prune -print 2>/dev/null | sort

hermes gateway status
hermes --profile senna gateway status
lsof -nP -iTCP:8642 -sTCP:LISTEN
ps aux | grep -i "hermes gateway" | grep -v grep
```

## Audit interpretation from session

Senna profile was ~1.5G, but the bulk was not sessions, logs, checkpoints, or skills:

- `profiles/senna/home`: ~1.4G
- `profiles/senna/home/Library/pnpm/store`: ~1.2G
- `profiles/senna/home/Library/Caches/Homebrew`: ~144M
- `profiles/senna/sessions`: ~18M
- `profiles/senna/checkpoints`: ~940K
- `profiles/senna/state-snapshots`: ~42M
- `profiles/senna/skills`: ~9.4M
- `profiles/senna/logs`: ~204K

Conclusion: the main cleanup candidate is the profile-home pnpm store/cache, not Hermes memory/session data. Do not delete it blindly; first confirm whether a workspace/GBrain workflow still needs that specific store.

## Approved lean Senna config changes applied

```bash
hermes config set display.compact true
hermes config set display.streaming true
hermes config set display.tool_progress new
hermes config set display.interim_assistant_messages false
hermes config set delegation.max_concurrent_children 2
hermes config set delegation.max_iterations 30
```

Verify by reading `config.yaml` or running:

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('~/.hermes/profiles/senna/config.yaml')
keys=('compact:', 'streaming:', 'tool_progress:', 'interim_assistant_messages:', 'max_concurrent_children:', 'max_iterations:')
for line in p.read_text().splitlines():
    if line.strip().startswith(keys):
        print(line)
PY
```

## Gateway/workspace rule

For Hermes Workspace/dashboard/API clients, the gateway should be the canonical profile's gateway. If Senna is the default profile, Workspace should connect to Senna's API server on `localhost:8642`, not a stale/default profile gateway. Since `API_SERVER_ENABLED` is snapshotted at gateway startup, changing `.env` requires a gateway restart.

Before changing gateway services, verify:

```bash
hermes profile list
hermes gateway status
hermes --profile senna gateway status
ps -p <reported_pid> -o pid,ppid,command
lsof -nP -iTCP:8642 -sTCP:LISTEN
```

Then summarize the exact service change and get user approval before starting/stopping/restarting gateways.
