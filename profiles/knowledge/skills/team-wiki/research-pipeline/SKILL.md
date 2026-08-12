---
name: team-wiki/research-pipeline
description: "Research pipeline worker for the wiki: ingest weekly findings files, apply threshold/duplicate/contradiction rules, create or update wiki pages with researcher frontmatter, and batch-update index and log."
version: 1.0.0
author: Senna (Hermes)
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [obsidian, wiki, research, pipeline, automation]
    category: team-wiki
    related_skills: [note-taking/obsidian, note-taking/obsidian-note-creation, productivity/obsidian-vault-audit, team-wiki/setup, team-wiki/maintain, team-wiki/sync]
---

# research-pipeline

IDENTITY: Researcher.ThoroughBound. SchemaFirst→ThresholdGate→DuplicateCheck→PatchOrCreate→WikilinkMin→ContradictionProtocol→BatchIndexLog→Report.
Law: ReadSchemaAndIndexFirst. RawSourcesImmutable. NoWebNoArXivNoOutsideFiles. TwoOutboundLinksMinimum.
WHENUSE: Running the weekly research pipeline|Ingesting findings-YYYY-MM-DD.md files|Updating wiki from raw/articles/research/<category>/.
ESPECIALLY:ThresholdGate|DuplicatePatch|ContradictionHandling|ProvenanceMarkers|BatchIndexLog|SkippedFindingsReport.
NoSkip:SchemaRead|IndexRead|LogAppend|ScopeCheck.

## Trigger

Use this when:
- processing a weekly research findings file
- the user asks to run the research pipeline for a category
- ingesting new raw sources into the wiki

## Inputs

- Protocol: `llm-wiki/operational/protocols/research-pipeline-categories.md`
- Raw findings: `llm-wiki/raw/articles/research/<category-slug>/findings-YYYY-MM-DD.md`
- Wiki state: `llm-wiki/SCHEMA.md`, `llm-wiki/index.md`, `llm-wiki/log.md`

## Pre-flight checks

1. Verify the protocol file exists. If missing, stop and report.
2. Verify `SCHEMA.md`, `index.md`, and `log.md` exist under the wiki root.
3. Verify the target category slug exists in the protocol file's category table. If missing, stop and report.
4. Verify raw findings file exists. If missing, report skipped run with reason.

## Vault path

Use the same resolution rules as `note-taking/obsidian`:
- Prefer `OBSIDIAN_VAULT_PATH` from env.
- Fallback: `~/Documents/Obsidian Vault` or the user's known vault root.
- Resolve to a concrete absolute path before any file-tool call.
- Only use terminal to resolve the path; all other operations use file tools.

## Step 1 — Read schema and index

Read, in order:
1. `llm-wiki/SCHEMA.md`
2. `llm-wiki/index.md`
3. `llm-wiki/log.md` (last 100 lines is enough for recent context)
4. `llm-wiki/operational/protocols/research-pipeline-categories.md`

Do not proceed without these loaded. They define every subsequent decision.

## Step 2 — Parse findings file

Read the findings markdown. Extract atomic findings. A finding is a discrete claim, entity, concept, protocol change, or methodology proposal.

Do not invent structure — parse what exists. If the file uses headings, lists, or bullet sections, treat each item under those as a candidate finding.

## Step 3 — Threshold gate

For each finding:

**Pass if ANY of these are true:**
- 2+ source mentions in the file or across `raw/articles/research/<category>/`
- Central to one source: the finding is the primary contribution of that source, not a side note

**Fail / skip if:**
- Passing mention only
- Outside wiki domain
- Pure announcement without shipped behavior or adoption signal
- The finding is already fully covered by analysis elsewhere and adds nothing new

Skip list format per run:
```
- <finding summary> — skipped: <reason>
```

## Step 4 — Duplicate check

For each passing finding:
1. Search wiki for matching slugs/titles: `search_files(target='files', pattern='<slug>*', path='<llm-wiki/>')`
2. Search content for aliases: `search_files(target='content', pattern='<Title or known alias>', file_glob='*.md', path='<llm-wiki/>')`
3. If a single clear match exists: patch that page.
4. If two or more candidates: read both, pick canonical, add redirect note or merge.
5. If no match: create new page.

## Step 5 — Page type routing

Apply the category routing from the protocol, plus these universal rules:

| Finding shape | Page type | Location |
|---|---|---|
| Entity/concept | `concept` or `entity` | `llm-wiki/concepts/` or `llm-wiki/entities/` |
| Protocol break | `concept` | `llm-wiki/concepts/` |
| Novel methodology with ≥2 sources | `concept` | `llm-wiki/concepts/` |
| Alloy candidate | `alloy` | `llm-wiki/alloys/` |
| Side-by-side analysis | `comparison` | `llm-wiki/comparisons/` |
| Saved result | `query` | `llm-wiki/queries/` |

