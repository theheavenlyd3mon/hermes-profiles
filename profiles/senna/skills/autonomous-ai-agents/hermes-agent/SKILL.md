---
name: hermes-agent
description: Configure, extend, or contribute to Hermes Agent itself — its CLI, config, models, providers, tools, skills, voice, gateway, plugins, or any feature.
triggers:
  - "configure hermes"
  - "hermes config"
  - "hermes setup"
  - "hermes model"
  - "hermes tools"
  - "hermes plugins"
  - "hermes gateway"
  - "hermes skill"
  - "hermes profile"
  - "hermesd"
  - "nous portal"
  - "auxiliary vision"
  - "auxiliary.vision"
  - "monitor"
  - "dashboard"
  - "tui"
  - "hermes plugin"
  - "plugin development"
version: 1.0.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development, plugins, plugin-development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

## Conceptual Overview (for non-developers)

This section explains how Hermes works *conceptually* — skip it if you already know what a background service or long-polling bot is.

**The core idea:** Hermes has two modes of operation:

1. **Terminal/CLI chat** — you open a terminal, type `hermes`, and we talk directly. You see everything as it happens. This is the default and does NOT require the gateway.
2. **Messaging platforms** — Telegram, Discord, Slack, WhatsApp, etc. These require the **gateway**, which is a background process that waits for messages to arrive and routes them to the agent.

The gateway is like a **phone line** installed at your house. The terminal is like walking into the shop and talking face-to-face. You don't need the phone on when you're already at the front counter. But if you want people to reach you from elsewhere (Telegram messages, etc.), you leave the phone on.

**Does the gateway need to stay on always?** Only if you want those platforms to answer immediately. The gateway runs as a background process — once started, it stays alive on its own. It uses negligible resources on a modern machine.

**Which profile's gateway?** Each profile has its own gateway. They are independent. If you set up Telegram under Senna, you must start `hermes --profile senna gateway start`.

```bash
grep TELEGRAM_BOT_TOKEN ~/.hermes/profiles/senna/.env    # token exists here?
grep TELEGRAM_BOT_TOKEN ~/.hermes/.env                     # or here (root)?
hermes gateway status                                       # which profile's gateway is running?
hermes profile list                                         # see all profiles + gateway state
```

What makes Hermes different:

- **Self-improving through skills** — saves reusable procedures as skills that load into future sessions
- **Persistent memory across sessions** — remembers who you are, preferences, environment details
- **Multi-platform gateway** — Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, 10+ others
- **Provider-agnostic** — swap models/providers mid-workflow; credential pools rotate across API keys
- **Profiles** — independent instances with isolated configs, sessions, skills, and memory
- **Extensible** — plugins, MCP servers, custom tools, webhooks, cron scheduling

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              Root-level API keys and secrets (all profiles)
~/.hermes/profiles/<name>/.env  Profile-specific keys (overrides root)
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools (PER-PROFILE)
~/.hermes/hermes-agent/     Source code (if git-installed)
```

**auth.json vs auth.lock:** `auth.json` has the actual credential pool data. `auth.lock` is just a concurrency lock (0 bytes). A profile with only `auth.lock` and no `auth.json` has an empty credential pool.

**.env loading order:** Root `.env` loads first (global defaults), then profile `.env` (overrides matching keys). See `references/env-architecture.md` for the full guide.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

**Multi-model hierarchy:** Hermes supports separate model slots for primary conversation, fallback providers, auxiliary tasks (vision, compression, session search), subagent delegation, and per-session overrides. See `references/model-hierarchy.md` for details.

**Mixture of Agents (native):** `moa` is a virtual provider — named presets in `config.yaml` under `moa.presets` (reference_models + aggregator, explicit provider/model pairs). Presets appear in every model picker (`/model <preset> --provider moa`, `hermes model`, Dashboard, Desktop). `/moa <prompt>` = one-shot through the default preset. Tunables: `reference_max_tokens` (cap advisor output, ~600 for speed), `fanout` (`user_turn` default/cheapest, `per_iteration`, `every_n:N`), per-slot `reasoning_effort`, `privacy_filter`. Reference failures degrade gracefully (turn continues). Aggregator cannot be another preset. CLI: `hermes moa list|configure [name]|delete <name>`. Docs: `website/docs/user-guide/features/mixture-of-agents.md`.

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth add nous --type oauth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

> **Per-profile credential isolation:** Each profile has its own `auth.json`. See `references/auth-symlink-pattern.md` for the symlink pattern.

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed. See `references/stt-setup-quickstart.md` for exact setup commands.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

**`/voice on` vs `/voice tts`:**
- `/voice tts` — TTS only. Agent speaks its replies. You still type.
- `/voice on` — bidirectional. You speak (STT), agent speaks back (TTS).
- Both require `/reset` (CLI) or `/restart` (gateway) after changing config.

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

---

## Spawning Additional Hermes Instances

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

```bash
# One-shot mode
hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'

