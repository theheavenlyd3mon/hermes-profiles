---
name: llm-wiki
description: "Karpathy's LLM Wiki: build/query interlinked markdown KB."
version: 2.6.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative]
    category: research
    related_skills: [obsidian, arxiv, fabric-promote-review]
---

# Karpathy's LLM Wiki

Build and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki
compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**Division of labor:** The human curates sources and directs analysis. The agent
summarizes, cross-references, files, and maintains consistency.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base
- Asks to ingest, add, or process a source into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- References their wiki, knowledge base, or "notes" in a research context
- Asks to review past sessions, conversations, or chats for wiki-worthy material
- Asks to audit skills or tools for wiki-worthy knowledge
- Runs a scheduled/stale-page research task against wiki pages
- Asks to refresh, update, or renew aging wiki content
- **You surface, summarize, or analyze external content (GitHub repos, web articles, concepts, blog posts) for the user — proactively assess wiki-worthiness before the user asks "where does this go?"**

## Wiki Location

**Location:** Set via `WIKI_PATH` environment variable (e.g. in `~/.hermes/.env`).

If unset, defaults to `~/wiki`.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
```

The wiki is just a directory of markdown files — open it in Obsidian, VS Code, or
any editor. No database, no special tooling required.

## Architecture: Three Layers

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams referenced by sources
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
├── queries/            # Layer 2: Filed query results worth keeping
├── alloys/             # Layer 2: Narrative syntheses (essays, docs, exports)
└── _ghosts/            # Layer 2: Ghost note registry (optional — tracks links to non-existent pages)
```

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent.
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

## Resuming an Existing Wiki (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

⓪ **Verify the wiki path.** `$WIKI_PATH` in `.env` may be stale, wrong cased (macOS HFS+ masking), or point to a moved/deleted directory. Before reading any files, confirm the path exists:

```bash
ls -d "${WIKI_PATH}" 2>/dev/null || { echo "WIKI_PATH ($WIKI_PATH) does not exist — check .env for correct path"; }
```

If the path doesn't exist, search nearby directories for the actual location:
```bash
# Search for the vault directory containing the wiki
find "$(dirname "$WIKI_PATH")" -maxdepth 1 -type d -iname "*wiki*" 2>/dev/null
# Or search the whole vault for SCHEMA.md
find "~/Hermes Vault/Hermes" -maxdepth 3 -name "SCHEMA.md" 2>/dev/null
```

Common causes of WIKI_PATH mismatch:
- Case difference on macOS (e.g., env says `LLM-Wiki` but directory is `llm-wiki` — HFS+ hides this)
- Vault reorganization (wiki moved from `LLM-Wiki/` to `llm-wiki/`)
- Profile migration (env copied from another profile with different paths)

① **Read `SCHEMA.md`** — understand the domain, conventions, and tag taxonomy.
② **Read `index.md`** — learn what pages exist and their summaries.
③ **Scan recent `log.md`** — read the last 20-30 entries to understand recent activity.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
# Verify path exists before orientation reads
if [ -d "$WIKI" ]; then
  read_file "$WIKI/SCHEMA.md"
  read_file "$WIKI/index.md"
  read_file "$WIKI/log.md" offset=<last 30 lines>
else
  echo "WIKI_PATH=$WIKI not found — check .env or WIKI_PATH variable"
fi
```

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick `search_files` for the topic
at hand before creating anything new.

## Initializing a New Wiki

When the user asks to create or start a wiki:

1. Determine the wiki path — options in priority order:
   - From `$WIKI_PATH` env var if already set
   - Ask the user if they want it inside their existing Obsidian vault (recommended for multi-agent setups — see "Multi-Agent Integration")
   - Default: `~/wiki`
2. Create the directory structure (use individual paths, not shell brace expansion — see Pitfalls)
3. Ask the user what domain the wiki covers — be specific
4. Write `SCHEMA.md` customized to the domain (see template below)
5. Write initial `index.md` with sectioned header
6. Write initial `log.md` with creation entry
7. Confirm the wiki is ready and suggest first sources to ingest

### SCHEMA.md Template

Adapt to the user's domain. The schema constrains agent behavior and ensures consistency:

```markdown
# Wiki Schema

## Domain
[What this wiki covers — e.g., "AI/ML research", "personal health", "startup intelligence"]

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- **Provenance markers:** On pages that synthesize 3+ sources, append `^[raw/articles/source-file.md]`
  at the end of paragraphs whose claims come from a specific source. This lets a reader trace each
  claim back without re-reading the whole raw file. Optional on single-source pages where the
  `sources:` frontmatter is enough.
- **Composition fields:** Every page must set `composes:` and `composed_by:` in frontmatter to
  make the synthesis hierarchy explicit. A page that synthesizes existing knowledge lists those
  pages in `composes:`. Pages that build on this one are tracked in `composed_by:` (filled
  automatically when a higher-tier page lists it). This creates upward/downward traceability
  and exposes open dependencies — when `composes:` references a non-existent page, the wiki
  knows what wants to exist.
- **Ghost note practice:** When a page mentions a concept that deserves its own page, link to
  it even if it doesn't exist yet. These are ghost notes. When a ghost accumulates 3+ backlinks,
  promote it to a full page. The lint report surfaces ghosts by backlink count so growth is
  data-driven, not arbitrary.
- **Workflow-state in frontmatter:** Each page has a `workflow:` field indicating its maturity
  (seedling → developing → stable → needs-review → stale). This is distinct from topic tags.
  Lint uses workflow to surface pages that need attention.

## Frontmatter
  ```yaml
  ---
  title: Page Title
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: entity | concept | comparison | alloy | query | summary
  tags: [from topic taxonomy below]
  sources: [raw/articles/source-name.md]
  # Composition fields — what this page synthesizes and what builds on it
  composes: [other-page-slug]          # pages this page draws from ([[wikilinks]])
  composed_by: [higher-tier-page]      # pages that build on this — filled automatically
  topics: [cross-cutting-cluster]      # 2-4 broad topics for NEAR-clustering (singular nouns)
  workflow: seedling | developing | stable | needs-review | stale
  # Optional quality signals:
  confidence: high | medium | low        # how well-supported the claims are
  contested: true                        # set when the page has unresolved contradictions
  contradictions: [other-page-slug]      # pages this one conflicts with
  ---
  ```

`composes:`, `composed_by:`, `topics:`, and `workflow:` are the **self-building layer**.
- `composes:` — Creates compositional traceability. A page whose `composes:` references a
  non-existent page is signaling a ghost note that wants to be filled.
