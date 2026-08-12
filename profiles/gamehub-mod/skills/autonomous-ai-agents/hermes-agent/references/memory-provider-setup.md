# Memory Provider Setup (Mnemosyne)

Installing a third-party memory provider like Mnemosyne into the Hermes Agent runtime.

## Overview

Hermes uses a Python virtual environment at `~/.hermes/hermes-agent/venv/` for all plugin code. Memory providers with Hermes integration (Mnemosyne, Honcho, Mem0, etc.) must be installed into this venv and registered with Hermes to appear in `hermes memory status`.

## Mnemosyne Installation

Mnemosyne (`AxDSan/mnemosyne`) is a local-first SQLite-backed memory system. Package name: `mnemosyne-memory`.

### Step 1: Bootstrap pip (if missing from the venv)

The Hermes venv may not have pip installed. Bootstrap it:

```bash
~/.hermes/hermes-agent/venv/bin/python -m ensurepip --upgrade
```

### Step 2: Install the package

```bash
~/.hermes/hermes-agent/venv/bin/python -m pip install --upgrade --no-cache-dir "mnemosyne-memory"
```

Install optional features (dense retrieval + local LLM consolidation):
```bash
~/.hermes/hermes-agent/venv/bin/python -m pip install --upgrade --no-cache-dir "mnemosyne-memory[all]"
```

**⚠️ Warning:** The `[all]` extras pull in `llama-cpp-python` and `ctransformers`, which compile from source (C++ build). This can take 2+ minutes and may time out during agent tool calls. If you only need the base memory system (semantic recall, storage, consolidation), the plain `mnemosyne-memory` install above is sufficient.

### Step 3: Register with Hermes

The Hermes installer creates a symlink at `~/.hermes/profiles/<profile>/plugins/mnemosyne/` and sets `memory.provider: mnemosyne` in config.yaml:

```bash
~/.hermes/hermes-agent/venv/bin/python -m mnemosyne.install
```

### Step 4: Verify

```bash
hermes memory status       # Should show "Provider: mnemosyne"
```

## Pitfalls

### Duplicate YAML key overrides provider

After `mnemosyne.install` sets `memory.provider: mnemosyne`, the config may still contain an old `provider: ''` line further down. YAML uses **last-key-wins** — the empty string overrides `mnemosyne` silently.

**Diagnosis:** `hermes memory status` shows "Provider: (none — built-in only)" even though `grep provider: config.yaml` shows `mnemosyne`.

**Fix:** Search for duplicate keys:
```bash
grep -n 'provider:' ~/.hermes/profiles/senna/config.yaml
```
Remove the second occurrence of `provider: ''` under the `memory:` block.

### venv regenerated after Hermes upgrade

Hermes upgrades (especially v0.9 → v0.10+) may regenerate the venv, wiping pip-installed packages. Mnemosyne must be reinstalled after such upgrades. See `hermes-config-upgrade-pitfalls` in the LLM-Wiki for the full post-upgrade restoration checklist.

### `hermes memory setup` shows "Built-in only" as default

The Hermes interactive `hermes memory setup` picker shows "Built-in only" as the pre-selected option every time. This is normal Hermes UI behavior — your previous selection IS saved. Just select "mnemosyne" and press Enter.

### Symlink-compatible with profile plugin directory

If the profile plugins dir (`~/.hermes/profiles/<profile>/plugins/`) is a symlink to the global plugins dir (`~/.hermes/plugins/`), the `mnemosyne.install` command works transparently — the mnemosyne plugin symlink resolves through the chain and lands in the global directory. No special handling needed.

## Verification Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Package installed | `~/.hermes/hermes-agent/venv/bin/python -c "import mnemosyne; print(mnemosyne.__version__)"` | Version number (e.g. 2.3) |
| Provider in config | `grep -A5 '^memory:' ~/.hermes/profiles/senna/config.yaml` | `provider: mnemosyne` (appears once) |
| Plugin link exists | `ls -la ~/.hermes/profiles/senna/plugins/mnemosyne/` | Directory with `__init__.py` |
| No duplicate keys | `grep -n 'provider:' ~/.hermes/profiles/senna/config.yaml \| grep memory` | Exactly one match |
| Runtime active | `hermes memory status` | "Provider: mnemosyne" |

## Other Memory Providers

The same pattern applies to other pip-based memory providers — install into the Hermes venv, register via the provider's Hermes installer (or `hermes memory setup`), and watch for the duplicate YAML key bug. Providers installed via `hermes plugins install` (git repos with `plugin.yaml`) follow a different path — see `plugin-audit-methodology.md`.
