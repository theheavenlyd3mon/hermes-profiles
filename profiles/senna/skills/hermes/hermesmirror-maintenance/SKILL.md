---
name: hermesmirror-maintenance
description: Recurring review / maintenance / upkeep lifecycle for the HermesMirror project (a MagicMirror² fork with deep Hermes Agent integration). Covers establishing ground truth across the local PC clone and the GitHub fork, the security audit of the two standalone Python API plugins + the bridge, npm vulnerability remediation with a force-caution, and reconciling the AGENTS.md build plan against git reality. Use when the user says "review hermesmirror", "maintenance on the mirror", "upkeep", "check for vulnerabilities", "go back over the build plan", or any periodic health pass on the project.
---

# HermesMirror Maintenance

## What HermesMirror is
- A **MagicMirror² fork** (MIT). Local clone: `~/projects/HermesMirror`. GitHub: `<your-github-username>/HermesMirror`. Default branch **`master`** (not `main`). Upstream remote `upstream` = `MagicMirrorOrg/MagicMirror`.
- Four MagicMirror² modules in `modules/`: `hermes-bridge` (polls the kanban API), `hermes-dashboard`, `hermes-status`, `hermes-chat` (Phase 2).
- **Two standalone Hermes plugins live OUTSIDE the repo** (Hermes-side infra, survive `hermes update`):
  - `~/.hermes/plugins/kanban-api/` — aiohttp server on **port 8643**, serves `kanban.db` tasks as JSON (`GET /api/kanban/board`).
  - `~/.hermes/plugins/session-api/` — aiohttp server on **port 8644**, serves raw LCM conversation transcripts (`GET /api/session/messages`) from the active profile's `lcm.db`.
- `AGENTS.md` in the repo root is the roadmap (Phases 1 / 1.5 / 2 / 3). It is the authoritative plan doc but **lags reality** — trust `git`/`gh` over it.
- **Desktop app caveat (2026-08-03):** the Hermes desktop app ships a bundled Kanban plugin (off by default, Settings → Plugins) that reads the same kanban DB in-process via `ctx.rest`. The `kanban-api`/`session-api` HTTP plugins exist for the mirror's LAN bridge only — do NOT propose converting them into desktop surfaces; their data is already native on desktop. See `hermes-feature-education/references/desktop-plugin-conversion-audit.md`.

## Triggers
"review hermesmirror" · "maintenance on the mirror" · "upkeep" · "check for vulnerabilities" · "go back over the build plan" · any periodic health pass.

## Phase 0 — Establish ground truth (ALWAYS first; batch as parallel reads)
```
cd ~/projects/HermesMirror
git status -s
git log --oneline -10
git fetch origin
git rev-list --left-right --count HEAD...origin/master     # 0 0 = in sync
gh api repos/<your-github-username>/HermesMirror --jq '{description, pushed_at, topics: .topics}'
npm audit
```
Then read `AGENTS.md` and the two plugin `__init__.py` files. Do not assume the doc matches git.

