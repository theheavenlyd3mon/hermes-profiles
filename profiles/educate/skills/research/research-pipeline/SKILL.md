---
name: research-pipeline
title: Multi-Agent Research Pipeline
description: "Hermes-native research pipeline: multi-phase agents, integrity gates, source verification, claim audit. Inspired by ARS architecture."
version: 1.0.0
author: Senna (Hermes)
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [research, multi-agent, pipeline, verification, academic, integrity]
    category: research
    related_skills: [arxiv, llm-wiki, open-source-research, research-paper-writing, plan, writing-plans]
---

# Research Pipeline

A multi-phase, multi-agent research pipeline for Hermes. Decomposes research into specialized phases with integrity gates between them. Inspired by ARS (Academic Research Skills) architecture — adapted for Hermes's kanban/foreman multi-agent system.

**Core principle:** Decompose research into phases. Each phase has a specialized agent. Integrity is enforced structurally between phases, not hoped for.

## When This Skill Activates

- User asks to research a topic deeply (not just a quick search)
- User wants to write a research paper, report, or literature review
- User asks to verify claims, citations, or sources
- User wants a systematic review or evidence synthesis
- User says "do research on X" and expects more than a web search

## Pipeline Modes

| Mode | When to use | Depth | Est. cost |
|------|-------------|-------|-----------|
| `quick` | Quick overview, 500-1500 words | Shallow | ~$0.50 |
| `full` | Comprehensive report, 3000-8000 words | Deep | ~$2-4 |
| `fact-check` | Verify specific claims | Targeted | ~$0.30 |
| `socratic` | No clear research question yet | Guided dialogue | ~$1-2 |
| `systematic` | PRISMA-style systematic review | Deepest | ~$4-8 |

**Default:** `full` when the user has a clear topic. `socratic` when they don't.

## Pipeline Phases

### Phase 1: SCOPING
**Agent:** Research Question Architect
**Deliverable:** Research Question Brief

1. Decompose the topic into domain, key concepts, relationships
2. Generate 3-5 candidate research questions
3. Score each using FINER framework (see below)
4. Define scope boundaries (IN/OUT/ASSUMPTIONS)
5. Decompose into 2-3 sub-questions

**Gate:** User confirms RQ brief before proceeding.

#### FINER Framework (Research Question Quality)

Score each question 1-5 on:

| Criterion | Weak (1) | Strong (5) |
|-----------|----------|------------|
| **F**easible | Cannot be answered with available methods | Clearly answerable with identified methods |
| **I**nteresting | Trivial or well-established | Addresses a genuine puzzle |
| **N**ovel | Duplicates existing work | Offers new perspective |
| **E**thical | Significant concerns | No issues; benefits outweigh risks |
| **R**elevant | No significance | Informs policy, practice, or theory |

**Minimum:** Average ≥ 3.0, no criterion below 2.

### Phase 2: RESEARCH
**Agent:** Research Team (3 subagents)
**Deliverable:** Annotated Bibliography + Synthesis Report

Three parallel subagents:
1. **Bibliography Agent** — Systematic literature search using `web_search`, `arxiv` skill, and academic APIs
2. **Source Verification Agent** — Grade every source on evidence hierarchy. Detect predatory journals.
3. **Synthesis Agent** — Integrate sources, resolve contradictions, identify gaps

**Subagent delegation pattern:**
```
delegate_task(tasks=[
  {"goal": "Find and annotate 10-15 sources on [topic]", "role": "leaf"},
  {"goal": "Verify source quality for [bibliography]", "role": "leaf"},
  {"goal": "Synthesize findings into a coherent narrative", "role": "leaf"}
])
```

**Gate:** Annotated bibliography reviewed before writing.

### Phase 3: INTEGRITY CHECK
**Purpose:** Machine-verified checkpoint between research and writing.
**Pattern:** 7-mode failure checklist.

| Mode | What it checks |
|------|----------------|
| M1 | Fabricated references (WebSearch every single one) |
| M2 | Incorrect citations (author, year, title match) |
| M3 | Misrepresented claims (source says what we claim?) |
| M4 | Missing citations (claims without sources) |
| M5 | Predatory journal sources |
| M6 | Outdated sources (superseded by newer work) |
| M7 | Logical fallacies in synthesis |

**Rule:** Every reference must be WebSearch-verified. No "difficult to verify" verdicts. VERIFIED or NOT_FOUND.

**Gate:** All 7 modes must PASS. User acknowledges before proceeding.

### Phase 4: WRITING
**Agent:** Writer Agent
**Deliverable:** Draft document

- Follow the outline approved in Phase 1
- Use only verified sources from Phase 2
- Apply IRON RULE markers for any claim without direct citation
- Include citation format (APA 7.0 default)

### Phase 5: REVIEW
**Agent:** Review Team (3 subagents)
**Deliverable:** Review Reports + Editorial Decision

Three independent reviewers working WITHOUT cross-referencing:
1. **Domain Expert** — Literature coverage, theoretical contribution
2. **Methodology Reviewer** — Research design, evidence quality, reproducibility
3. **Devil's Advocate** — Core argument challenges, logical fallacy detection, strongest counter-arguments

**Critical:** Reviewers never see each other's reports. Prevents groupthink.

