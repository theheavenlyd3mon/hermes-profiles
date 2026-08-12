---
name: hermes-feature-education
description: Educate users on Hermes Agent features they may not know about — feature discovery, organized walkthroughs, CLI reference, system capabilities, and depth progression. Use when a user asks "teach me hermes features", "what can you do", "what features am I not using", or similar onboarding/feature-discovery questions.
triggers:
  - "teach me about hermes"
  - "what features do you have"
  - "what am i not using"
  - "educate me on hermes"
  - "how do i use [feature]"
  - "what is [hermes feature]"
  - "walk me through hermes"
  - "hermes feature overview"
  - "explain [acp/eikons/lsp/cron/webhooks/etc]"
  - "hermes onboarding"
  - "tell me everything hermes can do"
  - "what's new that i should know about"
  - "i dont use [feature]"
  - "show me around hermes"
version: 1.0.0
author: Senna (from user feature-education session)
---
# Hermes Feature Education

Guide users through Hermes Agent's capabilities — from the features they already use to the ones they've never seen. This is onboarding and feature discovery, not configuration or setup (those go in `hermes-agent` skill).

## Identity

Educator.Discoverer. Start where the user is: assess what they know, then reveal what they don't. Structured, categorized, depth-progressive. Never dump everything at once — give an overview, then dig deeper where they ask.

## Core Principles

1. **Start with version context** — `hermes --version` tells you what's available
2. **Categorize features** — users absorb structured information faster than flat lists
3. **Depth progression** — overview first, then deep dive on request ("go more in depth on...")
4. **Prefer show-don't-tell** — show actual tool output (`hermes lsp status`, `eikon_list`, `hermes sessions stats`) rather than describing capabilities
5. **End with actionable recommendations** — "Try X first, then Y, then Z"

## Feature Categories

Organize Hermes capabilities into these buckets when educating:

### A. Session & Chat Control (slash commands)
- `/new`, `/retry`, `/undo` (basic)
- `/compress`, `/rollback`, `/background`, `/queue`, `/resume` (power user)
- `/model`, `/personality`, `/reasoning`, `/voice`, `/yolo`, `/skin` (config on the fly)
- `/branch`, `/fast`, `/insights` (utility)

### B. CLI Commands (outside session)
- `hermes chat -q` — one-shot queries
- `hermes config`, `hermes model` — config
- `hermes setup` — interactive wizards
- `hermes doctor`, `hermes status` — health
- `hermes sessions` — list, browse, prune, stats
- `hermes cron` — scheduled tasks
- `hermes webhook` — HTTP callbacks
- `hermes acp` — ACP server (IDE integration)

### C. Tools & Capabilities (in-session toolset)
- `delegate_task` — background subagents
- `cronjob` — schedule recurring tasks
- `execute_code` — sandboxed Python
- `vision_analyze`, `image_generate`, `text_to_speech`
- `memory` / `mnemosyne_*` — persistent memory
- `skill_manage` / `skill_view` / `skills_list`
- Web search, browser, file tools

### D. Gateway & Messaging
- Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, DingTalk, Feishu, WeCom, Weixin, BlueBubbles, Home Assistant, Teams, Google Chat (20+)
- `hermes gateway run/start/stop/status/setup`
- `/approve`, `/deny`, `/sethome`, `/platforms` — gateway slash commands

### E. Profiles
- `hermes profile list/create/use/delete/rename/export/import`
- Per-profile isolation: config, sessions, memory, skills, auth
- `hermes auth add/list/remove` — credential pools per profile

### F. Advanced Features (most likely unknown)
- **LSP (Language Server Protocol)** — semantic diagnostics on every write
- **Eikons** — animated ASCII art TUI avatars
- **ACP (Agent Communication Protocol)** — interop with Copilot/Codex/Claude Code
- **Webhooks** — HTTP POST listeners on the gateway
- **Session checkpoints** — workspace rollback with `/rollback`
- **Credential pools** — multiple API keys per provider, auto-rotation
- **MCP (Model Context Protocol)** — external server integration
- **NO_AGENT cron** — script-only scheduled jobs, zero LLM cost
- **SOUL.md** — identity/personality file loaded from `HERMES_HOME/SOUL.md` only
- **AGENTS.md** — project context files with progressive subdirectory discovery
- **Personalities** — 15+ built-in + custom via config
- **Context files** — .hermes.md, AGENTS.md, CLAUDE.md, .cursorrules auto-detection
- **Default profile** — `hermes profile use <name>` sets which profile loads on bare `hermes`

## SOUL.md Architecture (common confusion)

This is the most common conceptual gap. Clarify it explicitly:

### Default / No Profile
- `HERMES_HOME` = `~/.hermes/`
- Loads `~/.hermes/SOUL.md`
- This is the "root" identity — used when no `-p` flag or `hermes profile use default`

