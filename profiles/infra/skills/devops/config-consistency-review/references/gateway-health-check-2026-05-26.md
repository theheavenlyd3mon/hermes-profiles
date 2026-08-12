# Gateway Health Check — 2026-05-26

Diagnostic pattern for Discord bot gateway health across multiple Hermes profiles.

## The Check Command Sequence

```bash
# 1. List all hermes gateway services with PIDs and exit codes
launchctl list | grep hermes

# 2. For detailed status of a specific gateway:
launchctl list ai.hermes.gateway-<name>
# This returns the full plist info including:
#   LastExitStatus, PID, ProgramArguments, StandardOutPath, StandardErrorPath, OnDemand

# 3. Verify the PID is actually alive:
ps -p <PID> -o comm=

# 4. Check profile directory exists:
ls ~/.hermes/profiles/<name>/

# 5. Check gateway logs:
cat ~/.hermes/profiles/<name>/logs/gateway.log | tail -20
cat ~/.hermes/profiles/<name>/logs/gateway.error.log | tail -20
```

## Exit Code Meanings

| Exit Code | Meaning |
|-----------|---------|
| 0 | Clean exit / running normally |
| 1 | Crashed or errored (Python exception, config error) |
| 256 | Exit code 1 displayed as raw value (Python import error, config issue) |
| -15 | Killed by SIGTERM (often from `launchctl kickstart -k` or KeepAlive timeout) |
| -9 | Killed by SIGKILL (force-killed) |
| empty/"-" | No PID — service not running (stopped or crashed without restart) |

## Common Patterns

### Healthy gateway
- Launchd: PID present, exit=0
- Process: `python` alive at that PID
- Profile directory: exists with config files
- Logs: recent entries, no errors

### Crashed gateway (most common failure)
- Launchd: exit=1 or exit=256
- Process: PID present (may have been restarted by KeepAlive)
- Profile directory: may be empty or missing entirely
- Logs: often BLANK — gateway fails before logger initializes

### Killed gateway
- Launchd: exit=-15
- Process: may still be alive if KeepAlive restarted it
- Usually means SIGTERM was sent (kickstart -k, or manual kill)

### Missing profile
- Launchd: shows PID and seemingly running
- Profile directory: does NOT exist at `~/.hermes/profiles/<name>/`
- The gateway starts but has no config to load — may loop-crash
- Fix: create the profile directory, write config.yaml, .env, SOUL.md

### Port collision
- Multiple gateways with `api_server.enabled: true` all try port 8642
- Symptom: gateways crash-restart in a loop (SIGTERM flood in logs >5 in recent)
- Fix: disable api_server for bot-only profiles, only coordinator (Senna) needs it

## Diagnostic Red Flags

1. **Empty log files on a gateway that has been running** = gateway is failing before log initialization, or stderr is going to a different fd
2. **Exit=0 but profile directory is missing** = gateway loaded with defaults, not functional
3. **Both exit=1 and a process still showing** = KeepAlive restarted it after crash, check if it's stable
4. **Launchd reports PID but `ps -p <PID>` returns nothing** = zombie service entry, needs bootout + kickstart
5. **Multiple gateways sharing the same venv path** = they all point to `~/.hermes/profiles/senna/hermes-agent/venv/bin/python` — this is expected (shared venv), but each must have its own `--profile` argument

## The Single-Command Status Summary

```bash
for svc in senna researcher secretary coder foreman architect; do
  echo "=== $svc ==="
  launchctl list ai.hermes.gateway-$svc 2>&1 | grep -E "LastExitStatus|PID|OnDemand" | sed 's/^/  /'
  ls ~/.hermes/profiles/$svc/ >/dev/null 2>&1 && echo "  PROFILE: exists" || echo "  PROFILE: MISSING"
done
```

## Pitfalls

1. **Don't trust exit=0 alone** — always verify the profile directory exists and has config files
2. **Don't trust PID presence alone** — the process might be running but crashed in a loop; check exit code
3. **Log files at the plist's StandardOutPath may be empty even for failing gateways** — check the process's stderr directly if needed
4. **Heritaged plists may not be on disk** — `launchctl list <label>` shows the loaded state even if the .plist file was deleted; always check launchctl, not just ~/Library/LaunchAgents/
