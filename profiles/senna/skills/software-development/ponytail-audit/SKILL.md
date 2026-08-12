---
name: ponytail-audit
description: >
  Audit a code surface (module, package, integration, CLI, MCP/tool layer) for
  over-engineering and missing capabilities using the user's "Ponytail lens"
  (minimalist / xkcd-Ponytail engineering ethos: YAGNI, delete dead code,
  reuse in-codebase, kill duplication). Trigger when the user says "audit X for
  over-engineering / missing capabilities", "review under Ponytail lens", "find
  bloat / gaps in <module>", or asks to slim down or gap-check an integration,
  importer set, CLI, or tool surface. Produces a ranked report of
  delete-or-simplify items, genuine gaps with implementation plans, and a
  top-3 priority list.
---

# Ponytail Audit

Audit a codebase surface for two things: **(A) over-engineering** — code that
should be deleted or collapsed — and **(B) missing capabilities** — gaps where
the system already owns the pieces but doesn't wire them together, or where the
documented surface lies about what the code does.

The lens is the user's: *Ponytail* = xkcd's minimalist engineer. Default to the
simplest thing that works. Every "nice to have" is guilty until proven needed.
Duplication is a bug. Dead code is debt you ship.

## When to use

- User says "audit <area> for over-engineering and missing capabilities".
- User says "review under Ponytail lens" / "Ponytail lens".
- Any request to find bloat, dead code, or gaps in a module/integration/CLI.
- After writing a large feature surface, as a self-review pass before declaring done.

## Procedure

