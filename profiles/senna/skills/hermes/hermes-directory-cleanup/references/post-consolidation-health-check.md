# Post-Consolidation Health Check

After symlinking profile hermes-agent to root, verify everything resolves
correctly. Run these checks in order — each catches a different failure mode.

## 1. CLI Chain

```bash
hermes --version
# Should print version, project path, python version
```

## 2. Symlink Resolution

```bash
# Same inode = correct
stat -f "%i" ~/.hermes/hermes-agent/
stat -f "%i" ~/.hermes/profiles/<name>/hermes-agent/

# Venv binaries accessible through symlink
ls ~/.hermes/profiles/<name>/hermes-agent/venv/bin/hermes
ls ~/.hermes/profiles/<name>/hermes-agent/venv/bin/python
```

## 3. MCP Binaries

```bash
# Check every MCP server configured in root AND profile configs
grep -r 'command:' ~/.hermes/config.yaml ~/.hermes/profiles/*/config.yaml

# Each binary must exist at its absolute path
ls -la /path/to/each/mcp/binary
```

If a binary is missing (e.g. `iknowkungfu-mcp`), install it:
```bash
# pip may be missing from root venv — bootstrap it first
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python pip
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python <package>
```

## 4. All Profile Gateways

```bash
for p in senna architect coder foreman oracle researcher secretary; do
  pid=$(pgrep -f "profile $p gateway" 2>/dev/null)
  if [ -n "$pid" ]; then
    uptime=$(ps -p $pid -o etime= 2>/dev/null)
    echo "  $p: RUNNING (PID $pid, up $uptime)"
  else
    echo "  $p: NOT RUNNING"
  fi
done
```

## 5. Discord Connection

```bash
grep 'discord.*connected\|discord.*error\|discord.*fail' \
  ~/.hermes/profiles/<name>/logs/gateway.log | tail -5
# Should show "Connected as ..." with no recent 4004 errors
```

## 6. Memory Provider (Mnemosyne)

```bash
# Config check
grep 'provider: mnemosyne' ~/.hermes/profiles/<name>/config.yaml

# DB exists and was recently written
ls -la ~/.hermes/mnemosyne/data/mnemosyne.db

# Diagnostics (unset LLM vars = normal, uses defaults)
tail -5 ~/.hermes/mnemosyne/logs/diagnose_*.jsonl
```

## 7. Dashboard

```bash
hermes dashboard --no-open &
sleep 5
lsof -iTCP:9119 -sTCP:LISTEN -P
# Should show python listening on 9119
```

## 8. Obsidian Vault

```bash
ls ~/.hermes/profiles/<name>/skills/ | wc -l   # skills present
ls "/Users/<user>/Hermes Vault/"                 # vault accessible
```

## Common Post-Consolidation Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `hermes: command not found` | Root hermes-agent was moved/deleted | Reinstall hermes |
| MCP binary not found | Binary was in profile venv, not root | `uv pip install` in root venv |
| Gateway crash-looping (4004) | Multiple gateways fighting for Discord token | Stop all, restart one |
| `No messaging platforms enabled` | Duplicate `platforms:` key in config.yaml | Merge into single key |
| Config not picked up | Profile reads its own config, not root | Check both config.yaml files |
