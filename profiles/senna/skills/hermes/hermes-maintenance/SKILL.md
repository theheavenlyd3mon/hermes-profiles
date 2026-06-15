---
name: hermes-maintenance
description: "Hermes maintenance: post-update health checks, plugin audits, MCP binary verification, profile wrapper repair, and stale artifact cleanup. Use after `hermes update`, when diagnosing Hermes issues, or during periodic health audits."
triggers:
  - "hermes update"
  - "post-update"
  - "health check"
  - "plugin audit"
  - "mcp not working after update"
  - "hermes broken after update"
  - "stale plugins"
  - "profile wrapper"
  - "hermes maintenance"
tags: [hermes, maintenance, update, health, plugins, mcp, profiles]
metadata:
  hermes:
    related_skills: [gateway-fleet-ops, gateway-health-check, hermes-agent, native-mcp]
---

# Hermes Maintenance

Post-update health checks, plugin audits, and repair workflows. Run after every `hermes update` or when something breaks unexpectedly.

## Post-Update Health Check

After `hermes update`, run this checklist in order. Stop at the first failure and fix before continuing.

### 1. Version Verification

```bash
~/.hermes/hermes-agent/venv/bin/hermes --version
```

Expected: shows current version, "Up to date". If the wrapper is broken, see [Profile Wrapper Repair](#profile-wrapper-repair).

### 2. Profile CLI Wrapper Check

The profile wrapper at `~/.hermes/profiles/<name>/home/.local/bin/hermes` must point to the real venv:

```bash
cat ~/.hermes/profiles/senna/home/.local/bin/hermes
```

Expected: `exec "~/.hermes/hermes-agent/venv/bin/hermes" "$@"`

**If broken** (points to non-existent path like `profiles/senna/hermes-agent/venv/...`):
```bash
cat > ~/.hermes/profiles/senna/home/.local/bin/hermes << 'EOF'
#!/usr/bin/env bash
unset PYTHONPATH
unset PYTHONHOME
exec "~/.hermes/hermes-agent/venv/bin/hermes" "$@"
EOF
chmod +x ~/.hermes/profiles/senna/home/.local/bin/hermes
```

### 3. MCP Binary Verification

`hermes update` runs `uv` cache cleanup that can clear pip-installed MCP binaries from the venv. Check each configured MCP server:

```bash
# Check all configured MCP binaries exist
for bin in iknowkungfu-mcp codegraph; do
  ls -la ~/.hermes/hermes-agent/venv/bin/$bin 2>/dev/null || echo "MISSING: $bin"
done
```

**If missing**, reinstall in the venv:
```bash
cd ~/.hermes/hermes-agent && source venv/bin/activate && pip install <package-name>
```

Specific packages:
- `iknowkungfu` → provides `iknowkungfu-mcp` + `kfu`
- `codegraph` → installed via npm globally, not pip
- `mnemosyne-memory` → core memory (v3.3.0 as of 2026-06). Also needs `fastembed` + `sqlite-vec` (separate packages)
- `rtk-hermes` → provides `rtk-rewrite` plugin via entry points. Install with `uv pip install --python <venv-python> rtk-hermes`

### 4. Mnemosyne Memory Provider Verification

`hermes update` can wipe `mnemosyne-memory`, `fastembed`, and `sqlite-vec` from the venv entirely. The plugin symlinks may still exist but point to a non-existent `hermes_memory_provider` directory ("phantom symlink"). Your memory provider config (`memory.provider: mnemosyne`) will silently fail.

```bash
# Quick check — does the package exist?
~/.hermes/hermes-agent/venv/bin/python3 -c "import mnemosyne; print(mnemosyne.__version__)" 2>&1

# If ModuleNotFoundError, reinstall:
cd ~/.hermes/hermes-agent && ./venv/bin/pip install mnemosyne-memory fastembed sqlite-vec

# Run the installer to fix symlinks and verify provider:
~/.hermes/hermes-agent/venv/bin/python3 -m mnemosyne.install

# Verify vector search works (scores should be > 0):
~/.hermes/hermes-agent/venv/bin/python3 -c "
from mnemosyne.core.memory import Mnemosyne
m = Mnemosyne('~/.hermes/profiles/senna/home/.hermes/mnemosyne/data/mnemosyne.db')
results = m.recall('test', top_k=1)
print('score:', results[0].get('score', 0) if results else 'no results')
"
```

**Intel Mac pitfall:** Do NOT install `mnemosyne-memory[all]` — it builds llama-cpp-python from source which hangs on Intel. Always install `mnemosyne-memory fastembed sqlite-vec` individually.

**Two databases:** Global (`~/.hermes/mnemosyne/data/`) vs Profile (`~/.hermes/profiles/<name>/home/.hermes/mnemosyne/data/`). The active instance uses the profile DB. `mnemosyne stats` CLI reports from the profile DB.

**Mnemosyne MCP vs Native Plugin:** Mnemosyne ships an MCP server (`mnemosyne mcp`) for external clients (Cursor, Claude Code, Codex). For Hermes, the native `hermes_memory_provider` plugin is superior — it hooks into agent lifecycle (pre_llm_call, post_tool_call, session_start). Do NOT add mnemosyne to `mcp_servers` in Hermes config; it's redundant and loses lifecycle integration.

**After reinstall, restart gateway** to pick up the plugin: `hermes gateway restart --profile senna`

> Full recovery procedure with verification scripts: see `references/mnemosyne-post-update-recovery.md` and `references/rtk-hermes-post-update-recovery.md`

### 5. Config Consistency Audit

After updates, the config can accumulate stale references. Check for mismatches:

```bash
# Find plugins in enabled list that don't exist on disk
grep -A50 "^  enabled:" ~/.hermes/profiles/senna/config.yaml | grep "^  - " | while read -r entry; do
  name=$(echo "$entry" | sed 's/  - //')
  found=0
  for d in ~/.hermes/plugins/ ~/.hermes/profiles/senna/plugins/; do
    [ -d "$d$name" ] && found=1
  done
  [ $found -eq 0 ] && echo "STALE in enabled list: $name"
done

# Find plugins on disk not in enabled list (auto-discovered, may be intentional)
for d in ~/.hermes/plugins/*/; do
  name=$(basename "$d")
  grep -q "  - $name$" ~/.hermes/profiles/senna/config.yaml 2>/dev/null || echo "Not in enabled list (auto-discovered): $name"
done
```

Stale entries in `plugins.enabled` are harmless (Hermes ignores missing dirs) but should be cleaned up for clarity. Remove with `patch` or `hermes config edit`.

### 6. Plugin Health Audit

Check all plugins have valid manifests:

```bash
for d in ~/.hermes/plugins/*/; do
  name=$(basename "$d")
  if [ -f "$d/plugin.yaml" ] || [ -f "$d/plugin.json" ]; then
    echo "OK  $name"
  else
    count=$(find "$d" -type f 2>/dev/null | wc -l)
    echo "STALE  $name ($count files, no manifest)"
  fi
done
```

Stale directories with no manifest and no meaningful files are safe to remove:
```bash
rm -rf ~/.hermes/plugins/<stale-name>
```

### 7. Gateway Status

```bash
# Check launchd-managed gateways
launchctl list | grep hermes

# Check running processes
ps aux | grep "hermes.*gateway" | grep -v grep
```

All Discord fleet profiles should be running. If gateways are down, see `gateway-fleet-ops` skill.

### 9. Cron Job Health Check

After updates, cron jobs can break due to model routing changes or wiped dependencies. Check for failures:

```bash
hermes cron list 2>&1 | grep -E "error:|TimeoutError"
```

Common post-update cron failures:
- **"Not supported model"** — model routing bug where fallback provider model is sent to primary endpoint. Fix: `hermes cron edit <job_id> --model <correct-model>`
- **TimeoutError** — job exceeded idle limit. Usually a provider streaming issue or DNS failure.
- **Discord delivery failures** — intermittent DNS resolution (`nodename nor servname`). Usually transient.

Check the cron output directory for detailed error logs:
```bash
ls -lt ~/.hermes/profiles/senna/cron/output/ | head -10
cat ~/.hermes/profiles/senna/cron/output/<job-id>/<timestamp>.md
```

### 10. Skill Sync Verification

The update syncs bundled skills. Check for any that were skipped or errored:

```bash
# Count skills per profile
for p in senna default; do
  count=$(ls ~/.hermes/profiles/$p/skills/*/*/SKILL.md 2>/dev/null | wc -l)
  echo "$p: $count skills"
done
```

## Profile Wrapper Repair

**Root cause:** The profile wrapper at `~/.hermes/profiles/<name>/home/.local/bin/hermes` is a bash script that hardcodes the venv path. If the venv moves, is recreated, or the profile was set up with a wrong path, the wrapper breaks silently — `hermes` commands fail with "No such file or directory".

**Symptoms:**
- `hermes --version` returns "No such file or directory"
- `hermes status` fails with exit code 126
- Gateway restart commands fail

**Fix:** Rewrite the wrapper to point to the real venv (see step 2 above).

**Prevention:** After any update that rebuilds the venv, verify the wrapper path still resolves.

## Plugin Audit

Run periodically or when behavior seems off:

```bash
# List all plugins with version info
for d in ~/.hermes/plugins/*/; do
  name=$(basename "$d")
  yaml="$d/plugin.yaml"
  if [ -f "$yaml" ]; then
    version=$(grep "^version:" "$yaml" 2>/dev/null | head -1)
    desc=$(grep "^description:" "$yaml" 2>/dev/null | head -1 | cut -c1-80)
    echo "OK  $name $version"
  else
    echo "??  $name (no plugin.yaml)"
  fi
done
```

### Known Plugin Layout (Senna profile)

| Plugin | Purpose | Has Manifest |
|--------|---------|:---:|
| hermes-lcm | Lossless Context Management (DAG engine) | ✓ |
| icarus | Self-memory + replacement models | ✓ |
| kanban-api | Kanban board HTTP API | ✓ |
| katana | Security (taint tracking, scanners) | ✓ |
| session-api | Session conversation HTTP API | ✓ |
| web-search-plus | Multi-provider web search | ✓ |
| hermes-achievements | Gamified tracking (data-only) | data-only |
| hermes-mnemosyne | Memory provider (symlink → venv) | symlink |
| rtk-rewrite | Terminal command rewriting (entry point plugin) | entry point |

## Pitfalls

- **pip binaries cleared during update**: `hermes update` runs `uv` cache cleanup and can remove pip-installed binaries from the venv. Always verify MCP binaries exist after updating. Reinstall with `pip install <package>` in the venv.
- **Profile wrapper stale path**: The wrapper hardcodes the venv path. If you move or recreate the venv, the wrapper breaks. Always verify after venv changes.
- **launchd exit 5 on older macOS**: Some macOS versions can't manage gateway via launchd. The update falls back to background process mode. Gateway won't auto-restart on crash or auto-start at login. This is expected — not an error.
- **CUA driver Apple Silicon only**: The CUA (Computer Use Agent) driver only ships Apple Silicon builds. Intel Macs get a warning during update. computer_use tool won't work on Intel.
- **Empty plugin directories are harmless**: Empty dirs like `hermes-mnemosyne` or `mnemosyne` with no files are leftovers from old installs. Safe to remove but not harmful.
- **Phantom plugin symlinks**: A symlink can exist in `~/.hermes/plugins/` pointing to a directory that no longer exists in the venv site-packages. The plugin appears "installed" but loads nothing. Always verify the target exists: `ls -la ~/.hermes/plugins/<name>`. The `mnemosyne.install` command fixes this automatically for mnemosyne.
- **Mnemosyne wiped during update**: Unlike most pip packages, `mnemosyne-memory` + `fastembed` + `sqlite-vec` can be completely removed by the update's cache cleanup. This is the most common post-update breakage for memory. Always verify after updating.
- **RTK-hermes wiped during update**: Same as mnemosyne — `rtk-hermes` (the `rtk-rewrite` plugin) gets cleared by the update's cache cleanup. The config still references `rtk-rewrite` in `plugins.enabled` but the package is gone. Reinstall with: `~/.local/bin/uv pip install --python ~/.hermes/hermes-agent/venv/bin/python --upgrade rtk-hermes`
- **Cron jobs failing with "Not supported model"**: After a provider/model change, cron jobs with `model: null` (meaning "use default") can fall back to the `fallback_providers` model name and send it to the wrong endpoint. Example: jobs try `deepseek-v4-pro` on the `xiaomi` endpoint which rejects it. **`hermes cron edit` has no `--model` flag.** Fix by editing jobs.json directly. **CRITICAL: The model field MUST be a plain string, NOT a dict.** Setting `{'provider': 'xiaomi', 'model': 'mimo-v2.5-pro'}` causes `'dict' object has no attribute 'lower'` because the cron system calls `.lower()` on the model value. Correct format: `"mimo-v2.5-pro"`.
  ```python
  import json
  path = "~/.hermes/profiles/senna/cron/jobs.json"
  with open(path) as f:
      data = json.load(f)
  for job in data['jobs']:
      if 'Not supported model' in str(job.get('last_error','')):
          job['model'] = 'mimo-v2.5-pro'  # STRING, not dict
  with open(path, 'w') as f:
      json.dump(data, f, indent=2, default=str)
  ```
  Restart the gateway afterward to pick up changes. Re-trigger the jobs with `hermes cron run <job_id>`. Check results after 60-90s — if some still show the old error, the scheduler cached the pre-fix config. Re-trigger once more.
- **Gateway restart required for MCP**: MCP tools only load at startup. After any MCP config change, restart the gateway: `hermes gateway restart --profile <name>`.
- **Stale __pycache__**: The update clears 80+ stale `__pycache__` directories automatically. If you see import errors after update, a manual `find ~/.hermes/hermes-agent -name __pycache__ -exec rm -rf {} +` may help.
- **Fabric handoff silently fails**: An agent (especially Researcher or cron jobs) may report "Entry saved, assigned to X" but the entry never appears in `fabric_pending` or `fabric_search`. The agent's `fabric_write` call can fail silently (API error, timeout, token issue) while the agent still reports success based on the call *returning* rather than the entry *persisting*. **Verification**: Always check `fabric_pending` or `fabric_search` for the expected entry after a cross-agent handoff. If missing, the research is often still in Discord messages — search `#research-lab` or the agent's channel with `fetch_messages`. Re-save manually from there.