# Background for long tasks
hermes chat -q 'Set up CI/CD for ~/myapp' &
```

For interactive PTY spawning (tmux), multi-agent coordination, and session resume, see `references/spawning-details.md`.

---

## Quick Troubleshooting

**Gateway shows 1 platform but Telegram won't connect:**
The gateway reads `.env` from the profile dir, not root. Add vars to profile `.env` and restart.
See `references/troubleshooting.md` → "Gateway Telegram not connecting" for full diagnosis.

**Tool not available:**
1. `hermes tools` — check if toolset is enabled
2. Some tools need env vars in `.env`
3. `/reset` after enabling tools

**Model/provider issues:**
1. `hermes doctor` — check config
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. HTTP 404 "Model not found" — verify the provider hosts that model

**Changes not taking effect:**
- Tools/skills: `/reset` starts a new session
- Config: Gateway → `/restart`. CLI → exit and relaunch.
- Code changes: restart the process

**`/new` freezes or creates a 0-message session:**
See `references/session-new-freeze-deadlock.md` — known issue with session-transition deadlock.

For the full troubleshooting guide (voice, plugins, env corruption, platform-specific issues, etc.), see `references/troubleshooting.md`.

---

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session — see `references/slash-commands.md` |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` — see `references/cli-reference.md` |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |

---

## Reference Files (load on demand)

These detailed guides are available via `skill_view(name='hermes-agent', file_path='references/<file>')`:

| File | What's in it |
|------|-------------|
| `cli-reference.md` | Full CLI commands and flags (chat, config, tools, skills, mcp, gateway, sessions, cron, webhooks, profiles, auth) |
| `slash-commands.md` | All in-session slash commands |
| `browser-automation.md` | Browser tool setup, Browserbase config, real-time viewing |
| `lsp-diagnostics.md` | LSP semantic diagnostics, supported languages, npm security |
| `security-toggles.md` | Secret redaction, PII filtering, command approval, shell hooks |
| `spawning-details.md` | Interactive PTY (tmux), multi-agent coordination, session resume |
| `local-optimization.md` | Service stack health, gateway alignment, hermesd |
| `troubleshooting.md` | Full troubleshooting: voice, plugins, env corruption, platform issues |
| `contributor-guide.md` | Project layout, adding tools/commands, testing, commit conventions |
| `env-architecture.md` | .env loading order, consolidation, audit checklist |
| `model-hierarchy.md` | Multi-model slots, fallback chains, auxiliary config |
| `auth-symlink-pattern.md` | Cross-profile credential sharing via symlinks |
| `stt-setup-quickstart.md` | Zero-to-working STT setup (Groq or local faster-whisper) |
| `session-new-freeze-deadlock.md` | `/new` freeze diagnosis and fix |
| `memory-provider-setup.md` | Installing pip-based memory providers into Hermes venv |
| `plugin-development.md` | Plugin authoring guide |
| `plugin-authoring-pattern.md` | Plugin patterns and conventions |
| `image-generation-providers.md` | Image gen provider setup (FAL, OpenAI, etc.) |
| `cron-automation-patterns.md` | Cron job design patterns |
| `team-profile-config-management.md` | Multi-profile config management |
| `service-stack-health.md` | Verifying all Hermes services are healthy |
| `mnemosyne-consolidation-cron.md` | Mnemosyne memory consolidation setup |
| `iknowkungfu-integration.md` | Skill registry integration |
| `third-party-frontends.md` | Open WebUI, LibreChat, and other frontend integrations |
| `capability-inventory-audit.md` | Full capability audit checklist |
| `comprehensive-health-audit.md` | Deep health audit procedure |
| `post-update-plugin-verification.md` | Plugin verification after updates |
| `system-audit-pattern.md` | Systematic audit methodology |

---