## Phase 1 — Security audit (recurring; see `references/maintenance-state-2026-07.md`)
**STATUS 2026-07-20: core hardening IMPLEMENTED** — token gate (`X-Mirror-Token` vs `HERMES_MIRROR_TOKEN`, constant-time compare; empty token = open dev mode) on both plugins + hermes-chat/bridge node_helpers; bind host now configurable via `HERMES_MIRROR_HOST` (default `127.0.0.1`); no CORS headers are sent (the design doc's old `Access-Control-Allow-Origin: *` line was stale — the plugins never emitted CORS). Each review now = **verify the gate is still wired**, not re-propose it. Remaining items to re-check and rank:
1. **Empty token = open dev mode** — if `HERMES_MIRROR_TOKEN` is unset the gate is a no-op; the risk returns the moment a plugin is bound off-loopback.
2. **`session-api` returns raw conversation transcripts** from the LCM DB — if any pasted conversation contained secrets/keys, they leak to anything that can reach 8644.
3. **Hardcoded `profiles/senna/` path** in session-api (brittle across profiles).
4. **Forward-looking LAN exposure**: the intended deploy is Hermes on the Mac, MagicMirror on a Pi over the LAN. If either plugin is ever bound `0.0.0.0` to reach the Pi, an empty token → full task + conversation leakage to the whole LAN.
**Do NOT flip the bind host during a routine review unless the user asks** — it changes the deployment model. See `references/security-hardening-2026-07.md` for what shipped.

## Phase 2 — npm vuln remediation (FORCE-CAUTION pitfall)
- **ENV QUIRK (critical):** `NODE_ENV=production` is set in the shell profile, so plain `npm install` silently skips ALL devDependencies (vitest, eslint, etc.). ALWAYS use `npm install --include=dev` before running tests. Without this: `vitest: command not found` and the code subagent will burn its entire timeout flailing.
- **SCOPED TESTS ONLY:** Full `npm test` (and even bare `npx vitest run`) HANGS indefinitely (400s+, confirmed 2026-07-28) — the upstream MM suite is huge AND the `tests/electron/` specs block forever. You MUST scope by spec path, and note that scoping by `modules/hermes-*` SOURCE dirs finds nothing (tests are not colocated). The correct scoped command:
  ```
  npx vitest run tests/unit/modules/
  ```
  Expect **436/436 PASS** (2026-07-28). The hermes-chat empty-state failure is FIXED (2026-07-20: distinguish `sessionStatus === null` = never-connected from `{ connected: false }` = connection-failed; 29/29 client tests pass). **Two node_helper suites (hermes-chat, hermes-bridge) were silently failing to COLLECT** — `Cannot find module 'node_helper'` — pre-existing since `2c624c44`. **FIXED 2026-07-20** (commit `05d511b4`): patched `Module.prototype.require` in each spec to return a mock for the bare id (same pattern as the weather spec). Both suites now collect and pass (55 tests). Full unit suite: 539/540 (1 pre-existing macOS systeminfo failure). See `references/vitest-node-helper-collection-bug.md`.
- Run `npm audit fix` **NON-force** first. As of 2026-07-28 the original 5 highs are ALL cleared: `ws`/`engine.io`/`socket.io-adapter` (07-16), `undici` **pinned to 8.7.0** (07-21 session, lockfile committed as `42070009` on 07-28), `brace-expansion` (non-force fix 07-28). Remaining 3 are docs tooling only (markdownlint-cli2 chain): `linkify-it` high, `js-yaml`/`markdown-it` moderate — **deferred by explicit user decision 2026-07-28** (only fix path is `--force` → breaking markdownlint-cli2 upgrade). Do not re-litigate; just re-check each cycle in case an in-range fix ships.
- Re-run `npm audit` AND the scoped vitest command above — confirm still green before reporting. **`npm audit` results decay**: NEW advisories appear against already-pinned versions (brace-expansion appeared between 07-21 and 07-28 with zero dependency changes), so a clean audit last week proves nothing today.
- `undici` resolution history (kept for the procedure, now RESOLVED): out-of-range advisories on a fork get a **minimal safe pin, never `--force`** (peer-dep breakage risk). Pattern: `npm view undici versions`, read the advisory range, recommend the pin, user decides, apply, verify tests. Treat version numbers as disposable — re-run `npm audit` each session; only the procedure is durable.

## Phase 3 — Build-plan reconciliation / doc drift
- `AGENTS.md` drifts behind git. Verify every "unchecked" roadmap item against `git log` / `git status` / `gh`. Mark done what actually shipped.
- Known drift pattern: a Phase "Push to fork" left `[ ]` even though `gh` shows the commit pushed. Confirm "shipped" with `git rev-list --left-right --count HEAD...origin/master` (0 0) AND `gh api .../commits --jq '.[0].sha[0:8]'` matching local `HEAD`.
- **Uncommitted local edits (e.g. `config/config.js` gaining the `hermes-chat` module block) are usually intended local work, not mistakes** — fold them into a git commit step; do NOT "fix" by reverting.
- Phase 3 items (YAML config, CSS variable theming, Docker-first deploy): assess now-vs-later. User prefers **maintenance-first after idle periods** before new feature work.

### Verifying claims in AGENTS.md (don't trust the doc's own numbers)
- **Tests are NOT colocated.** They live in `tests/unit/modules/<module>/*_spec.js` (note `_spec.js`, NOT `*.test.js`). A `find -name "*.test.js"` returns nothing — that's expected, not a missing-tests alarm. Count with `grep -rhoE "\b(it|test)\(" tests/unit/modules/hermes-* | wc -l`. (2026-07-20: 182 hermes tests across 6 spec files; ~521 repo-wide.)
- **The "Test results" table (≈lines 121-129) goes stale fast.** It hardcodes a pass count and an ESLint error count that change as tests/lint are added. Re-run `npm test` and `npm run lint:js` each cycle instead of trusting the table. (2026-07-20: doc said "357/358 pass, 12 ESLint errors"; reality was ~521 tests and 0 errors / 32 warnings since commit `a0e0913f`.)
- **The "Research sources" section can list files that were never committed.** Verify each with `find` before treating it as real — dead references are doc drift too. (2026-07-20: all 4 listed research briefs absent from repo and disk.)
- **`config/config.js` is force-added/tracked even though `.gitignore` line 28 lists it** — so it legitimately shows as `M` in `git status`. That's the "intended local work" case above, not an ignore bug. `package-lock.json` churn (transitive bumps like `@emnapi/core`) is install noise, not deliberate — commit or `git checkout` at owner discretion.
- **Committing? Read `references/commit-hook-workflow.md` first.** The husky pre-commit hook (lint-staged) has four gotchas: (1) `git add` refuses `modules/*` paths even though they're tracked — use `git add -f` for the hermes modules; (2) `prettier --write` reformats WHOLE staged files, inflating diffs far beyond your edits — re-verify tests/lint/content after the commit lands; (3) prettier throws `SyntaxError` on ` ```js ` Markdown fences holding a bare object literal with `//` comments — fix with `<!-- prettier-ignore -->` on the line before the fence; (4) `eslint --fix [SIGKILL]` in the hook is a resource kill, NOT a lint error — `npm run lint:js` is the source of truth. Diagnose, don't reach for `--no-verify`.

## Dispatch pattern (orchestrator / Senna)
Delegate the three workstreams in **ONE `delegate_task` call** (background, parallel), each scoped read-only:
- `security` → ranked audit of the two plugins + bridge (no code change, no push).
- `code` → `npm install --include=dev` FIRST (NODE_ENV=production drops devDeps), then `npm audit fix` (non-force) + **scoped** tests (`npx vitest run tests/unit/modules/` — full suite HANGS on electron specs) + recommend pins (no commit/push).
- `research` → Phase 3 reconciliation + doc-drift list (no file edits).
Explicit in every context: **"DO NOT commit, push, or launch Electron."** Orchestrator consolidates the three reports, then proposes git actions (commit stray `config.js`, apply doc fixes, security hardening) for the user's go-ahead. Never let a delegate touch the repo.

## Pitfalls (embedded)
- AGENTS.md lags reality — trust `git`/`gh` over the doc.
- **`NODE_ENV=production` is in the shell profile** → plain `npm install` drops devDeps → `vitest: command not found`. Always `npm install --include=dev` first.
- **Full `npm test` HANGS (not just slow)** — upstream MM suite + `tests/electron/` specs block forever (400s+ confirmed). Run scoped: `npx vitest run tests/unit/modules/` (436 tests). Scoping by `modules/hermes-*` source dirs finds zero specs — tests live under `tests/unit/modules/`.
- **Vitest "0 tests" can mean a suite FAILED TO LOAD, not "nothing to run."** A spec that throws at module-load reports `numTotalTests: 0` with suite `status: "failed"` — it looks like a pass unless you check suite status. When reading `--reporter=json`, iterate `testResults[]` and flag any `status === "failed"` with `assertionResults.length === 0` (the `message` holds the load error, e.g. `Cannot find module 'node_helper'`). A green-looking pass count can hide a dead suite.
- **Bare `require("node_helper")` in specs: patch `Module.prototype.require` IN EACH SPEC, not globally.** The `vitest-setup.js` shim delegates unknown ids to the real Node resolver, so `vi.mock("node_helper")` never intercepts. The fix (proven 2026-07-20, 55 tests pass): in each spec, save `originalRequire`, patch `Module.prototype.require` to return a mock for the bare id, `require()` the module under test, then restore `originalRequire`. This is the same pattern the weather spec uses. Do NOT patch the shim globally in `vitest-setup.js` — that returns the real base class and breaks `vi.spyOn`. Do NOT use `resolve.alias` in `vitest.config.mjs` — it was proposed but never verified; the in-spec patch is simpler and proven. See `references/vitest-node-helper-collection-bug.md`.
- `npm audit fix --force` on a fork can break peer deps — research pins, don't force.
- The two API plugins are in `~/.hermes/plugins`, **not** under `projects/HermesMirror` — don't hunt for them in the repo.
- session-api hardcodes profile `senna` — cross-profile use is brittle.
- Uncommitted `config/config.js` edits are intentional local work, not errors.
- Never launch Electron (`npm start`) for testing — use `npm test` / `npm run server` headless.

See `references/maintenance-state-2026-07.md` for the audited advisory list, plugin security notes, and the parallel-delegation briefs captured from the 2026-07-16 review session. `references/security-hardening-2026-07.md` records the token-gate / bind-host / no-CORS hardening that shipped 2026-07-20. `references/vitest-node-helper-collection-bug.md` documents the silent node_helper suite-collection failure and the require-shim-vs-`vi.mock` gotcha. `references/commit-hook-workflow.md` documents the husky/lint-staged commit gotchas (git add -f for modules, prettier whole-file reformat, prettier-ignore for JS fences, eslint SIGKILL ≠ lint error). Re-run `npm audit` each cycle — version numbers there go stale; the procedure above does not.