- `composed_by:` — Inverse of composes. Starts empty; gets filled when higher-tier pages
  list this page in their `composes:`. Enables upward navigation (what builds on this?).
- `topics:` — NEAR-clustering without requiring explicit wikilinks between every member.
  Two pages sharing `topics: [agent-orchestration]` are related even if they never link
  directly. Singular noun phrases (e.g., `knowledge-management`, not `knowledge management`).
- `workflow:` — Maturity indicator that drives lint prioritization. Seedling = just created,
  developing = active work area, stable = well-established, needs-review = potentially stale,
  stale = 90d+ without update.

`confidence` and `contested` are optional but recommended for opinion-heavy or fast-moving
topics. Lint surfaces `contested: true` and `confidence: low` pages for review so weak claims
don't silently harden into accepted wiki fact.

### raw/ Frontmatter

Raw sources ALSO get a small frontmatter block so re-ingests can detect drift:

```yaml
---
source_url: https://example.com/article   # original URL, if applicable
ingested: YYYY-MM-DD
sha256: <hex digest of the raw content below the frontmatter>
---
```

The `sha256:` lets a future re-ingest of the same URL skip processing when content is unchanged,
and flag drift when it has changed. Compute over the body only (everything after the closing
`---`), not the frontmatter itself.

**Computing sha256:** Use this one-liner after saving the raw file:
```bash
# Compute sha256 of the body (everything after first --- closing delimiter)
awk '/^---$/ {c++; next} c >= 2 {print}' raw/articles/source-file.md | shasum -a 256
# Or for the whole file (less precise but simpler):
shasum -a 256 raw/articles/source-file.md | awk '{print $1}'
```

## Tag Taxonomy

Two tiers: **workflow-state** (maturity indicators) and **topic tags** (domain classification).
Rules: every page must have one workflow value. Topic tags are optional but recommended.
All topic tags must come from the topic taxonomy below. Add new tags to this taxonomy BEFORE using them.

### Workflow-State Tags
- `seedling` — brand new page, needs development, may be a thin stub
- `developing` — actively worked on, being filled with research
- `stable` — well-established, cross-referenced, confidence high
- `needs-review` — potentially stale or contradicted by newer sources
- `stale` — 90+ days without an update despite being referenced by other pages

### Topic Tags

See `references/schema-second-brain-agent-knowledge.md` for a concrete example
with a 20-tag taxonomy covering agents, architectures, security, and research.

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. If a new tag is needed,
add it here first, then use it. This prevents tag sprawl.

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

## Entity Pages
One page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

## Alloy Pages

Narrative syntheses — essays, blog posts, documentation intended for an external audience.
Alloys draw from multiple concept/entity/comparison pages and transform them into a coherent,
export-ready narrative.

Include:
- Context / why this synthesis matters
- The claim or argument, grounded in wiki sources
- Direct references to source pages via `[[wikilinks]]`
- Audience note (who this is written for)
- Version / draft status

The alloy tier is the **payoff layer** — it proves the wiki's value by producing something
someone else can read. Without it, knowledge stays internal.

## Comparison Pages

Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report
```

### index.md Template

The index is sectioned by type. Each entry is one line: wikilink + summary.

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total pages: N

## Entities
<!-- Alphabetical within section -->

## Concepts

## Comparisons

## Alloys

## Queries
```

**Scaling rule:** When any section exceeds 50 entries, split it into sub-sections
by first letter or sub-domain. When the index exceeds 200 entries total, create
a `_meta/topic-map.md` that groups pages by theme for faster navigation.