0. **Look up any unfamiliar lens/tool/term first.** If the user references a method, plugin, or lens you don't recognize (e.g. they say "use ponytail" and you don't know it), STOP before doing anything else, search GitHub/web for it, and report back what it is and how it applies. Do NOT guess or proceed blind. (User's explicit rule: "if you don't know what it is, stop and search, then report back.") Only continue once the term is understood — and if it is an installable plugin, review its source for safety (no network calls, no destructive ops) before installing.

1. **Map the surface in parallel.** Batch `read_file` / `search_files` calls —
   read every file in the target directory in one turn (the runtime executes
   independent reads concurrently). For a wide surface, enumerate files first
   with `search_files(target='files')`, then read the top-level + each
   sub-area.
2. **Build the duplication map.** `search_files` for: function/class names that
   repeat across files; identical helper bodies; copy-pasted blocks. Greps are
   your proof — don't eyeball "looks similar".
3. **Build the dead-code map.** For any class/function/variable you suspect is
   unused, `search_files` the *whole repo* for its name. A symbol is dead only
   if zero non-definition references exist (tests count as a reference — note
   them explicitly).
4. **Build the claim-accuracy map.** Cross-check docstrings/tool-schemas against
   actual call sites. The most common over-engineering tell is a tool/flag
   *documented* but *not wired* (e.g. a schema field read but never forwarded).
   Two axes:
   - *Code-vs-docs*: docstrings/tool-schemas vs actual call sites (above).
   - *Imports-vs-manifest*: grep every `import X` / `from X import` in the
     audited surface, then check `[project.dependencies]` and each
     `[project.optional-dependencies]` extra in `pyproject.toml`. A module that
     imports `nacl`, `argon2`, `keyring`, etc. but whose extra only declares
     `cryptography` is a contradiction — either declare the extra or delete the
     unused branch. **Check BOTH the root `pyproject.toml` AND any sub-package
     manifest** (e.g. `integrations/*/pyproject.toml`); the core may be
     zero-dependency while an integration sub-package declares deps — don't
     conflate the two when judging a "zero-dependency" claim.
5. **Look for gaps in (B).** Identify subsystems that already exist but are
   unreachable from a documented entry point (CLI command missing, MCP tool not
   exposed), or safety/quality passes (PII scan, idempotency, dry-run preview)
   that exist elsewhere but aren't applied at the highest-risk boundary.
6. **Write the report** in the structure below. Rank by effort-vs-value.

## Verification discipline (no false positives)

- Never call a symbol "dead" without a repo-wide grep proving no other caller.
- Never call a block "duplicate" without confirming it is byte-for-byte (or
  near-identical) repeated — note divergence points.
- Confirm duplication is fixable (shared base/mixin exists or is cheap to add)
  before recommending deletion of overrides.
- For "half-wired flags", trace the value from schema → handler → downstream
  call and show exactly where it's dropped.

## Report structure (the format that worked)

**A. Over-engineering / delete-or-simplify** — each item:
`File:lines` — what it is — *Ponytail rung* — fix.
Use rungs:
- `(1) YAGNI` — built for a future that hasn't arrived; delete or defer.
- `(2) reuse in-codebase` — identical logic duplicated N times; lift to one
  shared base/helper.
- `(3) correctness/footgun` — misleading or half-wired; fix or remove.
- `(5) one line` — trivial cleanup (no-op branch, unused import).
- `(6) security / minimum that works` — never simplify away. Wildcard CORS,
  auth headers, TLS, constant-time compares, transaction wrappers. These look
  like "extra code" but removing them is a regression, not a simplification.
  Flag as KEEP, with reasoning, not as a delete candidate.

**B. Missing capabilities (gaps)** — each item:
- **Idea** (one line), **Implementation** (how, noting zero/low new deps),
  **Plan** (numbered steps), **Why** (what breaks / contradicts today).

**C. Top 3 prioritized recommendations** — (S)mall / (M)edium effort tags,
each a self-contained next action that delivers the most value.

**Cross-cutting flag (when it applies).** If the package headline makes a
sweeping claim (e.g. "Zero-Dependency, Sub-Millisecond", "Fully Private") that
the audited subsystem does NOT satisfy, call it out explicitly with proof and a
one-line recommendation (scope the claim / guard the heavy import). This is a
legitimacy gap, not a style nit — flag it last so it's unmissable.

## Common over-engineering signatures (checklist)

### Recall / ranking hot-loops (highest-leverage, look FIRST)
These three show up constantly in hybrid vector+FTS scorers and each is a
sweeping-claim contradiction ("sub-millisecond" / "O(1)"):
- **Per-candidate hot-loop DB query.** Inside the scoring loop a `SELECT ...
  WHERE source LIKE '%id%'` (leading wildcard → index unusable → full table
  scan per candidate). Fix: batch all candidate IDs into ONE indexed
  `IN (...)` query before the loop, fold into dicts, O(1) lookup inside. See
  `references/recall-rank-hotloop-patterns.md` (Pattern 1).
- **Multi-tier cache that `invalidate()`-s on every write.** The SQL table /
  embedding-cosine-scan tiers / TTL machinery become dead weight; the
  cosine tiers claim "O(1)" but loop all entries per `get()` = O(n·d). Fix:
  collapse to ONE in-memory dict. See the same reference (Pattern 3).
- **Cache keyed only on the query string** while `recall()` accepts filters
  (`author_id`, `from_date`, `memory_type`, ...) → cross-scope result bleed
  (correctness bug, rung 3). Fix: filter-aware key (Pattern 2 in the reference).
- **Recomputed loop-invariant** inside the per-candidate loop (e.g. a popcount
  table built every iteration). Hoist to a module-level constant (rung 5).

- A lazy proxy / builder class with 5+ methods that is never instantiated
  outside its own module → dead scaffold, delete.
- N subclasses each overriding a base method with ~60 lines that reproduce the
  base plus one identical SQL/loop block → lift the delta into the base, delete
  overrides.
- A `validate()` whose only branch is `if x: pass` → no-op; remove or enforce.
- The *same* helper function defined identically in 2+ files (e.g.
  `_resolve_default_scope`, DB-path resolution) → one shared module.
- A utility method (`_content_hash`, `_slugify`) only referenced by a unit test
  and never in production → either use it or drop it.
- A tool/CLI flag exposed in a schema but silently ignored on one code path →
  footgun; thread it through or delete from schema.
- A "self-healing" import guard (`if not hasattr(logging, "getLogger"):
  sys.modules.pop("logging"); reimport`) defending against an unreachable
  failure mode → delete (rung 1/5). stdlib modules are always importable.
- Two crypto/transport backends doing the SAME job (e.g. PyNaCl `SecretBox`
  duplicating `cryptography.fernet.Fernet`) → keep the one the extra actually
  declares; delete the undeclared duplicate (rung 6 — minimum that works).
- A speculative "stub" method that builds a rich data structure for a future
  LLM/consumer that doesn't exist and is invoked nowhere → dead YAGNI (rung 1).
- A complex algorithm (transitive-closure, fixed-point) implementing a feature
  the docs label "planned" and that no call site reaches → dead code even
  though it's impressive; delete (rung 1).
- A dead reassignment / unreachable branch inside an `if` (re-sets a variable to
  the value it already holds, imports a module never used) → rung 5.
- A **second, divergent extraction/engine module** that re-implements an
  existing subsystem with a *different prompt shape / output schema* and is
  reachable only from benchmarks or a `self._client` field that is never
  instantiated on the production path. e.g. `extraction/client.py`
  (`ExtractionClient`, flat fact-array prompt) vs `core/extraction.py`
  (`extract_facts_safe`, multi-category MEMORIA prompt) → eval measures a
  *different* system than production; collapse to one source of truth
  (rung 2). Reachability proof: grep the class for instantiation
  sites outside tests/benchmarks; `_extraction_client = None` that is
  only ever set in `_benchmarks/` looks unreachable in prod — BUT a
  non-benchmark *test* that imports the class directly (e.g.
  `from mnemosyne.extraction.client import ExtractionClient`) is proof
  of life and OVERRIDES the benchmark-only read. When a test
  constructs the object, the module is live; do NOT delete it. (This
  session: `mnemosyne/extraction/` was flaggable as benchmark-only
  dead because the only *production* instantiation is in `_benchmarks/`;
  but `tests/test_c13b_extraction_diagnostics.py` imports
  `ExtractionClient` directly and builds it — kept.)
- A **full subsystem with zero callers** (its `def harmonize()` / `def run()`
  appears only in its own module + docstrings + `build/` copies). Grep for the
  call name repo-wide; if it's never invoked, the whole module (schema creation,
  LLM loop, helpers) is dead YAGNI (rung 1) — unless a documented entry point is
  *planned*, in which case WIRE it now or label it clearly as not-yet-shipped.
