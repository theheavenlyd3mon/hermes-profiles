---
name: team-wiki/ingest
description: Ingest a source into Team-Wiki: capture raw, extract entities, create/update pages, cross-link
version: 1.0.0
author: Hermes Agent Team
license: MIT
metadata:
  hermes:
    tags: [team-wiki, ingest, pipeline, gbrain, entity-extraction]
    related_skills: [team-wiki/sync, team-wiki/maintain, researcher]
---

# Team-Wiki Ingest

Automated pipeline for ingesting external knowledge sources into the Team-Wiki knowledge graph. Captures raw content, synthesizes entities and concepts, creates structured markdown pages, and establishes typed links across the wiki.

## Prerequisites

- Team-Wiki initialized and indexed (`team-wiki/setup`, `gbrain sync` run at least once)
- GBrain MCP server running (or CLI available)
- `WIKI_PATH` environment variable set
- Source material accessible (URL, local file, or clipboard text)
- Appropriate citation data: title, source URL, publication date, author(s)

## Ingestion Pipeline

Each source passes through four stages:

### Stage 1: Capture Raw

Save the source material as a dated raw file under `WIKI_PATH/.raw/` (gitignored in Obsidian but tracked in GBrain raw store):

```bash
# Example: ingest from URL
gbrain file upload --source "https://example.com/article" --title "Article Title" --type url
```

Creates: `.raw/2026-04-25-article-title.md` with frontmatter pointing to original URL.

### Stage 2: Entity & Concept Extraction (GBain Enrichment)

GBrain's entity extraction (via LLM) identifies:
- People, companies, projects, skills, infrastructure from the content
- Key concepts and techniques
- Temporal events with dates

Produces an "enrichment JSON" attached to the raw file.

### Stage 3: Page Creation/Update

For each identified entity:
1. Check if entity page already exists in `entities/{type}/`; if so, append to timeline
2. If new, create entity page with:
   - YAML frontmatter: `title`, `created`, `updated`, `type=entity`, `tags` (with domain prefix), `sources` (link to raw file)
   - Summary paragraph (2–3 sentences)
   - `## Details` section with extracted facts
   - `## Relationships` section with `[[wikilinks]]` to other entities
   - `## References` with citation to raw source
3. Update `index.md` if a new entity was added

### Stage 4: Sync & Index

```bash
gbrain sync --repo "$WIKI_PATH" && gbrain embed --stale
```

The new content becomes searchable and linked.

## Ingest Workflow (Skill Interface)

```bash
# Ingest from a URL with minimal metadata
skill:team-wiki/ingest \
  --source-type url \
  --url "https://blog.example.com/hermes-agent-teams" \
  --title "Building Agent Teams with Hermes" \
  --date 2026-04-25

# Ingest from a local document (PDF → text processed externally)
skill:team-wiki/ingest \
  --source-type file \
  --file "/path/to/article.md" \
  --title "Paper Title" \
  --authors "Jane Doe, John Smith" \
  --venue "Conference on AI Agents"
```

**Required flags:**
- `--source-type`: `url`, `file`, `clipboard`, or `text`
- `--title`: Human-readable title
- `--date`: Publication date (YYYY-MM-DD)

**Optional flags:**
- `--authors`, `--venue`, `--doi` — bibliographic data
- `--tags` — additional tags beyond auto-detected
- `--dry-run` — preview without writing

## Source Types

| Type | Handling |
|------|----------|
| `url` | Fetch HTML/text, strip boilerplate, store raw URL in frontmatter |
| `file` | Read markdown or plain text from disk |
| `clipboard` | Read from system clipboard (macOS `pbpaste`, Linux `xclip`) |
| `text` | Raw string passed inline (for API use) |

## Entity Type Mapping

Incoming sources are classified into page types per SCHEMA.md:

- **agent**: Mentions Hermes agent roles (foreman, coder, etc.) → `entities/agents/`
- **skill**: Tools, frameworks, libraries → `entities/skills/`
- **infrastructure**: Systems, runtimes, services (Hermes, GBrain, Icarus, OpenAI) → `entities/infrastructure/`
- **company**: Organizations (Anthropic, OpenAI, 37signals) → `entities/companies/`
- **person**: Humans (Karpathy, Tan, etc.) → `entities/people/`
- **project**: Code repos, initiatives → `entities/projects/`
- **concept**: Topics, techniques, frameworks not fitting above → `concepts/`

## Citation and Provenance

Every created/updated page must preserve provenance:
- `sources:` frontmatter array includes raw file path or URL
- Inline citations: `^[raw/2026-04-25-hermes-teams.md]` reference raw source
- `## References` section with full citation

## Idempotency

Ingest is safe to re-run: if the same source (by title + date) is processed again, it appends to existing pages rather than creating duplicates. Deduplication based on normalized title + source fingerprint.

## Quality Gates

Before marking ingest complete:
- All new pages have ≥2 `[[wikilinks]]` (enforced by `team-wiki/maintain`)
- Frontmatter validates per SCHEMA
- `gbrain sync` finishes without errors
- Embedding count increases (vector search updated)

## Automation

This skill is typically called by:
- `researcher` agent when discovering new information
- `secretary` agent during daily knowledge capture
- Cron or webhook when a new article is published

## See Also

- `gbrain file upload` and `gbrain enrich` primitives
- `llm-wiki` skill (Karpathy's three-layer wiki pattern)
- `team-wiki/sync` (to refresh after ingest)
