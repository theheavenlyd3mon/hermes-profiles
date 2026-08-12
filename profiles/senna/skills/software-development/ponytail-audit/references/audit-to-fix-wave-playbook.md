# Audit → Fix Wave Playbook (Ponytail sweep)

Reusable pattern for turning a Ponytail read-only audit into real, committed
fixes via `delegate_task`, without concurrent-edit collisions.

## Why waves, not one batch

`delegate_task` runs N subagents in parallel sharing one git worktree. If two
edit the same file, the second write wins and the first is lost silently. Group
by subsystem so each specialist owns disjoint files.

## Wave split (mnemosyne example)

- Wave 1a — security (persona / canonical / triples / annotations / content_sanitizer / plugins / cli)
- Wave 1b — embeddings/LLM (embeddings / veracity / shmr / binary_vectors / aaak / extraction)
- Wave 1c — importers/CLI (importers/*/base, mcp_tools, tool_schemas, cli)
- Wave 2a — sync + DR (sync / sync_server / hermes_memory_provider / dr/recovery)
- Wave 2b — recall/ranking (beam / query_cache / query_intent / mmr / recall_diagnostics)

Intersection note: `cli.py` + `mcp_tools.py` were touched by BOTH the security
wave (forget --hard, persona) and the importer wave (providers on CLI). Owner =
ONE specialist; the orchestrator reconciles on landing.

## Subagent brief skeleton (per specialist)

```
REPO: <path> — REAL project. Branch: <feature> (VERIFY git branch --show-current;
do NOT switch, do NOT push, do NOT git add -A). Real edits, verify with real
output, never fabricate.

MISSION: <the findings this specialist owns, with file:line from the audit>

For each finding: Idea / Implementation / Plan (numbered) / Why.

PONYTAIL safety carve-outs APPLY: never remove validation/security.

VERIFY: <import smoke test> + <pytest -k filter> + <new regression test>.

COMMIT (after verify passes): git add ONLY these files: <explicit list>.
git commit -m "<scope>: <what>". Retry on lock up to 3x. NEVER git add -A.

RETURN: files changed, real test output, anything NOT safely done (with why).
```

## Git guard (non-negotiable)

- `git branch --show-current` == feature branch before editing.
- Stage ONLY owned files by name — never `git add -A` / `git add .`.
- NEVER `git push` from a subagent (orchestrator decides when to push).
- On `fatal: ... Lock` → sleep 3s, retry, up to 3×.
- One commit per specialist per wave; message scoped to that subsystem.

## After each wave (orchestrator)

1. `git status` + `git log --oneline -n` — confirm only expected files changed.
2. Run the project test suite; fix regressions before next wave.
3. Reconcile any shared-file intersections (re-read, merge both diffs, retest).
4. Only then dispatch the next wave.
