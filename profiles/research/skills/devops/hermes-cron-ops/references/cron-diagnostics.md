# Cron Diagnostics — error signatures, jobs.json field map, verification recipe

Worked from a real incident (2026-07-11): 7 research-pipeline crons, 6 failing.

## The two failure signatures (read the output file, not just status)

Output files live at `~/.hermes/profiles/<profile>/cron/output/<job_id>/<timestamp>.md`.

**A. Inference-config drift guard (hard abort, `last_status: error`)**
```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted
since this job was created (model 'stepfun/step-3.7-flash:free' -> 'tencent/hy3:free'),
and this job is unpinned. No inference call was made.
```
Also fires on provider axis: `(provider 'nous' -> 'custom')`.
Cause: job created unpinned (`"model": null`); global default changed after creation.

**B. Skills silently skipped (soft failure, can show `last_status: ok`)**
```
[IMPORTANT: The following skill(s) were listed for this job but could not be found
and skipped: research-pipeline, llm-wiki, arxiv. Start your response with a brief
notice so the user is aware...]
```
Cause: skill installed in nested duplicate dir (e.g. both `skills/research/llm-wiki/SKILL.md`
and `skills/research/llm-wiki/llm-wiki/SKILL.md`). Fix = remove the nested dir.

## jobs.json field map (the ground truth)

File: `~/.hermes/profiles/<profile>/cron/jobs.json`. Per job:
- `provider` — explicit pin. When set to current global provider, the provider-drift axis clears.
- `model` — explicit model pin. Often stays `null` even after a successful paired update.
- `model_snapshot` — the model captured at creation / last update. THE drift guard compares
  this against the live global model. When `model_snapshot` == current global model, the
  model-drift axis clears — even if `model` is still `null`.
- `last_error` — exact RuntimeError text from the last run (better than `last_status`).

The `cronjob list`/`update` API responses UNDER-REPORT: `model` may echo `null` while
`model_snapshot` actually changed. Read jobs.json to confirm, not the API echo.

## Quirk: model-only update is a no-op

```
cronjob action=update job_id=<id> model=tencent/hy3:free
# => {"error":"No updates provided."}  (changes nothing)
```
ALWAYS pair model with provider:
```
cronjob action=update job_id=<id> provider=nous model=tencent/hy3:free
```

## Verification recipe (run AFTER any repair)

Pin the job, fix any nested-dup skill dirs, then:
```bash
cronjob action=run job_id=<id>
f=$(ls -t ~/.hermes/profiles/<profile>/cron/output/<id> | head -1)
grep -q "Skipped to prevent unintended spend" "$f" && echo "GUARD ERROR STILL PRESENT"
grep -q "Skill(s) not found and skipped"        "$f" && echo "SKILL SKIP STILL PRESENT"
```
Healthy = NEITHER grep matches, AND the file shows the skill actually loaded
(`The user has invoked the "X" skill… The full skill content is loaded below`) and produced
real work (not a degenerate stub like `\boxed{A}`).

## Worked result of the incident
- Before fix: `2026-07-07` run → GUARD ERROR PRESENT + SKILL SKIP PRESENT, `last_status: error`.
- After fix: `2026-07-11` run → no guard error, skills loaded OK, `last_status: ok`, 1763-line
  real output. (Monday `llm-agents` had falsely reported `ok` all along — its skills were
  skipped; the false `ok` is why `last_status` alone can never be trusted.)
