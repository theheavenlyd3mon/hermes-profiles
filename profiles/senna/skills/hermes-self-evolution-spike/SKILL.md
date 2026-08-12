---
name: hermes-self-evolution-spike
description: Run Nous Research's hermes-agent-self-evolution (DSPy + GEPA skill optimizer) against THIS Hermes install, rerouted to Nous models (no Claude needed). Safe sandbox — emits a before/after diff + holdout score, never auto-merges. Use to tune a SKILL.md's body via evolutionary search.
---

# Self-Evolution Spike — run GEPA on a skill, on Nous

Evolves the *body* of a SKILL.md (strips YAML frontmatter, mutates the prose, reassembles) by generating eval examples, running GEPA (falls back to MIPROv2), and scoring baseline-vs-evolved on a holdout set. Output is a diff + metrics only. **It never edits the live skill or opens a PR on its own** — you review and merge manually.

## When to use
- User asks to "self-evolve", "tune", "optimize", or "improve" a skill or prompt.
- User references hermes-agent-self-evolution or wants the agent to improve its own instructions.
- You want a data-driven pass at a procedural skill before hand-editing it.

## Source repo
- `NousResearch/hermes-agent-self-evolution` — Phase 1 (skill evolution) implemented; Phases 2–5 planned. Early but real.
- Safety model: mutates **only the SKILL.md body** (frontmatter preserved), runs offline from any live session, emits a **diff + PR for human merge** — never hot-swaps into a running agent. Dual optimizer: GEPA with automatic MIPROv2 fallback.
- Dependency is the **OpenAI SDK only** (`openai>=1.0.0`) — NOT Anthropic/Claude. Reroutable to Nous.
- Default models hardcoded `openai/gpt-4.1` (optimizer) / `openai/gpt-4.1-mini` (eval/judge); override via `--optimizer-model` / `--eval-model`.
- Eval dataset sources: `synthetic` (LLM-generated), `golden` (your JSONL), `sessiondb` (mines ~/.hermes state).
- **Pick the target by usage, not memory.** Run `scripts/skill_usage.py [profile]` — it mines `~/.hermes/profiles/<profile>/state.db` and ranks skills by real `skill_view` call counts. Evolve a heavily-used *procedural* skill (clear pass/fail), not a fuzzy/tonal one.

## Prereqs (one-time)
```
git clone --depth 1 https://github.com/NousResearch/hermes-agent-self-evolution.git ~/hermes-agent-self-evolution
cd ~/hermes-agent-self-evolution
uv venv .venv && source .venv/bin/activate
uv pip install "dspy>=3.0.0" rich click pyyaml
python -c "import dspy; print(dspy.__version__, hasattr(dspy,'GEPA'))"   # expect 3.x, GEPA True
```
Clone lives at `~/hermes-agent-self-evolution` (verified). dspy 3.2.1 has both GEPA + MIPROv2.

## Reroute to Nous (no Claude)
The repo hardcodes `openai/gpt-4.1` / `openai/gpt-4.1-mini`. Nous proxies those slugs, but litellm (used by dspy) **strips one `openai/` prefix**, so you must pass the **double prefix** `openai/openai/gpt-4.1*`. Full procedure, auth-store key location, and error transcripts are in skill `nous-openai-reroute`. Point the OpenAI SDK at Nous:
```
KEY=$(python3 - <<'EOF'
import json,os
auth=json.loads(open(os.path.expanduser('~/.hermes/auth.json')).read_text())
print(auth.get('providers',{}).get('nous',{}).get('agent_key',''))
EOF
)
export OPENAI_BASE_URL=https://inference-api.nousresearch.com/v1
export OPENAI_API_KEY="$KEY"
```
Do NOT commit the key. It lives in `~/.hermes/auth.json` (`providers.nous.agent_key`), NOT config.yaml/.env — load it from there at runtime. (The old snippet reading `config.yaml` returns an empty key; use auth.json.)

## Find the skill
`find_skill` crawls `<hermes_repo>/skills/` for `<name>/SKILL.md`. To target a PROFILE skill (not the core agent tree), pass the profile dir:
```
--hermes-repo ~/.hermes/profiles/senna
```
This makes `skills/narrative/SKILL.md` discoverable. Core agent source at `~/.hermes/hermes-agent` also works (auto-discovered) but edits there are riskier — prefer profile skills for spikes.

