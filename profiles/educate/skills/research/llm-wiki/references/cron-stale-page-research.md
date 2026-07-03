# Cron Stale-Page Research Workflow

Recipe for the scheduled wiki refresh pass. Runs as a cron job with no user interaction.

## Scope

Research and update 3-4 stale or seedling wiki pages per cycle. Keeps cost ~$0.10-0.15 and stays within a single cron turn.

## Discovery (execute_code)

Find candidate pages by modification age and line count:

```python
import os, datetime

wiki = "/Users/noctis/Hermes Vault/Hermes/llm-wiki"
pages = []
for subdir in ["concepts", "entities", "comparisons", "alloys"]:
    dirpath = os.path.join(wiki, subdir)
    if not os.path.exists(dirpath):
        continue
    for f in os.listdir(dirpath):
        if not f.endswith('.md'):
            continue
        fp = os.path.join(dirpath, f)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fp))
        with open(fp, 'r') as fh:
            lines = len(fh.readlines())
        # Read frontmatter for workflow/confidence
        with open(fp, 'r') as fh:
            head = fh.read(500)
        pages.append({
            'path': fp, 'file': f, 'dir': subdir,
            'mtime': mtime, 'age_days': (datetime.datetime.now() - mtime).days,
            'lines': lines,
            'seedling': 'workflow: seedling' in head,
            'low_conf': 'confidence: low' in head,
        })

# Prioritize: seedlings first, then by age
pages.sort(key=lambda x: (not x['seedling'], -x['age_days']))
```

### Selection criteria (in priority order)
1. `workflow: seedling` pages — explicitly marked as needing development
2. Pages >14 days old with <100 lines — likely stubs
3. Pages with `confidence: low` — weak claims need corroboration
4. Index entries without a summary line (no `—` after the wikilink)
5. Pages with duplicate sections or structural issues

### Skip conditions
- Pages >200 lines and `workflow: stable` — already well-developed
- Pages updated in last 7 days — too recent to be stale
- Operational pages (`operational/`) — not knowledge pages

## Research (web_search + web_extract)

For each candidate page:
1. Read the page content
2. `web_search` with 2-3 queries on the topic (include "2026" for currency)
3. `web_extract` the top 1-2 most promising URLs
4. Evaluate: does the finding add substantive depth beyond what the page already covers?

### What counts as wiki-worthy
- New implementations, tools, or frameworks in the space
- Quantified adoption metrics, benchmarks, or case studies
- Corrections or contradictions to existing claims
- Industry coverage (blogs, conference talks) confirming or extending the page's thesis

### What to skip
- Marketing content without substance
- Duplicates of information already on the page
- Announcements without shipped products/results

## Update pattern

Append an `## Updates` section to each refreshed page:

```markdown
## Updates

### YYYY-MM-DD — Brief Headline

[Concise factual paragraphs with provenance markers.]
^[source-domain.com/article-path]
```

Rules:
- **Append only** — never rewrite or remove existing content
- **Bump `updated` date** in frontmatter
- **Do NOT add** web research URLs to `sources:` — those are for raw ingestions
- Use provenance markers `^[source]` on paragraphs drawing from specific sources

## Index and log hygiene (while you're there)

During the research pass, also fix:
- Missing summary lines in index.md (entries without `—` after wikilink)
- Duplicate sections in any page encountered
- Out-of-date "Last updated" date in index.md header

Batch all index fixes into one `patch` call. Use Python for log.md appends:

```python
with open(log_path, 'r') as f:
    content = f.read().rstrip()
with open(log_path, 'w') as f:
    f.write(content + "\n\n## [YYYY-MM-DD] update | ...\n- ...\n")
```

## Notion logging

After research, log to all 3 Notion databases (Agent Logbook, Research Vault, Cost Tracker).
Use the temp-file-then-curl pattern — write JSON payloads to `/tmp/notion_*_payload.json`,
then `curl -d @/tmp/notion_*_payload.json`. Clean up temp files after.

## Cost target

~$0.10-0.15 per pass (3-4 pages × 2-3 searches + extractions + updates + 3 Notion writes).
