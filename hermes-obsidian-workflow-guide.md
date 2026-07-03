# Hermes Agent × Obsidian: The Second Brain Workflow

> A practical guide for setting up Obsidian as an AI agent's central knowledge store
> within a Hermes Agent multi-agent workflow. Self-contained — an agent reading this
> document can fully replicate the system.

---

## Table of Contents

1. [Overview](#overview)
2. [The Memory Stack](#the-memory-stack)
3. [Vault Structure](#vault-structure)
4. [SCHEMA.md Template](#schemamd-template)
5. [The Knowledge Agent (Secretary Role)](#the-knowledge-agent-secretary-role)
6. [Core Workflows](#core-workflows)
7. [Environment Variables](#environment-variables)
8. [Cron Jobs](#cron-jobs)
9. [Pitfalls & Gotchas](#pitfalls--gotchas)
10. [Quick Start Checklist](#quick-start-checklist)
11. [Skills to Install](#skills-to-install)

---

## Overview

Obsidian isn't just a human notebook — it's the agent's central knowledge store.
Every concept, entity, session summary, and architectural decision flows through
a structured vault that both humans and agents can read, search, and maintain.

**Four-layer memory stack:**

```
┌─────────────────────────────────────────────────────┐
│  Mnemosyne   — Hot facts, always injected           │  ← Agent auto-writes
├─────────────────────────────────────────────────────┤
│  Fabric      — Session capture, operational logs    │  ← All agents + cron
├─────────────────────────────────────────────────────┤
│  LLM-Wiki    — Curated knowledge (Karpathy pattern) │  ← Agent on approval
├─────────────────────────────────────────────────────┤
│  Obsidian    — The vault that holds it all          │  ← Human browses in app
└─────────────────────────────────────────────────────┘
```

The **knowledge/secretary agent** owns vault maintenance. Other agents read freely,
but only the knowledge agent writes wiki pages, maintains the index, enforces
structure, and runs health checks. This single-writer model prevents merge conflicts
and keeps the vault clean.

---

## The Memory Stack

### Layer 1: Mnemosyne (Always-Injected Hot Facts)

**What it is:** A compact block of text injected into every agent session.
Contains user preferences, environment details, and tool quirks.

**Who writes:** The agent itself, automatically, when it detects a stable preference.

**What it handles:**
- User preferences (output style, communication tone, timezone)
- Environment details (OS, installed tools, paths)
- Tool quirks (known workarounds, configuration gotchas)

**Key properties:**
- Never trained or curated — it's raw injection
- Small by design (fits in context window)
- Auto-updated when patterns stabilize across sessions

### Layer 2: Fabric / Icarus (Session Capture + Operational Logging)

**What it is:** Structured markdown entries capturing what happened during sessions.

**Who writes:** All agents and cron jobs append entries.

**What it handles:**
- Session summaries (`agent-session-YYYY-MM-DD_HHMM.md`)
- High-signal decisions (`agent-decision-*.md`)
- Daily operational logs (`daily/YYYY-MM-DD.md`)
- Task outcomes, errors, resolutions

**Key properties:**
- Append-only — entries are never modified after creation
- Structured frontmatter (status, training_value, topics, tags)
- The memory curator scans this layer to promote valuable content upward

### Layer 3: LLM-Wiki (Curated Knowledge Base)

**What it is:** The Karpathy-pattern knowledge base — atomic, interlinked pages.

**Who writes:** The knowledge agent, only after curation approval.

**What it handles:**
- Concepts and topics (e.g., "retrieval-augmented-generation")
- Entities (people, organizations, products)
- Comparisons (side-by-side analyses)
- Alloys (narrative syntheses, essays)
- Queries (filed research results)
- Operational knowledge (protocols, decisions, conventions)

**Key properties:**
- Every page has YAML frontmatter and cross-references
- Pages are atomic — one concept per page
- Graph-connected — minimum 2 outbound wikilinks per page
- Quality-gated — nothing enters without approval

### Layer 4: Obsidian (The Vault)

**What it is:** The filesystem directory that holds everything — wiki, notes,
fabric entries, archives. Browsed by humans in the Obsidian app.

**Who owns:** The knowledge agent maintains structure. Humans browse and approve.

**Key properties:**
- All layers above are stored as markdown files here
- Obsidian's graph view reveals knowledge connections
- Tags, links, and search work across all layers
- Single source of truth for the entire knowledge system

---

## Vault Structure

```
vault/
├── llm-wiki/                   # THE BRAIN — Karpathy-pattern knowledge base
│   ├── concepts/               # Concept/topic pages
│   │   ├── retrieval-augmented-generation.md
│   │   ├── transformer-architecture.md
│   │   └── ...
│   ├── entities/               # Entity pages (people, orgs, products)
│   │   ├── openai.md
│   │   ├── anthropic.md
│   │   └── ...
│   ├── comparisons/            # Side-by-side analyses
│   │   ├── gpt-4-vs-claude.md
│   │   └── ...
│   ├── alloys/                 # Narrative syntheses (essays, docs)
│   │   ├── ai-safety-landscape.md
│   │   └── ...
│   ├── queries/                # Filed research results
│   │   ├── 2026-06-llm-benchmarks.md
│   │   └── ...
│   ├── operational/            # Agent system knowledge
│   │   ├── agents/             # Per-agent scratch spaces
│   │   │   ├── research-agent.md
│   │   │   ├── knowledge-agent.md
│   │   │   └── ...
│   │   ├── protocols/          # Handoff rules, kanban workflow
│   │   │   ├── handoff-protocol.md
│   │   │   ├── kanban-workflow.md
│   │   │   └── ...
│   │   ├── conventions/        # Standards, style guides
│   │   │   ├── naming-conventions.md
│   │   │   ├── code-style.md
│   │   │   └── ...
│   │   └── decisions/          # Architectural decisions with rationale
│   │       ├── 2026-01-adr-001-vault-structure.md
│   │       └── ...
│   ├── raw/                    # Immutable source material — NEVER MODIFY
│   │   ├── articles/           # Web articles, clippings
│   │   ├── papers/             # PDFs, academic papers
│   │   ├── transcripts/        # Meeting notes, interviews
│   │   └── assets/             # Images, diagrams
│   ├── _archive/               # Superseded pages (moved, not deleted)
│   ├── SCHEMA.md               # Conventions + tag taxonomy
│   ├── index.md                # All pages with one-line summaries
│   └── log.md                  # Append-only action log
├── icarus/                     # Agent memory fabric entries
│   ├── agent-decision-*.md     # High-signal decisions
│   ├── agent-session-*.md      # Session summaries (fabric entries)
│   └── daily/                  # Daily agent logs
│       ├── 2026-06-17.md
│       └── ...
├── notes/                      # Quick captures (lower barrier than wiki)
│   ├── random-thought-on-rag.md
│   └── ...
└── 4-Archive/                  # Archived/dead weight
    ├── old-notes/
    └── ...
```

**Design principles:**
- `llm-wiki/` is the knowledge base — structured, curated, graph-connected
- `icarus/` is operational memory — append-only session/decision logs
- `notes/` is the inbox — low-friction capture, curated into wiki over time
- `4-Archive/` is the graveyard — stuff that's dead weight but not deleted
- `raw/` is immutable — source material is never modified after ingestion

---

## SCHEMA.md Template

Place this file at `vault/llm-wiki/SCHEMA.md`. Customize the `[DOMAIN]` placeholder.

```markdown
# LLM-Wiki Schema & Conventions

## Domain

[DOMAIN] — e.g., "AI/ML research, software engineering, and agent operations"

## File Naming

- **Lowercase, hyphenated:** `retrieval-augmented-generation.md`
- **No spaces, no underscores** (except in frontmatter dates)
- **Descriptive but concise:** `transformer-attention.md` not `transformers.md`
- **Entity pages:** use the canonical name — `openai.md`, `anthropic.md`
- **Comparisons:** `thing-a-vs-thing-b.md`
- **Alloys:** descriptive noun phrases — `ai-safety-landscape.md`
- **Decisions:** `YYYY-MM-DD-adr-NNN-short-title.md`

## Frontmatter

Every wiki page MUST have YAML frontmatter with these fields:

```yaml
---
title: "Page Title"                    # REQUIRED — human-readable title
created: 2026-06-17                    # REQUIRED — ISO date, never changes
updated: 2026-06-17                    # REQUIRED — ISO date, updated on edit
type: concept                          # REQUIRED — one of: concept | entity | comparison | alloy | query | decision | protocol | convention | agent-profile
tags:                                  # REQUIRED — at least one from taxonomy
  - topic:ai
  - workflow:curated
sources:                               # REQUIRED for content pages — provenance
  - url: "https://example.com/article"
    title: "Source Title"
    accessed: 2026-06-17
composes:                              # OPTIONAL — pages this page synthesizes
  - "[[transformer-architecture]]"
  - "[[attention-mechanisms]]"
composed_by:                           # OPTIONAL — pages that synthesize this one
  - "[[ai-safety-landscape]]"
topics:                                # OPTIONAL — freeform topic tags (use sparingly)
  - attention
  - scaling
workflow: curated                      # REQUIRED — draft | curated | archived
confidence: high                       # OPTIONAL — low | medium | high
contested: false                       # OPTIONAL — true if claims are disputed
contradictions:                        # OPTIONAL — explicit contradictions
  - page: "[[other-page]]"
    claim: "States X, but this page states Y"
    resolution: "Y is correct because Z"
---
```

**Field reference:**

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `title` | Yes | string | Human-readable page title |
| `created` | Yes | date | ISO date of page creation |
| `updated` | Yes | date | ISO date of last meaningful edit |
| `type` | Yes | enum | Page type (see taxonomy below) |
| `tags` | Yes | list | At least one tag from the taxonomy |
| `sources` | Yes* | list | Provenance — where the content came from |
| `composes` | No | list | Wikilinks to pages this one synthesizes |
| `composed_by` | No | list | Wikilinks to pages that synthesize this one |
| `topics` | No | list | Freeform topic keywords |
| `workflow` | Yes | enum | `draft` / `curated` / `archived` |
| `confidence` | No | enum | Confidence level in the content |
| `contested` | No | bool | Whether claims are disputed |
| `contradictions` | No | list | Explicit contradictions with other pages |

*Required for content pages (concepts, entities, comparisons, alloys). Optional for operational pages.

## Wikilinks

- Use Obsidian-style wikilinks: `[[page-name]]` or `[[page-name|Display Text]]`
- **Minimum 2 outbound wikilinks per page** — isolated pages break the graph
- Link to existing pages when possible; broken links are acceptable but flagged in lint
- Use descriptive display text when the page name is technical: `[[retrieval-augmented-generation|RAG]]`

## Provenance Markers

When citing sources inline, use this format:

```
> [!source] Source: [Title](https://example.com) — accessed 2026-06-17
```

For claims from multiple sources:

```
> [!source] Sources: [Article A](url-a), [Paper B](url-b)
```

## Composition Fields

When a page synthesizes multiple source pages:

```yaml
composes:
  - "[[transformer-architecture]]"
  - "[[attention-mechanisms]]"
  - "[[scaling-laws]]"
```

The composed pages should reciprocate:

```yaml
composed_by:
  - "[[how-transformers-work]]"
```

## Tag Taxonomy

### Workflow Tags (Tier 1 — State Tracking)

| Tag | Meaning |
|-----|---------|
| `workflow:draft` | Work in progress, not yet curated |
| `workflow:curated` | Reviewed and approved |
| `workflow:archived` | Superseded or no longer relevant |
| `workflow:promoted` | Promoted from notes/fabric |
| `workflow:needs-review` | Flagged for review |
| `workflow:stale` | Not updated in 90+ days |

### Domain Tags (Tier 2 — Topic Classification)

Customize these for your domain. Examples:

| Tag | Domain |
|-----|--------|
| `topic:ai` | Artificial intelligence |
| `topic:ml` | Machine learning |
| `topic:llm` | Large language models |
| `topic:agents` | AI agents |
| `topic:engineering` | Software engineering |
| `topic:devops` | DevOps, infrastructure |
| `topic:research` | Research methodology |
| `topic:security` | Security, privacy |
| `topic:business` | Business, strategy |
| `topic:tools` | Tools, utilities |

### Type Tags (Tier 2 — Content Shape)

| Tag | Meaning |
|-----|---------|
| `type:howto` | Step-by-step instructions |
| `type:reference` | Factual reference material |
| `type:opinion` | Subjective analysis |
| `type:summary` | Condensed summary of source |
| `type:comparison` | Side-by-side analysis |

## Page Thresholds

**When to CREATE a new page:**
- A concept, entity, or topic is referenced 3+ times across sessions
- A source contains substantive information worth preserving
- User explicitly requests a page
- A fabric entry has `training_value: high` and covers a new topic

**When to ADD TO an existing page:**
- The new information is about the same concept/entity
- It's a correction, update, or addition to existing content
- It's less than a paragraph of new material

**When to SPLIT a page:**
- Page exceeds 200 lines
- Page covers 3+ distinct sub-topics
- A section has grown to rival the rest of the page

## Contradiction Policy

When a new source contradicts existing content:

1. **Do not silently overwrite** — this breaks trust
2. Add the new information with a `contested: true` flag
3. Document both claims in the `contradictions` field
4. If resolution is clear, update with rationale
5. If resolution is unclear, mark both and flag for user review

```yaml
contested: true
contradictions:
  - page: "[[existing-page]]"
    claim: "States that X is true"
    new_evidence: "Source Y states that X is false"
    resolution: "pending"  # or "resolved: Y is correct because Z"
```
```

---

## The Knowledge Agent (Secretary Role)

The knowledge agent is the single writer for the vault's curated content. It keeps
the graph connected, the index current, and the structure clean.

### Identity Block

```
IDENTITY: Organized.Thorough.Precise.Worker.
STYLE: Structured output. Obsidian-native markdown. Backlinks and tags over folders.
       Atomic notes. YAML frontmatter. Silent on vault unless asked.
AVOID: Vague titles | orphan notes | missing frontmatter | redundant content |
       over-nesting folders | breaking vault conventions
DEFAULTS: ObsidianMarkdown | YAML frontmatter | Backlinks | AtomicNotes |
          TagTaxonomy | MOC(MapOfContent)
```

### Responsibilities

**Owns (must maintain):**
- `index.md` — complete, current, one-line summary per page
- `log.md` — append-only action log
- Vault directory structure — correct folders, no rogue directories
- `SCHEMA.md` enforcement — frontmatter validation, tag compliance
- Lint/health checks — orphans, broken links, staleness

**Creates (on approval):**
- Wiki pages from approved sources
- Entity pages from recurring references
- Concept pages from curated notes
- Comparison pages from research queries

**Monitors (automated scans):**
- `notes/` for promotion candidates (3+ wikilinks, tagged, stable)
- `icarus/` for high-value fabric entries (`training_value: high`)
- `llm-wiki/raw/` for new sources awaiting processing
- Vault health metrics (orphans, broken links, staleness)

**Reports (on schedule):**
- Weekly vault health summary
- Orphan page count and list
- Wikilink graph density
- Promotion candidate queue
- Stale content alerts

**Never (hard rules):**
- Auto-deletes anything — archive first, delete only on explicit approval
- Auto-promotes without approval — wiki quality matters
- Modifies files in `raw/` — sources are immutable
- Creates pages without cross-references
- Uses tags outside the taxonomy
- Skips index.md or log.md updates

### Agent Prompt Template

When configuring the knowledge agent, include this in its system prompt:

```
You are the knowledge agent for this vault. Before ANY operation:

1. Read SCHEMA.md for conventions
2. Read index.md for current state
3. Read log.md for recent actions

When creating or updating pages:
- Always use YAML frontmatter per SCHEMA.md
- Always include minimum 2 outbound wikilinks
- Always update index.md after changes
- Always append to log.md after changes
- Use tags only from the taxonomy in SCHEMA.md

When linting:
- Report orphans, broken links, missing frontmatter
- Never auto-fix — propose fixes for approval
- Flag stale content (>90 days without update)

When promoting from notes/ or icarus/:
- Always propose first, wait for approval
- Cross-reference against index.md to avoid duplicates
- Create proper wiki pages with full frontmatter
```

---

## Core Workflows

### 1. Ingest (Source → Wiki)

When a new source (article, paper, transcript) needs to be captured and processed.

**Step-by-step:**

```bash
# 1. Capture raw source to raw/
# For web articles:
curl -s "https://example.com/article" > ~/vault/llm-wiki/raw/articles/example-article.md

# For manual captures, write the content directly:
# Use the agent's write tool to create the file
```

**2. Add raw frontmatter to the source file:**

```yaml
---
title: "Original Article Title"
source_url: "https://example.com/article"
ingested: 2026-06-17
sha256: "abc123..."  # Optional: content hash for dedup
type: raw-source
---
```

**3. Check existing pages to avoid duplicates:**

```bash
# Search index.md for related pages
# Search wiki directory for related content
# Use search_files tool: pattern = relevant keywords, target = content
```

**4. Write/update wiki pages with proper frontmatter:**

For each concept, entity, or topic in the source that meets the page threshold:

```yaml
---
title: "Concept Name"
created: 2026-06-17
updated: 2026-06-17
type: concept
tags:
  - topic:ai
  - workflow:curated
sources:
  - url: "https://example.com/article"
    title: "Original Article Title"
    accessed: 2026-06-17
workflow: curated
confidence: high
---

# Concept Name

Summary of the concept...

## Key Points

- Point 1
- Point 2

## Related

- [[related-concept-a]]
- [[related-concept-b]]
- [[entity-responsible]]
```

**5. Cross-reference:**

Every new page must link to at least 2 existing pages (or create links to pages
that will exist). Use `search_files` to find related content.

**6. Update index.md:**

Append the new page to the index:

```markdown
- [[concept-name]] — One-line summary of the concept
```

**7. Update log.md:**

Append an entry:

```markdown
## 2026-06-17 14:30 — Ingested: Example Article
- Captured raw source to `raw/articles/example-article.md`
- Created: [[concept-name]], [[entity-name]]
- Updated: [[existing-concept]] (added new information)
- Cross-references: concept-name → existing-concept, related-topic
```

**8. Report what changed:**

Summarize for the user:
- New pages created
- Existing pages updated
- Cross-references added
- Any issues (duplicates found, contradictions detected)

### 2. Curation (Notes → Wiki)

The memory curator monitors `notes/` for content worth promoting to the wiki.

**Promotion threshold — a note qualifies if ANY of:**
- Referenced by 3+ wikilinks across the vault
- Tagged with a concept/topic tag
- Content has been stable (unchanged) across 2+ sessions
- User explicitly requests promotion

**Workflow:**

```
1. SCAN: List files in notes/, check frontmatter and content
2. PROPOSE: Present candidates to user with rationale
3. APPROVE: User reviews and approves/rejects
4. CREATE/UPDATE: Build proper wiki page with full frontmatter
5. INDEX: Update index.md with new entry
6. LOG: Append to log.md
7. (Optional) MOVE: Move promoted note to notes/_promoted/ or archive
```

**Scanning script (agent logic):**

```python
# Pseudocode for the curator's scan logic
notes = list_files("~/vault/notes/")
for note in notes:
    content = read_file(note)
    wikilinks = extract_wikilinks(content)
    tags = extract_frontmatter_tags(content)
    
    score = 0
    if len(wikilinks) >= 3:
        score += 3  # Well-connected
    if any_tag_in_taxonomy(tags):
        score += 2  # Already tagged
    if content_unchanged_across_sessions(note, sessions=2):
        score += 1  # Stable content
    
    if score >= 3:
        propose_promotion(note, score, rationale)
```

### 3. Fabric Promotion (Session Data → Wiki)

A cron job scans `icarus/` entries daily for high-value content to promote.

**Criteria for promotion candidate:**
- `status: completed` (session/task finished successfully)
- `training_value: high` (contains reusable knowledge)
- Not already promoted (no `promoted: true` field)
- Contains content not already in index.md

**Workflow:**

```
1. SCAN: Read all agent-session-*.md files from last 24h
2. FILTER: status=completed AND training_value=high AND NOT promoted
3. DEDUPLICATE: Cross-reference content against index.md
4. PROPOSE: Present candidates to user
5. APPROVE: User reviews
6. CREATE: Build wiki pages from fabric content
7. MARK: Set promoted: true on source fabric entry
8. INDEX + LOG: Update index.md and log.md
```

**Fabric entry frontmatter (for reference):**

```yaml
---
title: "Session Summary — 2026-06-17"
created: 2026-06-17T14:30:00
agent: research-agent
status: completed
training_value: high
topics:
  - rag-optimization
  - vector-databases
promoted: false
---
```

### 4. Lint & Health Check

Run this daily (or on demand) to keep the vault clean.

**Full lint checklist:**

```
□ Orphan pages
  - Find pages with zero inbound wikilinks
  - Report: page name, last modified, suggested connections

□ Broken wikilinks
  - Find wikilinks pointing to non-existent pages
  - Report: source page, broken link target, count

□ Index completeness
  - Compare filesystem pages vs index.md entries
  - Report: pages missing from index, index entries with no file

□ Frontmatter validation
  - Check all pages have required fields (title, created, updated, type, tags, workflow)
  - Report: pages with missing/invalid frontmatter

□ Stale content
  - Find pages with updated date >90 days ago
  - Report: page name, last updated, days stale

□ Contradictions
  - Search for conflicting claims across pages on same topics
  - Report: page pairs, conflicting claims

□ Page size
  - Find pages >200 lines
  - Report: page name, line count, suggested split points

□ Tag audit
  - Find tags not in SCHEMA.md taxonomy
  - Report: tag, pages using it, suggested taxonomy tag

□ Ghost note detection
  - Find broken wikilinks with 3+ backlinks (pages people keep trying to link to)
  - Report: ghost target, backlink count, suggested creation

□ Log rotation
  - Check log.md size
  - If >500 entries, archive old entries to log-archive-YYYY-MM.md
```

**Lint output format:**

```markdown
# Vault Lint Report — 2026-06-17

## Summary
- Total pages: 142
- Issues found: 7

## Issues

### P1 — Must Fix
| Issue | Page | Detail |
|-------|------|--------|
| Missing frontmatter | concepts/old-note.md | No YAML block |
| Broken wikilink | entities/openai.md:15 | Links to [[nonexistent-page]] |

### P2 — Should Fix
| Issue | Page | Detail |
|-------|------|--------|
| Orphan page | concepts/niche-topic.md | 0 inbound links |
| Stale content | concepts/outdated-info.md | 127 days since update |

### P3 — Nice to Fix
| Issue | Page | Detail |
|-------|------|--------|
| Freeform tag | concepts/misc.md | Uses `#random-tag` not in taxonomy |
| Oversized page | concepts/huge-topic.md | 312 lines, consider splitting |
```

### 5. Vault Audit & Cleanup

A deeper pass than daily lint. Run monthly or when the vault feels cluttered.

**Phase 1: Scan**
```
- Generate full directory tree
- Classify issues into categories:
  - Clutter (misplaced files, root-level noise)
  - Duplicates (near-identical content)
  - Oversized (pages >200 lines)
  - Untitled/unnamed (files with generic names)
  - Empty directories
  - Convention violations
```

**Phase 2: Prioritize**
```
P1: Clutter + duplicates (immediate impact)
P2: Oversized pages + untitled files (quality)
P3: Empty directories (housekeeping)
P4: Convention violations (consistency)
```

**Phase 3: Execute**
```
For each priority level:
  - Create kanban tasks (todo → in-progress → done)
  - Execute fixes one at a time
  - Verify each fix before moving on
```

**Phase 4: Verify**
```
- Re-run lint checklist
- Confirm all issues resolved
- Check graph integrity (no new broken links)
```

**Phase 5: Update References**
```
- Update index.md to reflect all changes
- Update any pages that reference moved/renamed files
- Append audit summary to log.md
```

### 6. Weekly Health Report

Collect these metrics every Monday:

```markdown
# Vault Health Report — Week of 2026-06-16

## Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Total pages | 142 | — |
| Pages modified (7d) | 18 | Healthy |
| Directory count | 12 | — |
| Wikilinks per page | 2.3 | Healthy (target: 1.0-3.0) |
| Tagged pages | 138/142 (97%) | Healthy |
| Untagged pages | 4 | Needs attention |
| Orphan pages | 3 | Needs attention |
| Notes in inbox | 7 | — |
| Root-level files | 0 | Clean |

## Orphan Pages
1. [[niche-topic-a]] — Last updated 2026-05-10
2. [[niche-topic-b]] — Last updated 2026-04-22
3. [[old-experiment]] — Last updated 2026-03-15

## Stale Content (>90 days)
1. [[outdated-info]] — 127 days stale
2. [[deprecated-method]] — 98 days stale

## Promotion Candidates
1. `notes/rag-optimization-tips.md` — 4 wikilinks, stable 3 sessions
2. `notes/docker-gotchas.md` — tagged, stable 2 sessions

## Recommendations
- Connect 3 orphan pages to the graph
- Review 2 stale pages for archival
- Promote 2 notes to wiki
```

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `OBSIDIAN_VAULT_PATH` | Absolute path to the vault root | `~/vault` or `/path/to/vault` |
| `WIKI_PATH` | Absolute path to the wiki directory | `~/vault/llm-wiki` |
| `ICARUS_OBSIDIAN` | Enables Icarus → Obsidian sync | `1` |
| `FABRIC_DIR` | Where fabric entries are stored | `~/vault/icarus` |

**Setting them:**

```bash
# In your shell profile (~/.bashrc, ~/.zshrc, etc.)
export OBSIDIAN_VAULT_PATH="$HOME/vault"
export WIKI_PATH="$HOME/vault/llm-wiki"
export ICARUS_OBSIDIAN=1
export FABRIC_DIR="$HOME/vault/icarus"
```

**Or in Hermes agent configuration:**

```yaml
env:
  OBSIDIAN_VAULT_PATH: ~/vault
  WIKI_PATH: ~/vault/llm-wiki
  ICARUS_OBSIDIAN: "1"
  FABRIC_DIR: ~/vault/icarus
```

---

## Cron Jobs

Recommended automated schedules for vault maintenance.

### Daily Lint (4:00 AM)

```yaml
name: wiki-health-check
schedule: "0 4 * * *"
agent: knowledge-agent
prompt: |
  Run a full lint check on the wiki at $WIKI_PATH.
  Check: orphans, broken wikilinks, index completeness,
  frontmatter validation, stale content, page size.
  Report issues by priority (P1/P2/P3).
  Do NOT auto-fix — report only.
```

### Daily Fabric Promotion Scan (5:00 AM)

```yaml
name: fabric-promotion-scan
schedule: "0 5 * * *"
agent: knowledge-agent
prompt: |
  Scan $FABRIC_DIR for promotion candidates from the last 24h.
  Criteria: status=completed, training_value=high, promoted!=true.
  Cross-reference against $WIKI_PATH/index.md.
  Propose candidates with rationale. Wait for approval.
```

### Weekly Vault Summary (Monday 6:00 AM)

```yaml
name: weekly-vault-summary
schedule: "0 6 * * 1"
agent: knowledge-agent
prompt: |
  Generate a full vault health report for $OBSIDIAN_VAULT_PATH.
  Include: page count, modification rate, wikilink density,
  tag coverage, orphan count, stale content, promotion candidates,
  inbox status, root-level clutter.
  Format as the weekly health report template.
```

### Monthly Vault Audit (1st of month, 7:00 AM)

```yaml
name: monthly-vault-audit
schedule: "0 7 1 * *"
agent: knowledge-agent
prompt: |
  Run a deep vault audit on $OBSIDIAN_VAULT_PATH.
  Phase 1: Full scan — directory tree, issue classification.
  Phase 2: Prioritize — P1 through P4.
  Phase 3: Propose fixes as kanban tasks. Wait for approval.
  Phase 4: Execute approved fixes.
  Phase 5: Update index.md, log.md, and references.
```

---

## Pitfalls & Gotchas

These are the mistakes that will silently degrade your vault. Read them.

### Immutability

- **Never modify files in `raw/`** — sources are immutable after ingestion. If a source is wrong, add a note in the wiki page, don't "fix" the raw file.

### Orientation

- **Always orient first** — before any vault operation, read `SCHEMA.md`, `index.md`, and `log.md`. Skipping this leads to convention violations and duplicate pages.

### Index & Log Discipline

- **Always update `index.md` and `log.md`** — every page creation, update, or structural change must be reflected in both. Skipping this degrades the wiki silently — orphan pages appear, the index goes stale, and the graph breaks down.

### Page Creation Rules

- **Don't create pages for passing mentions** — a concept mentioned once in a conversation doesn't need a page. Follow the page thresholds in SCHEMA.md.
- **Don't create pages without cross-references** — a page with zero wikilinks is invisible to the graph. Every page needs minimum 2 outbound links.

### Frontmatter

- **Frontmatter is required on every wiki page** — it enables search, filtering, staleness detection, and the lint system. Pages without frontmatter are flagged as P1 issues.

### Tags

- **Tags must come from the taxonomy** — freeform tags decay into noise over time. If you need a new tag, propose it as a taxonomy update first.

### Index Management

- **Sequential patches to `index.md` create duplicate entries** — when adding multiple pages, batch all additions into a single write operation. Don't append one at a time.

### Page Size

- **Keep pages scannable** — if a page exceeds 200 lines, it's a split candidate. Atomic notes are easier to link, search, and maintain.

### Contradictions

- **Handle contradictions explicitly** — when new information conflicts with existing content, document both claims in the `contradictions` frontmatter field. Don't silently overwrite.

### Deletion

- **Don't auto-delete** — move to `_archive/` first. Delete only on explicit user approval. What looks dead today might be useful tomorrow.

### Promotion

- **Don't auto-promote** — wiki quality matters. Always propose promotion candidates and wait for approval. The curator's job is to identify, not to decide.

### File Operations

- **Check wikilinks before moving files** — moving or renaming a wiki page breaks all incoming wikilinks. Update all references, or use Obsidian's rename feature which handles this automatically.

### Fabric Entries vs Transcripts

- **`agent-session-*.md` files are NOT raw transcripts** — they're structured fabric entries with frontmatter. Don't treat them as archival candidates.
- **Date-stamped files (`YYYY-MM-DD_HHMM.md`) in `daily/` ARE operational logs** — safe to archive after rotation.

### Case Sensitivity

- **`WIKI_PATH` case-sensitivity** — macOS filesystems are case-insensitive but case-preserving. Linux is case-sensitive. If you develop on macOS and deploy to Linux, ensure consistent casing in all paths and filenames.

### Graph Integrity

- **Never break the graph carelessly** — every wikilink is a connection. Renaming, moving, or deleting pages without updating references creates dangling links that accumulate into a broken graph.

---

## Quick Start Checklist

Setting this up from scratch? Follow these steps in order.

```
□ 1. Set environment variables
     export OBSIDIAN_VAULT_PATH="$HOME/vault"
     export WIKI_PATH="$HOME/vault/llm-wiki"
     export ICARUS_OBSIDIAN=1
     export FABRIC_DIR="$HOME/vault/icarus"

□ 2. Create vault directory structure
     mkdir -p $OBSIDIAN_VAULT_PATH/{llm-wiki/{concepts,entities,comparisons,alloys,queries,operational/{agents,protocols,conventions,decisions},raw/{articles,papers,transcripts,assets},_archive},icarus/daily,notes,4-Archive}

□ 3. Write SCHEMA.md for your domain
     Copy the template above, customize [DOMAIN] and topic tags.
     Place at $WIKI_PATH/SCHEMA.md

□ 4. Initialize index.md and log.md
     echo "# LLM-Wiki Index\n\nAll wiki pages with one-line summaries.\n" > $WIKI_PATH/index.md
     echo "# LLM-Wiki Log\n\nAppend-only action log.\n" > $WIKI_PATH/log.md

□ 5. Configure knowledge agent SOUL.md
     Add the identity block and responsibilities from the
     "Knowledge Agent" section to your agent's system prompt.

□ 6. Set up cron jobs
     Configure the 4 cron jobs from the "Cron Jobs" section:
     - Daily lint (4am)
     - Daily fabric promotion scan (5am)
     - Weekly vault summary (Monday 6am)
     - Monthly vault audit (1st of month, 7am)

□ 7. Start ingesting sources
     Pick your first source. Run the Ingest workflow.
     Build the graph one page at a time.

□ 8. (Optional) Install Hermes skills
     Install the skills listed in the next section to
     power automated vault operations.
```

---

## Skills to Install

These skills provide the tooling that powers the workflows described above.

| Skill | Purpose | What It Does |
|-------|---------|--------------|
| `obsidian` | Vault operations | Read, write, search, and manage files in an Obsidian vault with proper frontmatter handling |
| `llm-wiki` | Karpathy-pattern knowledge base | Create and manage atomic, interlinked wiki pages with the full Karpathy methodology |
| `memory-curator` | Automated memory hygiene | Scan notes and fabric entries for promotion candidates, manage the curation pipeline |
| `fabric-promote-review` | Fabric → wiki promotion | Review fabric entries, propose promotion candidates, manage the promotion workflow |

**Installing skills:**

```bash
# In Hermes Agent, use the skill install command
hermes skill install obsidian
hermes skill install llm-wiki
hermes skill install memory-curator
hermes skill install fabric-promote-review
```

Or use the agent's built-in skill management to search and install from the registry.

---

## Appendix: File Templates

### Empty Wiki Page Template

```markdown
---
title: "Page Title"
created: 2026-06-17
updated: 2026-06-17
type: concept
tags:
  - topic:example
  - workflow:draft
sources:
  - url: "https://example.com"
    title: "Source Title"
    accessed: 2026-06-17
workflow: draft
confidence: medium
---

# Page Title

Brief summary of this page in 1-2 sentences.

## Key Points

- Point 1
- Point 2
- Point 3

## Details

Elaboration on the key points...

## Related

- [[related-page-1]]
- [[related-page-2]]
- [[related-page-3]]
```

### Fabric Entry Template

```markdown
---
title: "Session Summary — 2026-06-17 14:30"
created: 2026-06-17T14:30:00
agent: agent-name
status: completed
training_value: medium
topics:
  - topic-one
  - topic-two
promoted: false
---

# Session Summary

## What Happened
Brief description of the session.

## Decisions Made
- Decision 1: rationale
- Decision 2: rationale

## Outcomes
- Outcome 1
- Outcome 2

## Learnings
- Learning 1
- Learning 2
```

### Index Entry Format

```markdown
- [[page-name]] — One-line summary of what this page covers
```

### Log Entry Format

```markdown
## YYYY-MM-DD HH:MM — ACTION: Description
- Detail 1
- Detail 2
- Pages affected: [[page-1]], [[page-2]]
```

---

## Appendix: Wikilink Conventions

```
Basic link:         [[page-name]]
With display text:  [[page-name|Display Text]]
Section link:       [[page-name#Section]]
Block link:         [[page-name#^block-id]]
```

**When to use each:**
- `[[page-name]]` — default, use when the page name is readable
- `[[page-name|Display]]` — when the page name is technical or long
- `[[page-name#Section]]` — when linking to a specific section
- Avoid block links unless the page is very long and sections are ambiguous

---

## Appendix: Recommended Obsidian Plugins

These plugins enhance the agent-human collaboration:

| Plugin | Purpose |
|--------|---------|
| **Graph Analysis** | Visualize wikilink density, find orphans |
| **Dataview** | Query frontmatter across pages |
| **Templater** | Auto-apply page templates |
| **Tag Wrangler** | Manage and rename tags in bulk |
| **Periodic Notes** | Automated daily/weekly note creation |
| **Front Matter Tag Suggest** | Autocomplete tags from taxonomy |

---

*This document is self-contained. An agent reading it can set up the full vault
structure, configure the knowledge agent, establish cron jobs, and begin ingesting
sources without additional context.*
