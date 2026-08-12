# Post-Update Sweep Checklist

Run after any `hermes update`, profile migration, or venv recreation.

## Quick Sweep (parallel)

```bash
# 1. Core health
hermes --version && hermes config check && hermes doctor 2>&1 | head -60

# 2. Plugins — verify enabled list is proper YAML, not stringified JSON
grep -A 20 "^plugins:" "$HERMES_HOME/config.yaml"
hermes plugins list

# 3. Tools
hermes tools list

# 4. Pip-installed plugins (THESE GET WIPED on venv recreation)
~/.hermes/hermes-agent/venv/bin/pip3 show rtk-hermes 2>&1
~/.hermes/hermes-agent/venv/bin/pip3 show mnemosyne-memory 2>&1

# 5. Memory system
hermes memory

# 6. Gateway processes
ps aux | grep "hermes.*gateway" | grep -v grep
launchctl list | grep hermes

# 7. Cron jobs
hermes cron list --all 2>&1

# 8. Scripts exist and are executable
ls -la "$HERMES_HOME/scripts/"*.sh "$HERMES_HOME/scripts/"*.py 2>&1

# 9. MCP servers
grep -A 10 "^mcp_servers:" "$HERMES_HOME/config.yaml"

# 10. API connectivity (from hermes doctor)
hermes doctor 2>&1 | grep -E "✓|✗|⚠" | head -20
```

## npm Deprecation Warnings

During `hermes update`, npm may emit deprecation warnings (inflight, glob, rimraf,
@babel/plugin-proposal-private-methods, rcedit, boolean). These are **transitive
dependency warnings from upstream packages** — cosmetic only, no functional impact.
See `references/npm-deprecation-warnings.md` for details. Do NOT manually upgrade.

## Known Recovery Commands

```bash
# Reinstall pip-installed plugins wiped by venv recreation
~/.hermes/hermes-agent/venv/bin/pip3 install rtk-hermes
~/.hermes/hermes-agent/venv/bin/pip3 install mnemosyne-memory fastembed sqlite-vec

# Fix plugins.enabled if stored as stringified JSON
~/.hermes/hermes-agent/venv/bin/python3 -c "
import yaml
with open('$HERMES_HOME/config.yaml') as f:
    cfg = yaml.safe_load(f)
cfg['plugins']['enabled'] = [proper, list, here]
with open('$HERMES_HOME/config.yaml', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
"

# Restart gateway to pick up changes
hermes gateway restart
```

## Signals That Something Got Wiped

| Symptom | Likely Cause |
|---------|-------------|
| `hermes memory` shows "NOT installed" | mnemosyne-memory pip package gone |
| `rtk-rewrite` not found in plugin list | rtk-hermes pip package gone |
| `plugins.enabled` is a single quoted string | config set via `hermes config set` with JSON |
| `no such module: vec0` on vec tables | sqlite-vec v2 tables with v3 package (harmless) |
| Doctor says "invalid API key" for working keys | Key values may have been corrupted in .env |
