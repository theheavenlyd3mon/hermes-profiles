---
name: llms-txt-mirroring
description: Use when bulk-pulling llms.txt knowledge bases to markdown.
---

# llms-txt-mirroring

Bulk-mirror an llms.txt knowledge base to local Markdown. Sites following the
llms.txt convention (agentwikis.com, many agent-facing doc sites) publish a
machine-readable catalog at `/llms.txt` and serve every page as raw Markdown
at `/raw/<wiki>/<path>`. No browser, no scraping, no HTML cleanup — just
parallel curl.

## When to use
- User asks to "pull", "mirror", or "save" a wiki/knowledge base that exposes llms.txt (agentwikis.com is the canonical case; check any agent-doc site for `/llms.txt` first).
- User wants a large set of doc pages locally for offline reading, RAG, or diffing against another source.
- NOT for gated/anti-bot content — that's `gated-content-retrieval` (xurl, Browserbase).

## Steps
1. **Fetch the catalog.** `curl -s https://<site>/llms.txt`. This lists every
   wiki + every page as `/raw/<wiki>/<path>.md` links, with scope/freshness
   frontmatter per wiki. Save as `catalog-llms.txt`.
2. **Extract page paths.** `grep -o '/raw/[a-z0-9-]*/[^)]*\.md' catalog-llms.txt | sort -u > all-pages.txt`. Count with `wc -l` — this is the expected total.
3. **Parallel download.** Use `scripts/mirror-llms-txt.sh <llms.txt-url> [dest_dir]` — 12 workers via xargs -P pulled 1,479 pages in ~37s with zero failures.
4. **Verify.** Downloaded `.md` count must equal the expected count; zero-byte files must be 0. Report both numbers.
5. **Read the right pages.** Per-wiki `README.md` is often boilerplate (the
   Karpathy "LLM Wiki" template — layers raw/ vs wiki/, ingest ops). The real
   catalog is `<wiki>/wiki/index.md` (master index with per-page list and
   confidence/freshness). Content pages live under `wiki/concepts/`,
   `wiki/syntheses/` (decision pages — usually the highest-value), `wiki/summaries/`.

## Pitfalls
- Don't `web_extract` the HTML landing page expecting full content — llms.txt is the canonical agent entry point and gives every URL in one fetch.
- Some wikis have an EMPTY `README.md` (hyperframes) — check `index.md`, not the README, when a wiki looks blank.
- XL/Pro tier pages are gated: the free raw endpoints only serve the base tier. Indexes will reference XL pages that 404 or are absent — that's expected, not a broken pull.
- Frontmatter on each page carries `updated`, `confidence`, and version/build pins — use it for freshness claims rather than trusting the landing page.
- `xargs -P` without `-n 1 -I{}` plus a function export is the reliable pattern for parallel curl with per-item destination dirs.

## Support files
- `scripts/mirror-llms-txt.sh` — generalized mirror script (llms.txt URL + dest dir).
- `references/agentwikis-com.md` — agentwikis.com catalog snapshot: 51 wikis, page counts, local mirror location, and scope notes for the key wikis.
