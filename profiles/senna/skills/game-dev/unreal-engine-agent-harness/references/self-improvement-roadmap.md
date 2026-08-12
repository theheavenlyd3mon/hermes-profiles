# Self-Improvement Roadmap for the UE Agent Harness

Mined 2026-07-17 from `~/hermes-agent-self-evolution` (DSPy+GEPA spike)
and `~/.hermes/plugins/icarus` (fabric). Verdict: **GEPA later (M4),
Collect → Evaluate now with stdlib only.**

## The self-evolution loop (as actually implemented in the spike)

Only Phase 1 (skill-file optimization) is implemented; `evolution/{tools,prompts,code,monitor}/` are empty stubs.

1. **Select target** — `evolution/skills/evolve_skill.py::evolve()` → `find_skill()` (rglob SKILL.md) → `load_skill()` parses frontmatter + body.
2. **Build eval dataset** — `evolution/core/dataset_builder.py`: `EvalExample{task_input, expected_behavior, difficulty, category, source}` → `EvalDataset` train/val/holdout (0.5/0.25/0.25) as JSONL. Three sources: `SyntheticDatasetBuilder` (LLM reads artifact, emits rubric-style cases), `GoldenDatasetLoader` (hand-curated), `build_dataset_from_external()` in `core/external_importers.py` (mines ~/.claude, ~/.copilot, ~/.hermes sessions; heuristic pre-filter → LLM relevance score; **has a SECRET_PATTERNS regex worth copying verbatim**).
3. **Wrap as DSPy module** — `skills/skill_module.py::SkillModule`: artifact text becomes a Signature input field, run through `dspy.ChainOfThought`.
4. **Optimize** — `dspy.GEPA(metric=..., max_steps=N).compile(module, trainset, valset)`; falls back to `dspy.MIPROv2(auto="light")` on exception (dspy 3.x renamed GEPA's kwargs — expected).
5. **Fitness** — `core/fitness.py`: fast in-loop proxy `skill_fitness_metric` (keyword overlap), selective `LLMJudge` (correctness 0.5 / procedure 0.3 / conciseness 0.2, minus length penalty, emits textual feedback GEPA reflects on).
6. **Constraint gates** — `core/constraints.py::ConstraintValidator`: size limit, ≤+20% growth, non-empty, structure; `run_test_suite()` shells `pytest -q` zero-tolerance. Failed variants saved as `evolved_FAILED.md`, never deployed.
7. **Holdout A/B + report** — baseline vs evolved scored on holdout → `output/<name>/<ts>/{baseline,evolved}_skill.md + metrics.json`. One real run: narrative skill 0.476→0.556 (+16.8%), 5 iters, 191s.
8. **Deploy** — PLAN.md says git branch + PR + human merge; **not implemented in code** (no pr_builder.py).

## Portability map (what's Hermes-specific)

| Portable verbatim | Hermes-specific |
|---|---|
| EvalExample/EvalDataset schema + JSONL splits | SessionDB importer paths (~/.claude, ~/.copilot, ~/.hermes) — pattern ports, paths don't |
| SECRET_PATTERNS scrubber regex | TBLite/YC-Bench benchmark gates |
| SkillModule DSPy wrapper | Size limits (15KB skills / 500-char tool desc) — motivation is Hermes prompt caching |
| Constraint-gate philosophy (hard reject, save FAILED) | `find_skill` crawling ~/.hermes/skills |
| metrics.json before/after artifact format | PR-based deploy (Hermes GitHub workflow) |
| GEPA/MIPROv2 themselves (pip install dspy) | |

## Harness's structural advantage: deterministic eval signals

Hermes must pay for LLM-as-judge. A UE harness gets binary ground truth free:

- **UBT exit code** (`tools/build.py::build_module` already returns it) — strongest single signal.
- **Compiler error taxonomy** — `parse_build_errors()` yields `{file,line,severity,code,message}`; MSVC/UHT codes (C2065, C2664…) are finite and learnable. Recurring codes → new eval cases.
- **Mechanical invariants from the session log:** `dry_run` before `write_file` on same path; every new `.h` has a `.cpp` pair. No judge needed.
- **Editor bridge success** — `editor_command`/`compile_blueprints` return binary ok/error.
- **Efficiency** — iterations_used, build_attempts vs configured maxes (a better prompt = same success, fewer turns = real $ saved).
- **Future (Windows/live editor):** PIE automation test pass/fail via bridge `-ExecCmds="Automation RunTests"`; hot-reload layout-change detection from diffs.

## Fabric / fine-tuning path (the OTHER Hermes self-improvement loop)

Fabric ships as the **Icarus plugin** (`~/.hermes/plugins/icarus/`), NOT in the fork repo. Pipeline:

- `tools.py::fabric_write` → markdown entries w/ YAML frontmatter in `~/fabric/`: `{id, agent, timestamp, type, summary, training_value, verified, evidence}` + links (`review_of`, `revises` as agent:id). **Quality-tagged at write time**, not export time.
- `export-training.py::extract_pairs` → (user, assistant) JSONL pairs, modes: high-precision (high-value+verified+linked) / normal / high-volume.
- `state.start_training` → Together AI fine-tune; `fabric_eval` gates switch at avg score ≥0.7; `fabric_rollback_model` = .env restore.

**How it complements GEPA:** GEPA mutates *program text* ($2-10/run, works with 3 examples); fabric tunes *weights* (needs 100s of pairs, changes priors so good behavior costs no prompt tokens). GEPA first; fine-tune is the month-3 capstone.

**Harness equivalent:** build-fix trajectories are a perfect corpus (verified outcome = exit 0). Export successful (write → build-fail → parse → fix → build-pass) trajectories as assistant completions; fine-tune a small local model (ollama/lmstudio providers already in `llm.py`) as a cheap first-pass build-fixer. Phase 4+ only — corpus first.

## Roadmap

**Phase 1 — Collect (1-2 days, stdlib only).**
Extend `eval/metrics.py::SessionMetrics` into a trajectory record (schema below); add `eval/score.py::score_session(path)` computing the deterministic signals; add `eval/harvest.py` (external_importers pattern pointed at `sessions/*.jsonl` + the secret scrubber).

**Phase 2 — Evaluate (2-3 days).**
`datasets/tasks.jsonl` — 15-30 UE tasks in EvalExample schema (categories: new-class, build-fix, refactor, editor-command, blueprint). `eval/run_suite.py` — run Agent per task in stub mode, score, write `eval/results/<ts>.json` (the batch_runner equivalent; sequential is fine at this scale). `test_stub.py` becomes the hard gate.

**Phase 3 — Optimize (only after 1-2 produce data).**
First target: `prompts/system.txt` (smallest, highest leverage). **Plain A/B first** (`eval/ab_test.py`: two prompt files × suite → compare) — gets 80% of the value with zero DSPy. Add GEPA only once: 20+ task suite, 50+ real sessions, validated metric. Then its trace-reading (it sees *which* build error a prompt caused) beats hand-tuning. Est. M4.

**Lighter-than-GEPA options that fit earlier:** prompt A/B; bandit-style tool-docstring swaps (docstrings feed `tools/schema.py::schema_for` directly, trivially swappable); MIPROv2 if one DSPy optimizer wanted.

## Trajectory JSONL schema (start collecting NOW)

One line per session in `sessions/trajectories.jsonl` (keep per-session raw logs as replay source):

```json
{
  "session_id": "20260717_004309",
  "ts_start": "...", "ts_end": "...",
  "harness_version": "git:87cfbbe",
  "config": {"provider": "...", "model": "...", "max_build_retries": 3},
  "task": "...", "task_category": "new-class", "project": "MyGame",
  "plan": [{"tool": "...", "reason": "..."}],
  "steps": [{"n": 1, "tool": "build_module", "args": {...}, "ok": false, "ms": 31200,
             "exit_code": 1, "errors": [{"file": "...", "line": 14, "code": "C2065", "message": "..."}]}],
  "outcome": {"final_status": "success", "build_attempts": 2, "build_success": true,
              "error_codes_seen": ["C2065"], "files_written": ["...h", "...cpp"],
              "header_cpp_pairs_complete": true, "dry_run_before_write": true,
              "iterations_used": 7, "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0},
  "labels": {"training_value": "high", "verified": true, "source": "human-review"}
}
```

Fields that don't exist today and why: `steps[]` (the GEPA trace — raw logs have it scattered), `error_codes_seen` (builds the taxonomy), `dry_run_before_write`/`header_cpp_pairs_complete` (mechanical gates), `labels` (fabric lesson: tag quality at write time), `harness_version`+`config.model` (**you cannot A/B prompts later without knowing which config produced which trajectory**).
