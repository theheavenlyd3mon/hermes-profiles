# Post-Build Verification & Readiness Review

## When to Use

After all implementation tasks are done and the project runs, but before submission/delivery. Use this when the user asks for "a final review," "what else needs to be done before submission," or "have the team look it over."

## Pattern: Parallel Review + Iterative Fix

### Phase 1 — Dispatch Parallel Reviewers

Don't do the review yourself. Fan out 3 specialist reviewers in one `delegate_task(tasks=[...])`:

```python
delegate_task(tasks=[
    {"goal": "Code review: check imports, run entrypoint, fix any import/env errors, verify pipeline on 3 sample runs", "toolsets": ["terminal", "file"]},
    {"goal": "Security audit: check .gitignore, scan for secrets in HEAD, verify LICENSE/CONTRIBUTING/CHANGELOG present", "toolsets": ["terminal", "file", "web"]},
    {"goal": "Completeness review: check README accuracy vs actual files, submission doc consistency, verify video/demo files exist locally", "toolsets": ["terminal", "file"]},
])
```

All 3 run in parallel. Wait for all results before acting.

### Phase 2 — Triage Findings

When results come back, triage each finding:

- **CRITICAL** — Pipeline crashes, secrets exposed, missing required files — fix first
- **HIGH** — Doc claims don't match implementation, inconsistent phase counts — fix after critical
- **MEDIUM** — Missing references, word count issues, cosmetic — fix last

### Phase 3 — Surgical Fix + Verify (One at a Time)

Fix ONE issue at a time with a targeted patch, then verify with a focused script. Do NOT batch multiple fixes — each fix needs separate verification.

```python
# 1. Read current state
read_file("path/to/file")

# 2. Apply surgical patch
patch(path="...", old_string="...", new_string="...")

# 3. Verify with focused ad-hoc script
# Create under /var/folders/.../T/hermes-verify-<name>.py
```

### Phase 4 — Pipeline End-to-End Verification

After all fixes are applied, run a full end-to-end verification on ALL supported scenarios:

```python
# Test all urgency paths
for label, report in [
    ("emergency", "I smell gas, possible gas leak"),
    ("urgent", "AC not cooling, newborn"),
    ("routine", "garbage disposal humming"),
]:
    result = await run_pipeline(report)
    # Check all 10 phases pass
    # Check guardrails pass
    # Check recommendation exists
```

### Phase 5 — Git Commit

Only after ALL paths pass:

```bash
git add -A && git commit -m "fix: ..."
git push
```

## Common Pitfalls

### Venv vs System Python

After subagent code changes, verify that the venv Python is being used, not the system Python. System Python often lacks project dependencies (`stripe`, `pyyaml`, `openai`).

**Fix:** Run verification with the explicit venv path:
```bash
.venv/bin/python3 -c "import agent; print('ok')"
```

Don't rely on shell `.venv/bin/activate` being active — terminal calls are fresh shells each turn.

### Subagents Overwrite Each Other's Fixes

When two subagents modify the same file (e.g. `agent.py`), one can overwrite the other's changes. Always check `git diff --stat` after parallel tasks land to see which files were touched. Re-read any file modified by a subagent before editing it yourself.

### Subagent Verification Scripts May Not Execute

Subagents may claim to have written verification scripts to `/var/folders/.../T/` but the sandbox can refuse writes to that path. Always run a manual verification after subagent work rather than trusting "15/15 passed" claims.

### Import Path Dependency

If `agent.py` uses `from tools.triage import ...` (relative to project root), it will fail when run from any other directory. Fix by adding the project root to `sys.path` before imports:

```python
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
```

### API Response Shape Mismatch

When calling external AI APIs (Nemotron, GPT, etc.), the response JSON shape can vary between calls even with the same prompt. Always guard response access:

```python
raw = await api_call(...)
if not isinstance(raw, dict):
    raw = {}  # fallback
rec = raw.get("recommendation")
if not isinstance(rec, dict):
    rec = {"vendor_name": cheapest["vendor_name"], ...}
```

### Guard Against Hanging API Calls

Wrap async API calls in `asyncio.wait_for` with a short timeout (e.g. 8s for ranking, 30s for generation). If the API is slow/unresponsive, fall back to deterministic logic instead of blocking the pipeline.

```python
try:
    result = await asyncio.wait_for(api_call(...), timeout=8.0)
except asyncio.TimeoutError:
    result = None  # fallback to deterministic logic
```
