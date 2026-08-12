---
name: npm-dependency-remediation
description: >-
  Remediate npm vulnerability advisories on a Node project or fork with minimal
  risk. Clears in-range advisories via non-force `npm audit fix`, isolates
  force-required bumps (out-of-range) behind a human decision, and verifies the
  test suite stays green — including the NODE_ENV=production dev-dependency trap
  that makes `npm test` fail with "vitest: command not found". Trigger when the
  user says "npm audit shows highs", "remediate vulnerabilities", "update deps
  on the fork", "fix npm audit", or asks to clear security advisories during a
  maintenance pass.
---

# npm Dependency Remediation

Clear `npm audit` highs on a Node project (especially a fork pinned to an
upstream's dependency ranges) without silently breaking peer deps.

## When to use
- `npm audit` reports high/critical advisories.
- Pre-release or maintenance pass: "clear the vulnerabilities".
- A fork (e.g. MagicMirror²) where `package.json` ranges are constrained by
  upstream — a force-bump can cascade into breakage.

## Procedure
1. **Enumerate.** `npm audit` — note each advisory's severity AND whether the
   fix is in-range (npm prints `To address all issues, run: npm audit fix`) vs
   force-required (`fix available via npm audit fix --force` with an
   out-of-range version like `undici@8.7.0`).
2. **In-range fix.** `npm audit fix` (NO `--force`). This bumps PATCH versions
   in `package-lock.json` only; `package.json` stays untouched when no new range
   is needed. Re-run `npm audit` to confirm the cleared count.
3. **Force-required: DO NOT auto-apply.** `npm audit fix --force` installs
   OUTSIDE the stated range and can break the project's pinned peer deps (esp.
   on a fork). Instead research the minimal safe pin:
   `npm view <pkg> versions --json` + the advisory's vulnerable range, pick the
   lowest version that resolves the advisory, assess peer-dep breakage, and
   **report to the user for a decision** (leave pending vs pin now).
4. **Verify green** — but dodge the dev-dep trap (below). Scope the test run.
5. **Confirm lockfile-only change.** `git diff --name-only` should show
   `package-lock.json` and nothing structural. `git diff package.json` should be
   EMPTY (audit fix didn't widen ranges). Grep the lockfile diff for the expected
   package names to prove only patch bumps landed, no top-level manifest churn.

## Pitfalls
- **Advisory lists decay — compare package names, not counts, before redoing work.** `npm audit` output is time-sensitive: NEW advisories are published continuously for the SAME installed versions, so an audit run weeks after a successful remediation will show vulnerabilities again — different packages/GHSAs, not a failed fix. Before concluding prior remediation didn't stick, diff the current advisory package names against the original task's list (e.g. July 16 list: ws/engine.io/undici; July 28 list: brace-expansion/js-yaml/markdown-it — all new, fix confirmed). Verify prior work with `npm ls <pkg>` against the recommended pin, not by re-reading audit counts.
- **Lockfile-only remediation diffs sit UNCOMMITTED when the task says "no commit/push".** A later session may have finished the fix and left it in the working tree. `git status --short` showing ` M package-lock.json` with no other structural changes IS the prior session's verified work — commit it (after confirming tests were green) rather than re-running the remediation. Seen 2026-07-28 on HermesMirror: July 21 session left a 50+/20- lockfile diff uncommitted; it was the completed fix, not dirt.
- **Trust live `npm audit` over task-context advisory lists.** A request may
  cite "1 high undici + 3 moderate js-yaml/markdown-it" from stale intel; the
  live tree often shows a different set. Also, a named-package advisory can
  surface ONLY via its transitive sub-dep — e.g. an "undici advisory" appears
  in the audit as `fast-uri` (undici's URI parser), fixable in-range with no
  undici pin or `overrides` entry needed. Before researching a force-pin for
  the named package, check whether its sub-deps already carry the advisory as
  an in-range fix. (Seen 2026-07-21 on HermesMirror: expected undici pin,
  actual fix was plain `npm audit fix` bumping fast-uri 3.1.2→3.1.4.)
- **NODE_ENV=production (or `.npmrc` `omit[]=dev`) makes `npm install` skip
  devDependencies.** `node_modules` looks populated (~8 bin entries) but
  `vitest`/`eslint` are absent → `npm test` fails with
  `vitest: command not found`, and a bare `npm install` reports "up to date"
  while still missing dev bins. **FIX:** `npm install --include=dev`. Capture
  this as the install command, not as "tests are broken".
- **Full `npm test` is slow** (300+ tests can exceed a 600s delegate timeout).
  For verification run module-scoped:
  `node_modules/.bin/vitest run tests/unit/modules` (or any sub-path). Use
  `--reporter=dot --no-color` and pipe to a log file to watch progress live —
  a piped `| tail` buffers everything until exit, so you can't tell if it's
  alive. `pgrep -fl vitest` confirms the worker is running.
- **Don't dispatch a subagent to run `npm audit fix` + full `npm test`
  together** — the long test run can hit the 600s cap and time out with partial
  work. Either run directly with a hard tool timeout, or scope tests. If you do
  delegate, separate the fast fix from the slow verification.
- **Pre-existing failures are not your regression.** A suite with 1 failed test
  + N file-load errors where the failures are in an unrelated module (e.g. a
  `require("node_helper")` alias that doesn't resolve in this checkout, or a
  DOM-string assertion) is NOT caused by a lockfile patch bump — confirm by
  checking the failure is in code you didn't touch and `package.json` is
  unchanged.

## Verification discipline
- After fix: `git diff --stat package-lock.json` shows only expected bumps.
- `npm audit` high count dropped to the force-required remainder(s) only.
- Module-scoped test run passes (the code you touched / that matters).
