# Environment Key Distribution — 21-Profile Fleet

## The Only 5 Keys Needed

All other services are either Nous-subscription-managed (FAL, Browserbase, TTS, Whisper, Firecrawl), internal to Hermes (fabric, memory, kanban), or run locally (ComfyUI, Blender, Ollama, Obsidian).

### XIAOMI_API_KEY (same key, 15 profiles)
```
XIAOMI_API_KEY=<user fills in>
XIAOMI_BASE_URL=https://token-plan-sgp.xiaomimimo.com/v1
```
Profiles: senna, code, creative, research, finance, infra, security, ue5, mlops, cyber-red, cyber-blue, cyber-blue-cloud, cyber-blue-forensics, cyber-blue-compliance, cyber-blue-soc

### OPENROUTER_API_KEY (same key, 6 profiles)
```
OPENROUTER_API_KEY=<user fills in>
```
Profiles: knowledge, business, media, homelab, social, communication

### DISCORD_BOT_TOKEN (unique per bot, 8 profiles)
```
DISCORD_BOT_TOKEN=<unique per bot>
DISCORD_ALLOWED_USERS=<user's Discord ID>
```
| Profile | Channel |
|---------|---------|
| senna | #your-orchestrator-channel |
| code | #engineering |
| creative | #design-studio |
| research | #research-lab |
| finance | #market-intel |
| knowledge | #writing-desk |
| infra | #operations |
| security | #security-ops |

## Template File Location
`~/Documents/template.env` — user fills in values, then distribute to `~/.hermes/profiles/<name>/.env`

## Audit Methodology (how this was determined)
1. Read `config.yaml` → `platform_toolsets.cli` for each profile
2. Mapped toolsets to external service requirements
3. Verified that builtin skill file references (Linear, Notion, HuggingFace, W&B, etc.) are NOT active toolsets — they're just catalog skills that Hermes loads by default
4. Confirmed Nous subscription covers: image_gen (FAL), browser (Browserbase), TTS, Whisper, Firecrawl
5. Confirmed internal tools need no keys: fabric, memory, kanban, delegation, todo, session_search, cronjob

## Pitfalls
- **Don't trust skill file references for key requirements.** A profile with 84 builtin skills will reference dozens of services (Linear, Notion, HuggingFace, W&B, Together, Anthropic, OpenAI) that it never actually uses. The configured toolsets in config.yaml are the source of truth.
- **XIAOMI_BASE_URL is non-standard.** It's not the usual Xiaomi endpoint — it's `https://token-plan-sgp.xiaomimimo.com/v1`. Always include it alongside the API key.
- **Discord tokens are per-bot, not shared.** Each of the 8 Discord bot profiles needs its own unique token from the Discord Developer Portal. The other keys (Xiaomi, OpenRouter) are shared across their respective profile groups.
- **DISCORD_ALLOWED_USERS is the same value** across all 8 Discord profiles — it's the user's Discord user ID.
