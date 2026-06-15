---
name: profile-model-fleet
description: Current model assignments for all Hermes profiles across multi-provider fleet (Nous + Xiaomi + DeepSeek), with pricing, reasoning_effort, and swarm role mapping. Use this to re-apply after resets or to audit profile-level model configs.
version: 4.0.0
platforms: [macos, linux]
triggers: [profile model, model assignment, profile fleet, nous provider models, xiaomi provider models, deepseek provider models, profile config model, swarm organization]
metadata:
  hermes:
    tags: [profile, model, nous, xiaomi, deepseek, config, pricing, fleet, swarm]
    related: [foreman-orchestration, kanban-orchestrator, hermes-companion-apps]
---

# Profile Model Fleet — Three-Provider Assignments

The fleet uses three providers:
- **Xiaomi MiMo** (`provider: xiaomi`, `base_url: https://token-plan-sgp.xiaomimimo.com/v1`) — primary heavy lifter, 1B token giveaway
- **DeepSeek Direct** (`provider: deepseek`, `base_url: https://api.deepseek.com`) — premium reasoning for research/market analysis
- **Nous Portal** (`provider: nous`, `base_url: https://inference-api.nousresearch.com/v1`) — free tier for lightweight workers (deepseek-v4-flash:free)
- **OpenRouter** (`provider: openrouter`) — used by secretary for owl-alpha

## Profile → Model Map (as of 2026-06-13)

### Three-Provider Fleet (updated)
- **Xiaomi MiMo** (`provider: xiaomi`, `base_url: https://token-plan-sgp.xiaomimimo.com/v1`) — primary for user-facing and heavy profiles
- **OpenRouter** (`provider: openrouter`, `base_url: https://openrouter.ai/api/v1`) — free tier models for lightweight workers
- **Nous Portal** (`provider: nous`, `base_url: https://inference-api.nousresearch.com/v1`) — legacy, no longer primary

### Domain-Based Profile Map (17 profiles, June 2026)

#### Tier 1 — Xiaomi MiMo v2.5 (user-facing Discord bots + heavy workers)
| Profile | Reasoning | Channel | Role |
|---------|-----------|---------|------|
| **senna** | — | #nexus-hq | Coordinator, front door, fleet management |
| **code** | high | #engineering | All coding — merged coder + debugger + reviewer |
| **creative** | — | #design-studio | Design, visual art, image gen, UI/UX |
| **research** | high | #research-lab | Investigation, data gathering, analysis |
| **finance** | high | #market-intel | Trading, market analysis (renamed oracle) |
| **infra** | — | #operations | DevOps, deployment, networking (renamed devops) |
| **security** | high | #security-ops | Security audits, vulnerability management |
| **ue5** | high | — (Kanban only) | Unreal Engine 5 development |
| **mlops** | high | — (Kanban only) | ML training, fine-tuning, inference |
| **cyber-red** | xiaomi/mimo-v2.5 | high | Offensive security (~160 skills) |
| **cyber-blue** | — | — | Coordinator → delegates to sub-profiles |
| **cyber-blue-cloud** | xiaomi/mimo-v2.5 | high | Cloud security (~123 skills) |
| **cyber-blue-forensics** | xiaomi/mimo-v2.5 | high | Forensics + threat intel (~35 skills) |
| **cyber-blue-compliance** | xiaomi/mimo-v2.5 | high | Compliance + IAM (~22 skills) |
| **cyber-blue-soc** | xiaomi/mimo-v2.5 | high | SOC + network + IR (~371 skills) |

#### Tier 2 — OpenRouter Free: Owl Alpha (text/knowledge workers)
| Profile | Channel | Role |
|---------|---------|------|
| **knowledge** | #writing-desk | Obsidian vault, documentation, wiki (renamed secretary) |
| **business** | — (Kanban only) | Strategy, marketing, product |
| **social** | — (Kanban only) | Social media, content creation |

#### Tier 3 — OpenRouter Free: DeepSeek V4 Flash (lightweight automations)
| Profile | Channel | Role |
|---------|---------|------|
| **media** | — (Kanban only) | *arr stack, music, gaming |
| **homelab** | — (Kanban only) | Smart home, IoT |
| **communication** | — (Kanban only) | Email, messaging |

