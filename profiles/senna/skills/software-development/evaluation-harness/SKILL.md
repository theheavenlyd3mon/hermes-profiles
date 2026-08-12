---
name: evaluation-harness
title: Evaluation Harness
description: Add observability and evaluation instrumentation to UE Agent Harness
category: software-development
author: user
created: 2026-07-16
---

# Evaluation Harness

> **Note:** This skill is a stub. The canonical, up-to-date coverage lives in the
> **`unreal-engine-agent-harness`** umbrella skill (game-dev category), which
> documents the full eval architecture, the deterministic scoring system, the
> 26-task suite, and all pitfalls. This stub exists only for backward
> compatibility with cron jobs and references that predate the umbrella.

## What exists

The eval harness is built into `agentunreal/eval/` as a deterministic,
LLM-judge-free scoring system. The engine (UBT exit codes, MSVC error taxonomy,
the dry_run-before-write invariant) provides binary ground truth, so scoring
reads the harvested trajectory + the agent's own metrics and checks rubric
expectations mechanically.

### Files
- `agentunreal/eval/metrics.py` — `SessionMetrics` dataclass, saved to
  `sessions/metrics.jsonl` per run.
- `agentunreal/eval/harvest.py` — folds `sessions/*.jsonl` into
  `sessions/trajectories.jsonl` with `outcome` (build_success, build_attempts,
  dry_run_before_write, files_written, steps, error_codes_seen).
- `agentunreal/eval/score.py` — `Score` dataclass + `score_run()` + `aggregate()`.
  Hard constraints: `must_build`, `max_build_attempts`, `requires_dry_run`,
  `forbidden_error_codes`.
- `agentunreal/eval/suite.py` — `EvalExample` loader + `materialize_fixture()`.
  Tasks in `agentunreal/eval/tasks/*.json`, kinds: new-class/build-fix/refactor/editor-command.
- `agentunreal/eval/run_suite.py` — stub-mode runner with a scripted LLM.
  `python -m agentunreal.eval.run_suite --json` runs all tasks.
- `agentunreal/eval/ab.py` — A/B two system prompts → pass-rate/build/attempt/violation deltas.

### Agent integration
- `agentunreal/core/agent.py` — `SessionMetrics` in `run()`, `on_event` hook,
  `sessions/*.jsonl` logging with `tool_name` per tool message.

## Verification
```
pytest test_stub.py -v                          → 15 passed
python -m agentunreal.eval.run_suite --json     → 26 tasks, 26 passed, 0 violations
```

## Key pitfalls (from 2026-07-23 expansion session)
1. **Prompt path resolution:** `Path("prompts/system.txt")` breaks when run as
   a module from a tmp dir. Use `Path(__file__).resolve().parent.parent.parent / "prompts" / name`.
2. **ScriptedLLM planner collision:** The eval runner's scripted LLM must handle
   `tools is None` (the planner call) separately so it doesn't consume the first
   scripted tool call.
3. **Session file selection:** `sorted(glob("*.jsonl"))[-1]` picks `metrics.jsonl`
   (alphabetically last). Filter out `metrics.jsonl` and `trajectories.jsonl`.
4. **Harvest enrichment:** The raw log must include `tool_name` in tool messages
   so the harvester can verify `dry_run → write_file` ordering.
5. **Tool parameter naming:** ScriptedLLM args must match `inspect.signature`
   of the real tool (e.g. `module_name`, not `module`).

See `references/eval-harness-debugging.md` in the `unreal-engine-agent-harness`
skill for the full debugging transcript. This skill's
`references/eval-session-transcript.md` has the session summary and
`scripts/run_test_suite.py` runs both pytest and the eval suite.