An **Editorial Synthesizer** then:
- Resolves disagreements mechanically
- Produces Accept / Minor Revision / Major Revision / Reject decision
- Generates a Revision Roadmap

**Gate:** User reviews editorial decision.

### Phase 6: REVISE
**Agent:** Writer Agent (revision mode)
**Deliverable:** Revised Draft + Point-by-Point Response

- Address every item in the Revision Roadmap
- Track what changed (delta report)
- Max 2 revision rounds. Unresolved items → "Acknowledged Limitations"

### Phase 7: FINAL INTEGRITY
**Purpose:** Zero-tolerance re-verification after revision.
**Pattern:** Re-run all 7 modes from Phase 3 on the revised draft.
**Rule:** Must PASS with zero issues. No skip permitted.

### Phase 8: FINALIZE
**Deliverable:** Publication-ready output

- Format as requested (MD, DOCX, PDF via Pandoc/LaTeX)
- Include AI disclosure statement
- Include process summary

## Anti-Hallucination Protocol

### Source Verification (Mandatory for Every Reference)

```
For each reference:
  1. WebSearch: "[author] [title] [year]"
  2. Verify: title, authors, year, journal/conference, DOI
  3. Verdict: VERIFIED | NOT_FOUND | MISMATCH
  4. NOT_FOUND = suspected fabrication → remove or flag
```

**Never trust AI memory for citations.** Always verify via external search.

### Citation Hallucination Taxonomy

| Type | Freq. | Detection |
|------|-------|-----------|
| Total Fabrication | ~28% | WebSearch title + author |
| Plausible Author | ~23% | Verify author's publication list |
| Incomplete | ~19% | Flag missing DOI + volume + pages |
| Partial Mashup | ~18% | Cross-verify all metadata against ONE source |
| Subtle Distortion | ~12% | Compare each field individually |

### Claim Verification

Every factual claim in the output must:
1. Have a cited source
2. The source must be VERIFIED (Phase 3)
3. The claim must accurately represent the source

Claims without citations get IRON RULE markers: `[CLAIM WITHOUT CITATION]`

## Temporal Verification

Catch time-related errors in drafts:

1. **Future-as-past arithmetic** — Dates that couldn't have existed when claim was made
2. **Anachronistic citations** — Citing a 2026 paper for a 2020 phenomenon
3. **Deictic time-bombs** — "Currently" and "recently" that will be wrong when read later
4. **Causal inversions** — "X enabled Y" when Y preceded X

**Simple implementation:** Regex scan for deictic phrases (`currently`, `now`, `at present`, `recently`, `the latest`) and flag them for review.

## Devil's Advocate Pattern

A dedicated agent that runs at multiple phases. Its job:

1. **Challenge core arguments** — What's the strongest counter-argument?
2. **Detect logical fallacies** — Ad hominem, straw man, false dichotomy, appeal to authority
3. **Identify confirmation bias** — Are we only finding evidence that supports our thesis?
4. **Stress-test conclusions** — What would change our mind?

This is NOT optional. It's a structural requirement. Every research output goes through the Devil's Advocate.

## Session State (Material Passport Pattern)

For long research sessions that may span multiple context windows:

1. After each phase, save key artifacts to `fabric_write`:
   - Research question brief
   - Annotated bibliography
   - Integrity gate verdicts
   - Editorial decisions
   - Revision history

2. Use `mnemosyne_remember` for durable facts:
   - Research topic and scope
   - Key findings and conclusions
   - Sources verified/not verified
   - Revision decisions made

3. On session resume, `fabric_recall` + `mnemosyne_recall` to reconstruct state.

## Implementation Notes

### Cost Optimization

- Use cheaper models (MiMo, Qwen3) for research phases (broad search, synthesis)
- Use stronger models only for final review and integrity gates
- The pipeline structure itself reduces cost by preventing rework
- `quick` mode skips Phase 5 (review) entirely
- `fact-check` mode runs only Phases 2-3

### Delegation Pattern

Use `delegate_task` for parallel work within phases:
- Phase 2: 3 parallel subagents (bibliography, verification, synthesis)
- Phase 5: 3 parallel subagents (domain, methodology, devil's advocate)

Use sequential execution for phase transitions with gates between them.

### Integration with Existing Skills

- **arxiv** — For paper search in Phase 2
- **llm-wiki** — Store research findings as wiki pages
- **open-source-research** — For GitHub/code-related research
- **research-paper-writing** — For ML-specific paper writing (NeurIPS/ICML)
- **obsidian** — Store notes in Obsidian vault

## Pitfalls

- **Don't skip integrity gates** — They exist because "being careful" isn't enough. Machine verification catches what human diligence misses.
- **Don't let reviewers cross-reference** — Independent review produces better feedback than collaborative review.
- **Don't trust AI memory for citations** — Always WebSearch. Even GPT-4o has 56% citation error rate.
- **Don't use "currently" or "recently"** — These are temporal time-bombs. Use specific dates.
- **Don't exceed 2 revision rounds** — Diminishing returns. Acknowledge limitations and move on.
- **Don't run full pipeline for quick questions** — Use `quick` or `fact-check` mode. Full pipeline is for serious research.
- **Don't parallelize phase transitions** — Each phase depends on the previous phase's output. Gates must pass before proceeding.