### log.md Template

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, index.md, log.md
```

## Core Operations

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture the raw source:**
   - URL → use `web_extract` to get markdown, save to `raw/articles/`
   - PDF → use `web_extract` (handles PDFs), save to `raw/papers/`
   - Pasted text → save to appropriate `raw/` subdirectory
   - Name the file descriptively: `raw/articles/karpathy-llm-wiki-2026.md`
   - **Add raw frontmatter** (`source_url`, `ingested`, `sha256` of the body).
     On re-ingest of the same URL: recompute the sha256, compare to the stored value —
     skip if identical, flag drift and update if different. This is cheap enough to
     do on every re-ingest and catches silent source changes.

② **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)

③ **Check what already exists** — search index.md and use `search_files` to find
   existing pages for mentioned entities/concepts. This is the difference between
   a growing wiki and a pile of duplicates.

④ **Write or update wiki pages:**
   - **New entities/concepts:** Create pages only if they meet the Page Thresholds
     in SCHEMA.md (2+ source mentions, or central to one source)
   - **Existing pages:** Add new information, update facts, bump `updated` date.
     When new info contradicts existing content, follow the Update Policy.
   - **Cross-reference:** Every new or updated page must link to at least 2 other
     pages via `[[wikilinks]]`. Check that existing pages link back.
   - **Tags:** Only use tags from the taxonomy in SCHEMA.md
   - **Provenance:** On pages synthesizing 3+ sources, append `^[raw/articles/source.md]`
     markers to paragraphs whose claims trace to a specific source.
   - **Confidence:** For opinion-heavy, fast-moving, or single-source claims, set
     `confidence: medium` or `low` in frontmatter. Don't mark `high` unless the
     claim is well-supported across multiple sources.

⑤ **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically
   - Update the "Total pages" count and "Last updated" date in index header
   - Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
   - List every file created or updated in the log entry

⑥ **Report what changed** — list every file created or updated to the user.

A single source can trigger updates across 5-15 wiki pages. This is normal
and desired — it's the compounding effect.

### 2. Query

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also `search_files` across all `.md` files
   for key terms — the index alone may miss relevant content.
③ **Read the relevant pages** using `read_file`.
④ **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
⑤ **File valuable answers back** — if the answer is a substantial comparison,
   deep dive, or novel synthesis, create a page in `queries/` or `comparisons/`.
   Don't file trivial lookups — only answers that would be painful to re-derive.
⑥ **Update log.md** with the query and whether it was filed.

### 3. Session Review Ingest

When the user asks to review past conversations, sessions, or chat logs for wiki-worthy material:

① **Discover sessions:** Use `session_search` to find relevant sessions by keyword or date range.
② **Review session summaries:** Read the summaries to identify durable knowledge — decisions, architectures, workflows, entities, research findings.
③ **Filter for wiki-worthiness:** Not every session detail belongs in the wiki. Signals that a finding is wiki-worthy:
   - **Architectural decisions** with rationale (why X over Y)
   - **Entity information** about people, organizations, products, models
   - **Concepts or techniques** that took effort to discover or learn
   - **Configurations, conventions, or workflows** that would be painful to re-derive
   - **Contradictions or changes** in understanding over time
④ **Present to the user** as a categorized list of proposed additions with rationale. Do NOT create pages automatically — get approval first. This respects the user's curation role.
⑤ **On approval:** Ingest each approved item following the standard ingest process. If multiple items, batch them (one pass through existing pages, one index update, one log entry).

Signals that are NOT wiki-worthy:
- One-off command invocations (e.g., "run `npm install`")
- Transient debugging state (e.g., "the server was down for 5 minutes")
- Session meta (e.g., "the user was frustrated with the slow response")
- Content already captured in skills rather than knowledge (e.g., a tool fix belongs in a skill, not the wiki)
- Implementation-specific bug details (e.g., "Timer.connect() fix" — belongs in a skill, not the wiki)

### 3b. Fabric Promotion (Fabric → Wiki)

When the user asks to promote fabric (Icarus) entries to wiki pages — or when the
`fabric-promote-review` cron job has identified candidates and the user approves —
follow this workflow. This is distinct from Session Review Ingest: fabric entries
are already semi-structured (frontmatter, tags, summaries) rather than raw transcripts,
and the approval model is batch-based rather than per-item.

① **Assess fabric health first.** Before identifying candidates, run:
   - `fabric_report()` — note total entries, high-value count, and **usage rate**
   - If the usage rate is 0.0% (entries recalled but never linked), flag this in your
     output. The highest-leverage action may not be promotion — it may be closing the
     feedback loop by linking entries with `review_of`/`revises` fields. Usage rate <10%
     means the fabric is operating as a read-only archive rather than a learning system,
     and promotion candidates will be harder to evaluate without provenance links.

② **Identify candidates.** Find high-value completed fabric entries that aren't
   already covered by existing wiki pages:
   - Use `fabric_recall` with focused queries on the candidate topics
   - Check `fabric_report` for fabric health metrics (helps prioritize)
   - Cross-reference against the wiki's `index.md` to avoid duplicating existing pages
   - **Also cross-reference against the filesystem** — index.md may be out of date.
     Run `search_files` across content directories to catch unindexed pages (see
     Pitfalls: "Index drift from foreign creation context").

② **Recover full content.** Fabric entries stored in Icarus are often truncated at
   ~30 lines in the markdown files. Use multiple fallback strategies in order:
   - `fabric_recall` — the `_full` field contains the complete file content including
     body text below the frontmatter (preferred — richest source)
   - `lcm_grep` with session_scope='all' — search for unique phrases from the entry
     to find the original session that produced it, then drill in with `lcm_expand`
   - `session_search` — find the originating session for broader context
   
   If content is still truncated after these approaches, synthesize from what you have
   and flag the gaps — don't abandon the promotion.

③ **Check for multi-entry synthesis.** Multiple fabric entries often cover the same
   topic from different angles (e.g., a review entry + a deep-dive entry). Group related
   entries by topic and synthesize them into a single wiki page rather than creating
   N separate pages.

④ **Create wiki pages.** Follow standard Ingest steps ③-⑥ (existing page check,
   write/update, cross-reference, index update, log):
   - **Knowledge pages** (concepts, entities, comparisons) go in their respective
     content directories. Set `type: concept`, `workflow: seedling`, `confidence: medium`.
   - **Operational pages** (decisions, protocols, agent notes) go in
     `operational/decisions/`, `operational/protocols/`, etc. Set `type: summary`,
     `workflow: seedling`. Do NOT put operational content in `concepts/`.
   - List the fabric entry IDs in `sources:` as `[fabric:entry-id]`.
   - **composes backfill:** If the new page builds on an existing wiki page (e.g.,
     `multi-agent-topology` builds on `hermes-agent-team-architecture`), backfill
     `composed_by: [new-page-slug]` on the source page.
   - **Cross-links:** Minimum 2 outbound `[[wikilinks]]` per new page.
   - **Bulk updates:** Batch multiple promotions into one index update and one log entry.

⑤ **Update index.md.** Add new pages under the correct section, alphabetically.
   Bump the total page count and "Last updated" date in the index header.

⑥ **Log the promotion.** One log entry per batch, listing every file created or updated
   and the source fabric entry IDs:
   ```markdown
   ## [YYYY-MM-DD] create | Fabric → wiki promotion — N new pages
   - Agent: [agent-name]
   - Trigger: User request / cron promotion
   - Created: concepts/page-a.md — [one-line summary]
   - Created: concepts/page-b.md — [one-line summary]
   - Updated: concepts/existing-page.md — backfilled composed_by: [new-page-slug]
   - Updated: index.md — bumped to N pages, added N entries under [section]
   - Sources: fabric entries [entry-id-1], [entry-id-2]
   ```

**Approval model:** When the user says "if they are ready to be moved" or similar,
they're delegating readiness judgment to you. Check each candidate against standard
wiki-worthiness criteria (durable concept, not already covered, has substance beyond
a passing mention). If the entry is a `session` type with transient debugging detail,
it doesn't belong in the wiki. If it's a `decision` or `research` type with structured
findings, promote it. Report what you created after the fact rather than asking
per-item.

**Pitfall — truncated content:** Fabric entries in Icarus are stored as markdown files
whose body may be cut after ~30 lines. The `_full` field from `fabric_recall` often
contains the complete document. If even `_full` is truncated, use `lcm_grep` to locate
the original assistant output in the session that created the entry. The LCM database
preserves the full assistant message content.

**Pitfall — fabric tools not callable from cron context.** The Icarus plugin tools (`fabric_report`, `fabric_curate`, `fabric_search`, `fabric_recall`) are only available during interactive LLM sessions. In cron jobs, import the state module directly via `execute_code`: `from icarus import state`, then call `state.build_weekly_report()`, `state.search_entries()`, etc. See `references/fabric-cron-interaction.md` for the full pattern. Also, `search_entries` doesn't support `field:value` syntax — use `recall()` for semantic search or parse frontmatter from the filesystem.

**Pitfall — fabric_curate requires quoted entry IDs.** The `fabric_curate` tool expects entry IDs wrapped in literal quotes as part of the string parameter. IDs returned by `fabric_recall` appear as `"7902a715"` (with quotes in the JSON output), and `fabric_curate` needs those quotes included: pass `"7902a715"` (with the quotes as part of the parameter value), not `7902a715`. Passing the bare hex produces `"entry not found"`. This is inconsistent with other fabric tools that accept bare hex IDs. If `fabric_curate` returns "entry not found" on the first try, check whether you're including the quotes.

**Pitfall — unset training values invisible to fabric_search.** `fabric_report` may
report N entries with unset training values (e.g., `3 unset`), but `fabric_search`
cannot discover them individually. These entries don't have the field set to a value
of `"unset"` — the `training_value` field is simply absent from their frontmatter.
They are typically very recent session-type entries created before the fabric frontmatter
template was populated. If you lack filesystem access to the fabric directory (common in
cron contexts), note the count in your report and continue — unset entries represent <1%
of the corpus and self-correct as sessions age and get reassigned via `fabric_curate`.
Do not block the promotion review on curation of a handful of unset entries.

**Pitfall — wiki corpus saturation (steady state).** After repeated promotion cycles,
the wiki may reach a point where its coverage (number of pages, topic breadth) exceeds
the rate at which new durable knowledge enters the fabric. In this steady state, reviews
produce zero promotions and the task becomes a quick health check rather than a discovery
session. Recognize this pattern: if the wiki is at 50+ pages and the fabric corpus grew
<100 entries since the last review that produced a promotion, expect zero candidates. Skip
deep candidate investigation (fabric_recall, lcm_grep spelunking) when the count comparison
predicts zero hits — just confirm with a quick spot-check of the newest high-value entries
and deliver the report. This saves significant token cost (5-10 tool calls per review).

**Cron-friendly alternative:** For the fabric promotion workflow that runs in cron context (no interactive fabric tools), see the `fabric-promote-review` skill. It uses filesystem scanning via `search_files` instead of `fabric_report`/`fabric_curate`.

### 4. Lint

When the user asks to lint, health-check, or audit the wiki:

① **Orphan pages:** Find pages with no inbound `[[wikilinks]]` from other pages.
```python
# Use execute_code for this — programmatic scan across all wiki pages
import os, re
from collections import defaultdict
wiki = "<WIKI_PATH>"
# Scan all .md files in entities/, concepts/, comparisons/, queries/
# Extract all [[wikilinks]] — build inbound link map
# Pages with zero inbound links are orphans
```

② **Broken wikilinks:** Find `[[links]]` that point to pages that don't exist.

   **Cross-wiki validation:** When the wiki lives in a vault alongside another
   wiki (e.g., `Team-Wiki/` next to `LLM-Wiki/`), a wikilink may target a page
   in the other wiki. Before flagging as broken, check whether the slug exists
   in the sibling wiki's content directories. If a link spans wikis, note it as
   a **cross-wiki reference** rather than a broken link — it's valid, just not
   local. The lint report should separately list links that are genuinely broken
   (no match in any wiki) vs. cross-wiki references that work but cross boundaries.

③ **Index completeness:** Every wiki page should appear in `index.md`. Compare
   the filesystem against index entries.

④ **Frontmatter validation:** Every wiki page must have all required fields
   (title, created, updated, type, tags, sources). Tags must be in the taxonomy.

   **Common pattern — batch-created pages inherit wrong schema:** Pages created
   in bulk from skill reviews, session reviews, or source batch-ingests often
   carry their source's frontmatter fields instead of the wiki's required fields.
   The most frequent gap is the `type` field (missing on 6+ pages in one real
   batch) because skill SKILL.md files don't have `type: concept`. Other common
   gaps: `title` may be inferred from filename rather than set explicitly, and
   `sources` may be empty. When reviewing batch-created pages, always verify
   frontmatter conforms to the wiki SCHEMA, not the source format.

⑤ **Stale content:** Pages whose `updated` date is >90 days older than the most
   recent source that mentions the same entities.

⑥ **Contradictions:** Pages on the same topic with conflicting claims. Look for
   pages that share tags/entities but state different facts. Surface all pages
   with `contested: true` or `contradictions:` frontmatter for user review.

⑦ **Quality signals:** List pages with `confidence: low` and any page that cites
   only a single source but has no confidence field set — these are candidates
   for either finding corroboration or demoting to `confidence: medium`.

⑧ **Source drift:** For each file in `raw/` with a `sha256:` frontmatter, recompute
   the hash and flag mismatches. Mismatches indicate the raw file was edited
   (shouldn't happen — raw/ is immutable) or ingested from a URL that has since
   changed. Not a hard error, but worth reporting.

   **Pitfall — placeholder/fake hashes:** Stored SHA256 values that look like
   repeating hex patterns (e.g., `f15b61bb5a704b76...`, `a2520b1d3c8c9f4e...`,
   `b1c2d3e4f5a6b7c8...`), or the literal string `placeholder`, are NOT real
   digests — they were inserted as placeholders during initial ingestion before
   hash computation was standardized. If a `sha256` value matches another file's
   stored hash (impossible for real SHA256), or appears obviously patterned,
   flag it as **placeholder hash — needs real computation**, not as drift.
   Before computing the mismatch, validate the stored value looks like a real
   SHA256 hex digest (64 hex chars, no pattern repetition across files).

⑨ **Page size:** Flag pages over 200 lines — candidates for splitting.

⑩ **Tag audit:** List all tags in use, flag any not in the SCHEMA.md taxonomy.

   **Common pattern — generic tags from bulk creation:** `methodology`,
   `quality`, `testing`, `debugging`, `prototyping`, `exploration`, `planning`,
   `hermes` are not in most taxonomies. They come from skill frontmatter
   carrying over to wiki pages during batch ingests. When flagging these,
   suggest either (a) remap to taxonomy-equivalent tags (e.g., `methodology` →
   `workflow` or `concept`), or (b) add them to SCHEMA.md if the domain scope
   genuinely requires them. Prefer remapping — taxonomy discipline prevents clutter.

⑪ **Log rotation:** If log.md exceeds 500 entries, rotate it.

⑫ **Report findings** with specific file paths and suggested actions, grouped by
   severity (broken links > orphans > source drift > contested pages > stale content > style issues).

⑬ **Append to log.md:** `## [YYYY-MM-DD] lint | N issues found`