- **A standalone `token_counter.py` / cost module with zero importers** (grep
  `import token_counter` returns nothing) while the same `estimate_tokens`
  helper is duplicated in 2+ real modules → delete the standalone module, reuse
  the shared helper (rung 1 + 2).
- **A reverse/decode map with no decoder.** `REV_CATEGORY` / `REV_PHRASE` style
  dicts built "for decode" but no `decode()` function exists anywhere (grep
  `def decode`) → the reverse maps are dead; delete them, keep `encode()`.

## Common missing-capability patterns (gaps)

- A subsystem (importers, providers) with a registry + `import_from_*`
  functions, but the primary CLI only reaches one variant → expose the registry
  on the CLI (`--from <provider>`, `--list-providers`).
- A PII/secret scanner that exists in `core/` but isn't run at the ingestion
  boundary (imports pull raw third-party dumps) → wire it post-transform.
- `dry_run` that returns only a count → add a `preview` of first N transformed
  items so mapping bugs are catchable before commit.
- Import branded "idempotent" but re-inserts blindly for most providers → add a
  stable content-hash dedup key (reuse the already-written unused hash helper).
- Tool-schema `description` listing only 2 of 8 supported providers → fix the
  doc to match the code.
- Adapter↔server contract drift: a client sends `since_token` but the server
  reads `since`, or the client persists a cursor under key `X` while the engine
  reads key `Y` → silent full re-sync every cycle. Fix the key name and align
  the cursor namespace; add a regression test asserting the cursor advances.
- A `import keyring` (or any optional lib) inside an adapter with NO entry in
  any `pyproject.toml` → fails silently (returns "") when not preinstalled.
  Either declare the dep or delete the branch.
