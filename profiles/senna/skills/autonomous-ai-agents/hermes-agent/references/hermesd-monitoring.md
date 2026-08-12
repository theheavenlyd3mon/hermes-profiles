# hermesd — TUI Monitoring Dashboard

`hermesd` is a **separate TUI process** from the Hermes gateway. It provides a real-time dashboard showing gateway status, sessions, token/cost, tools, cron, skills, logs, and memory. It does **not** run the agent — it monitors it.

## Quick Start

```bash
hermesd                          # Reads root ~/.hermes/ — works for most setups
hermesd --snapshot               # One-shot text snapshot to stdout, no TUI
hermesd --refresh-rate 2         # Poll every 2 seconds (default: 5)
hermesd --snapshot-panel 2       # Snapshot only panel 2 (sessions)
```

## Known Issue: `--profile senna` Fails

```
hermesd --profile senna  →  Error: Profile 'senna' does not exist
```

The `--profile` flag is supposed to read profile-scoped data from `~/.hermes/profiles/<name>/`, but profile detection is currently broken. **Workaround**: run `hermesd` without `--profile` — it still detects the running gateway process via `ps` scan and shows session/config data from the root hermes home. The dashboard works correctly even though Panel 9 shows "Source: root".

## Dashboard Panels (1–10)

| Panel | Content | What It Shows |
|-------|---------|---------------|
| 1 | **Gateway & Platforms** | Running? PID, version, connected platforms (api_server, telegram, etc.) with ● indicators |
| 2 | **Sessions** | Active/total count, message count, tool call count, recent session IDs with type icons (tui ●, cron ●) and age |
| 3 | **Tokens / Cost** | Today input/output tokens, cache read tokens, estimated dollar cost (today + total) |
| 4 | **Tools** | Available tool count, total calls, background procs, checkpoint count, recent session tool usage |
| 5 | **Config** | Model name, provider, personality, compression settings, gateway tools limit |
| 6 | **Cron** | Last tick age, job count, error count, job list with schedules |
| 7 | **Skills / Integrations** | Skill count + categories, credential pools, plugins/MCP count, integration status checks |
| 8 | **Logs** | Live tail of gateway log — most recent lines with timestamps and session IDs |
| 9 | **Profiles** | Current data source root, discovered profile count |
| 10 | **Memory** | Memory provider (mnemosyne, etc.), file count, SOUL presence |

## Data Sources

hermesd aggregates from these files under the active hermes home (default: `~/.hermes/`):

| Data | Source File |
|---|---|
| Gateway state | `<profile>/gateway_state.json` — pid, platform states, active agent count |
| Platform connections | `<profile>/channel_directory.json` — all messaging channels with connection status |
| Sessions | `<profile>/state.db`, `<profile>/lcm.db` — SQLite session databases |
| Cron jobs | `<profile>/cron/jobs.json` |
| Logs | `<profile>/logs/gateway.log` |
| Config | `<profile>/config.yaml` |

## gateway_state.json Structure

```json
{
  "pid": 1683,
  "kind": "hermes-gateway",
  "gateway_state": "running",
  "active_agents": 0,
  "platforms": {
    "api_server": {
      "state": "connected",
      "error_code": null,
      "error_message": null
    },
    "telegram": {
      "state": "connected",
      "error_code": null,
      "error_message": null
    }
  }
}
```

## channel_directory.json Structure

```json
{
  "updated_at": "2026-05-14T08:41:29",
  "platforms": {
    "telegram": [{"id": "6494314827", "name": "User Name", "type": "dm"}],
    "discord": [],
    "slack": [],
    ...
  }
}
```

## Gateway Not Listed in Config

There is **no** top-level `gateway:` key in `config.yaml`. Gateway settings (platforms, channels, timeouts) are spread across multiple sections:
- `agent.gateway_timeout`, `agent.gateway_timeout_warning`, `agent.gateway_auto_continue_freshness`
- `platforms:` section (api_server, etc.)
- `telegram:` section (when Telegram is configured)
- Per-platform `allowed_channels`, `channel_prompts`, `free_response_channels` under the platform block

## Troubleshooting

### "Gateway shows off / no messages"
1. Press **r** to refresh the TUI
2. Check Panel 1 for gateway status (● = running)
3. Check Panel 8 (logs) for recent activity
4. Verify gateway process exists: `ps aux | grep "gateway run" | grep -v grep`
5. Check `gateway_state.json` for platform connection states
6. Check `gateway.log` for inbound messages and errors
7. Verify the gateway launchd plist is loaded: `hermes gateway status`

### hermesd shows stale data
The TUI refreshes on the interval set by `--refresh-rate` (default 5s). If data seems old, wait for the next refresh cycle or press **r**.

### Gateway exits with exit code 9
Exit code 9 = SIGKILL. Common causes:
- launchd OnDemand killed the process due to idle timeout
- macOS memory pressure terminated it
- Another process (dual gateway conflict) sent a kill signal