⑭ **Ghost note detection:** Find all broken `[[wikilinks]]` — these are candidate ghost notes.
   Count backlinks to each non-existent page and report the top 10 ghosts by backlink count.
   These are the pages the wiki itself has voted to prioritize. The lint report should list them
   separately from regular broken links, as "ghost notes (N backlinks)" so the operator knows
   which ghosts to promote to full pages first.

### 5a. Lint Fix Workflow (SHA256 Placeholder Recovery)

After lint detects placeholder SHA256 hashes in `raw/` sources, fix them with the companion script:

```bash
# Preview what would change (dry run)
python3 ~/.hermes/profiles/senna/skills/research/llm-wiki/scripts/fix-sha256-hashes.py "$WIKI" --dry-run

# Apply fixes
python3 ~/.hermes/profiles/senna/skills/research/llm-wiki/scripts/fix-sha256-hashes.py "$WIKI"
```

**When to run this:** The lint script (`scripts/wiki-lint.py`) flags placeholder hashes as `[INFO]` lines.
These appear when raw files were ingested before hash computation was standardized. The fix script
recomputes real SHA256 digests and rewrites the frontmatter in-place.

**What NOT to fix:** `[WARN] SHA256 mismatch` lines indicate real drift — the raw file was modified
after ingestion. Since `raw/` is immutable by convention, these require investigation (was the file
accidentally edited? did the source URL change?) rather than blind recomputation.