- Stdlib `urllib` transport over the internet with a single `urlopen` and no
  retry/backoff → wrap in a 2-attempt loop with short exponential backoff
  (zero new deps). Sync/HTTP utilities should survive one transient drop.
- Deploy healthchecks already probe the server (`/sync/status`) but there is no
  lightweight `/healthz` and no error surfacing in `get_status` → add a liveness
  route + an error counter exposed in status (zero deps, big observability win).
- Conflict resolution is last-writer-wins only, silently discarding one side on
  divergence → add a `keep_both` mode (sibling memory with a `conflict:` prefix)
  with no LLM needed, to preserve data the docs claim to protect.
- **Embedding cache asymmetry.** `embed_query` is `lru_cache`d but `embed()`
  (documents) is not, so identical content re-embedded on re-index / edit /
  summary hits the model every time. Mirror the query cache: key on the
  tuple of prefixed doc texts, share one cache, cap `maxsize` ~1024. Often the
  single biggest cost + latency win in an embeddings subsystem, and it's the
  gap that breaks a "sub-ms / cheap" claim on repeated content.
- **No observability on the expensive boundary.** Extraction/LLM layers carry
  full process-global diagnostics (tier counters, success-rate) but the
  embeddings layer — which makes the actual network/GGUF calls — exposes none
  (an `_API_CALL_COUNT` incremented but never read counts as NO observability).
  Add a tiny mirror of the extraction-diagnostics pattern: API-call count, embed
  latency, cache hit-rate, local-load-failures. Fold cost logs into the same
  surface instead of three overlapping, partly-unread cost mechanisms.
- **Local→API fallback gap.** Embedding transport is chosen *once at import*
  by name heuristics; a runtime local-model load/embed failure then yields
  `None` and silent recall degradation. If an API key/URL is configured, retry
  the failed embed via the API (trust-boundary safe — no untrusted input).
- **Branding-vs-reality on "zero-dependency / sub-millisecond".** When the
  package headline claims zero-dep / sub-ms, check whether the audited
  subsystem actually holds: embedding/LLM layers effectively require `numpy` +
  optional heavy backends (`fastembed`, `llama-cpp-python`, `ctransformers`,
  `huggingface-hub`) and are network/GGUF-bound (ms–seconds, never sub-ms).
  The claim holds only for the FTS5 + lightweight-fallback recall path. Either
  guard the heavy imports behind a clean optional path or scope the claim in
  docs so the layer isn't misrepresented. Don't let the marketing line mask
  real cost.
- **Veracity / trust-ranking silent bugs.** In a "Bayesian veracity" layer,
  check the weight table ordering (`unknown` must be the LOWEST tier, not above
  `inferred`/`tool`/`imported`), and reconcile docstrings vs the actual formula
  (`1 - 0.7^n` claimed but an incremental `old + (1-old)*w*0.3` implemented).
  Also flag auto-resolve paths that ignore veracity/recency and contradict a
  richer conflict model elsewhere in the same module.

