---
name: wiki-health-check
description: "Periodic wiki maintenance pass: broken links, orphans, stubs, duplicates, SHA256 drift, tag audit."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wiki, maintenance, cron, audit, health-check]
    category: devops
    related_skills: [llm-wiki, wiki-ingest, wiki-lint]
---

# Wiki Health Check

Run periodic health checks on the LLM Wiki to catch and fix structural issues before they compound.

## When to Run

- As a daily/weekly cron job
- After major content additions (bulk ingests)
- Before archiving or splitting the wiki

## Check List

1. **Broken wikilinks** — links to non-existent pages
2. **Orphan pages** — no inbound links from other pages
3. **Incomplete sections (stubs)** — pages missing core content
4. **Duplicate content** — overlapping pages on same topic
5. **Tag drift** — out-of-taxonomy tags
6. **Source SHA256 drift** — raw source files modified after ingestion
7. **Page size** — pages over 200 lines are candidates for splitting
8. **Log rotation** — log.md exceeds 500 entries

## Lint Script

Use `scripts/wiki-lint.py` from the llm-wiki skill. It implements all 12 checks above:

```bash
WIKI_PATH="${WIKI_PATH:-~/wiki}"
python3 "$WIKI_PATH/scripts/wiki-lint.py" "$WIKI_PATH"
```

The script outputs:
- Check results (OK or issues found)
- File paths for issues
- Suggested actions

## Fix Workflow

1. Run lint
2. Read lint output
3. For each issue category:
   - **Broken links** → create missing pages or replace with plain text
   - **Orphans** → add inbound links from related pages or promote ghost notes
   - **Stubs** → expand with additional research
   - **Duplicates** → merge content, keep best version
   - **Tag drift** → update tags to match taxonomy or expand taxonomy
   - **SHA256 drift** → verify raw source hasn't been modified; recompute if placeholder
   - **Large pages** → plan split into sub-topics
4. Re-run lint to verify fixes
5. Update index.md and log.md
6. Log results to Notion Agent Logbook (database ID: `9dc914a6-6736-40af-a0b9-d1af9fc5e8a1`)

## Notion Logging

After fixes, log to Notion Agent Logbook:

```python
# Payload structure (adjust property names to match your schema)
payload = {
    "parent": {"database_id": "9dc914a6-6736-40af-a0b9-d1af9fc5e8a1"},
    "properties": {
        "Name": {"title": [{"text": {"content": "Wiki health check: YYYY-MM-DD"}}]},
        "Agent": {"select": {"name": "cron"}},
        "Type": {"select": {"name": "task"}},
        "Date": {"date": {"start": "YYYY-MM-DD"}},
        "Status": {"select": {"name": "completed"}},
        "Tags": {"multi_select": [{"name": "wiki"}, {"name": "maintenance"}]},
        "Cost": {"number": 0.05},
        "Summary": {"rich_text": [{"text": {"content": "Summary of checks and fixes"}}]}
    }
}
```

## Related

- `llm-wiki` — the core knowledge compounding pattern
- `wiki-ingest` — adding new sources
- `wiki-lint` — comprehensive lint implementation (same script as this skill uses)
- `notion-agent-logbook` — logging agent activities to Notion
