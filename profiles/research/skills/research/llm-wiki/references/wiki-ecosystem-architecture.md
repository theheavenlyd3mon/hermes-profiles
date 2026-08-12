# Wiki Ecosystem Architecture

This document describes how the persistent knowledge layer works when deployed inside a Hermes agent stack with Obsidian. It covers the pipeline from capture → curation → promotion → wiki.

## Pipeline Overview

```
Sources (web, sessions, user input, research)
         ↓
Capture (raw/ ingestion via llm-wiki skill)
         ↓
Mnemosyne (hot layer — preferences, env facts, always injected)
         ↓
Memory/Icarus (fabric entries for session-specific outcomes)
         ↓
Curation (memory-curator skill monitors Inbox + fabric-promote-review cron)
         ↓
Promotion (curator proposes, cron proposes from fabric)
         ↓
Wiki (llm-wiki pages with proper frontmatter + cross-links)
```

This pipeline is part of a **four-layer memory stack**: Mnemosyne (always-injected) → Fabric (operational) → LLM-Wiki (curated) → Obsidian (personal vault). See [memory-curator's memory-stack-architecture reference](/skills/productivity/memory-curator/references/memory-stack-architecture.md) for the full architecture, graduation pipeline, and comparison with TencentDB-Agent-Memory.

## Cron Chaining Pattern

The `context_from` field on a cron job injects the results of named jobs as context tokens. Use this to build aggregation chains:

1. Worker jobs run independently at staggered times (2am → 3am → 4am → 5am).
2. Worker jobs deliver to `origin` when the user needs to take action (e.g., fabric promotion candidates), or `local` when they're for aggregation only (lint, consolidation).
3. A single aggregator job (e.g., morning-briefing) has `context_from: [job_id1, job_id2, ...]` listing all the workers whose results should be injected.
4. The aggregator runs after all workers complete and produces one unified report to `origin`.

**Current pipeline:** overnight-wiki-research (2am, local) → memory-consolidation (3am, local) → wiki-health-check (4am, local) → fabric-promote-review (5am, origin) → morning-briefing (7am, origin, context_from: all four above).

## Memory Flow

### Inbox → Wiki Path
Items dropped into `0-Inbox/` are reviewed by the memory-curator skill. When an item has 3+ wikilinks or is tagged `concept`, it is proposed for promotion to llm-wiki. The curator never auto-promotes — user approval is required.

### Fabric → Wiki Path
Session fabric entries with `status: completed` and `training_value: high` are scanned daily by the `fabric-promote-review` cron. For each entry with no existing wiki page (checked against `index.md`), a promotion candidate is proposed with suggested section, slug, and summary.

### Unification Decision (2026-05-13)
Originally, vaults maintained separate `Team-Wiki/` (operational) and `LLM-Wiki/` (knowledge) directories. These were merged into a single wiki at `llm-wiki/` with an `operational/` subdirectory structure. The Team-Wiki/ archive lives at `4-Archive/Team-Wiki-archive/`.

## Wiki Sections (post-merge)

```
llm-wiki/
├── entities/        # People, orgs, products, models
├── concepts/        # Concepts, techniques, paradigms
├── comparisons/     # Side-by-side analyses
├── queries/         # Filed research answers
├── alloys/          # Synthesized narratives from multiple pages
├── operational/     # How the agent system works
│   ├── agents/      # Per-agent scratch spaces (transient)
│   ├── protocols/   # Handoff rules, kanban workflow
│   ├── conventions/ # Standards, style guides
│   └── decisions/   # Architectural decisions with rationale
├── raw/             # Immutable source material
│   ├── articles/
│   ├── papers/
│   ├── transcripts/
│   └── assets/
├── _archive/        # Superseded pages
├── SCHEMA.md        # Conventions + tag taxonomy
├── index.md         # All pages with one-line summaries
├── log.md           # Append-only action log (rotated at 500)
└── .lint-report.md  # Automated lint output
```

## Key Principles

1. **Raw sources are never modified.** Corrections go in wiki pages.
2. **Promotion requires user approval.** Nothing auto-writes to the wiki.
3. **Contradictions are explicit.** Mark with `contested: true` and `contradictions:` frontmatter.
4. **Pages are scannable in 30 seconds.** Split over 200 lines.
5. **Ghost notes drive growth.** 3+ backlinks → promote to full page.
6. **One wiki, two domains.** Knowledge (concepts/entities) and operations (protocols/decisions) share the same index, same SCHEMA, same tag taxonomy.

## Deprecated Components

- **GBrain** — Knowledge graph plugin evaluated and removed on 2026-05-13. All artifacts cleaned. Postgres fallback existed but was never used.
- **team-wiki/sync** cron — No longer needed since Team-Wiki was archived.
