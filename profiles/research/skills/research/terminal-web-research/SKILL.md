---
name: terminal-web-research
description: "Web research via curl when web tools are unavailable."
version: 1.0.0
author: Senna (Hermes)
license: MIT
metadata:
  hermes:
    tags: [research, web-scraping, curl, search-fallbacks, subagent, source-verification]
    category: research
    related_skills: [safe-web-research, research-pipeline, grounded-citations, research-methodology]
---

# Terminal-Only Web Research

Source-grounded web research using only `curl` — for subagents/sandboxes where
`web_search`/`web_extract` are not configured, or when configured search tools
fail. Validated 2026-08-11 on a podcast-research sweep (macOS, curl 8.x).

## When to Use

- You are a research subagent and `web_search`/`web_extract` are not in your toolset.
- Search tools exist but error out (subscription/rate-limit/blocked), and browser
  tools are unavailable.
- You must verify sources, quotes, or URLs for a source-grounded deliverable and
  need exact article URLs, not just snippets.

## Core rule

**Search engines block curl; article pages usually do not.** Once you have even
one candidate URL, stop searching and fetch the article directly with a desktop
browser UA. Direct fetches of nymag.com, usatoday.com, theguardian.com,
rollingstone.com, substack all succeeded while every search engine challenged
the same IP.

Use a full desktop UA, e.g.:
`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36`

## Search-engine fallback chain (tested with curl)

| Engine | Endpoint | Result | Detect block |
|---|---|---|---|
| DuckDuckGo HTML | `https://html.duckduckgo.com/html/?q=<urlencoded>` | Often "anomaly/challenge" page | `grep -c anomaly` |
| DDG lite | `https://lite.duckduckgo.com/lite/?q=` | Same challenge | same |
| Bing | `https://www.bing.com/search?q=` | captcha page | `grep -c captcha` |
| Mojeek | `https://www.mojeek.com/search?q=` | No parseable results | empty parse |
| **Brave** | `https://search.brave.com/search?q=` | **WORKS — reliable** | — |

Brave raw-HTML parse (no JS):
```python
import re, html
raw = <curl stdout>
links = []
for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"', raw):
    u = html.unescape(m.group(1))
    if any(x in u for x in ("brave.com", "braveusercontent", "reddit.com/", "youtube.com")):
        continue
    if u not in links: links.append(u)
snips = [re.sub(r"<[^>]+>", "", s).strip()[:200] for s in
         re.findall(r'<div class="snippet[^"]*"[^>]*>(.*?)</div>', raw, flags=re.S)]
```
Notes: DDG blocking is **transient** — an earlier run from the same IP produced
clean results; retry after 20-60s or switch to Brave. Sleep 2-3s between queries.

## URL discovery without a search engine

- **Wikipedia `?action=raw`** — `curl 'https://en.wikipedia.org/wiki/<Title>?action=raw'`
  returns wikitext with ALL citation URLs intact. Rendered HTML snapshots strip
  citation URLs into bare `[5]` footnotes — useless. This recovered an exact
  NYMag article URL after two guessed URL patterns 404'd.
- **Wayback CDX API** — find a real article URL from a known site-path prefix:
  `https://web.archive.org/cdx/search/cdx?url=<site>/<path>/*&output=text&limit=500&collapse=urlkey`
  then grep. `&filter=urlkey:.*<term>.*` works on small sets.
  - Do NOT use domain-wide `matchType=domain` (504 timeouts).
  - `archive.org/wayback/available?url=...` rate-limits fast (429); ≥20s between calls.
- **Decode saved DDG result pages** — DDG result links are redirects
  `//duckduckgo.com/l/?uddg=<urlencoded-target>`; recover targets with
  `urllib.parse.unquote(re.search(r'uddg=([^&]+)', href).group(1))`.

## Fetching & block detection

- Bulk-fetch many URLs in ONE script (ThreadPoolExecutor 5-8 workers, 3 retries,
  one curl subprocess per URL). See `scripts/fetch_strip_pages.py` for a
  ready-to-run fetcher+stripper (reads a slug→URL mapping, saves
  `pages/<slug>.html` + `pages/<slug>.txt`, retries, treats `<20KB` as failure).
- **Size thresholds:** real article pages were 100KB-1.8MB; Cloudflare/404/
  challenge shells were ~5-15KB. `< 20KB` ⇒ suspected block. Some outlets
  (Consumer Reports, Zendesk help pages, radiologybusiness.com, mediaite.com)
  return ~6KB JS-only shells even for correct URLs — stripped text of ~60 chars
  = blocked/JS-only; find the story syndicated elsewhere (yahoo.com, dnyuz.com).
- Strip recipe: remove `<script>`/`<style>` (flags=re.S), remove tags,
  `html.unescape`, collapse whitespace.
- **Paywalls:** article body truncates at the paywall even when the page fetches
  fully (NYMag cut mid-sentence). Don't read linearly — `str.find()` on key
  terms (names, dates, "spokesperson", "denies") and print ±1000-char windows.

## Pitfalls

- **Tool-call budget:** a research sweep easily hits a 50-call ceiling mid-write.
  Batch ALL fetches into one script call, run searches via one script, and write
  the deliverable file incrementally as sections finish — never defer the entire
  write to the end.
- **Don't trust memory of URLs/titles:** verify each URL (guessed URL patterns
  failed; CDX/`action=raw` found the real ones).
- **Frame transient blocks as retry-or-fallback**, never "engine X is broken" —
  a later run from the same IP may succeed.
- **Attribution discipline:** for each claim record outlet + author + date +
  access date; quoted spokespeople inside an article are the subject's response,
  not the outlet's position.