## Run
```
cd ~/hermes-agent-self-evolution && source .venv/bin/activate
# 1) dry-run validates setup, spends no API calls
python -m evolution.skills.evolve_skill --skill <name> --hermes-repo ~/.hermes/profiles/senna --dry-run
# 2) real run; bound iterations to control cost (default 10)
python -m evolution.skills.evolve_skill --skill <name> --hermes-repo ~/.hermes/profiles/senna --iterations 5 --eval-source synthetic
```
`--eval-source` options: `synthetic` (default, LLM-generated), `golden <dir>`, `sessiondb` (mines claude-code/copilot/hermes history).

## Output
`output/<skill>/<timestamp>/` → `evolved_skill.md`, `baseline_skill.md`, `metrics.json` (holds baseline vs evolved holdout score, size delta, improvement). Diff manually:
```
diff output/<skill>/<ts>/baseline_skill.md output/<skill>/<ts>/evolved_skill.md
```
No auto-merge happens — copy the body into the live skill only after you approve.

## Unblocking creative/tonal skills (eval rubric)
The fuzzy-target problem (below) is real but **solvable**. Before evolving a creative skill (`narrative`, `murim-narrative`), author a **deterministic scored rubric** and feed it as a `golden` eval set (`--eval-source golden <dir>`). The LLM-judge can't score "noir tone", but a checklist can:
- Stability-trap 7-item mandatory pass rate (see `narrative` skill).
- Tier-1 banned-word count == 0.
- Em-dash density ≤ 2/page.
- ≥1 genuinely surprising sentence present.
Encode each as a pass/fail row in `golden/rubric.jsonl` (scored 0/1). The optimizer now has a real gradient instead of vibes. Pattern source: `NirDiamant/agents-towards-production` evals tutorials.

## Caveats / what the run actually optimizes
- This repo evolves the **DSPy module's instruction prompt** (how an agent *applies* the skill), NOT the SKILL.md prose. `evolved_skill.md` is often byte-identical to `baseline_skill.md` even when the holdout score moved — the gain is in the internal `TaskWithSkill` signature. Don't expect rewritten skill text.
- **Creative skills are fuzzy targets.** The LLM-judge (`skill_fitness_metric`) scores task adherence, not tone. Evolving a prose/craft skill may show small or negative "improvement" because the judge can't measure voice. Treat the diff as a suggestion, not an authority.
- Constraint gates: skill ≤15KB, ≤20% growth, semantic-preservation check vs baseline. Evolved text failing gates is saved as `evolved_FAILED.md` and not deployed.
- Cost scales with iterations × dataset size × eval calls. Start at 5 iterations (~3 min on Nous, ~$0.10-0.30).
- GEPA in dspy 3.x has a different `__init__` (no `max_steps`; uses `max_full_evals`/`max_metric_calls`). `evolve_skill.py` calls the old signature, so it raises and **auto-falls back to MIPROv2** — this is fine and expected.

## Bugs found & fixed during first run (already patched in our clone)
- `_check_skill_structure` requires YAML frontmatter, but `evolve_skill.py` passed only the *body fragment* to the validator → valid output wrongly rejected as `evolved_FAILED.md`. **Fix**: validate `evolved_full` (reassembled skill) instead of `evolved_body`. Patch already applied to `~/hermes-agent-self-evolution/evolution/skills/evolve_skill.py`.
- Nous credential live in `~/.hermes/auth.json` under `providers.nous.agent_key` (OAuth JWT), NOT in `config.yaml` or `.env`. Load it from there at runtime; never commit it.
- litellm strips ONE `openai/` prefix, but Nous needs the full `openai/gpt-4.1*` slug. **Fix**: pass `openai/openai/gpt-4.1` (double prefix) as the model name so Nous receives `openai/gpt-4.1`. `dspy.LM("openai/openai/gpt-4.1-mini", api_key=..., api_base="https://inference-api.nousresearch.com/v1")` works. (General reroute procedure + error transcripts: skill `nous-openai-reroute`.)
- Missing deps for the MIPROv2 fallback: install `dspy[optuna]` (not just `dspy`).