### Model Selection Guide (updated)

| Work type | Best model | Why |
|-----------|-----------|-----|
| **User-facing conversation** | mimo-v2.5 (xiaomi) | Good quality, user has 1B tokens |
| **Code generation / deep reasoning** | mimo-v2.5 (xiaomi) + reasoning_effort: high | Best quality for implementation |
| **Text / knowledge work** | owl-alpha:free (openrouter) | Good prose, 1M context, free |
| **Lightweight checks / automations** | deepseek-v4-flash:free (openrouter) | Free, fast, good enough |
| **ML training / inference** | mimo-v2.5 (xiaomi) + reasoning_effort: high | Complex reasoning needed |

**Key change (June 2026):** Nous Portal free tier (deepseek-v4-flash:free) is no longer available. All free-tier models route through OpenRouter instead. OpenRouter has 26 free models including Owl Alpha (1M context, tools) and DeepSeek V4 Flash.

**Rule of thumb:** mimo-v2.5 for anything user-facing or heavy. Owl Alpha for text/knowledge. DeepSeek V4 Flash for lightweight automations. All OpenRouter free models have rate limits (20 req/min, 200 req/day).

## Config templates

Xiaomi (mimo-v2.5):
```yaml
model:
  provider: xiaomi
  default: xiaomi/mimo-v2.5
  base_url: https://token-plan-sgp.xiaomimimo.com/v1
```

OpenRouter free — Owl Alpha:
```yaml
model:
  provider: openrouter
  default: openrouter/owl-alpha:free
  base_url: https://openrouter.ai/api/v1
```

OpenRouter free — DeepSeek V4 Flash:
```yaml
model:
  provider: openrouter
  default: openrouter/deepseek/deepseek-v4-flash:free
  base_url: https://openrouter.ai/api/v1
```

DeepSeek Direct (paid):
```yaml
model:
  provider: deepseek
  default: deepseek-v4-pro
  base_url: https://api.deepseek.com
```

Nous Portal (legacy):
```yaml
model:
  provider: nous
  default: deepseek/deepseek-v4-flash:free
  base_url: https://inference-api.nousresearch.com/v1
```

## Reasoning Effort Map (updated June 2026)

| Level | Profiles | When to use |
|---|---|---|
| `none` | senna, creative, knowledge, infra, business, media, homelab, social, communication | Routing, triage, text work, light automation |
| `high` | code, research, finance, security, ue5, mlops, cyber-red, cyber-blue | Deep reasoning — implementation, analysis, security |

**Note:** No profiles use `xhigh` in the new design. The old reviewer/council profiles that needed xhigh were merged into code or removed.

## Notes

- **Each profile needs its own API keys in its own `.env`** — profiles do NOT inherit from root `~/.hermes/.env`. Root `.env` is only read by processes that resolve to the default profile (senna). All other profiles must have the relevant key in `~/.hermes/profiles/<name>/.env`.
- **Hermes internal secrets store.** API keys can also be stored in Hermes' internal config (via `hermes config set` or the setup wizard). These are visible via `hermes config show` but not readable as plaintext. Profiles may access these keys without .env files — verify with a smoke test.
- **Nous Portal free tier (deepseek-v4-flash:free) is no longer available (as of June 2026).** Use OpenRouter free models instead. OpenRouter has 26 free models including Owl Alpha and DeepSeek V4 Flash.
- **OpenRouter free models have rate limits:** 20 requests/minute, 200 requests/day per model. Fine for workers, risky for high-frequency cron jobs.
- **Xiaomi model name:** Use `xiaomi/mimo-v2.5` (not `mimo-v2.5-pro` unless specifically needed). Verify model ID with `hermes config show` after setting.
- **Xiaomi base URL is non-standard:** `https://token-plan-sgp.xiaomimimo.com/v1` — not the default Xiaomi API. Always include in config.yaml.
- **DeepSeek Direct requires DEEPSEEK_API_KEY.** If missing, fall back to OpenRouter with `provider/model` format.
- **Model name format**: Always use `provider/model` format (e.g. `xiaomi/mimo-v2.5`, `openrouter/owl-alpha:free`). Bare model names may work but the provider prefix is the canonical form.
