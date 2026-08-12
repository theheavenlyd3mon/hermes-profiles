# Skills-Audit Reference — 2026-07-20 (Eldrath Pipeline)

## Context
User wanted to build a skills library for a 5-book progression-fantasy series. We needed tools covering: architecture/structure, organizational writing, humanization of AI writing, consistency, writing methodologies, emotion evocation, and Obsidian integration.

## Hub Browse Results
Total loaded in hub: **79,876 skills** across community sources (clawhub, skills.sh, lobehub, etc.)

## Candidates Inspected + Decision Log

| Skill | Verdict | Reason |
|-------|---------|--------|
| `ai-agent-creative-writing-workshop` | SKIP | Web-server-based workshop tool; not relevant to manuscript pipeline |
| `pordl-creative-writer` | SKIP | API-key routing skill; we're using local/Darwin model |
| `the-storytellers-workbench` | ✅ INSTALLED | Craft-level literary fiction diagnosis — tension engine, voice contracts, pacing |
| `writing-claw` | ✅ INSTALLED | Narrative OS with saga→chapter→scene hierarchy, character registry, state tracking |
| `novel-writers` | SKIP | Urban fantasy specific; too narrow genre scope |
| `creative-writing-craft` | ✅ INSTALLED | Story architecture templates, scene structure, revision checklists by genre |
| `obsidian` (clawhub) | ✅ ALREADY INSTALLED | Generic vault file operations |
| `blader/humanizer` | ✅ ALREADY INSTALLED | Anti-AI pattern stripping with soul/personality guidance |
| `conorbronsdon/avoid-ai-writing` | ✅ ALREADY INSTALLED | Tiered vocabulary triage with detect/rewrite modes |
| `haowjy/creative-writing-skills` | NOT INDEXED | Three sub-skills (Story Architecture, Prose Quality, Character Depth) found on GitHub but not in hub index — may need manual install later |
| `danjdewhurst/story-skills` | NOT INDEXED | Saga-format story bible, character files, faction artifacts. GitHub only. May be useful for Book 1→5 planning. |

## Key Learnings Recorded

1. **humanizer + avoid-ai-writing are complementary, not redundant.** See SKILL.md body.
2. **Pipeline sequence matters:** de-AI pass runs AFTER narrative-revisor revises pass, never before.
3. **Hub editability:** Hub-installed skills have `created_by=None` → cannot be edited via `skill_manage`. Only agent-created skills are editable.
4. **Multi-word CLI searches required:** single-word queries return empty results consistently.

## What Still Needs Building (Custom Skills)

These gaps were identified during audit and exist outside the hub:

| Gap | Status | Notes |
|-----|--------|-------|
| Multi-book continuity engine | PLANNED | Track Noctis power progression, faction relations, plot threads across 5 books |
| Power system tracker | PLANNED | Star-rating magic system (1-10), magic types/pathways, escalation logic |
| Emotional beat mapper | PLANNED | Internal emotional arcs separate from plot progression per character/book |
| Writing methodology tracker | PLANNED | Sprint targets, revision quotas, process metrics |
| Obsidian novel-specific templates | PLANNED | Story bible wikilinks, faction graphs, timeline views — beyond generic obsidian skill |