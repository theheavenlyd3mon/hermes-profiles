---
name: hermes-update-triage
description: Decide whether to run `hermes update` by triaging the unreleased upstream commits the local install is behind. Buckets raw commits by relevance to THIS user's fleet (not a generic changelog) and returns a go/no-go. Use when the user asks "what's new in the repo vs what I have", "are the new commits worth getting", "should I update hermes", or `hermes --version` reports "N commits behind".
triggers:
  - "should I update hermes"
  - "are the new commits worth getting"
  - "what's new in the hermes repo"
  - "what am I behind on"
  - "commits behind"
  - "is hermes update worth it"
  - "new skills since"
author: Senna
version: 1.0.0
---

# Hermes Update Triage

Answer **"I'm N commits behind upstream — is it worth getting?"** This is NOT a
released-version changelog (that's `hermes-version-summary`, which reads
RELEASE_v*.md). Here there are no release notes yet — you triage raw commits and
filter through the user's actual stack.

## Workflow

### 1. Establish the gap
```bash
hermes --version                                  # installed ver + "N commits behind"
cd ~/.hermes/hermes-agent
git fetch origin 2>&1 | tail -3                   # MUST fetch first or range is stale
git status -sb | head -3                          # dirty tree? warn BEFORE offering update
# Snapshot the list ONCE, then analyze the file — never re-run git log per slice
# (rtk-rewrite intercepts each git invocation separately; see Pitfalls)
git log --format='%h|%s' HEAD..origin/main > /tmp/hermes_triage.txt
git rev-list --count HEAD..origin/main            # ground-truth N; must equal wc -l of the file
git diff --stat HEAD..origin/main | tail -1       # scale: files / insertions
```

### 2. Strip noise, isolate signal
```bash
# Drop test/ci/docs/fmt-only — rarely affect runtime
git log --oneline HEAD..origin/main --format="%h %s" | grep -viE "^.{8} (test|fmt|ci|docs)\("
# Features only
git log --oneline HEAD..origin/main --format="%h %s" | grep -E "feat\("
```

### 3. Bucket by relevance to THIS user
- 🟢 **Worth getting** — hits their surfaces: cron fleet (model pins, drift
  guard, failure recording — they run ~14+ crons and have been burned by drift),
  memory/mnemosyne/LCM pipeline (flush-before-teardown, compression prompt
  preservation), gateway fleet + Discord, MCP discovery/locking, session/profile
  isolation, model catalog + pricing changes (they run a pricing watchdog cron),
  provider-aware tooling, web_search/DDGS stability, secrets scrubbing,
  macOS TUI/CLI fixes, voice pipeline.
- 🟡 **Nice-to-have** — desktop/Electron features (only if they use the app),
  wake-word/voice-chat UX, new platform adapters (Photon, Buzz) unless asked.
- ⚪ **Skip** — platform adapters they don't run, CI pipeline, test coverage,
  docs cleanup, provider-scoped fixes for providers they don't use.

### 4. Verdict + offer
One line: update or not, and why. Then offer to run `hermes update`.

## Variant: "will the update fix THIS bug?"

When the user is debugging a specific failure and suspects an update will cure
it, triage the gap AGAINST THE FAILING FILES before promising anything:

```bash
cd ~/.hermes/hermes-agent && git fetch origin
# Does the gap touch the code path that broke?
git diff --stat HEAD origin/main -- agent/<module>.py
# Empty diff = the update will NOT fix it (hygiene only)
git log --oneline HEAD..origin/main --grep="<feature>" -i   # named fixes in gap?
git merge-base --is-ancestor <sha> HEAD && echo LOCAL || echo MISSING  # is a known fix already local?
```

Observed 2026-07-31: 72 commits behind, but the gap touched zero MOA files
(`agent/moa_loop.py`, `agent/chat_completion_helpers.py`, `agent/conversation_loop.py`)
— so the update would not have fixed the MOA crash the user was seeing, even
though the SimpleNamespace-tolerance fix that IS upstream was already local.
Verdict was: update for hygiene, don't promise it fixes MOA. Same check applies
to any feature: gap empty on the failing module → the honest answer is "update
won't cure this; here's the real workaround."

## Variant: "any new SKILLS since vX?"

Bundled skills live in the hermes-agent repo under TWO roots: `skills/` and
`optional-skills/` (~181 SKILL.md files as of 2026-07). Triage them like commits:

```bash
cd ~/.hermes/hermes-agent && git fetch origin -q
# Upstream skill delta since local HEAD:
git diff --name-status HEAD origin/main -- skills optional-skills
# Locally-added/modified profile skills since a date:
find ~/.hermes/profiles/<profile>/skills -maxdepth 2 -name SKILL.md -newermt 'YYYY-MM-DD'
```

- `~/.hermes/profiles/<profile>/skills/.bundled_manifest` records which bundled
  skills are materialized locally (name:content-hash per line) — diff it after an
  update to see what the bundle changed.
- Empty upstream diff = the honest answer is "no new skills, the churn is core
  code" — then bucket the commit log per §3 and say that. Don't invent skill news.

## Pitfalls
- **rtk-rewrite silently truncates `git log` to ~50 lines.** With the rtk-rewrite plugin active, bare `git log` through the terminal tool gets intercepted and capped — you see 50 commits while `git rev-list --count` reports the true N (observed 2026-07-28: 50 shown vs 391 real; again 2026-07-29: consecutive calls ALTERNATED between 50 and 610 on the same range, including inside `execute_code`'s `terminal()`). The user's "N commits behind" number then disagrees with your triage. Fix: snapshot once — `git log --format='%h|%s' HEAD..origin/main > /tmp/file` — verify `wc -l` equals `git rev-list --count`, then grep/python the FILE for all further slicing. If the file itself comes out short, rerun with `/usr/bin/git log` (absolute path bypasses the rewrite). Same failure class as the rtk `grep` interception in hermes-maintenance.
- **Dirty tree before update.** If `git status -sb` shows local modifications (observed: `agent/model_metadata.py` dirty), flag it in the verdict BEFORE offering `hermes update` — user must stash/commit first.
- **Fetch first.** `HEAD..origin/main` is empty/stale without `git fetch origin`.
- **Don't dump all N commits.** The user wants the filtered few that matter to
  *their* stack. Bucket hard; lead with 🟢.
- **Installed version ≠ git HEAD.** `hermes --version` shows the release tag;
  local HEAD may already carry post-release commits. `HEAD..origin/main` is the
  true missing delta.
- **Provider-scoped fixes can be skip-tier.** A `fix(...)` scoped to a provider
  they don't use (Codex OAuth) is ⚪ even though it's a fix.
- **After they say yes**, hand off to `hermes-maintenance` for the post-update
  health check (MCP binaries, mnemosyne/rtk venv wipes, profile wrapper).
- **Plugins have their own upstream remotes.** Git-managed plugins (e.g.
  `hermes-lcm`, `web-search-plus`) may have `origin` (user fork) AND `upstream`
  (canonical repo) remotes. A plugin can be up-to-date with `origin` but behind
  `upstream`. After `hermes update`, also check git plugins against their
  upstream remotes — see `hermes-maintenance` §6b for the multi-remote audit
  script. Non-git plugins (eikon, katana, kanban-api, session-api) are bundled
  with Hermes and auto-updated; only git-managed plugins need manual pulling.

## Overlap note (for curator)
Adjacent to `hermes-version-summary` (released-version reporting). Distinct
question + workflow; kept separate. If consolidating, this is the "unreleased
triage" half, version-summary is the "released report" half.