### Profile Active (e.g. `hermes -p senna`)
- `_apply_profile_override()` sets `HERMES_HOME` = `~/.hermes/profiles/senna/`
- `load_soul_md()` reads from `$HERMES_HOME/SOUL.md` → resolves to `~/.hermes/profiles/senna/SOUL.md`
- **Per-profile SOUL.md IS auto-loaded** — the profile directory's SOUL.md becomes the identity

### Both Levels Coexist
- `~/.hermes/SOUL.md` — identity when running as default profile
- `~/.hermes/profiles/<name>/SOUL.md` — identity when that profile is active
- They are **separate files** in **separate directories**. Same content is coincidence, not coupling.

### Impact of Missing SOUL.md
If `$HERMES_HOME/SOUL.md` doesn't exist, Hermes falls back to the built-in default identity ("You are Hermes Agent, an intelligent AI assistant..."). This means:
- A profile without a SOUL.md will use the fallback identity
- `hermes profile create` auto-seeds a template SOUL.md to prevent this

## Plugin Systems (common confusion)

Hermes has TWO plugin systems; users routinely conflate them. A user saying "I have plugins installed" almost always means AGENT plugins — check `~/.hermes/desktop-plugins/` before claiming any desktop plugins exist.

| | Agent plugins | Desktop plugins |
|---|---|---|
| Adds | tools, hooks, slash commands, backends | UI: panes, statusbar chips, palette commands, pages, keybinds, themes |
| Format | Python + `plugin.yaml` manifest | plain JS ESM (`plugin.js`) |
| Path | `~/.hermes/plugins/<name>/` | `~/.hermes/desktop-plugins/<name>/` |
| Loader | agent runtime | the desktop app (hot-reloads on save) |
| Enable | `plugins.enabled` in config.yaml | Settings → Plugins, or `defaultEnabled: false` opt-in |

Full taxonomy + ground-truth inventory workflow: `references/plugin-systems-and-inventory.md`

When the user asks which of THEIR plugins could become desktop surfaces (or "what can I see on desktop"), run the conversion audit: `references/desktop-plugin-conversion-audit.md` — the two data doors (`ctx.rest` vs `host.request`), the bundled-Kanban finding (desktop app ships one, off by default — never rebuild it from `kanban-api`), and the tiered fleet assessment. Lead with surfaces that SHOW things (user is visual-first).

## Discovery Workflow

### Step 1 — Establish baseline
```bash
hermes --version
```
This tells you what version they're on and what features exist.

### Step 2 — Check what they already use
Ask or infer from context. In this session the user said "i honestly dont use alot of the features" — wide-open education.

### Step 3 — Categorized overview
Present the categories above. List features under each, one line per feature. Use emoji prefixes for scannability.

### Step 4 — Deep dive on request
When the user says "go more in depth on X", do:
1. Load relevant reference file if it exists (`references/hermes-feature-catalog.md`)
2. Show real tool output (`hermes lsp status`, `hermes sessions stats`, `eikon_list`)
3. Explain what it is, how it works, and what they gain from using it
4. Offer to set it up or walk through it right now

### Step 5 — Recommend next actions
Pick 3-5 concrete things they should try now. Order by immediate value:
- Session prune if they have 500+ sessions (reclaims disk)
- SOUL.md if they haven't customized it
- LSP if they write code
- Cron if they have recurring tasks
- Eikons for fun/cosmetic

## Pitfalls

- **Don't dump everything at once** — categorize and let the user pick depth
- **Don't describe capabilities without showing real output** — run the actual commands
- **Don't skip version context** — features that exist in latest may not be in their install
- **Don't conflate "new" with "unknown"** — a feature may have existed for releases but the user just never used it
- **Don't assume they know CLI from slash commands** — explain the difference
- **Bundled skills vs installed skills** — `hermes-agent` is bundled/protected; user-created skills are editable
- **Slash commands work in both CLI and gateway** — but some are CLI-only (marked in reference)

## Reference Files

- `references/hermes-feature-catalog.md` — full feature catalog for deep-dive education
- `references/plugin-systems-and-inventory.md` — agent vs desktop plugin taxonomy + inventory workflow (config allow-list is ground truth)
- `references/desktop-plugin-conversion-audit.md` — which installed agent plugins can become desktop surfaces (data doors, bundled-Kanban finding, tiered fleet assessment)
- `references/hermes-skill-ecosystem.md` — skill sourcing model: builtin vs created vs installed, cross-machine profile replication

## Related Skills

- `hermes-agent` — configuration, setup, providers, tools (loaded when the user asks to configure, not when they ask to learn)
- `hermes-version-summary` — what's new / release notes
- `hermes-soul-authoring` — writing SOUL.md
- `hermes-skin-authoring` — TUI skins
- `hermes-image-generation` — image gen setup
