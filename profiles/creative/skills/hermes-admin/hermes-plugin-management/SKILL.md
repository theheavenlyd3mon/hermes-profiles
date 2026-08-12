---
name: hermes-plugin-management
description: "Install Hermes plugins via CLI, not manual clone."
---

# Hermes Plugin Management

Third-party plugins extend Hermes with new toolsets. They follow a standard architecture: `plugin.yaml` + `__init__.py` with `register(ctx)` function.

## Installation Workflow

### The Right Way: Use the CLI

```bash
hermes plugins install <owner/repo>
# or
hermes plugins install <git-url>
```

**Options:**
- `--enable` or `-e`: Auto-enable after install (skip confirmation)
- `--no-enable`: Install disabled, enable later
- `--force` or `-f`: Remove existing and reinstall

**Example:**
```bash
hermes plugins install CliffWade/hermes-image-studio --enable
```

The CLI:
1. Clones the repo to the correct profile-specific plugins directory
2. Registers it in Hermes' plugin discovery system
3. Optionally enables it immediately

### The Wrong Way: Manual Git Clone

**DO NOT** manually clone into `~/.hermes/plugins/` or `~/.hermes/profiles/<name>/plugins/`.

Manual clones are not discovered by `hermes plugins enable/disable` because they bypass Hermes' plugin registry. Even if the directory structure and `plugin.yaml` are correct, the CLI won't recognize them.

**Symptoms of manual clone:**
- `hermes plugins enable <name>` returns "Plugin not installed or bundled"
- Plugin directory exists but doesn't appear in `hermes plugins list`

**Fix:** Remove the manual clone and use `hermes plugins install` instead.

## Plugin Lifecycle

### List Installed Plugins

```bash
hermes plugins list                    # Full table
hermes plugins list --plain --no-bundled  # Compact, user-installed only
```

### Enable/Disable

```bash
hermes plugins enable <name>
hermes plugins disable <name>
```

The `<name>` must match the `name:` field in the plugin's `plugin.yaml`, NOT the directory name.

### Update

```bash
hermes plugins update <name>
```

Pulls latest changes from the source repository.

### Remove

```bash
hermes plugins remove <name>
# or
hermes plugins uninstall <name>
```

## Plugin Directory Structure

Plugins are stored in profile-specific directories:
- **Global plugins:** `~/.hermes/plugins/` (shared across profiles)
- **Profile-specific:** `~/.hermes/profiles/<profile>/plugins/` (only for that profile)

The `hermes plugins install` command places plugins in the active profile's directory by default.

Each plugin directory contains:
```
<plugin-name>/
├── __init__.py          # Entry point with register(ctx) function
├── plugin.yaml          # Metadata: name, version, description, provides_tools
├── README.md            # Documentation
└── (other modules)      # engine.py, tools.py, schemas.py, etc.
```

## Plugin Architecture

Standard plugin pattern:

```python
# __init__.py
def register(ctx) -> None:
    """Called by Hermes plugin loader."""
    ctx.register_tool(
        name="tool_name",
        toolset="toolset-name",
        schema={...},  # JSON Schema
        handler=handler_function,
        check_fn=optional_gate_function,
        emoji="🎨"
    )
```

The `plugin.yaml` declares metadata:
```yaml
name: plugin-name
version: 1.0.0
description: "What it does"
author: "Author"
kind: backend  # or 'standalone'
provides_tools:
  - tool_name_1
  - tool_name_2
```

## Gating on Credentials

Many plugins gate their tools on API keys being present. The `check_fn` parameter in `register_tool` is called before the tool is made available:

```python
def _check_api_key() -> bool:
    try:
        # Check if API key is set
        return bool(os.environ.get("API_KEY"))
    except:
        return False

ctx.register_tool(
    name="my_tool",
    ...
    check_fn=_check_api_key,  # Tool only registers if this returns True
)
```

This prevents errors when credentials aren't configured.

## Troubleshooting

### Plugin Not Found After Install

**Symptom:** `hermes plugins enable <name>` says "not installed"

**Cause:** Manual git clone instead of `hermes plugins install`

**Fix:**
```bash
rm -rf ~/.hermes/profiles/<profile>/plugins/<name>
hermes plugins install <owner/repo> --enable
```

### Plugin Name Mismatch

**Symptom:** Directory exists but CLI can't find it

**Cause:** Directory name doesn't match `plugin.yaml` name field

**Fix:** The CLI uses the `name:` from `plugin.yaml`, not the directory name. If they don't match, use the yaml name in CLI commands.

### Tools Not Available After Enable

**Symptom:** Plugin shows as enabled but tools don't appear in session

**Cause:** Gateway needs restart to load new plugins

**Fix:**
```bash
hermes gateway restart
```

Then start a new session.

## Common Patterns

### Zero-Dependency Plugins

Well-designed plugins use only Python stdlib (urllib, sqlite3, json, os, re). No `requirements.txt`, no pip installs. Clone and it works.

### Safe-by-Design

If required credentials aren't set, tools simply don't register. No crashes, no stack traces. Set the key when ready.

### Organized Output

Plugins that generate files should:
- Save to a configurable directory (via env var like `PLUGIN_OUTPUT_DIR`)
- Use descriptive filenames: `YYYYMMDD_HHMMSS_preset_seed_subject.ext`
- Track history in SQLite for later retrieval

## Working with Plugins Before Gateway Restart

After `hermes gateway restart`, the current session doesn't have the new tools loaded. To test or use plugin functionality immediately, import the engine directly:

```python
import os, sys

# Set required env vars (plugins often read from ~/.hermes/.env)
env_path = os.path.expanduser("~/.hermes/.env")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("REQUIRED_KEY="):
            os.environ["REQUIRED_KEY"] = line.split("=", 1)[1].strip("\"'")
            break

# Add plugin to Python path
plugin_dir = os.path.expanduser("~/.hermes/profiles/<profile>/plugins/<name>")
sys.path.insert(0, plugin_dir)

# Import and use the engine directly
from plugin_package import engine
result = engine.do_thing(param="value")
```

This bypasses the tool registration layer and calls the plugin's logic directly. Useful for testing or when you need immediate results without waiting for a new session.

## Pitfalls

1. **Manual clone doesn't work** — Always use `hermes plugins install`. Manual clones bypass the registry.

2. **API key gating is silent** — If a plugin's required API key isn't set in `~/.hermes/.env`, tools simply don't register. No error message, no stack trace. Check the plugin's `_check_*` function to see what env var it needs.

3. **Output paths are hardcoded** — Many plugins default to specific directories (e.g., `/Volumes/Spare Drive/...`). Override via env var or pass the correct path when calling the engine directly.

4. **Gateway restart required** — After installing/enabling a plugin, restart the gateway before starting a new session. Current session won't have the tools until restart.

2. **Gateway restart required** — After installing/enabling a plugin, restart the gateway before starting a new session.

3. **Profile-specific paths** — Plugins install to the active profile. Check `~/.hermes/profiles/<profile>/plugins/` not just `~/.hermes/plugins/`.

4. **Name vs directory** — CLI commands use the `name:` from `plugin.yaml`, not the directory name. They may differ.

5. **Credential gating** — If tools don't appear, check that required API keys are set in `~/.hermes/.env` or environment.

6. **Zero-dep preferred** — Plugins with no external dependencies are more reliable. Avoid plugins requiring `pip install`.
