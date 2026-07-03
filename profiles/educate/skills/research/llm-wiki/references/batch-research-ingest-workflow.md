# Batch Research-and-Ingest Workflow

When the user asks to "research X and add it to the wiki" (vs. handing you a single source), the workflow is research-driven rather than source-driven. This is a common pattern for knowledge-gap filling.

## Workflow

1. **Orient** — read SCHEMA.md, index.md, recent log.md (standard)
2. **Research phase** — multiple `web_search` calls targeting different facets of the topic
   - Use `web_search_plus` with `mode='research'` if available (multi-provider synthesis)
   - Fall back to standard `web_search` (5-count) across 3-5 query variants
   - Run searches in parallel where possible
3. **Extract phase** — `web_extract` on the 3-5 most promising URLs (max 5 per call)
   - Prioritize primary sources (official docs, arxiv, engineering blogs) over aggregators
   - Two batches of 5 covers most research sessions
4. **Gap analysis** — compare extracted content against existing wiki pages
   - Read the `composes:` / `composed_by:` fields to understand what's already connected
   - Check index.md for existing coverage; `search_files` for unindexed pages
   - Present proposed pages to user with rationale (or proceed if user said "all of them")
5. **Ingest phase** — batch all new pages in one `execute_code` block
   - Save raw sources first (all at once)
   - Create all wiki pages (all at once)
   - Backfill `composed_by` on existing pages
   - Update index.md and log.md last
6. **Report** — table of what was created, cross-referenced, and updated

## Key Decisions

- **Page count:** 4-8 new pages is typical for a research pass. More than 10 suggests the topic should be split into multiple sessions.
- **Confidence:** Set `confidence: medium` for pages synthesized from web research alone (no primary papers). Set `high` only when multiple authoritative sources converge.
- **Workflow:** New pages start as `developing`, not `seedling` — they already have substance from the research.
- **Source naming:** Use descriptive slugs: `anthropic-context-engineering-2025.md`, not `source1.md`.

## Common Pitfalls

- **Research breadth vs depth:** 4 targeted searches beat 10 broad ones. Each search should have a distinct angle (e.g., "context engineering Anthropic", "context engineering techniques", "context engineering vs prompt engineering").
- **web_extract truncation:** Pages over 5000 chars get LLM-summarized. For critical sources, note that the extracted content may omit details.
- **Duplicate detection:** Always check the wiki BEFORE creating pages, not after. A page about "MCP" already exists — the new content may belong as an update, not a new page.
- **Cross-reference density:** Every new page needs 2+ outbound wikilinks. When creating 6 pages that all reference each other, the cross-linking happens naturally. When pages are on distinct subtopics, you need to explicitly link back to existing pages.
- **Batch creation of 5+ pages:** Do NOT create pages one at a time with `write_file` — each call adds latency and partial failures leave the wiki inconsistent. Use a single `execute_code` block with a Python dict of `{filename: content}` and a loop. This is atomic per script, faster, and lets you inject dynamic dates once. See "Batch Page Creation Technique" below.
- **Sequential patches to index.md after batch creation:** After creating N pages in execute_code, do the index.md and log.md updates in the SAME or immediately-following execute_code block. Mixing `patch` with `execute_code` write_file on index.md risks line-number prefix corruption.

## Variant: External Catalog Review

When the user points at a large structured source (awesome-list, knowledge base, curated repo like Library of Alexander, Papers With Code, etc.) rather than asking you to research from scratch:

1. **Delegate extraction** — spawn parallel subagents (one per relevant section/category) to extract and summarize. Pass the repo structure so each agent knows its section.
2. **Orient on wiki** — read SCHEMA.md, index.md, log.md (standard orientation).
3. **Gap analysis** — cross-reference extracted content against existing wiki pages. Present a categorized assessment:
   - HIGH PRIORITY: new pages worth creating (gaps in wiki coverage)
   - MEDIUM PRIORITY: existing pages to update (new data for known topics)
   - SKIP: out of domain, passing mentions, already covered