**Cron recipe for lint→fix→log→Notion:**
1. Run `wiki-lint.py` and capture output
2. If placeholder hashes found, run `fix-sha256-hashes.py` to recompute
3. Append findings to `log.md`
4. Log to Notion Agent Logbook (see `notion-agent-logbook` skill for the POST pattern)

**Reusable lint script:** `scripts/wiki-lint.py` in this skill's directory is a
complete, runnable lint implementation. It handles all 12 checks above, cross-wiki
link validation (`--sibling` flag), and SHA256 placeholder detection. Use it in
cron jobs instead of writing ad-hoc Python each time.

**Lint fix patterns:** `references/lint-fix-patterns.md` has quick-reference tables
for fixing each type of lint finding (broken links, index mismatches, low cross-refs,
source drift, tag issues). Consult it when acting on lint results.

- **Pitfall — lint script false positives on operational/ pages.** The `wiki-lint.py` script's index-completeness check scans top-level content directories (`entities/`, `concepts/`, `comparisons/`, `queries/`, `alloys/`) but does NOT recurse into `operational/` subdirectories (`operational/protocols/`, `operational/conventions/`, `operational/decisions/`, `operational/agents/`). Pages in `operational/` that are correctly listed in `index.md` will be flagged as `[WARN] '[[slug]]' in index.md but no page file`. Before acting on index-completeness warnings, verify the page doesn't exist under `operational/` with `search_files`. This false positive hit 2 pages in the 2026-06-03 lint pass (`cron-injection-scanner`, `notion-data-sources-api`).
- **Reference for Team-Wiki skeleton detection:** `references/team-wiki-lint-pattern.md`
documents the specific signals of an empty/skeleton Team-Wiki (README-only pages,
placeholder dates, broken index entries). Useful when linting co-located wikis in
the same vault.

**Reference for ecosystem architecture:** `references/wiki-ecosystem-architecture.md`
describes the full capture → curation → promotion → wiki pipeline, cron chains,
memory flow, and the operational/ section pattern. Essential reading when setting
up or debugging the overnight pipeline.

**Reference for HermesMirror project code review:** `references/hermes-mirror-code-review-notes.md`
captures common bugs found during module reviews (backoff conflation, shallow
mutation, missing defaults, stylelint BEM conflicts) and project rules for the
MagicMirror² fork at `~/projects/HermesMirror`.

### 5. Refresh (Stale Page Research)

Periodically refresh aging wiki pages with current research. Useful as a cron job or scheduled task. This is distinct from Ingest (which adds new sources) and Lint (which health-checks structure) — Refresh actively updates page content with new developments.

① **Find the stalest page.** Sort concept/entity pages by modification time to identify the page that hasn't been updated longest:

   ```bash
   # macOS (BSD stat):
   stat -f "%Sm %N" "$WIKI/concepts/"*.md | sort

   # Linux (GNU stat):
   stat -c "%y %n" "$WIKI/concepts/"*.md | sort

   # Alternative using ls (cross-platform):
   ls -lt "$WIKI/concepts/"*.md | tail -1
   ```

   Pick the oldest one by sorting ascending. Focus on one page per refresh cycle to keep research scope contained.

   **Tie-breaking:** If multiple pages share the same modification time (from a batch-backfill or bulk-creation event), prefer the one with no existing "## Updates" section — it is more likely to be genuinely stale. Check by reading frontmatter `updated` date or scanning for the Updates heading. If both have Updates sections, the one with the older frontmatter date is the true stalest.

② **Read the page's current content.** Use `read_file` to get the full markdown. Note the frontmatter `updated` date and `confidence` level — these tell you how stale the page is and how firmly its claims were held.

③ **Web research the topic.** Search for recent developments, corrections, or new information. Use `web_search` (or `web_search_plus` if available for deep/verbose results) with date range filters (past year, past 6 months) and dig into specific sources with `web_extract`. Look for:
   - New implementations, forks, or derivative work
   - Real-world adoption reports or case studies
   - Corrections, controversies, or evolved understanding
   - Enterprise/production adoption patterns

④ **Evaluate findings.** Not every search result is wiki-worthy. Ask:
   - Does the new finding add substantive depth beyond what the page already covers?
   - Is it a correction or contradiction to existing claims?
   - Is it a completed project or shipped product (not just an announcement)?
   - Is the finding grounded in multiple sources or real-world usage?

   If nothing meaningful was found, report that and skip the update.

⑤ **Append findings as an "## Updates" section.** Format:

   ```markdown
   ## Updates

   ### YYYY-MM-DD — Brief Headline
   
   [Concise factual paragraphs. Each finding gets its own paragraph or bullet.
   Include dates, version numbers, star counts for projects where relevant.
   Cite specific sources with ^[raw/articles/source-file.md] provenance markers
   when synthesizing from web search results.]
   ```

   **Concrete append technique:** Read the page with `read_file`, identify the very last line (or the last item in the final bulleted/listed section), then use `patch` to replace that line with the same line plus the new Updates content below it. This anchor guarantees uniqueness because it's the only occurrence of the final line. Example:

   ```bash
   # Identify the last content line of the file. For a page ending in:
   # - [[agent-failure-modes]] — the pitfalls that emerge
   # Use that exact line as the old_string, and the same line plus your new
   # ## Updates section as the new_string.
   ```

   **Critical rules:**
   - Do NOT rewrite or remove existing content — only append.
   - Do NOT merge updates into the body of the page. The "## Updates" section preserves what the page said at time of creation vs. what's known now.
   - Bump the `updated` date in frontmatter.
   - Do NOT add the original page's source file to `sources:` — the web research isn't a raw ingestion, it's a refresh.

