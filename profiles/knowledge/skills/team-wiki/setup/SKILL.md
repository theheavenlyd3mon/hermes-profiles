---
name: team-wiki/setup
description: Bootstrap Team-Wiki directory with SCHEMA.md, index.md, log.md, and folder READMEs
version: 1.0.0
author: Hermes Agent Team
license: MIT
metadata:
  hermes:
    tags: [team-wiki, setup, bootstrap, gbrain]
    related_skills: [team-wiki/sync, team-wiki/maintain, team-wiki/ingest, llm-wiki]
---

# Team-Wiki Setup

Initializes the Team-Wiki shared knowledge directory structure and core files. Creates the domain-specific schema, index, log, and folder scaffolding required for GBrain sync.

## Prerequisites

- GBrain installed and initialized (`gbrain init` already run, database at `~/.hermes/shared-brain/brain.pglite`)
- Obsidian vault directory exists
- `WIKI_PATH` environment variable set (e.g., `~/Hermes Vault/Hermes/Team-Wiki`)
- User has confirmed Team-Wiki is separate from personal PARA vault

## What This Does

Creates the following structure under `WIKI_PATH`:

```
Team-Wiki/
├── SCHEMA.md          # Domain conventions, tag taxonomy, page types
├── index.md           # Alphabetical catalog of all entities
├── log.md             # Append-only chronological action log
├── entities/
│   ├── README.md
│   ├── agents/        (foreman, coder, architect, debugger, reviewer, secretary, researcher, devops, data-analyst, security, senna)
│   ├── people/        (andrej-karpathy, garry-tan, …)
│   ├── companies/     (anthropic, openai, 37signals, …)
│   └── projects/      (hermes-agent, team-wiki, hermes-workspace, …)
├── concepts/          (pglite, mitre-attack, rag, …)
├── comparisons/       (hermes-vs-swarmclaw, …)
└── queries/           (research questions & answers)
```

Writes domain-specific conventions into `SCHEMA.md` (Hermes ecosystem: agents, skills, infrastructure, companies, people, projects). Sets up tag taxonomy using `domain:item` prefixes.

## Invocation

```bash
# With WIKI_PATH set
skill:team-wiki/setup

# Or explicit path
skill:team-wiki/setup --wiki-path ~/Hermes\ Vault/Hermes/Team-Wiki
```

## Post-Setup

1. Review `SCHEMA.md` and adjust taxonomy tags to match your domain
2. Populate initial index.md with any existing known entities
3. Ensure GBrain MCP server is configured in `~/.hermes/config.yaml`
4. Run `gbrain sync --follow --repo $WIKI_PATH` to start continuous sync (or configure Hermes cron)

## Verification

- All expected directories exist under `WIKI_PATH`
- `SCHEMA.md` contains domain: Hermes agent ecosystem and tag taxonomy
- `log.md` contains initialization entry with timestamp
- `index.md` has placeholder sections matching SCHEMA categories

## Notes

- This skill is idempotent: running it twice is safe (skips existing files)
- Do NOT migrate existing PARA vault notes into Team-Wiki unless explicitly requested; they remain separate
- The schema follows `llm-wiki` patterns: MECE directories, compiled truth + timeline layers, enrichment on every signal
