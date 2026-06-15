---
name: hermes-mcp-profile-isolation
description: Add/configure MCP servers under Hermes profile isolation — the root cause of "MCP server configured but not showing up" when using non-default profiles.
---

# Hermes MCP & Profile Isolation

When MCP servers are configured but `hermes mcp list` shows "No MCP servers configured" (or the gateway doesn't load them), the root cause is almost always **profile isolation**.

## Root Cause

Hermes uses `get_hermes_home()` → `get_config_path()` to find config:

```python
def get_config_path():
    return get_hermes_home() / "config.yaml"
```

Under a non-default profile (e.g. `senna`), `HERMES_HOME` is set to `~/.hermes/profiles/<profile>/`, so `load_config()` reads:

```
~/.hermes/profiles/<profile>/config.yaml
```

**NOT** the global `~/.hermes/config.yaml` or the HOME-scoped `~/.hermes/profiles/<profile>/home/.hermes/config.yaml`.

## Fix

Add `mcp_servers` to the **profile config** file:

```yaml
# ~/.hermes/profiles/<profile>/config.yaml
mcp_servers:
  <server-name>:
    command: /absolute/path/to/binary
    enabled: true
```

Always use an **absolute path** for the `command` — under profile isolation, `HOME` is overridden so relative PATH lookups may fail.

## Verify

```bash
# Check that the config is picked up
hermes mcp list

# Should show your servers. If empty, check which config is being read:
python3 -c "
from hermes_cli.config import load_config, get_config_path
print('Config path:', get_config_path())
c = load_config()
print('Has mcp_servers:', 'mcp_servers' in c)
"
```

## Restart Gateway

After adding MCP servers to the profile config, restart the gateway:

```bash
hermes gateway start    # if using launchd
# or
hermes gateway run --replace   # for manual/foreground
```

## Tilde Expansion Pitfall (Critical)

Under profile isolation, `HOME` is overridden to `~/.hermes/profiles/<profile>/home/`. This means:

- `~/.hermes/hermes-agent/venv/bin/python3` expands to `~/.hermes/profiles/senna/home/.hermes/hermes-agent/venv/bin/python3` — **wrong path, file not found**.
- The real venv lives at `~/.hermes/hermes-agent/venv/bin/python3`.

**Rule:** Always use the **absolute path** to the Hermes venv when running pip/python from a profile-isolated terminal session:

```bash
# WRONG — tilde expands to profile HOME
~/.hermes/hermes-agent/venv/bin/pip install foo

# RIGHT — absolute path bypasses profile HOME override
~/.hermes/hermes-agent/venv/bin/python3 -m pip install foo
```

This affects any `~` path that targets the real user home, not just MCP configs. Applies to all terminal commands in profile-isolated sessions (cron jobs, gateway scripts, agent terminal calls).

## Pitfall: Missing API Key in Profile .env (Critical)

When changing a profile's model provider (e.g. `deepseek` → `xiaomi`), the new provider's API key must exist in the **profile's `.env` file**, not just the global `~/.hermes/.env`.

**Symptom:** Gateway starts but first message fails with:
```
RuntimeError: Provider '<name>' is set in config.yaml but no API key was found.
```

**Root cause:** Each profile has its own `.env` at `~/.hermes/profiles/<profile>/.env`. Global `.env` keys are NOT inherited by profile-isolated sessions.

**Fix:** Copy the provider's API key lines from another profile's `.env` (or the global `.env`) into the target profile's `.env`:

```bash
# Example: copying xiaomi keys from architect to designer
cat ~/.hermes/profiles/architect/.env | grep "^XIAOMI" >> ~/.hermes/profiles/designer/.env
```

Then restart the gateway:
```bash
# Kill and let launchd restart, or:
hermes gateway restart  # from a shell outside the gateway
```

**Rule:** When switching a profile's provider, ALWAYS check that the new provider's API key exists in `~/.hermes/profiles/<profile>/.env` before restarting the gateway. The global `.env` does not cover profile-isolated sessions.

## Pitfall: Profile-Local Venv Paths in MCP Config

A subtle variant of the tilde expansion issue: the config uses an absolute path,
but points to a **profile-local venv** that doesn't exist instead of the main venv.

**Symptom:** MCP server fails to start, binary not found, but the path looks correct.

**Example of the wrong path:**
```yaml
# WRONG — points to a profile-local venv that was never created
command: ~/.hermes/profiles/senna/hermes-agent/venv/bin/iknowkungfu-mcp
```

**Correct path:**
```yaml
# RIGHT — the main Hermes venv where packages are actually installed
command: ~/.hermes/hermes-agent/venv/bin/iknowkungfu-mcp
```

**How it happens:** When setting up MCP servers from within a profile-isolated
session, the agent may construct a path using the profile's directory structure
(`profiles/<name>/hermes-agent/venv/`) instead of the real venv at
`~/.hermes/hermes-agent/venv/`. The profile-local hermes-agent directory may
be a stale duplicate checkout or may not exist at all.

**Rule:** The Hermes venv is ALWAYS at `~/.hermes/hermes-agent/venv/` (the root
checkout). Never use a profile-local path for MCP binary commands.

## Example: iknowkungfu

```yaml
mcp_servers:
  iknowkungfu:
    command: ~/.hermes/hermes-agent/venv/bin/iknowkungfu-mcp
    enabled: true
```

The binary path comes from `which iknowkungfu-mcp` run inside the Hermes venv.