⑥ **Log the action.** Append to `log.md`:

   ```markdown
   ## [YYYY-MM-DD] update | [page-name] — [brief research scope]
   - Agent: [agent-name] (cron)
   - Trigger: Scheduled stale-page research / user request
   - Researched: [topics/keywords searched]
   - Updated: [specific page path] — appended "## Updates" section with N findings areas; bumped updated date
   ```

**Cron recipe:** For the full stale-page research workflow as a scheduled cron job (discovery, selection, research cadence, Notion logging), see `references/cron-stale-page-research.md`.

   **Pitfall:** When appending to `log.md` with `patch`, the `old_string` anchor MUST be a sufficiently unique string that won't be consumed by neighboring entries. Prefer anchoring on the exact heading of the most recent existing entry, and include my new entry BEFORE that heading in the `new_string`. Verify the result after patching — if the next entry lost its heading, add it back with a second patch.

   **Additional pitfall — partial-read warning:** If `log.md` was previously read with `offset=`/`limit=` (partial view), `patch` will issue a warning: "was last read with offset/limit pagination. Re-read the whole file before overwriting it." The patch still applies correctly — the warning is advisory. To avoid confusion, either (a) accept the warning as benign, or (b) re-read the full file first. The patch result is identical either way.

   **Additional pitfall — read_file line-number bleeding into ANY write operation:** `read_file` output format is `LINE_NUM|CONTENT`, e.g. `66|- some bullet`. The line-number prefix and `|` delimiter are display formatting, NOT file content. This corrupts writes in THREE contexts:

   1. **`patch` anchors** — including the prefix in `old_string` produces malformed results (e.g. `|- ` instead of `- `).
   2. **`execute_code` with `hermes_tools.read_file` → `hermes_tools.write_file`** — the entire content passed to `write_file` carries the prefixes, and they get written into the actual file. This is the most dangerous variant because it silently corrupts the whole file.
   3. **`execute_code` with `hermes_tools.read_file` → string manipulation → `write_file`** — even intermediate processing doesn't help if the initial read included prefixes.

   **Fix for execute_code workflows:** Use raw Python `open()` for index.md and log.md manipulation inside `execute_code`, NOT the `hermes_tools.read_file` / `hermes_tools.write_file` wrappers. Example:

   ```python
   with open('/path/to/index.md', 'r') as f:
       content = f.read()
   # ... manipulate content ...
   with open('/path/to/index.md', 'w') as f:
       f.write(new_content)
   ```

   If you must use hermes_tools.read_file, strip prefixes before passing to write_file:
   ```python
   import re
   result = read_file(path="...")
   lines = result["content"].split('\n')
   clean = [re.sub(r'^\s*\d+\|', '', l) for l in lines]
   ```

   **Detection:** After any index.md or log.md write, run `head -5` via terminal to verify no line-number prefixes leaked in. If you see `     1|# LLM Wiki Index` instead of `# LLM Wiki Index`, the file is corrupted — strip and rewrite.

   **Pitfall — `hermes_tools.read_file` KeyError in execute_code:** When `read_file` fails (file too large, path error, permission issue), the returned dict has no `content` key — only an error field. Accessing `result["content"]` raises `KeyError`. This is easy to miss because `read_file` normally succeeds. **Defense:** Always use raw Python `open()` for files you intend to read-modify-write inside `execute_code`, not `hermes_tools.read_file`. This avoids both the line-number prefix problem AND the KeyError-on-failure problem in one move:

   ```python
   with open('/path/to/file.md', 'r') as f:
       content = f.read()
   # ... manipulate ...
   with open('/path/to/file.md', 'w') as f:
       f.write(new_content)
   ```

   **Pitfall — patch replace_all=True creates corrupt duplicates on log files:** Using `patch` with `replace_all=True` on a log file where the `old_string` appears multiple times causes both instances to be replaced with the combined content — producing pipe-prefixed (`|`) lines and duplicated entries. This happens because patch applies the replacement to EVERY match, including the one that was already correctly written in a previous operation. **Rule for log appends: prefer `execute_code` with Python over `patch` for appending to `log.md`.** The Python approach reads the full file, appends new content as a string, and writes it back — no anchor uniqueness issues, no pipe-prefix corruption, no replace_all hazards:

   ```python
   with open('/path/to/log.md', 'r') as f:
       content = f.read()
   # Remove any pipe-prefixed lines that were introduced by prior corrupt patches
   lines = [l for l in content.split('\n') if not l.startswith('|')]
   # Trim trailing blank lines
   while lines and lines[-1].strip() == '':
       lines.pop()
   # Append new entry properly (no pipe prefix)
   lines.append('')
   lines.append('## [YYYY-MM-DD] action | Subject')
   lines.append('- Detail line with proper dash prefix')
   with open('/path/to/log.md', 'w') as f:
       f.write('\n'.join(lines) + '\n')
   ```

   Reserve `patch` for log.md only when the operation is a true in-place edit (replacing a specific string already inside the file, not appending). For appending, always use the Python approach.

### 6. Proactive Capture (Unprompted Wiki Discovery)

When you surface, summarize, or analyze external content for the user — a GitHub repo, web article, blog post, concept, or research finding — automatically evaluate wiki-worthiness before the user asks "where does this go?" This bridges the gap between research and knowledge compounding.

**Trigger conditions:** You've just used `web_extract`, `web_search`, or otherwise summarized external content. Before delivering the final summary, run a quick wiki-worthiness filter:

① **Evaluate against threshold:**
   - Does the content describe a durable concept, entity, comparison, or technique? (Not a transient announcement or one-off bug report.)
   - Is it central to the wiki's domain (LLM agents, tools, architectures, security, research)?
   - Would a future self benefit from rediscovering this without re-reading the original source?

   If yes to 2+ questions, it's wiki-worthy.

② **Propose placement with reasoning:**

   ```markdown
   **Wiki-worthiness assessment:** [threshold verdict]
   - Proposed page: `concepts/` or `entities/` or `queries/` — [page-slug]
   - Rationale: [one-line why it fits the wiki's domain]
   - Cross-links to: [[existing-page-1]], [[existing-page-2]]
   ```

   Include this as a tagged-on section after the summary, not a separate message. The user should see the analysis and the wiki signal in one read.

