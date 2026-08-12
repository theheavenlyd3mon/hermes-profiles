# Mnemosyne Post-Update Recovery

## Symptoms

After `hermes update`, mnemosyne tools (`mnemosyne_remember`, `mnemosyne_recall`, `mnemosyne_diagnose`) silently fail or return empty results. The config still shows `memory.provider: mnemosyne` but nothing works.

## Root Cause

The update's `uv` cache cleanup removes pip-installed packages from the venv. Mnemosyne has 3 packages that get wiped:
- `mnemosyne-memory` (core)
- `fastembed` (embedding model)
- `sqlite-vec` (vector search extension)

The plugin symlinks in `~/.hermes/plugins/` and `~/.hermes/profiles/<name>/plugins/` still exist but point to a non-existent `hermes_memory_provider` directory in site-packages. This is the "phantom symlink" pattern — the symlink resolves to nothing but doesn't look broken at a glance.

## Recovery Steps

### 1. Verify the problem
```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "import mnemosyne; print(mnemosyne.__version__)"
# Expected: ModuleNotFoundError
```

### 2. Reinstall packages
```bash
cd ~/.hermes/hermes-agent && ./venv/bin/pip install mnemosyne-memory fastembed sqlite-vec
```

**Intel Mac:** NEVER use `mnemosyne-memory[all]` — it tries to build llama-cpp-python from source which hangs on Intel. Always install the three packages individually.

### 3. Run the installer
```bash
~/.hermes/hermes-agent/venv/bin/python3 -m mnemosyne.install
```

This:
- Removes and recreates the profile plugin symlink
- Verifies `memory.provider = mnemosyne` in config
- Checks `is_available` returns True

### 4. Verify vector search
```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "
from mnemosyne.core.memory import Mnemosyne
import os
db = os.path.expanduser('~/.hermes/profiles/senna/home/.hermes/mnemosyne/data/mnemosyne.db')
m = Mnemosyne(db)
results = m.recall('test query', top_k=3)
for r in results:
    print(f\"  score={r.get('score', 0):.3f}  content={str(r.get('content',''))[:60]}\")
print('Vector search:', 'WORKING' if results and results[0].get('score', 0) > 0 else 'DEGRADED')
"
```

Scores > 0 = working. Scores = 0.0 everywhere = sqlite-vec not loaded (see vector-debugging reference).

### 5. Check stats
```bash
~/.hermes/hermes-agent/venv/bin/python3 -m mnemosyne.cli stats
```

Should show working memory count, episodic memory count, and knowledge triples.

### 6. Restart gateway
```bash
hermes gateway restart --profile senna
```

## Two Databases

| DB | Path | Used by |
|---|---|---|
| Global | `~/.hermes/mnemosyne/data/mnemosyne.db` | Older data, `mnemosyne_diagnose` |
| Profile | `~/.hermes/profiles/<profile>/home/.hermes/mnemosyne/data/mnemosyne.db` | Active instance for current profile |

The profile DB is the active one. Don't confuse them when checking stats.

## MCP Server (External Clients Only)

Mnemosyne ships `mnemosyne mcp` (stdio/SSE) for external clients like Cursor, Claude Code, and Codex. For Hermes, the native `hermes_memory_provider` plugin is the correct integration — it hooks into agent lifecycle hooks. Do NOT add mnemosyne to Hermes `mcp_servers` config.

```bash
# For external clients (NOT Hermes):
mnemosyne mcp                          # stdio
mnemosyne mcp --transport sse --port 8080  # SSE
```

## Latest Version

As of 2026-06: `mnemosyne-memory` 3.3.0 on PyPI. Install with:
```bash
pip install mnemosyne-memory fastembed sqlite-vec
```

## Prevention

Add mnemosyne verification to the post-update checklist. After every `hermes update`, run step 1 above. If it fails, run steps 2-6 before doing anything else.
