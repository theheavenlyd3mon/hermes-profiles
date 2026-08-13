# Hermes browser/web toolset troubleshooting

Diagnosed 2026-08 on the creative profile: browser tools missing from the session's
deferred-tool catalog despite `hermes tools list` showing `browser ✓ enabled`.
Root cause was a stack of config/env mismatches. Reuse this checklist.

## 1. Profiles read ONLY their own `.env` (biggest gotcha)

An active profile (e.g. `creative`) loads `~/.hermes/profiles/<profile>/.env` — NOT the
default `~/.hermes/.env`. Keys that exist in the default env are INVISIBLE to the profile:

- `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID`, `BROWSERBASE_PROXIES`
- `OPENAI_API_KEY`, `AGENT_BROWSER_EXECUTABLE_PATH`, etc.

Symptom: `hermes status` shows `Browserbase ✗ (not set)` even though the key exists in
`~/.hermes/.env`. Fix: copy the needed lines into the profile's `.env` (or `hermes auth`).

## 2. Diagnostic commands (run from the shell, not the agent)

- `hermes status` — per-profile API key presence (reads the active profile's `.env`).
- `hermes doctor` — toolset health. Key line: `⚠ browser (system dependency not met)`.
  Note: `agent-browser (Node.js) ✓` + `Chromium ✓` can both be installed while the
  *toolset* still reports unmet deps (config mismatch or missing profile env).
- `hermes tools list` — enabled/disabled per toolset. `✓ enabled browser` does NOT mean
  tools load in-session; deps must also be met.
- `hermes tools post-setup <KEY>` — installs a backend's deps. Valid keys include:
  `agent_browser`, `browserbase`, `camofox`, `cua_driver`, `ddgs`, `faster_whisper`,
  `kittentts`, `langfuse`, `piper`, `spotify`, `xai_grok`.
- Read the ACTIVE profile's config, not the default: `~/.hermes/profiles/<profile>/config.yaml`.

## 3. cloud_provider mismatch (silent failure)

`browser.cloud_provider` in config.yaml must match the credential you own:
- `browserbase` → needs `BROWSERBASE_API_KEY` (format `bb_live_*` or `bb_liv*`)
- `browser-use` → needs a browser-use.com key (a DIFFERENT service — not interchangeable)

The creative profile had `cloud_provider: browser-use` with a Browserbase key = no valid
credential → "system dependency not met". Also `hermes status` lists both separately
(`Browser Use ✗`, `Browserbase ✗`).

## 4. Firecrawl / web tools

- `web.backend: firecrawl` requires `FIRECRAWL_API_KEY` (cloud) or `FIRECRAWL_API_URL`
  (self-hosted) in the ACTIVE profile's `.env`. Until set, `web_search`/`web_extract`
  error with "Web tools are not configured."
- Alternative without keys: paid Nous Portal subscribers get web search, image gen, TTS,
  and browser through the Tool Gateway (`hermes model` / `hermes portal`). Requires a
  working portal login (`hermes status` shows `Nous Portal ✗` when the refresh token is stale).

## 5. Browser tools still not in the session?

Browser tools are loaded at session start. After fixing config/env, START A FRESH SESSION —
the deferred-tool catalog won't refresh mid-session. Until then, use the headless Chrome +
OpenRouter vision path in this skill's SKILL.md to verify HTML artifacts.
