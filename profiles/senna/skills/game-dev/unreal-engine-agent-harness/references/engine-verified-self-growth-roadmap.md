# Engine-Verified Self-Growth — Roadmap Reference

Condensed from the 2026-07-17 three-way diagnostic (ue-agent-harness × hermes-agent-fork × hermes-agent-self-evolution). Full artifacts in the harness repo: `docs/DIAGNOSTIC_AND_PLAN_2026-07.md`, `HERMES_ARCHITECTURE_REVIEW.md`, `docs/landscape-review-2026-07.md`, `docs/ui-design-spec.md`.

## The thesis

Self-growing (agent writes/optimizes its own skills+prompts) is commoditizing in 2026 — GEPA (~5.7k★), Claude Code auto-improving skills, Kulaxyz self-learning-skills. The open niche and the moat is **engine-verified** self-growth: the optimization/eval signal is binary UE ground truth, not an LLM judge.

## Why UE gives free ground truth (generic agents pay for it)

- **UBT exit code** — did the module compile. Strongest single signal.
- **MSVC/UHT error taxonomy** — C2065, C2664, unresolved-external, UHT "Unresolved type". Finite, learnable; recurring codes auto-generate targeted eval cases.
- **dry_run → write_file invariant** — mechanically checkable from the trajectory log (every write preceded by a dry_run on same path).
- **`.h`/`.cpp` pairing** — filesystem-verifiable after a session.
- **Editor/Blueprint compile success** — binary via the bridge.
- Future: PIE run + viewport screenshot diff.

Hermes/generic agents must run an LLM-as-judge to approximate "did it work." A UE harness reads it off the compiler. That asymmetry is the whole play.

## Build order (ponytail — stop when it stops paying)

- **Phase 0 — fix defects first.** Role-alternation bug (synthetic user msg mid-loop), dry_run→write_file hash gate, update stale README/roadmap/comparison docs. ~50 LOC + `tests/verify_phase0.py`.
- **Phase 1 — collect + safety (stdlib).** Skills system (`skills/<domain>/<name>/SKILL.md` + `skills_list`/`skill_view`, the self-growing backbone, ~80 LOC); normalized trajectory logging (`sessions/trajectories.jsonl`: per-step args/ok/errors, `error_codes_seen`, `dry_run_before_write`, `labels`); shadow-git checkpoint/revert; one-time project-scan→AGENTS.md domain map; confidence-tiered answers.
- **Phase 2 — evaluate (stdlib).** 15-30 hand-written UE tasks (`new-class`/`build-fix`/`refactor`/`editor-command`) with rubric expectations; deterministic `score_session` from trajectory logs; A/B prompt harness (two prompt files → run suite → compare). This is ~80% of prompt-optimization value with zero DSPy.
- **Phase 3 — grow.** Plugin system (drop-in dirs + hooks); context compression (UBT stdout is 5-50KB/attempt, loops die by context window); GEPA on `prompts/system.txt` first (metric = suite score; GEPA reads *why* builds fail); provider fallback chain.
- **Phase 4 — autonomy/capstone.** Cron scheduler; MCP server mode; PIE closed-loop playtest; fabric-style fine-tune export of verified build-fix trajectories → small local model as first-pass build-fixer.

## Hard-won ordering rule

Do NOT build GEPA before trajectories + a task suite exist. GEPA with ~3 examples + a keyword-overlap metric = noise. Collect → Evaluate → Optimize. Copy from the hermes-agent-self-evolution spike verbatim: the `EvalExample`/`EvalDataset` JSONL schema + train/val/holdout split, the `SECRET_PATTERNS` secret-scrubber, and the constraint-gate philosophy (hard-reject invalid variants, save `*_FAILED.md`, gate on `pytest` zero-tolerance).

## Fabric (fine-tuning path) — later capstone

Fabric is NOT in the hermes fork repo; it's the Icarus plugin (`~/.hermes/plugins/icarus/`). Quality-tagged markdown entries → JSONL pairs → Together AI fine-tune → eval-gated model swap (≥0.7). GEPA optimizes program *text* (cheap, ~$2-10, 3 examples); fine-tuning changes *weights* (needs hundreds of pairs, real cost). GEPA is the day-one loop; fine-tune is month-3+.

## Market / ecosystem watch

Epic shipped an experimental MCP plugin in UE 5.8 and will integrate Claude/Gemini/Codex natively in UE6. The community is converging on MCP. Recommend making the harness an MCP client/server rather than a parallel bespoke-bridge universe, or the ecosystem's tools stay unreachable. Nobody open-source currently ships Voyager-style skill self-authoring for game dev — the intersection (self-authored AND engine-verified) is open.
