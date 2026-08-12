---
name: gated-content-retrieval
description: Notes on fetching web content ordinary scrapers cannot reach — the xurl article API and the Browserbase dual-control browser session.
---

# gated-content-retrieval

Reference notes for pulling web content when normal scrapers return empty,
timeout, or say "not supported" on a protected URL.

## xurl article API (no browser)
`xurl` can fetch an X Article body: request `tweet.fields=article` on
`/2/tweets/<ID>` and read `data.article.plain_text` (+ `.title`).

Watch out: `xurl` may print a non-JSON warning line before the JSON. Piping its
stdout straight into `python3 -c "json.load(...)"` fails with
`JSONDecodeError: Extra data (line 7)`. Redirect to a file first, then parse.
If the API answers `402 ... credits-depleted`, this route is dead — fall through
to the browser route.

## GitHub file URLs (PDFs, notebooks, binaries)
A `github.com/<org>/<repo>/blob/main/<file>` URL returns the HTML viewer page,
NOT the file — web_extract on it yields GitHub chrome ("Uh oh!", file tree,
sign-in prompts). Rewrite to `raw.githubusercontent.com/<org>/<repo>/main/<file>`
before extracting. Works for PDFs (web_extract parses them) and any raw text.

## Browserbase dual-control session
`browser_navigate` creates ONE Browserbase session. That same session is
controllable by the agent over CDP and simultaneously viewable/operable from the
Browserbase dashboard → Sessions → Live View. `keepAlive` defaults true, so the
session survives across turns. Because one cloud browser is both agent-driven
and human-visible, a person can advance it past any step the agent cannot
automate, then the agent resumes.

For long articles the accessibility snapshot truncates — prefer a `browser_console`
JS eval that returns the article's plain_text field; fallback `browser_snapshot(full=true)`.

Browserbase is a paid backend; on a free plan the plugin auto-drops
proxies/keepAlive on a 402 but the session still works. This is NOT computer-use.