- **Security gaps that can masquerade as over-engineering but are MUST-FIX (rung 6 — never list these in section A as delete candidates):** a Ponytail sweep over an agent/memory system must actively hunt for these, because they are the highest-severity findings and are easy to misclassify as "extra code":
  - **Stored-memory → prompt injection.** Any path that renders stored `content` into agent prompt text (persona renderers, model-card builders, recall/export) MUST strip injection markers AND gate on a `trust_tier`/trust field. If the rendered output is persisted to disk (e.g. `persona.md`), re-sanitize from source on regenerate — otherwise a later `forget()` leaves the injected instruction live. This is the only class that yields direct agent control from data the system is built to store. *Fix:* shared `strip_injection_markers()` + `redact_secrets()` (reuse existing secret regexes), called at every render/export boundary.
  - **Right-to-be-forgotten not honored.** `forget()`/`end()` that only stamp `valid_until` (soft delete) while `export_all()`/`history()` still return the row, and no physical `purge()` exists. *Fix:* add `purge()` (physical DELETE, owner-scoped), default `export_all(include_history=False)`, document soft vs hard, wire a `--hard` forget tool.
  - **Non-atomic durable writes.** `write_bytes`/direct `f.write` with no temp+`os.replace`+`fsync` → corrupt payload on crash; an installer regex rewrite of a YAML config that silently drops sibling keys; `rmtree` of a *real* user directory with no `force` guard. *Fix:* temp+rename+fsync for blobs/config; real YAML parse/emit instead of regex; guard real-dir removal behind `force`.
  - **Plaintext PII-at-rest in DR.** `create_backup()` gzip-dumps the whole DB unencrypted; `restore_backup()` trusts any consistent file, ignoring a computed `backup_checksum`. *Fix:* encrypt backups (reuse existing sync-key / `secrets`+`hashlib`), verify checksum before restore.
  - **Plugin/extension dir auto-executes arbitrary code.** A directory globbed at startup and `exec_module`'d with no allowlist/signature → local-write gives full RCE in the process that holds all PII. *Fix:* gate behind an explicit allowlist in config; log each loaded plugin.
  - **Unvalidated store inputs.** `owner_id`/keys accepted unbounded; numeric `confidence` accepts `NaN`/`-inf`/out-of-range. *Fix:* length caps on key/text columns; clamp `confidence` to finite float ∈ [0,1]; document that callers authorize `owner_id`/scope.
  Surface these as CRITICAL/HIGH must-fix items in section B, never in section A.

### Localhost-bound API plugins (agent / bridge / sidecar setups)
A very common minimal-setup pattern: a tiny HTTP API (aiohttp / flask / fastapi
/ Express / `python -m http.server`) runs on `127.0.0.1` to feed a local
client (a MagicMirror module, an Electron renderer, a TUI, a dev dashboard).
These look "harmless — it's localhost" but the Ponytail security sweep MUST
treat them as internet-facing the moment the deployment story adds a second
machine (Raspberry Pi over LAN, container-to-host, remote dev). Audit checklist:
- **No auth + free resource params = full read.** If `session_id` / id is a
  query param with no owner check, any caller enumerates every record.
- **`Access-Control-Allow-Origin: *` is dead weight for a Node/Python client**
  (those clients don't enforce CORS) and is a *localhost drive-by* exfil vector
  today (a malicious page can `fetch('http://127.0.0.1:PORT')`). Delete the
  header; if a browser truly needs it later, set an explicit origin.
- **Raw DB transcripts / PII served verbatim** (LCM / SQLite / kanban dumps) =
  secret-disclosure path. Add a one-line redaction regex on `sk-` / `AKIA` /
  `Bearer ` / `ghp_` shapes BEFORE serializing. Heuristic, not a sanitizer —
  label it with a `ponytail:` comment.
- **Hardcoded profile/path** (`profiles/senna/`) is a correctness/trust smell;
  derive from an env var (`HERMES_PROFILE`).
- **LAN-exposure escalation (CRITICAL in the planned deploy):** host hardcoded
  `127.0.0.1` with no knob. The moment it's bound `0.0.0.0` to reach a Pi /
  container, zero-auth exposes everything to the LAN. Minimal fix: make host
  configurable AND refuse non-loopback bind unless an API token is set — couple
  "exposed" to "authenticated" so it can't be opened by accident.
- **Minimal hardening that stays lazy:** one shared `X-Api-Token` check
  (fail-closed, `hmac.compare_digest`), drop the CORS wildcard, redact
  transcripts, configurable host gated on token. ~10 lines/plugin.
No SQLi if queries are parameterized — verify that first; it's the cheap win.
See `references/localhost-api-plugin-security.md` for a worked example.

## Phase 2 — Delegate the fixes (audit → improve)

The user's usual next step after an audit is "delegate the team to complete the fixes." Run it as a **multi-wave delegation, NOT one batch**, because subagents editing the same file concurrently clobber each other.

**Wave discipline:**
- Group fixes so each wave's subagents own **disjoint files** — split by subsystem (security, embeddings, importers, sync, recall). Two specialists must NOT both touch `cli.py`/`mcp_tools.py` in the same wave.
- If a file is legitimately needed by two specialists (e.g. security's `cli.py` B2 + importer's `cli.py` A4), let ONE own it and note the intersection; **reconcile that file yourself** when the batch lands (re-read, merge both diffs, retest) rather than letting two agents race.
- Each subagent brief must include: the audit findings it owns (cite file:line), exact files to edit, the Ponytail safety carve-outs (never remove validation/security), verification commands, and a **strict git guard**: `git branch --show-current` must be the feature branch; NEVER `git add -A`; `git add` ONLY owned files; NEVER `git push`; focused commit message; retry on lock up to 3×.
- Dispatch with `delegate_task` in **background**; results re-enter as one batched message. Do not poll.
- After each wave: `git status` + `git log --oneline -n`, run the suite, reconcile any shared-file intersections, then launch the next wave.
- Honesty gate: if a fix can't be made safely (live caller found, tests break unfixably), the subagent returns it NOT-DONE-with-why; report that to the user, never fabricate success.

See `references/audit-to-fix-wave-playbook.md` for the exact subagent brief template and git-commit guard.

## Pitfalls

- Don't capture environment-dependent failures (missing binaries, uninstalled
  packages, `command not found`) as audit findings — those are setup, not code
  debt.
