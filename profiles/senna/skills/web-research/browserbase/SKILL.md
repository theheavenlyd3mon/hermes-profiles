---
name: browserbase
description: "Use when working with Browserbase or the browse CLI."
version: 1.0.0
author: Hermes Agent Team
license: MIT
metadata:
  hermes:
    tags: [browserbase, browse-cli, web-scraping, browser-automation, stagehand]
    related_skills: [gated-content-retrieval, safe-web-research]
---

# Browserbase (`browse` CLI)

Browserbase runs real Chrome browsers in the cloud that code or an agent can drive. The unified CLI is `browse` (v0.9.6+). **The API key alone resolves the project — there is NO `BROWSERBASE_PROJECT_ID` anywhere.** Never ask for one, never add it to `.env`, never pass `projectId` to a constructor. Older docs/training say it's required — that's outdated.

## Key location (this machine)

Current key lives in `~/.hermes/.env` as `BROWSERBASE_API_KEY`. Stale keys can linger in profile env files (`~/.hermes/profiles/*/.env`) — when a prompt shares a key, verify it matches the `.env` key before trusting it. Env may also export `BROWSERBASE_PROXIES=true` / `BROWSERBASE_ADVANCED_STEALTH=false`.

To run CLI commands: `export BROWSERBASE_API_KEY=$(grep "^BROWSERBASE_API_KEY=" ~/.hermes/.env | sed 's/^BROWSERBASE_API_KEY=//')`

## Setup & verify

```bash
browse --version && node --version    # both present → skip install
npm install -g browse@latest          # only if missing
npm uninstall -g @browserbasehq/cli @browserbasehq/browse-cli  # only if deprecated CLI shadows `browse` ("unknown command 'cloud'")
browse cloud projects list            # access check — returns projects if key works. Do NOT pick/copy a project id from it.
```

Every CLI command prints an **"Update available" banner** — informational noise, not an error. Strip it before parsing JSON: `browse ... 2>&1 | grep -v "Update available"`.

## Core commands

- **Fetch** (page content, no browser session): `browse cloud fetch "<url>" --format markdown` → JSON; extract the page with `.content`. Returns a payload, NOT a session row.
- **Search** (find URLs): `browse cloud search "<query>" --num-results N --json`
- **Sessions**: `browse cloud sessions list` — Fetch/Search don't create session rows; success for those is the 200/payload, not a new session.
- **Templates**: `browse templates list` (JSON). **Confirm a slug exists before cloning — slugs drift** (e.g. `amazon-product-scraping` no longer exists; closest is `gift-finder`). Clone into a disposable `/tmp` sandbox: `browse templates clone <slug> /tmp/<slug> --language typescript`.
- **Skills catalog**: `browse skills find "<task>" --json`, then `browse skills add <domain>/<task>`.
- **Driving a session**: `browse open <url>`, `browse snapshot`, `browse click/fill/get`, `browse doctor`, `browse cdp`.

## Free-tier constraints

- **Model Gateway**: included on Free but capped at **$5 of tokens** — Stagehand `act/extract/agent` can fail partway once spent. Leave `MODEL_API_KEY` (and other LLM provider keys) **blank**; a placeholder value triggers a misleading "API key not valid".
- **Proxies / Verified / auto-CAPTCHA**: paid tiers. Warn before running against bot-protected or auth-walled sites (LinkedIn, Yelp, Instagram, ticketing). Server-rendered sites (XenForo forums, docs sites) fetch fine on Free without proxies — test with Fetch before reaching for a browser session.

## Bulk fetch pattern

For multi-page scraping, loop `browse cloud fetch`, strip the banner, extract `.content` via python, write to files — see `references/bulk-fetch-recipe.md` for the exact loop.

## Pitfalls

- Don't pipe `browse` JSON through `head`/`cut`/`grep` in a way that clips session ids — surface full links verbatim.
- `browse` unified CLI ≠ deprecated `@browserbasehq/cli`. If `browse cloud` says "unknown command", uninstall the deprecated package.
- After a `browse templates clone`, follow the clone's printed "Next steps" for install/run (TS → `npm`, Python → `uv`/pip).
