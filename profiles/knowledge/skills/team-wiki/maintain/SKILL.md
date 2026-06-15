---
name: team-wiki/maintain
description: Daily lint and health-check: orphans, broken links, index completeness, tag audit, log rotation
version: 1.0.0
author: Hermes Agent Team
license: MIT
metadata:
  hermes:
    tags: [team-wiki, maintain, lint, quality, gbrain]
    related_skills: [team-wiki/sync, team-wiki/setup, team-wiki/ingest]
---

# Team-Wiki Maintain

Daily maintenance routine for the Team-Wiki knowledge base. Detects and reports quality issues: orphaned pages, broken wikilinks, missing index entries, tag inconsistencies, and log rotation.

## Prerequisites

- Team-Wiki initialized (`team-wiki/setup` already run)
- `WIKI_PATH` environment variable set
- GBrain database available (for cross-referencing entity graph)

## Checks Performed

### 1. Orphan Detection (`gbrain find-orphans`)

Finds pages with zero inbound links — content nobody can discover via backlinks. Ideally every entity page is linked from at least 2 other pages.

**Action:** Report orphans; consider adding `[[links]]` from related pages or marking as meta-only (e.g., schema pages may be intentionally orphaned).

### 2. Broken Link Audit (`gbrain find-broken` or grep-based)

Scans all markdown files for `[[wikilinks]]` pointing to non-existent pages (missing target file or missing page entry). Case-sensitive; hyphenated filenames must match exactly.

**Action:** Create missing pages, fix typos in links, or remove dead references.

### 3. Index Completeness (`index.md` audit)

Verifies every entity page in `entities/` is listed in `index.md` under the correct alphabetical section. The index is the human-readable directory; it must stay current.

**Action:** Append new entities to index sections, alphabetize within section.

### 4. Tag Taxonomy Audit

Ensures all pages use tags from the approved `domain:item` set in `SCHEMA.md`. Flags:
- Unknown domain prefixes
- Misspelled tags
- Missing required tags (all pages must have at least one domain tag)

**Action:** Correct tags per SCHEMA; add new domain items to SCHEMA if legitimate.

### 5. Log Rotation

`log.md` is append-only. When it exceeds 500 entries, archive it:
- Rename current `log.md` → `log-YYYY-MM-DD-XXX.md` (incrementing counter)
- Start a fresh `log.md` with a header linking to the archive
- Keep last 30 days of archived logs; cull older ones to `4-Archive/` if desired

### 6. Frontmatter Validation

Checks every markdown file for required YAML frontmatter fields per page type:
- `title`, `created`, `updated`, `type`, `tags[]`, `sources[]`
- Ensures dates are valid ISO format (`YYYY-MM-DD`)
- Ensures `type` matches directory location

**Action:** Fix malformed frontmatter; add missing fields.

## Invocation

```bash
# Run all checks and generate a report
skill:team-wiki/maintain

# With explicit wiki path
skill:team-wiki/maintain --wiki-path ~/Hermes\ Vault/Hermes/Team-Wiki
```

## Output

Produces a plain-text report to stdout:
```
[maintain] Team-Wiki Health Check — 2026-04-25
=============================================
Orphans: 3
  - [[agent:architect]] (no inbound links)
  - [[company:37signals]] (no inbound links)
  - [[concept:rag]] (no inbound links)

Broken links: 2
  - [[peron:andrej-karpathy]] (typo in entities/people/)
  - [[skill:system-design]] (missing file)

Index gaps: 4 entities not in index
  - agent:debugger
  - company:openai
  - concept:pglite
  - project:hermes-workspace

Tag issues: 1
  - agent:<user> uses unknown domain 'agent-<user>' (should be agent:<user>)

Log rotation: not needed (473 entries)
```

## Automation

Schedule via Hermes cron (daily at 02:00):

```
/cron add "0 2 * * *" "skill:team-wiki/maintain" --name "team-wiki-daily-lint"
```

Or run manually after bulk ingest operations.

## Remediation

Some checks offer auto-fix flags (future):
- `--fix-orphans` — Suggest link targets based on content similarity
- `--fix-index` — Update `index.md` automatically
- `--fix-tags` — Normalize tags per SCHEMA (with `--dry-run` preview)

Currently, the skill reports only; human or an agent (Secretary) applies corrections.

## See Also

- `gbrain find-orphans` / `gbrain find-broken`
- `team-wiki/setup` (for SCHEMA reference)
- `team-wiki/sync` (to re-index after structural changes)