- Wildcard CORS (`Access-Control-Allow-Origin: *`), auth/security headers, TLS
  setup, and transaction wrappers are NOT over-engineering even though they add
  lines. Never recommend deleting them as "simplification" — classify as
  KEEP (rung 6) and explain why. The audit must not trade security for brevity.
- When judging an extras/packaging claim, separate the *root* package manifest
  from *sub-package* manifests; an integration sub-package legitimately declares
  deps while the core stays zero-dep. The contradiction to flag is code importing
  an undeclared lib, not the existence of deps in a sub-package.
- Don't mirror upstream docs into the skill; capture condensed, reusable
  patterns.
- **Classify every dead-code grep hit as prod | test | benchmark
  before concluding "dead."** The repo-wide grep is mandatory, but the
  *reading* of its hits needs triage. A symbol is genuinely dead only
  if EVERY reference is (a) its own definition, or (b) a `_benchmarks/`
  call site with no production path. A non-benchmark **test** that
  imports/constructs it directly is proof of life — even when no
  production module constructs it (production may reach it lazily via
  `getattr` / a `= None` field set elsewhere, or the test IS the
  production smoke test). Concrete case this session: `grep` showed
  `ExtractionClient` instantiated only in `_benchmarks/`, which the
  audit's own rule would call "unreachable in prod" — yet
  `tests/test_c13b_extraction_diagnostics.py` does
  `from mnemosyne.extraction.client import ExtractionClient` and
  builds it. That makes it live. Rule: when a test imports the class
  confirms it constructs the object; if yes,
  KEEP. Report the triage (prod/test/benchmark counts) in the finding.
- **A public facade / `core/__init__.py` export is proof of life too.** A symbol
  that looks speculative because its only *direct* importers are tests can still
  be live via an indirection you'd skip: a property on the main `Memory`/`Client`
  class (e.g. `memory.compressor` lazily builds `MemoryCompressor`), plus an
  export in `core/__init__.py`. Grep BOTH the lazy `self.<x> =` facade AND the
  package `__init__`, not just `import SymbolName`. Case this session:
  `MemoryCompressor` had no production `import` but WAS live via the
  `memory.py` `compressor` property + `core/__init__.py` export + `test_patterns.py`
  → kept. When in doubt about a class with a facade, don't delete; collapse-tier
  or defer instead.
- **Don't delete a symbol mid-fix without re-grepping its new import sites.** If
  your own edit moved a module (e.g. `git mv chat_normalize.py _benchmarks/` to
  fix a "core vs benchmark" leak), update the importer's `from` line too — the
  file still exists, just relocated; the dead-code verdict was "move to
  `_benchmarks/`", not "delete".
- Don't over-prioritize cosmetic cleanups over the one duplicated base method
  that, if fixed, deletes 300 lines. Lead with the biggest leverage.
- The "Ponytail lens" is the user's reusable methodology, not a one-off task —
  keep it as the framing, not as a dated artifact.
