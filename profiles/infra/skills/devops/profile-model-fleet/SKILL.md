---
name: profile-model-fleet
description: Current model assignments for all Hermes profiles across multi-provider fleet (Nous + Xiaomi + DeepSeek), with pricing, reasoning_effort, and swarm role mapping. Use this to re-apply after resets or to audit profile-level model configs.
version: 3.1.0
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

## Profile → Model Map (as of 2026-05-27)

### Senna (default chat session)
| | |
|---|---|
| **Model** | `mimo-v2.5-pro` |
| **Provider** | `xiaomi` |
| **Base URL** | `https://token-plan-sgp.xiaomimimo.com/v1` |

### Oracle (market intelligence)
| | |
|---|---|
| **Model** | `deepseek-v4-pro` |
| **Provider** | `deepseek` |
| **Base URL** | `https://api.deepseek.com` |

> **NOTE (2026-05-27):** Researcher was briefly switched to xiaomi/mimo-v2.5-pro due to missing `DEEPSEEK_API_KEY` in its profile `.env`. Key was copied from root `.env`, researcher switched back to deepseek-v4-pro with `reasoning_effort: high`.

### Tier 1 — Lightweight (Xiaomi + OpenRouter, reasoning: none)
Fast, cheap workers for routing, triage, light tasks.
| Profile | Provider | Model | Role |
|---|---|---|---|
| **Foreman** | xiaomi | mimo-v2.5-pro | Swarm orchestrator — decomposes tasks, routes to specialists |
| **Secretary** | openrouter | owl-alpha | Inbox triage, docs, writing |
| **DevOps** | nous | deepseek-v4-flash:free | Ops health checks, dependency updates |
| **Data Analyst** | nous | deepseek-v4-flash:free | Light data queries |

**Deleted (2026-05-27):** council, explorer, librarian — generic boilerplate, no custom SOUL, no Discord bots.

### Tier 2 — Paid Heavy Lifters (Xiaomi MiMo v2.5 Pro)
| Profile | Reasoning | Role |
|---|---|---|
| **Coder** | `high` | Implementation — builds features, fixes bugs, writes tests |
| **Reviewer** | `xhigh` | Code review gate — blocks unsafe/untested work before merge |
| **Architect** | `high` | Structural design, architecture decisions, module planning |
| **Security** | `high` | Security audits, vulnerability assessment |
| **Debugger** | `high` | Root cause analysis, systematic debugging |

### Tier 3 — DeepSeek Direct (deepseek-v4-pro)
Premium reasoning via DeepSeek API. Best quality for research, analysis, and code generation.
| Profile | Provider | Model | Reasoning | Role |
|---|---|---|---|---|
| **Oracle** | deepseek | deepseek-v4-pro | `high` | Market intelligence, trading research, analysis |
| **Researcher** | deepseek | deepseek-v4-pro | `high` | Deep research, source synthesis, investigation |
| **Designer** | openrouter | deepseek/deepseek-chat-v3-0324 | `high` | UI/graphics/image generation — routed via OpenRouter (no DEEPSEEK_API_KEY set) |

### Model Selection Guide

When choosing a model for a new profile, match to the work type:

| Work type | Best model | Why |
|---|---|---|
| **Conversation / routing / triage** | mimo-v2.5-pro (xiaomi) | Cheapest, good enough for decisions |
| **Code generation** (HTML/CSS, JS, shaders, templates) | deepseek-v4-pro | Strongest at code output |
| **Deep reasoning** (research, analysis, strategy) | deepseek-v4-pro | Best reasoning quality |
| **Text / knowledge work** (writing, docs, curation) | owl-alpha (openrouter) | Good prose, knowledge retrieval |
| **Lightweight checks** (smoke tests, quick lookups) | deepseek-v4-flash:free (nous) | Free tier, fast |

**Rule of thumb:** If the profile generates code (even HTML/CSS for UI), use deepseek-v4-pro. If it routes or triages, use mimo. If it writes prose, use owl-alpha.

## Config templates

Xiaomi:
```yaml
model:
  provider: xiaomi
  default: xiaomi/mimo-v2.5-pro
  base_url: https://token-plan-sgp.xiaomimimo.com/v1
```

DeepSeek Direct:
```yaml
model:
  provider: deepseek
  default: deepseek-v4-pro
  base_url: https://api.deepseek.com
```

DeepSeek via OpenRouter (no DEEPSEEK_API_KEY needed):
```yaml
model:
  provider: openrouter
  default: deepseek/deepseek-chat-v3-0324
```

Nous free tier:
```yaml
model:
  provider: nous
  default: deepseek/deepseek-v4-flash:free
  base_url: https://inference-api.nousresearch.com/v1
```

## Reasoning Effort Map

| Level | Profiles | When to use |
|---|---|---|
| `none` | foreman, explorer, secretary, librarian, devops, data-analyst | Routing, triage, lookups |
| `high` | coder, architect, security, debugger | Deep reasoning — implementation, design |
| `high` | oracle, researcher, designer | Deep reasoning via DeepSeek direct — research, analysis, code generation |
| `xhigh` | reviewer, council | Maximum depth — gatekeeping, strategy |

## Notes

- **Each profile needs its own API keys in its own `.env`** — profiles do NOT inherit from root `~/.hermes/.env`. Root `.env` is only read by processes that resolve to the default profile (senna). All other profiles must have the relevant key in `~/.hermes/profiles/<name>/.env`.
- **OpenRouter as aggregator fallback**: If a profile's direct provider key is missing (e.g. DEEPSEEK_API_KEY), switch to OpenRouter with `provider/model` format instead of adding a new key. Designer uses this pattern. Verify current model IDs at openrouter.ai/models before committing.
- Xiaomi credentials: `XIAOMI_API_KEY` in each profile's `.env`. Check with `grep "XIAOMI_API_KEY" ~/.hermes/profiles/<name>/.env`.
- DeepSeek credentials: `DEEPSEEK_API_KEY` in each profile's `.env`.
- OpenRouter credentials: `OPENROUTER_API_KEY` in each profile's `.env`.
- **Model name format**: Always use `provider/model` format (e.g. `xiaomi/mimo-v2.5-pro`, `deepseek/deepseek-v4-pro`). Bare model names like `mimo-v2.5-pro` may work but the provider prefix is the canonical form.
- The `:free` suffix on deepseek v4 flash maps to Nous Portal's free-tier endpoint.
- User explicitly avoids deepseek-r1-0528.
- Senna stays on xiaomi/mimo — user has 1B MiMo tokens, reasonable for session profile.
- Oracle and Researcher use DeepSeek v4 Pro directly for best reasoning quality.
- Always verify with actual config: `grep -A5 "^model:" ~/.hermes/profiles/<name>/config.yaml`
- See `references/profile-key-inheritance.md` for the full explanation of why profiles don't inherit root `.env` keys.
