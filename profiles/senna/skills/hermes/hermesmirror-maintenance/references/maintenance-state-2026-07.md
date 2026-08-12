# HermesMirror Maintenance — State Snapshot (2026-07-20 review)

> Disposable facts only. Re-run `npm audit` each cycle; version numbers below will
> drift. The procedure in SKILL.md is what stays durable.

## 2026-07-20 reconciliation pass (read-only, no edits)
- **Sync:** `HEAD == origin/master == 2c624c44`; `git log origin/master..HEAD` empty; GH `pushed_at` 2026-06-04T15:37Z. Phases 1 / 1.5 / 2 = 100% shipped & pushed.
- **Doc-drift found (exact AGENTS.md lines):**
  - L105 `- [ ] Push to fork` → actually pushed (`2c624c44`). Fix to `[x]`.
  - L125 `357/358 pass` → stale. Repo now ~521 `it()`/`test()` blocks; hermes modules = **182** (board-utils 25, bridge node_helper 36, chat client 29, chat node_helper 19, dashboard 39, status 34).
  - L127 `⚠️ 12 ESLint errors` → stale. Commit `a0e0913f` = **0 errors, 32 warnings**.
  - L133–136 "Research sources" → all 4 docs (HERMES-ARCHITECTURE.md, ARCHITECTURE_REVIEW.md, smart-mirror-research-brief.md, research-brief.md) **absent** from repo and disk — dead references.
  - Minor count drift (optional): L89 dashboard "38"→39, L90 status "35"→34, L91 backoff "30"→36, L103 chat "38+24"→29+19.
- **Uncommitted (correct, leave alone):** `config/config.js` +11 (hermes-chat block; file is tracked despite `.gitignore` L28 → shows as `M`); `package-lock.json` +150/−218 transitive churn (`@emnapi/core` 1.10.0→1.11.1).
- **Phase 3 verdict:** CSS-variable theming = do next (cheap, visible); YAML config = later (MM core + all 4 modules assume config.js); Docker-first = later (no Pi target yet, Electron doesn't containerize).
- **Key technique:** tests are `tests/unit/modules/<mod>/*_spec.js`, NOT colocated `*.test.js` — `find -name "*.test.js"` returns nothing by design.

## npm audit — 1 high (as of 2026-07-20)
| Advisory | Severity | Fix path | Notes |
|---|---|---|---|
| `undici` 8.0.0–8.4.1 (installed 8.1.0) — 8 advisories: TLS cert-validation bypass (SOCKS5 ProxyAgent), WebSocket DoS (fragment bypass ×2), HTTP header injection (Set-Cookie percent-decoding), cross-origin routing (SOCKS5 pool reuse), response queue poisoning (keep-alive reuse), SameSite downgrade, cross-user info disclosure (cache whitespace) | high | `npm audit fix --force` → undici@8.7.0 (OUT of range) | direct dep of magicmirror@2.36.0; recommend manual pin to 8.7.0, do NOT --force |

**CLEARED since 2026-07-16:** `ws` <8.21.0, `engine.io`, `socket.io-adapter` (all gone after prior non-force fix), and `systeminformation` (no longer flagged — resolved upstream).

## Test results (2026-07-20)
- **ENV QUIRK hit:** `NODE_ENV=production` in shell profile → plain `npm install` skipped devDeps → `vitest: command not found`. Fix: `npm install --include=dev` (added 506 packages).
- **Full `npm test` times out at 180s+** (upstream MM suite is huge). Use scoped: `npx vitest run modules/hermes-bridge modules/hermes-dashboard modules/hermes-status modules/hermes-chat`.
- Scoped result: **126/127 pass**. 1 failure: hermes-chat `getDom` empty-state expects `'No active session'`, gets `'Gateway unreachable'` (session-api not running in test env — env-dependent, not a code regression).

## Plugin security surface (read-only review, 2026-07-20)
- `kanban-api` (`~/.hermes/plugins/kanban-api/__init__.py`, 8643): binds `127.0.0.1`, `GET /api/kanban/board`, no auth, `Access-Control-Allow-Origin: *`. Reads `kanban.db` via `hermes_cli.kanban_db`.
- `session-api` (`~/.hermes/plugins/session-api/__init__.py`, 8644): binds `127.0.0.1`, `GET /api/session/messages`, no auth, `CORS: *`, hardcoded `profiles/senna/` path with fallback scan, returns raw user/assistant messages capped 4000 chars each.
- Bridge (`modules/hermes-bridge/node_helper.js`): polls `http://127.0.0.1:8643/api/kanban/board`; self-starts polling in `start()` (works headless); exponential backoff 1s→30s cap.
- **Active exploit path confirmed:** malicious webpage → `fetch("http://127.0.0.1:8644/api/session/messages")` → CORS `*` allows cross-origin read → exfiltrates last 200 messages incl. any pasted secrets. No LAN needed.
- **Ranked findings (security subagent):** 3 HIGH (no auth, CORS `*`, raw transcript leak), 2 MED (hardcoded profile, future LAN exposure), 3 LOW (error detail leak, no fetch timeout, SQLite conn leak on error).
- **Recommended fix order (lazy):** (1) drop CORS headers entirely — bridge is Node-side fetch, doesn't need them, 4 deleted lines kills active exploit; (2) token gate `HERMES_MIRROR_TOKEN` env + `X-Mirror-Token` header, ~6 lines/plugin; (3) configurable bind host `HERMES_MIRROR_HOST` default 127.0.0.1; (4) redact secrets from session content (~10 lines regex).

## Proposed actions awaiting user go-ahead (2026-07-20)
1. Security hardening (drop CORS + token gate + configurable bind host, ~20 lines total)
2. Pin undici@8.7.0 manually in package.json
3. Commit config.js hermes-chat block + package-lock.json
4. Fix AGENTS.md drift (4 corrections above)
5. Fix hermes-chat empty-state test (mock gateway-unreachable properly)

## Parallel-delegation note (2026-07-20)
- `code` subagent **timed out at 600s** — its brief didn't warn about NODE_ENV=production or the full-suite timeout, so it burned time on `npm install`/`npm test` failures. Briefs now updated in SKILL.md dispatch pattern to include `--include=dev` and scoped vitest. Orchestrator filled the gap manually.
- `security` and `research` subagents completed successfully (63s and 226s respectively).
