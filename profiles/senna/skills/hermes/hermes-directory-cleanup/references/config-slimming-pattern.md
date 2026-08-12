# Config Slimming Pattern

## Problem
Per-profile `config.yaml` files accumulate ~754+ lines of boilerplate settings that are identical to Hermes defaults. Three bloated configs in a 22-profile setup totaled 1,626 lines with ~80% shared boilerplate. This makes audits harder, configs harder to diff, and suggests copy-paste maintenance rather than intentional configuration.

## Diagnosis — Identifying Defaults vs. Overrides

Hermes ships with sensible defaults for most settings. The following sections in a config file are almost always at their default value and can be removed:

| Section | Defaults-to-Strip Signs |
|---------|------------------------|
| `terminal` | `backend: local`, `timeout: 180`, `docker_image: nikolaik/python-nodejs:...` — all defaults unless using Docker/Modal |
| `browser` | `inactivity_timeout: 120`, `command_timeout: 30`, `engine: auto` — defaults |
| `web` | `backend: firecrawl`, `search_backend: ''` — defaults |
| `checkpoints` | `enabled: false`, `max_snapshots: 20` — disabled by default |
| `compression` | `enabled: true`, `threshold: 0.5`, `target_ratio: 0.2` — these are the Hermes defaults |
| `kanban` | `dispatch_in_gateway: true`, `failure_limit: 2` — defaults |
| `prompt_caching` | `cache_ttl: 5m`, `long_lived_prefix: true` — defaults |
| `auxiliary` | All sub-blocks (vision, web_extract, compression, curator, title_generation, etc.) — these are typical defaults. Only keep if `provider` or `model` differs from auto |
| `tts` | All sub-providers (edge, elevenlabs, openai, gemini, xai, mistral) — all defaults |
| `stt` | `enabled: true`, `provider: groq` — defaults |
| `voice` | `record_key: ctrl+b`, `max_recording_seconds: 120` — defaults |
| `display` | Most settings except `skin`, `personality`, `streaming` — defaults |
| `delegation` | All settings (`model: ''`, `provider: ''`, `max_concurrent_children: 3`) — defaults |
| `curator` | `enabled: true`, `interval_hours: 168` — defaults |
| `logging` | `level: INFO`, `max_size_mb: 5` — defaults |
| `gateway` | All sub-settings — defaults |
| `streaming` | `enabled: false`, `edit_interval: 0.8` — defaults |
| `secrets` | `bitwarden.enabled: false` — defaults |
| `platform_toolsets` | Lists of tool permissions — these are profile definitions, not config to set per-profile |
| `network`, `privacy`, `human_delay`, `context`, `memory` | All defaults |

## What to Keep

A slimmed config should contain **only** non-default values:

```yaml
# ~/.hermes/profiles/<name>/config.yaml — slimmed

model:
  default: <per-profile-model>
  provider: <per-profile-provider>
  base_url: ''              # only if non-standard

fallback_providers:
  - provider: <fallback-1>
    model: <model>
  - provider: <fallback-2>
    model: <model>

display:
  skin: <per-profile-skin>          # non-default skin
  personality: ''                   # only if set

sessions:
  auto_prune: true                  # if non-default
  retention_days: 90

discord:
  free_response_channels: '<channels>'

plugins:
  enabled:
    - plugin1
    - plugin2

mcp_servers:
  server_name:
    command: /path/to/binary
    enabled: true

custom_providers:
  - name: local-model
    base_url: http://localhost:8001/v1
    model: local-model
```

## Expected Savings

- **senna profile:** 754 lines → ~75 lines (~90% reduction)
- **security profile:** 551 lines → ~50 lines
- **maintenops profile:** 123 lines → ~20 lines
- **Aggregate:** ~1,400 lines of unnecessary boilerplate eliminated

## Verification

After slimming, verify the agent still works:
```bash
hermes --profile senna config validate 2>/dev/null || echo "Check formatting"
hermes --profile senna status 2>/dev/null  # loads config and reports status
```

## When Not to Slim

- If you use Docker/Modal/remote terminal backends, keep `terminal` section
- If you use the web dashboard, keep `dashboard` section
- If you have custom `auxiliary` model routing, keep those overrides
- If you use specific TTS/STT providers, keep those settings