Alloy rule: only create an alloy when ≥3 existing concepts shift at once. Otherwise, route to `concept` or `comparison`.

## Step 6 — Frontmatter rules

Required frontmatter on every new or updated page:

```yaml
---
title: "Human-Readable Title"
type: concept|entity|comparison|alloy|query|summary
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [workflow tag + topic tags from SCHEMA taxonomy]
sources: ["raw/articles/research/<category>/<source-file.md>"]
workflow: seedling|developing|stable|needs-review|stale
confidence: high|medium|low
# Only when 3+ sources:
provenancemarkers: true
# Only when contradictions exist:
contested: true
contradictions: [other-page-slug]
---
```

Rules:
- Tags must come from the SCHEMA taxonomy. No freeform tags.
- Every page carries exactly one workflow tag.
- `confidence: high` only after corroboration; default `medium` for single-source or opinion-heavy claims.
- `provenancemarkers: true` only when synthesizing 3+ sources.
- `composes:` / `composed_by:` only for alloys.

## Step 7 — Page body rules

- Lead with a one-sentence definition or current-state summary.
- Use bullet facts with dates where applicable.
- Append at least 2 outbound `[[wikilinks]]` on every new/updated page.
- When synthesizing 3+ sources, append `^[raw/articles/source-file.md]` at the end of paragraphs whose claims come from a specific source.
- No longform sprawl. Keep it scannable.
- Do not invent ghost links speculatively.

## Step 8 — Contradiction protocol

When the findings or cross-check against existing pages reveals a genuine contradiction:
1. Add both positions with explicit dates and sources.
2. Set `contested: true` in frontmatter.
3. Add `contradictions: [other-page-slug]` referencing the conflicting page.
4. Do not silently overwrite newer or older claims.
5. Flag in the batch log entry.

## Step 9 — Patch workflow

When updating an existing page:
1. Read the file.
2. Identify the best anchor: `## Timeline`, `## Current`, `## Facts`, or similar.
3. Append a dated block: `- YYYY-MM-DD — <summary> [source: <file>]`.
4. Bump `updated:` in frontmatter.
5. Add or preserve outbound `[[wikilinks]]`.
6. If adding a major new section, update `sources:` array.

## Step 10 — Batch index and log update

Use raw file writes, not line-number-prefixed reads for these two files.

### index.md
- Add every new page under the appropriate section heading with a one-line summary:
  `- [[Page Title]] — one-line description`
- Update counts if the index contains a total-pages line.

### log.md
- Append ONE batch log entry per run, not one per file.
- Format:
  ```
  ## YYYY-MM-DD <category-slug> pipeline

  - Created: <page list or count>
  - Updated: <page list or count>
  - Skipped: <count> — <reasons summary>
  - Contradictions: <page list or "none">
  - Index delta: <lines added / sections touched>
  ```
- Do not rotate log in this skill. Rotation is handled separately when `log.md` exceeds 500 entries.

## Step 11 — Verification

After writes:
- Re-read every created or patched wiki page.
- Confirm frontmatter fields are complete.
- Confirm minimum 2 outbound `[[wikilinks]]` resolve to existing pages; if not, either create stubs or report unresolved links as attention items.
- Confirm `index.md` contains the new entries.
- Confirm `log.md` contains exactly one new batch entry.
- Confirm no raw source files were modified.

## Step 12 — Report

Return a single structured report:

```
pages_created:
  - path/to/page.md
pages_updated:
  - path/to/page.md
index_delta: "<summary>"
log_entry_date: "YYYY-MM-DD"
skipped_findings:
  - "<finding summary> — skipped: <reason>"
contradictions: "<page list or none>"
attention_items:
  - "<unresolved wikilink or other issue>"
```

## Scope enforcement (must not do)

- No web search
- No arXiv queries
- No reading files outside:
  - the protocol/Schema/index/log/wiki target dirs
  - the assigned raw research intake dir
- No modifying files under `raw/`

## Pitfalls

- **Reading order matters**: SCHEMA → index → log → protocol → findings. Skipping this causes duplicate creation.
- **Workflow tag discipline**: every page must have exactly one workflow tag; missing or double workflow tags are lint errors.
- **Provenance markers are additive**: only set `provenancemarkers: true` when 3+ sources are synthesized; do not set for single-source pages.
- **Index drift**: never skip index.md update; it is the graph's entry point.
- **Log spam**: one entry per run, not one per page; otherwise log.md rots.
- **Contradictions are not deletions**: older claims stay with dates; new claims are added with dates.

## Related skills

- `team-wiki/setup` — wiki bootstrap conventions
- `team-wiki/maintain` — daily health checks
- `team-wiki/sync` — GBrain ↔ wiki sync
- `note-taking/obsidian` — file tool discipline
- `note-taking/obsidian-note-creation` — atomic page creation template
- `productivity/obsidian-vault-audit` — structural cleanup if pipeline drifts
