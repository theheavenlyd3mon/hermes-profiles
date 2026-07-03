# Autocontext — Recursive Self-Improving Harness

**Source**: https://github.com/greyhaven-ai/autocontext
**Stars**: 978 (May 2026)
**License**: Apache-2.0
**Language**: Python (pip) + TypeScript (npm)
**Status**: Evaluated 2026-05-10 — high signal, not yet adopted.

## What It Is

A harness that iterates on a goal against real evaluation, keeps what works, throws out what didn't, and produces a structured trace + reusable playbooks. Each iteration gets better, not just different.

## Architecture

```
Goal (plain language)
  ├── autocontext solve "improve X" --iterations 5
  │     ├── gen_1: propose → analyze → score
  │     ├── gen_2: learn from gen_1 → propose → analyze → score
  │     └── ...
  └── Output:
        ├── runs/<run_id>/trace.jsonl
        ├── runs/<run_id>/generations/gen_N/{strategy, analysis, score}.json
        ├── runs/<run_id>/report.md
        ├── runs/<run_id>/artifacts/
        ├── knowledge/<scenario>/playbook.md   ← accumulated lessons
        └── knowledge/<scenario>/hints.md
```

## Key Concepts

- **Competitor** — proposes strategies
- **Analyst** — evaluates outcomes
- **Playbook** — plain markdown the next run reads as context. Contains empirically-validated rules.
- **Trace** — every prompt, tool call, and outcome in order. Replayable, diffable.
- **Knowledge directory** — survives across runs. Lessons accumulate.

## Supported Backends

| Provider | Env Var |
|----------|---------|
| Pi (local coding agent) | `AUTOCONTEXT_AGENT_PROVIDER=pi` + `AUTOCONTEXT_PI_COMMAND` |
| Anthropic | `AUTOCONTEXT_AGENT_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` |
| OpenAI | `AUTOCONTEXT_AGENT_PROVIDER=openai` + `OPENAI_API_KEY` |
| Gemini | `AUTOCONTEXT_AGENT_PROVIDER=gemini` |
| Claude CLI | built-in |
| Codex CLI | built-in |
| MLX | built-in |

## Integration Points

- **MCP server** — `autoctx mcp-serve` exposes `autocontext_solve_scenario`, `autocontext_evaluate_output`, etc.
- **Hermes CLI skill** — `autoctx hermes export-skill` generates a SKILL.md for Hermes
- **Pi skill** — `pi install npm:pi-autocontext` loads natural-language tools
- **Hermes curator inspect** — `autoctx hermes inspect --json` checks integration state

## Assessment for Our Stack

**High signal.** Autocontext is a meta-cognition layer that sits *above* our existing tools:

| What we have | What autocontext adds |
|--------------|----------------------|
| Hermes LCM (context retention) | Iterative improvement across runs |
| Memory + Skills (knowledge persistence) | Structured playbooks with empirical validation |
| GHCRs / Dojo (correction loops) | Formal iteration with scoring + traceability |
| Our agent team (architect/coder/qa) | Automated competitor/analyst loop |

**Where it fits:**
- **Prompt engineering** — iteratively optimize system prompts against a rubric
- **Workflow optimization** — refine multi-step agent workflows with scored generations
- **Knowledge distillation** — produce playbooks from our own completed tasks

**Integration cost:**
- Hermes CLI skill export is automatic (`autoctx hermes export-skill`)
- Could run as a periodic cron task or ad-hoc via delegation
- The `playbook.md` output could feed into our LLM-Wiki or Team-Wiki

**Would integrate if:**
- We start doing structured prompt/workflow optimization (GHCR refinement, skill generation, etc.)
- The playbook → knowledge-base pipeline gets built (autoctx runs → LLM-Wiki ingestion)
