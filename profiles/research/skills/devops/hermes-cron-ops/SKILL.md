---
name: hermes-cron-ops
description: "Diagnose, repair, and verify Hermes scheduled cron jobs: inference-config drift-guard failures, silent skill-skip, untrustworthy last_status, and cronjob update pinning quirks."
version: 1.0.0
author: Hermes Agent (research profile)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, scheduler, debugging, pinning, drift-guard, verification]
    category: devops
    related_skills: [hermes-agent-skill-authoring, kanban-orchestrator]
---

# Hermes Cron Job Ops

Operate, diagnose, and repair Hermes scheduled cron jobs (the `cronjob` tool). This skill
covers the failure modes that are NOT visible from the cron registry's `last_status` field —
the cases where a job reports success but did nothing, or aborts with a spend-guard error
before doing any work.

## When to use

- A cron job shows `last_status: error` and you need the root cause.
- A cron job reports `ok` but produced no real output (false positive).
- You changed the global inference provider/model and jobs stop running.
- A cron run logs `Skill(s) not found and skipped`.
- You need to pin or re-pin a job's model/provider after a config change.

## Diagnostic workflow (always in this order)

1. **List, then READ the output logs.** `cronjob action=list` gives status, but the real story
   is in `~/.hermes/profiles/<profile>/cron/output/<job_id>/<timestamp>.md`. Read the most
   recent file. Two signatures tell you everything (see `references/cron-diagnostics.md`):
   - `RuntimeError: Skipped to prevent unintended spend: global inference config drifted` →
     drift guard (Failure mode A).
   - `[IMPORTANT: The following skill(s) were listed for this job but could not be found and
     skipped: ...]` → skill not loading (Failure mode B).

2. **Inspect the backing store directly.** `~/.hermes/profiles/<profile>/cron/jobs.json` holds
   the truth: `"provider"`, `"model"` (explicit pin — often `null`), `"model_snapshot"` (the
   config captured at creation; this is what the drift guard compares against), `"last_error"`.
   The API `list`/`update` responses under-report (see Pitfalls), so read this file to confirm
   ground truth rather than trusting the tool's echo.

3. **Verify a fix with a live run + output grep — never by `last_status` alone.**
   `last_status: ok` is NOT proof of success. A job whose skills were skipped still reports `ok`
   while emitting garbage (e.g. a degenerate `\boxed{A}` answer instead of the real task). After
   any repair, run `cronjob action=run job_id=<id>` then check the NEW output file:
   ```bash
   f=$(ls -t ~/.hermes/profiles/<profile>/cron/output/<job_id> | head -1)
   grep -q "Skipped to prevent unintended spend" "$f" && echo "GUARD ERROR"
   grep -q "Skill(s) not found and skipped"        "$f" && echo "SKILL SKIP"
   ```
   Absence of BOTH = genuinely healthy. Also confirm the run actually loaded the skill
   (e.g. `The user has invoked the "X" skill… The full skill content is loaded below`).

## Failure mode A — Inference-config drift guard (hard abort)

**Symptom:** run fails instantly with
`RuntimeError: Skipped to prevent unintended spend: global inference config drifted since this
job was created (model '<old>' -> '<new>'), and this job is unpinned. No inference call was made.`

**Cause:** the job was created unpinned (`"model": null`). After creation, the *global* default
inference config (provider and/or model) changed. Hermes refuses to spend on an unpinned job
whose effective config no longer matches what it was created with. There are two axes:
model drift (`stepfun/... -> tencent/hy3:free`) and provider drift (`nous -> custom`).

**Fix — pin the job to the current config.** Use `cronjob action=update` with BOTH `provider`
and `model` set:
```
cronjob action=update job_id=<id> provider=<prov> model=<model>
```
The guard clears once `model_snapshot` (in jobs.json) equals the current global model, and
`provider` is explicitly set. Confirm by reading jobs.json, not the API echo.

**Quirk — `model`-only updates are silently dropped.** Sending
`cronjob action=update job_id=<id> model=<model>` with no `provider` returns
`{"error":"No updates provided."}` and changes nothing. The explicit `model` pin may stay `null`
even when the call "succeeds" while paired with provider. ALWAYS send `provider` and `model`
together.

## Failure mode B — Skills silently skipped (soft failure, false `ok`)

**Symptom:** output opens with
`[IMPORTANT: The following skill(s) were listed for this job but could not be found and skipped:
research-pipeline, llm-wiki, arxiv]`. The job may still report `last_status: ok` because
inline-prompt execution didn't throw — it just ran without the skill's instructions.

**Cause (most common):** the skill is installed in a **nested duplicate directory**, e.g. BOTH
`skills/research/llm-wiki/SKILL.md` AND `skills/research/llm-wiki/llm-wiki/SKILL.md`.
The loader then sees two matches and either (a) throws
`Ambiguous skill name: 2 skills match… Refusing to guess` when resolved via `skill_view`, or
(b) silently skips the skill during cron load. The nested copy is almost always a stale duplicate
(verify with `md5`/`diff` before deleting). See `hermes-agent-skill-authoring` for the canonical
one-`SKILL.md`-per-dir layout.

**Fix:** remove the nested duplicate dir, keeping the canonical (outer) copy which also holds
`references/` and `scripts/`:
```bash
cd ~/.hermes/profiles/<profile>/skills/research
rm -rf llm-wiki/llm-wiki arxiv/arxiv research-pipeline/research-pipeline
```
Before deleting, confirm the outer copy is complete and the nested copy adds nothing: diff the
two `SKILL.md` files, and check the outer dir for `references/` + `scripts/` the nested one lacks.
If the two copies DIVERGE (different checksums), decide which is canonical before deleting either.

**Other causes of skill-skip:** `WIKI_PATH`/env mismatch, or the skill simply not installed for
that profile. Rule those out if no nested dup exists.

## Verification checklist (end of any cron repair)

- [ ] `jobs.json` shows `provider` = current global provider AND `model_snapshot` = current global model (drift cleared).
- [ ] No nested duplicate skill dirs remain.
- [ ] Live `cronjob action=run` produces an output file with NEITHER guard error NOR skill-skip notice.
- [ ] Output file shows the skill actually loaded and did real work (not a degenerate stub).

## Pitfalls

- **Never trust `last_status: ok` as success-proof.** Always read the output file. In a real
  incident a Monday job reported `ok` while emitting `\boxed{A}` because its skills were skipped.
- **`cronjob update` with a model-only payload is a no-op** — always pair `model` with `provider`.
- **The API `list`/`update` responses under-report.** `model` can show `null` post-update while
  `model_snapshot` (in jobs.json) actually changed. Read jobs.json for ground truth.
- **macOS HFS+ hides case differences** (`llm-wiki` vs `LLM-Wiki` both resolve) — that is NOT the
  cause of skill-skip when a genuine nested-dup structure exists. Don't chase case when the dir
  tree shows real nesting; fix the nesting instead.

## References

- `references/cron-diagnostics.md` — exact error signatures, jobs.json field map, and the grep
  verification recipe, with a worked example from a real incident.
