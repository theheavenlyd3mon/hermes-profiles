---
name: skills-audit
description: >
  Systematic methodology for auditing the Hermes Skills Hub (and external sources) 
  to identify gaps, overlaps, redundancies, and conflicts when building a skill library 
  for any project. Covers browsing, targeted searching, cross-referencing with web/GitHub, 
  comparing candidates against existing inventory, verifying install safety, and planning 
  installation order. Use when starting a new project and assembling tools, or when 
  evaluating whether to add external skills beyond what's currently installed.
version: 1.0.0
metadata:
  hermes:
    tags: [skills, audit, methodology, evaluation, hub, inventory]
    category: meta
---

# Skills Audit — systematic hub evaluation methodology

When starting a new project or expanding an existing one, use this method to 
assess the Hermes Skills Hub and external repositories, compare against current 
inventory, and plan installations without creating redundant or conflicting skills.

## Phase 1: Inventory current skills

Run `hermes skills list` to see all locally installed skills. Note:
- Which belong to class-level umbrellas (e.g., `writing-and-review/`)
- Which are standalone
- Which were hub-installed (`created_by: None` — these CANNOT be edited 
  via `skill_manage`; only agent-created skills are editable)
- Which are pinned (can be patched but not deleted by curator)

## Phase 2: Browse the hub

Run `hermes skills browse` to see the catalog size and page through topics 
relevant to your project domain. Note the total loaded count (79k+ as of 2026).

## Phase 3: Targeted CLI searches

Search the hub with multi-word queries matching each capability gap you've 
identified. Examples:
```bash
hermes skills search "fiction story craft"
hermes skills search "obsidian vault notes knowledge"
hermes skills search "humanize AI prose natural voice tone"
hermes skills search "emotion storytelling character depth feelings evoking"
hermes skills search "architecture plot structure worldbuilding consistency methodology prose"
hermes skills search "writing organization long-form"
```

Common failure: single-word searches return empty. Use phrases and compound terms.

## Phase 4: Cross-reference with web/GitHub

CLI searches alone miss repos not indexed in the hub. Search GitHub and 
community sites for relevant skills:
```bash
web_search("blader/humanizer github remove AI writing patterns")
web_search("danjdewhurst/story-skills github novel planning factions")
web_search("haowjy/creative-writing-skills github \"story architecture\"")
```

Verify repos exist, check star counts, review README content before recommending 
installation.

## Phase 5: Inspect top candidates

Use `hermes skills inspect "<candidate name>"` to preview SKILL.md content. 
Read the full preview (use `| tail -N` or pagination) to understand scope.

## Phase 6: Compare against existing inventory

Build an overlap matrix. Key questions:
- Does candidate cover territory already covered by another installed skill?
- Is it truly complementary (different approach, different phase in workflow), 
  or genuinely redundant?
- Can both coexist in the same pipeline without conflict?

Example finding: `humanizer` and `avoid-ai-writing` both remove AI patterns but 
have fundamentally different approaches:
- humanizer = pattern-by-pattern forensic analysis with soul/personality guidance
- avoid-ai-writing = tiered vocabulary triage with severity/priority system
→ They are COMPLEMENTARY, not redundant. Best combined workflow: detect mode 
  from avoid-ai-writing → prioritize P0/P1 hits → humanizer for deep rewrite.

## Phase 7: Verify scan safety

Before installing, note that every hub-installed skill runs through `skills-guard-v1` 
quarantine scanner. Check the verdict: SAFE → ALLOWED means proceed. Any non-SAFE 
verdict requires manual review.

## Phase 8: Plan installation order

Priority mapping:
1. P1 — Critical gaps (anti-AI pair, saga architecture)
2. P2 — High-value additions (craft diagnosis, prose quality)
3. P3 — Nice-to-have or custom-build candidates (Obsidian novel-specific skill)

Install incrementally: P1 batch first, evaluate, then P2.

## What DOESN'T exist in the hub (yet)

Frequently missing categories for novel/series work:
- Multi-book continuity management (tracking arcs/factions/power across volumes)
- Power system consistency engine (star ratings, magic types, progression tracking)
- Emotional beat mapper (internal emotional arcs separate from plot progression)
- Obsidian novel-specific templates (story bible wikilinks, faction graphs, timelines)
- Writing methodology tracker (sprint targets, revision quotas, process metrics)

These require either custom-built skills OR extending existing umbrella skills.

## Common pitfalls during audit

- **Single-word searches return nothing.** Always use phrases: "creative writing", 
  not just "writing"
- **Assuming no match in hub = doesn't exist externally.** Cross-reference with 
  GitHub/web searches — many community repos aren't fully indexed
- **Treating partial overlap as reason to skip install.** Different approaches to 
  the same problem (humanizer vs avoid-ai-writing) often complement rather than 
  compete
- **Installing everything at once.** Evaluate P1 first; some skills may never get 
  used in practice. Install iteratively
- **Not checking editability.** Hub-instilled skills (created_by=None) cannot be 
  modified via `skill_manage`. Only patch/edit agent-created skills. If a hub 
  skill needs fixing, file a PR upstream or build a custom wrapper skill instead

## Support files

- See session transcripts for specific skill discovery sessions and candidate 
  comparisons under references/audit-sessions/