# Hermes Profile Path Resolution Reference

## The Symlink Nesting Problem

On this machine, `~/.hermes/profiles/senna/` is a real directory, but HERMES_HOME and many tool paths resolve through symlinks that create nested path patterns. Commands like `cat`, `ls`, and `cd` will fail with confusing errors like:

```
cat: ~/.hermes/profiles/senna/home/.hermes/profiles/senna/home/.hermes/config.yaml: No such file or directory
```

This happens because the shell expands `~` and the first path component resolves correctly, but subsequent components follow symlinks that loop back into the same directory tree.

## How to Inspect Files Safely

**Use Python for path discovery:**
```python
import os, glob
hermes_root = os.path.expanduser("~/.hermes")

# Find all config.yaml files
for root, dirs, files in os.walk(hermes_root):
    dirs[:] = [d for d in dirs if d not in ('venv', '__pycache__', 'node_modules')]
    if 'config.yaml' in files:
        path = os.path.join(root, 'config.yaml')
        print(f"{path}  ({os.path.getsize(path)} bytes)")

# Find all .env files
for root, dirs, files in os.walk(hermes_root):
    dirs[:] = [d for d in dirs if d not in ('venv', '__pycache__', 'node_modules')]
    if '.env' in files:
        print(os.path.join(root, '.env'))
```

**Use `read_file` tool instead of `cat`/`head`** — it resolves paths correctly.

**Use `realpath` carefully:**
```bash
# This works (single argument):
python3 -c "import os; print(os.path.realpath(os.path.expanduser('~/.hermes/profiles/senna/.env')))"
```

## Actual Working Paths (as of session 2026-05-26)

```
Real config location:      ~/.hermes/profiles/senna/home/.hermes/config.yaml
Real venv Python:          ~/.hermes/profiles/senna/hermes-agent/venv/bin/python
Real hermes CLI:           ~/.local/bin/hermes
Shared venv (all gates):   ~/.hermes/profiles/senna/hermes-agent/venv/
Session DB (senna):        ~/.hermes/profiles/senna/sessions/
State DB (senna):          ~/.hermes/profiles/senna/state.db
Gateway logs (senna):      ~/.hermes/profiles/senna/logs/gateway.log
Launchd plists:            ~/Library/LaunchAgents/ai.hermes.gateway-*.plist
```

## Profile Resolution for Multi-Bot Fleets

When `HERMES_HOME=~/.hermes/profiles/senna`, the `--profile <name>` flag resolves to `~/.hermes/profiles/senna/` as the base, NOT `~/.hermes/profiles/<name>/`. The profile name selects a subdirectory or uses the same configs with different platform settings.

Each profile needs its own:
- `.env` file with that bot's Discord/Telegram token
- `config.yaml` with that bot's platform configuration
- `logs/` directory

## Finding Open File Handles

When log paths seem wrong, use `lsof` to find where the process is actually writing:

```bash
# Find all files a gateway process has open
lsof -p <PID> | grep -E '\.(log|txt|db)$'

# Find specifically log files
lsof -p <PID> | grep log
```

This reveals the actual log paths even when plist StandardOutPath/StandardErrorPath don't match reality.
