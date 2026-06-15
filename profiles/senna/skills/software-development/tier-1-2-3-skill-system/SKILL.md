---
name: tier-1-2-3-skill-system
description: Use when creating, editing, reviewing, or organizing agent skills. Decides whether a skill should be text-only (Tier 1), script-backed (Tier 2), or backed by an ML/specialist pipeline (Tier 3). Default answer is always the lowest tier that works.
version: 1.0.0
author: Hasan Ali (imported)
source: https://github.com/H-Ali13381/tier-1-2-3-skill-system
triggers:
  - skill review
  - create skill
  - organize skills
  - skill design
  - which tier
  - skill consolidation
---

# Tier 1-2-3 Skill System

## Core Philosophy

> Start simple, then promote only when the workflow proves it needs more machinery.
> The default answer is the lowest tier that works.

A skill is reusable operational knowledge. It should reduce future steering, capture real pitfalls, and make repeatable work reliable. Do not use this to justify overbuilding.

## When to Use

- Creating a new agent skill
- Reviewing or cleaning up an existing skill
- Deciding whether a workflow belongs in plain instructions, scripts, or a specialist model
- A skill is becoming too long, vague, or hard to operate
- Agents keep rewriting the same helper code for the same task
- A task needs perception, scoring, ranking, detection, or classification that the base agent cannot do reliably

## The Three Tiers

| Tier | Shape | Use When | Upgrade Trigger |
|------|-------|----------|-----------------|
| **1. Text-only** | `SKILL.md` | Value is judgment, policy, sequencing, taste, style, checklist | Agents repeatedly rewrite glue code or make mechanical mistakes |
| **2. Text + script** | `SKILL.md` + `scripts/` | Workflow has deterministic, repeatable mechanics (parse, validate, convert, audit, launch, package, benchmark, export) | Scripts and prompts cannot provide the missing perception, ranking, scoring, detection, or domain inference |
| **3. Text + script + ML pipeline** | `SKILL.md` + `scripts/` + training/eval/model artifacts | Agent needs non-native capability: classifier, detector, reranker, scorer, evaluator, verifier, specialist model | The specialist is stable enough to package as a tool, MCP server, CLI, or standalone skill |

**Short version:**
- Tier 1 teaches the agent **what to do**.
- Tier 2 gives the agent **deterministic machinery** to do it.
- Tier 3 gives the agent a **new sense organ**.

## Tier 1: Text-only

Use when the hard part is **judgment**.

**Good fits:** writing voice, review philosophy, research synthesis, design principles, safety rules, operational checklists

**Keep skill focused on:**
- Trigger conditions
- Decision rules
- Common mistakes
- Verification checklist
- One or two concrete examples

Avoid adding scripts when the agent only needs better taste, sequencing, or policy.

## Tier 2: Text + Script

Use when the skill would otherwise make agents keep inventing the same glue code.

**Good fits:** file validation, format conversion, skill packaging, report generation, project audits, benchmark aggregation, repeatable setup or launch commands

**Rules:**
- `SKILL.md` explains when, why, and how to call the script
- `scripts/` does the deterministic work
- Scripts should be idempotent where practical
- Scripts should expose flags or environment variables instead of requiring edits
- Scripts should verify success before exiting 0
- Scripts should avoid logging secrets
- Bulky rationale belongs in `references/`, not the main skill body

**Promotion signal:** if an agent writes the same helper script twice, make it a bundled script.

## Tier 3: Text + Script + ML Pipeline

Use when the base model lacks a **measurable capability** and ordinary scripts cannot fill the gap.

**Good fits:** wakeword/audio detection, screenshot/layout scoring, UI/theme coherence judging, search reranking, patch-risk classification, fact-consistency verification, domain-specific extraction, anomaly detection

**Rules:**
- Define inputs, outputs, metrics, and baselines before training
- Include hard negatives and failure cases
- Keep inference compact and machine-readable, preferably JSON
- Explain when to trust the specialist and when to abstain
- Explain how the specialist output changes the agent's next action
- Add an eval plan and model card before publishing a specialist model

**Promotion signal:** the missing piece is perception, ranking, scoring, detection, classification, or domain inference.

## Decision Checklist

Before writing or changing a skill, ask:

1. Is this durable operational knowledge?
2. Will it reduce future steering?
3. Which tier is the lightest reliable fit?
4. Can this be consolidated with an existing skill?
5. Is repeated mechanical work better handled by a script?
6. Is the missing capability actually ML-shaped and measurable?
7. What verification proves the skill works?

## Related Skill

Use `recursive-agent-improvement` when the decision reaches Tier 3 and the agent needs to turn a measurable failure into a specialist tool, evaluator, reranker, classifier, detector, verifier, or ML training pipeline. This skill chooses the lightest reliable shape; `recursive-agent-improvement` builds the Tier 3 capability.

Source repository: https://github.com/H-Ali13381/recursive-agent-improvement