③ **Offer to ingest or defer:**
   - If the content clearly passes threshold: "Want me to capture this in the wiki?"
   - If borderline: flag it briefly and let the user decide.

④ **On approval, follow the standard Ingest process** (steps ①-⑥ above). Batch multiple sources from the same research session into one ingest pass.

**Crucial distinction from Ingest:** Ingest is a *reactive* operation — the user hands you a source and says "put this in." Proactive Capture is *anticipatory* — you recognize wiki-worthy content during your own research and flag it unprompted. The user's pattern (proactively suggesting LLM-wiki) tells you they expect this from you.

**Pitfall — don't over-capture.** Not every interesting URL is wiki-worthy. A tweet thread, a release announcement, a changelog, a quick debugging tip — these belong in memory or skills, not the wiki. Reserve capture for knowledge that would be painful to re-derive.

## Working with the Wiki

### Searching

```bash
# Find pages by content
search_files "transformer" path="$WIKI" file_glob="*.md"

# Find pages by filename
search_files "*.md" target="files" path="$WIKI"

# Find pages by tag
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# Recent activity
read_file "$WIKI/log.md" offset=<last 20 lines>
```

### Bulk Ingest

When ingesting multiple sources at once, batch the updates:
1. Read all sources first
2. Identify all entities and concepts across all sources
3. Check existing pages for all of them (one search pass, not N)
4. Create/update pages in one pass (avoids redundant updates)
5. Update index.md once at the end
6. Write a single log entry covering the batch

- **For research-driven ingests** (user asks to "research X and add to wiki" rather than handing a source), see `references/batch-research-ingest-workflow.md` for the full workflow: parallel searches → extract → gap analysis → batch ingest.
- **For freestyle / topic-selection passes** (user says "pick N topics in {domains} and run the full pipeline"), see the "Freestyle / Topic-Selection Research Pass" variant in that same reference: gap analysis leads (pick topics with no existing page), then parallel sweep, raw `sha256` capture with the `__COMPUTE__` batch technique, and batch ingest. Watch for the cron-category coverage gap.
- **For external catalog review** (user points at a large structured source like an awesome-list, knowledge base, or curated repo), see the "External Catalog Review" variant in the same reference file. Key difference: the source is already structured, so the workflow is delegate-extract → gap-analyze → batch-create rather than search → extract → create.

### Archiving

When content is fully superseded or the domain scope changes:
1. Create `_archive/` directory if it doesn't exist
2. Move the page to `_archive/` with its original path (e.g., `_archive/entities/old-page.md`)
3. Remove from `index.md`
4. Update any pages that linked to it — replace wikilink with plain text + "(archived)"
5. Log the archive action

### Obsidian Integration

The wiki directory works as an Obsidian vault out of the box:
- `[[wikilinks]]` render as clickable links
- Graph View visualizes the knowledge network
- YAML frontmatter powers Dataview queries
- The `raw/assets/` folder holds images referenced via `![[image.png]]`

For best results:
- Set Obsidian's attachment folder to `raw/assets/`
- Enable "Wikilinks" in Obsidian settings (usually on by default)
- Install Dataview plugin for queries like `TABLE tags FROM "entities" WHERE contains(tags, "company")`

If using the Obsidian skill alongside this one, set `OBSIDIAN_VAULT_PATH` to the
same directory as the wiki path.

### Obsidian Headless (servers and headless machines)

On machines without a display, use `obsidian-headless` instead of the desktop app.
It syncs vaults via Obsidian Sync without a GUI — perfect for agents running on
servers that write to the wiki while Obsidian desktop reads it on another device.

**Setup:**
```bash
# Requires Node.js 22+
npm install -g obsidian-headless

# Login (requires Obsidian account with Sync subscription)
ob login --email <email> --password '<password>'

# Create a remote vault for the wiki
ob sync-create-remote --name "LLM Wiki"

# Connect the wiki directory to the vault
cd ~/wiki
ob sync-setup --vault "<vault-id>"

# Initial sync
ob sync

# Continuous sync (foreground — use systemd for background)
ob sync --continuous
```

