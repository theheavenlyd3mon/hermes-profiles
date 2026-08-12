## Browser Automation

Hermes supports three browser backends: **Browserbase** (cloud), **Camofox** (cloud), and **local Chromium** (installed browser). The `browser` toolset must be enabled (`hermes tools enable browser`) regardless of backend.

### Cloud Provider Setup (Browserbase)

Setting up a cloud browser provider requires **two separate configuration steps** — missing either causes a silent fallback to local Chromium with no error message.

**Step 1 — `.env` credentials (single canonical source in root `.env`):**
```bash
BROWSERBASE_API_KEY=sk-...
BROWSERBASE_PROJECT_ID=your-project-id
BROWSERBASE_PROXIES=true                # optional
BROWSERBASE_ADVANCED_STEALTH=false      # optional, Scale Plan only
```
These env vars are read from the root `~/.hermes/.env`. They are shared across all profiles — no need to duplicate per profile.

**Step 2 — `cloud_provider` per profile in each profile's `config.yaml`:**
```yaml
browser:
  ...
  engine: auto
  cloud_provider: browserbase    # ← THIS is the line that's often missing
  auto_local_for_private_urls: true
```

**Per-profile is the key insight for multi-agent setups:** The env vars (step 1) go in root `.env` once. But `cloud_provider: browserbase` must be set in **each profile's** `config.yaml` separately — the researcher, the architect, etc. If you enable browser on the researcher profile but its config.yaml has no `cloud_provider`, it silently falls back to local Chromium.

**Enable the browser toolset per profile:**
```bash
hermes --profile researcher tools enable browser
```

**The common pitfall:** The env vars are set, the `browser` toolset shows `✓ enabled`, but the agent uses local Chromium instead of Browserbase. Two possible causes:
1. Missing `cloud_provider: browserbase` in that profile's config.yaml
2. Missing BROWSERBASE env vars in root `.env` (or a profile `.env` overriding them to empty)

Diagnosis — check both in one go:
```bash
grep cloud_provider ~/.hermes/profiles/<name>/config.yaml   # should show browserbase
grep BROWSERBASE_API_KEY ~/.hermes/.env                     # should be set
grep BROWSERBASE_PROJECT_ID ~/.hermes/.env                  # should be set
hermes tools list | grep browser                            # should show ✓ enabled
```

### Viewing What the Browser Sees in Real-Time

When using Browserbase, you can watch exactly what the agent's browser is doing — live, as it happens. This is the most user-visible debugging/viewing method.

**Browserbase Live Debug URL:**
Every cloud browser session gets a live debug URL. When the agent starts using the browser, Browserbase generates a URL that you can open in your own browser to see a real-time feed of exactly what the agent's headless browser is looking at — every page load, click, scroll, and form fill. The agent can output this URL when it starts the browser session.

**Session Recordings (after the fact):**
Set `browser.record_sessions: true` in config.yaml:
```yaml
browser:
  record_sessions: true
  ...
```
This saves session replays that you can rewatch at `app.browserbase.com/sessions` or locally in `~/.hermes/browser_sessions/`. Good for auditing what happened after a research run.

**`browser_vision` screenshots:**
When the agent uses the vision tool on a browser page, it takes a screenshot and analyzes it with vision AI. On CLI, the agent describes what it sees — the actual screenshot is visible on messaging platforms (Telegram/Discord) where it renders as an image attachment.

### Full verification workflow:**
```bash
hermes profile list                              # confirm profile exists
grep cloud_provider ~/.hermes/profiles/*/config.yaml   # which profiles have it set?
grep BROWSERBASE ~/.hermes/.env                  # env vars present at root?
hermes --profile <name> tools list | grep browser  # tool enabled for target profile?
```

**Browser session recording:** Set `browser.record_sessions: true` in config.yaml to save browser session replays to `~/.hermes/browser_sessions/`. Off by default.

### Batch Setup for Multi-Profile Setups

When adding Browserbase to all team profiles (architect, coder, researcher, etc.) — or applying any shared config change across profiles — see `references/team-profile-config-management.md` for the full audit workflow, batch-apply patterns, and the symlink-vs-batch decision guide.