4. **Get approval** — present the assessment, let user choose scope ("all 7", "just the top 3", etc.)
5. **Batch create** — all new pages in one `execute_code` block (dict + loop pattern)
6. **Batch update existing pages** — read tails of target pages for anchors, apply updates via `execute_code` (read → modify → write, not `patch`)
7. **Batch navigation** — update index.md and log.md in one `execute_code` block
8. **Verify** — check page counts, index header, log tail for corruption

Key difference from research-driven ingest: the source is already structured and large (25 categories, 2500+ entries), so extraction is parallelized across subagents and the gap analysis is against a larger existing wiki.

## Example: Research-Driven (this session)

Research: AI & agentic AI topics for LLM-Wiki (70 pages → 76).

Searches: 4 parallel queries (agentic patterns, agent frameworks, A2A protocol, context engineering, agent security, framework comparison).

Extracted: 3 batches × 5 URLs = 10 raw sources saved.

Pages created:
- 4 concept pages (context-engineering, agent-to-agent-protocol, agent-security-architecture, agentic-ai-trends-2026)
- 2 comparison pages (agent-protocol-ecosystem, ai-agent-frameworks-2026)

Cross-references: 7 existing pages backfilled with `composed_by:`.

Total tool calls: ~25 (research) + ~15 (ingest) = ~40 for a 6-page research pass.

## Example: External Catalog Review

Source: Library of Alexander (github.com/Danielhogben/library-of-alexander) — 2500+ entries, 25 categories.

Extraction: 3 parallel subagents covering 10 sections (ai-models, coding-tools, ai-agents, local-llms, frameworks, vibe-code-audit, reverse-engineering, chinese-ai-ecosystem).

Gap analysis: Cross-referenced against 80 existing wiki pages. Identified 7 new pages + 3 existing page updates. Proposed to user with HIGH/MEDIUM/SKIP categorization.

Pages created (7): chinese-ai-ecosystem, model-landscape-2026, llm-inference-and-serving, agent-memory-systems, ai-security-and-red-teaming, computer-use-and-browser-agents, llm-routing-and-cost-optimization.

Pages updated (3): ai-agent-frameworks-2026 (+8 frameworks), vibe-coding (+spec-driven dev), hermes-security-posture (+red teaming tools).

Batch creation technique: single `execute_code` block with 7-entry Python dict, loop writing to `concepts/`. Index and log updated in a second `execute_code` block.

Total tool calls: ~5 (delegate) + 3 (read existing) + 1 (write raw) + 1 (create 7 pages) + 1 (update 3 pages) + 1 (index+log) + 1 (verify) = ~13 for a 7-page catalog ingest.

## Batch Page Creation Technique

When creating 5+ pages, use this pattern instead of individual write_file calls:

```python
import os
from datetime import date

WIKI = "/path/to/wiki"
TODAY = date.today().isoformat()

pages = {
    "page-slug-1.md": f"""---
title: Page Title 1
created: {TODAY}
updated: {TODAY}
type: concept
tags: [tag1, tag2]
sources: [raw/articles/source.md]
confidence: medium
topics: [cluster-name]
workflow: developing
---

# Page Title 1

Content with [[wikilinks]] to other pages.
""",
    "page-slug-2.md": f"""---
title: Page Title 2
...
""",
}

for filename, content in pages.items():
    path = os.path.join(WIKI, "concepts", filename)
    with open(path, 'w') as f:
        f.write(content.lstrip('\\n'))
    print(f"Created: concepts/{filename}")
```

Benefits:
- Single tool call for N pages (vs N write_file calls)
- Dynamic dates injected once via f-string
- Consistent frontmatter template across all pages
- Easy to review all content before execution

For index.md and log.md updates after page creation, use a second execute_code block that reads the file, modifies it, and writes it back — avoid mixing with patch.