**Continuous background sync via systemd:**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=/home/user/wiki
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# Enable linger so sync survives logout:
sudo loginctl enable-linger $USER
```

This lets the agent write to `~/wiki` on a server while you browse the same
vault in Obsidian on your laptop/phone — changes appear within seconds.

## Multi-Agent Integration (Hermes Ecosystem)

When the wiki lives inside a shared Obsidian vault that multiple agents access,
additional patterns apply:

### Wiki Inside an Existing Vault

The wiki can be a subdirectory of an existing vault rather than a standalone
directory. This enables `[[wikilinks]]` between wiki pages and project notes,
and all agents automatically have access via `OBSIDIAN_VAULT_PATH`.

**Setup steps (variant of Initializing a New Wiki):**

1. Put the wiki INSIDE the vault: `$VAULT/LLM-Wiki/`
2. Set `WIKI_PATH` in `~/.hermes/.env` to match
3. Agents resolve the path from the env var — no extra config per agent

```bash
# In ~/.hermes/.env:
WIKI_PATH="/Users/name/Obsidian Vault/LLM-Wiki"
```

### Agent Role Boundaries

In a multi-agent setup with role specialization:

- **All agents read the wiki** — it's a shared knowledge resource available to
  every profile via the vault path
- **Secretary agent** owns `index.md` and `log.md` maintenance. Other agents
  create/update knowledge pages; Secretary handles navigation upkeep
- **Durable facts from Icarus** — fabric entries that survive multiple sessions
  should be promoted to wiki pages. If an entry refers to a concept the wiki
  already covers, update the wiki page instead of creating a new fabric entry

### Team-Wiki vs LLM-Wiki Boundary

**Note: Unified Wiki Pattern (2026-05-13).** Originally, vaults maintained separate `Team-Wiki/` (operational) and `LLM-Wiki/` (knowledge) directories with different tag taxonomies and schemas. This created coordination overhead, cross-wiki link management, and inconsistent conventions. The recommended pattern is now: **unify into a single wiki** with an `operational/` section.

**Unification approach:** Add `operational/` as a top-level directory inside the wiki with subdirectories for `agents/` (per-agent scratch spaces), `protocols/` (handoff rules, kanban workflow), `conventions/` (standards, style guides), and `decisions/` (architectural decisions with rationale). Update the SCHEMA.md to document operational page types. Archive the old Team-Wiki directory (strip `.git` when moving). Update `index.md` to include an Operational section.

**If the vault still has a separate `Team-Wiki/`:**
- **Team-Wiki = operational** — agent handoffs, protocols, conventions,
  architecture decisions, team member profiles
- **LLM-Wiki = knowledge** — concepts, research, entities, comparisons,
  domain knowledge
- They cross-link via `[[wikilinks]]` where useful (e.g., a Team-Wiki protocol
  page links to a concept page in LLM-Wiki that explains the underlying technique)
- **But prefer merging** — the operational content belongs in the same wiki at `operational/`.

**Confirmed merged (2026-06-08):** In this environment, Team-Wiki has been archived
to `4-Archive/Team-Wiki-archive/` and its content merged into `llm-wiki/operational/`.
The `--sibling` cross-wiki lint flag and the `team-wiki-lint-pattern.md` reference
are retained for historical/multi-vault use but are not needed for this vault's
routine lint. Lint false-positive warnings about `operational/` pages (e.g.,
`cron-injection-scanner`, `notion-data-sources-api`) are expected — the lint script
does not recurse into `operational/`.

### .env Variable Convention

All Hermes profiles should set these for wiki-aware agents:

| Variable | Purpose |
|----------|---------|
| `WIKI_PATH` | Absolute path to the wiki (inside or outside vault) |
| `OBSIDIAN_VAULT_PATH` | Parent vault path (if wiki is inside a vault) |


## Pitfalls

- **Shell brace expansion on macOS:** When creating the directory structure, write each path as a separate argument to `mkdir -p`. Shell brace expansion (`mkdir -p {a,b,c}`) may create literal directories named `{a,b,c}` depending on the execution context. Always use explicit paths:

  ```bash
  mkdir -p "wiki/raw/articles" "wiki/raw/papers" "wiki/raw/transcripts" "wiki/raw/assets" \
           "wiki/entities" "wiki/concepts" "wiki/comparisons" "wiki/queries"
  ```

  Or call `mkdir -p` once per path. Verify the structure with `find` afterward.

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log before any operation in a new session.
  Skipping this causes duplicates and missed cross-references.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md. A name
  appearing once in a footnote doesn't warrant an entity page.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to SCHEMA.md
  first, then use them.
- **Sequential patches to index.md create duplicate entries.** When adding multiple entries to
  `index.md`, each `patch` call targets the current file state. Patch #1 inserts at position X,
  shifting content down; patch #2's `old_string` still references the pre-patch position, so the
  entry lands in the wrong spot or survives in two places. **Fix:** Batch all index additions into
  **one** `patch` call. For 3+ entries, use `execute_code` with Python to rewrite the entire
  section — append a string block to the file content and `write_file` it back. Reserve `patch`
  for single-entry additions to index.md only.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.
- **Patch-anchor uniqueness in log.md** — when appending to `log.md` with the `patch` tool, the
  `old_string` must be unique enough that it only matches the intended anchor text. Using a heading
  like `## [YYYY-MM-DD] action | title` as the anchor risks consuming the same string from the
  next entry. Instead, include a few surrounding lines (blank lines and adjacent formatting) in
  the anchor to guarantee uniqueness. After patching, always verify the result — if a neighboring
  entry lost its heading, add it back with a follow-up patch.
- **Don't create pages for every ghost note** — wait for the 3-backlink threshold. A ghost with
  1-2 backlinks is a signal to track, not to act. Creating pages for single-mention ghosts
  bloats the index the same way creating pages for passing mentions does. The lint report's
  ghost-note section tells you when a ghost has crossed the threshold.
- **Index drift from foreign creation context** — Pages created by agents or processes that
  don't load the wiki skill (vault triage, icarus extraction, session review by non-Secretary
  profiles, one-off user-directed creation) frequently skip index.md and log.md registration.
  The page exists on disk but nothing references it — it's an orphan that didn't go through
  standard ingest. **Detection:** During lint step ③ (index completeness), compare the full
  list of `.md` files in each content directory against index entries. Flag any page that
  exists on filesystem but not in index.md. **Prevention:** When creating a page outside the
  wiki operation flow, either load the wiki skill before writing, or add the page to index.md
  and log.md as a follow-up step. If you're not sure whether the creating agent loaded the
  wiki skill, run a post-creation index check.
- **Operational directory emptiness** — The `operational/` section is declared in SCHEMA.md
  and referenced in index.md, but its subdirectories (`agents/`, `protocols/`, `conventions/`,
  `decisions/`) may be completely empty for long periods. This is not a bug — it's a staging
  area that fills organically. The lint check should NOT flag empty operational directories as
  errors; they are placeholder structures that signal intent. Flag them only if SCHEMA.md
  mentions operational content that doesn't exist yet AND the referenced subdirectory has no
  files after 30+ days.
- **WIKI_PATH case-sensitivity drift** — On macOS, HFS+ (APFS) is case-insensitive by
  default, so `WIKI_PATH=/path/LLM-Wiki` works even when the actual directory is `llm-wiki`.
  On Linux, this silently breaks — `ls -d /path/LLM-Wiki` returns nothing, and all subsequent
  reads fail. **Detection:** During orientation step ⓪, compare the `ls -d` output path
  against `$WIKI_PATH`. If they differ by case, fix the env var:
  ```bash
  # Find the real path
  real_path=$(find "$(dirname "$WIKI_PATH")" -maxdepth 1 -type d -iname "$(basename "$WIKI_PATH")" 2>/dev/null)
  echo "WIKI_PATH should be: $real_path"
  ```
  **Prevention:** When initializing a wiki inside a vault, note the exact directory name
  from `ls` output, not from Obsidian's display name.

## Related Tools

[llm-wiki-compiler](https://github.com/atomicmemory/llm-wiki-compiler) is a Node.js CLI that
compiles sources into a concept wiki with the same Karpathy inspiration. It's Obsidian-compatible,
so users who want a scheduled/CLI-driven compile pipeline can point it at the same vault this
skill maintains. Trade-offs: it owns page generation (replaces the agent's judgment on page
creation) and is tuned for small corpora. Use this skill when you want agent-in-the-loop curation;
use llmwiki when you want batch compile of a source directory.

## References

- `references/fabric-cron-interaction.md` — How to interact with Icarus fabric from cron/execute_code context (direct Python import pattern)
