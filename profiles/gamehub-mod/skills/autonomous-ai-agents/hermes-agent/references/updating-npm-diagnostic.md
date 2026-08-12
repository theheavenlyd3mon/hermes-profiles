# Update-Time NPM Diagnostics

When the user reports npm deprecation warnings during `hermes update`, investigate systematically:

## Quick Check (current state)

```bash
# Check installed packages for deprecation field
python3 -c "
import json, os
for dirname in ['', 'ui-tui']:
    lockfile = f'~/.hermes/profiles/senna/hermes-agent/{dirname}/node_modules/.package-lock.json'
    if os.path.exists(lockfile):
        with open(lockfile) as f:
            data = json.load(f)
        dep = [(k, v['deprecated']) for k, v in data.get('packages',{}).items() if v.get('deprecated')]
        for k,v in dep:
            print(f'⚠ {k}: {v}')
"
```

## What `hermes update` does with npm

1. Calls `_update_node_dependencies()` which iterates the repo root and `ui-tui/`
2. For each, calls `_run_npm_install_deterministic()`:
   - Prefers `npm ci` (lockfile-preserving)
   - Falls back to `npm install` if lockfile is out of sync
   - Flags: `--silent --no-fund --no-audit --progress=false`
3. **Both stdout and stderr are captured** — only shown if `returncode != 0`
4. So deprecation warnings from npm go to the captured stderr, not the terminal normally

## How to surface the deprecation

```bash
# Run the exact command Hermes uses (visible output):
cd ~/.hermes/profiles/senna/hermes-agent
npm ci --silent --no-fund --no-audit --progress=false

cd ~/.hermes/profiles/senna/hermes-agent/ui-tui
npm ci --silent --no-fund --no-audit --progress=false

# If lockfile is stale (what hermes update falls back to):
npm install --silent --no-fund --no-audit --progress=false
```

## Where to look

| What | Where |
|------|-------|
| Update stdout log | `~/.hermes/logs/update.log` or `profiles/<name>/logs/update.log` |
| npm debug logs | `~/.npm/_logs/` (real home) or `~/.hermes/profiles/<name>/home/.npm/_logs/` (sandbox home) |
| Node module manifest | `node_modules/.package-lock.json` — check `deprecated` field |
| Package registry | `npm view <pkg> deprecated` for any package in question |

## Two npm installs managed by update

| Scope | `package.json` | Main deps |
|-------|---------------|-----------|
| **repo root** | `hermes-agent/package.json` | `agent-browser`, `@askjo/camofox-browser` (browser automation) |
| **ui-tui** | `hermes-agent/ui-tui/package.json` | `ink`, `react`, `nanostores`, `ink-text-input` (React Ink TUI) |

## Common causes

- **Lockfile rotation**: `npm ci` → `npm install` fallback when git-pull brought in lockfile changes. The fallback can print fresh registry deprecation info from the new lockfile's dependency versions.
- **Transient registry deprecation**: A publisher deprecated then rescinded a version. Fresh install resolves it.
- **Version mismatch**: The `package.json` range and the resolved lockfile version are slightly different. The `npm ci` step resolves strictly from the lockfile; `npm install` resolves from the range.
