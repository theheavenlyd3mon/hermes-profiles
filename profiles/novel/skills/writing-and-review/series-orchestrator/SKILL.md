---
name: series-orchestrator
version: 1.0.0
description: >
  Saga/series-level fiction orchestration. Handles multi-book continuity planning,
  cross-volume character arc tracking, power-system escalation management, external
  skill selection for writing pipelines, and Obsidian vault integration. Covers the
  gap between single-book narrative craft and franchise-level worldbuilding.
author: book-writer
license: MIT
category: writing-and-review
tags: [fiction, series, saga, continuity, power-systems, obsidian, skills-audit]
---

# Series Orchestrator — Multi-Book Fiction Pipeline Management

Orchestrates long-form fiction across 2+ books/sagas. Bridges single-book narrative craft
with franchise-level systems: character arcs spanning volumes, power-progression tracking,
faction relationship matrices, and toolchain/skills assembly.

## When to Use

Trigger when:
- A project spans multiple books/sagas/volumes
- You need to track character/power/faction state across books
- A power-magic system has explicit escalation rules (star ratings, cultivation ranks, etc.)
- You need to select/install external skills for a writing pipeline
- An Obsidian vault is needed for story bible/references/workspace
- Book-level plot threads need foreshadowing hooks in earlier books

## Skills Audit Process

When assembling a writing pipeline, use this systematic approach:

### Step 1: Query the Live Hub

```bash
hermes skills browse                          # see available categories
hermes skills search "<multi-word query>"     # use phrases, NOT single words
hermes skills inspect "<skill name>"          # preview content before installing
```

**Pattern:** Single-word queries often return zero results. Always use multi-word queries:
- ❌ `search "writing"` → empty
- ✅ `search "creative writing"` → 12 results
- ✅ `search "obsidian"` → 25 results

### Step 2: External Verification

After finding candidates in the hub, verify via web:
- Check GitHub stars, README quality, actual content vs description
- Look for author reputation and maintenance activity
- Cross-reference with community discussions (Reddit, dev.to, LinkedIn)
- Note installation commands (usually `hermes skills install <id>` or `npx skills add <repo>`)

### Step 3: Category Mapping

Map findings to these categories:

| Category | What to Look For | Key Skills Found (Eldrath project) |
|----------|------------------|-----------------------------------|
| **Architecture & Structure** | Saga→arc→chapter→scene hierarchy, franchise bibles, continuity anchors | `writing-claw` (Narrative OS), `story-skills`, `creative-writing-skills` |
| **Humanization** | Remove AI writing patterns, voice calibration, natural prose detection | `blader/humanizer` ⭐30k★, `avoid-ai-writing` ⭐2.5k★ |
| **Emotion Evocation** | Character interiority, emotional pacing, dialogue authenticity, tension theory | `the-storytellers-workbench`, `creative-writing-skills` (Prose Quality) |
| **Consistency** | Character registry, faction tracking, canon injection, state machines | `writing-claw` (Character Registry), `story-skills` (continuity state) |
| **Methodology** | Structured process, sprint targets, revision workflows, quality gates | `book-pipeline` (existing), `creative-writing-skills` (Story Architecture) |
| **Organization** | Story universe structuring, motif/theme management, wiki-style references | `writing-claw` (file-system metaphor) |
| **Obsidian Integration** | Vault scaffolding, wikilink automation, graph views, markdown bridges | Base `obsidian` skill (build custom for novel-specific needs) |

### Step 4: Install & Evaluate

Install candidate skills, then **use them for one real task** before deciding to keep. Document which ones proved useful and which didn't.

## Priority Tiers for Writing Skills

Based on the Eldrath series audit, priority ordering:

### P1 — Critical
- **`blader/humanizer`** — Removes 33 AI writing patterns; voice calibration. Install FIRST for any publication-targeted project.
- **`writing-claw`** — Narrative OS with character registry, gap-based tension theory, series-universe hierarchy. Critical for multi-book consistency.

### P2 — High
- **`danjdewhurst/story-skills`** — Story bible format, faction matrices, artifact tracking, chapter/state progress bar. Built for sagas.
- **`haowjy/creative-writing-skills`** — Three sub-skills: Story Architecture, Prose Quality, Character Depth. Excellent line-editing guidance.
- **`the-storytellers-workbench`** — Craft-level diagnosis engine: flat scenes, voice drift, pacing, character interiority.

### P3 — Medium
- **`modoojunko/awesome-novel-skill`** — Chinese-developed, fantasy/wuxia templates. Worldbuilding module may complement our approach.
- **Base `obsidian` skill** — Foundation for vault management. Novel-specific workflow built custom.

## Custom Skill Builds (Don't Exist Yet)

For series projects, these typically need to be built custom because they combine domain knowledge:

| Skill | Purpose | Why Build vs Find |
|-------|---------|-------------------|
| **Multi-book continuity engine** | Track character arcs, power levels, faction relations, plot threads across ALL books | No existing skill handles inter-book state management |
| **Power system tracker** | Star-ratings, magic types, cultivation paths, escalation rules | Domain-specific to each project's magic system |
| **Emotional beat mapper** | Internal emotional arcs per character per book | Distinct from plot progression; needs custom emotional framework |
| **Writing methodology tracker** | Sprint metrics, revision quotas, quality-slip detection | Combines process tracking with genre-specific quality markers |

## Premise Update / Ledger Re-Sync (mid-project)

When the user drops a plot, character, or world update (from Discord, a conversation, a brainstorm, a voice memo), propagate to ALL ledger files before drafting anything new. **Order matters** — downstream files depend on upstream:

1. **Read every ledger file** — plot-ledger, character-sheet, canon, foreshadow-bank, worldbuilding, concept. Identify what changed vs. what the user said.
2. **character-sheet.md** — new/renamed characters, species, roles, combat styles. Update sliders if arc changed.
3. **canon.md** — names, places, rules, timeline. New facts go here first; never let a fact appear in a chapter before it's in canon.
4. **plot-ledger.md** — re-map beats. If a single beat now covers multiple distinct events (e.g. "three dungeons" was one row), split into separate scene-level rows with their own scene IDs. Every new event gets a beat row.
5. **foreshadow-bank.md** — re-index:
   - New beats → new plant rows (especially trust-building scenes that set up later betrayal/payoff).
   - Changed chapter assignments → fix plant/payoff chapter columns.
   - Deleted beats → remove or mark `red-herring`.
   - Verify: every payoff row has a matching plant; no plant points to a chapter that no longer exists.
6. **worldbuilding.md** — new species, factions, magic rules, societal norms.
7. **concept.md** — update logline/premise notes if the story engine changed.
8. **Diff report to user** — table of files changed + what changed. Flag any `[TBD]` fields still open.

**Pitfall:** updating one ledger file and forgetting the others. Canon says "three dungeons" but plot-ledger still says "first dungeon." Foreshadow bank points to ch05 for a rescue that now happens in ch04. Always propagate to ALL files in one pass.

## Cross-Book Continuity Checklist

Before starting Book N, verify:

- [ ] All cliffhanger hooks from Book N-1 addressed or explicitly deferred
- [ ] Protagonist's power level is consistent with where they ended Book N-1
- [ ] New characters introduced have proper backstory established
- [ ] Faction relationships evolved logically (no sudden reversals without cause)
- [ ] Recurring locations/items have consistent descriptions
- [ ] Foreshadowing from Book N-1 pays off OR is retconned with justification
- [ ] Supporting character aging/timeline remains plausible
- [ ] Power scaling hasn't inflated beyond the system's internal logic

## Power System Tracking Template

For explicit power-scaling systems (star ratings, cultivation ranks, etc.):

Maintain a `power-progression.yaml` per main character:

```yaml
character: Noctis
book_1_entry:
  rating: 0  # unknown/low
  abilities: ["basic aura sensing"]
  limitations: ["incomplete training", "fear of full power expression"]
book_1_climax:
  rating: 2
  abilities: ["aura manipulation", "elemental affinity"]
book_2_entry:
  rating: 3
  # ...
```

Update at end of each drafting pass. Never let a character jump more than 1-2 stars per book without a compelling arc.

## Obsidian Vault Pattern (Series-Scale)

The vault IS the project root — not a parallel directory. One vault hosts ALL books + shared world lore. Structure:

```
{series-name}/                         ← vault root (e.g. the-eternal-frontier/)
├── 00-HOME.md                         ← Root MOC — single entry point, wikilinks to all
├── 01-World/                          ← SHARED across all books
│   ├── worldbuilding.md               ← pillars, magic laws, societal implications
│   ├── canon.md                       ← truth ledger (names, rules, timeline)
│   ├── factions/                      ← one file per faction
│   ├── species/                       ← one file per species
│   ├── magic-system/                  ← one file per magic subsystem
│   └── locations/                     ← one file per location
├── 02-Characters/                     ← SHARED — one file per character (spans all books)
│   ├── {protagonist}.md               ← full template (character-builder skill)
│   ├── {companions}.md
│   └── {antagonists}.md
├── 03-Books/                          ← Per-book ISOLATED working files
│   ├── book1-{slug}/
│   │   ├── concept.md
│   │   ├── plot-ledger.md
│   │   ├── foreshadow-bank.md
│   │   ├── voice-profile.md
│   │   ├── manuscript.yaml
│   │   ├── chapters/
│   │   ├── outlines/
│   │   └── reviews/
│   ├── book2-{slug}/
│   └── ...
├── 04-Series/                         ← Cross-book tracking
│   ├── series-overview.md             ← N-book arc summary + cross-book threads
│   ├── power-progression.md           ← protagonist star-rating per book
│   └── thread-tracker.md              ← open/resolved threads across books
└── 05-Resources/                      ← Meta / pipeline / craft references
    └── style-guide.md                 ← voice rules, banned words, tone defaults
```

### Design principles

1. **World and Characters are SHARED** — they live outside any single book so Book 2–5 reference the same canon. Character sheets track per-book arc state inside the file.
2. **Books are ISOLATED** — each book has its own ledger, foreshadow, chapters, reviews. No cross-contamination.
3. **00-HOME.md is the MOC** — every file is reachable via wikilinks from HOME. No orphans.
4. **Wikilinks everywhere** — `[[Noctis]]`, `[[Saora]]`, `[[Star Ratings]]` connect the graph.
5. **Folder numbering** — 00-05 prefix gives sort order and signals hierarchy at a glance.
6. **Series tracking (04-)** — power progression, thread tracker, and overview live here because they span books.

### Build order for a new series vault

1. Create folder skeleton (all dirs)
2. Write 00-HOME.md with wikilinks (even to files that don't exist yet — Obsidian shows them as unresolved)
3. Move/copy existing flat files into correct positions
4. Create stubs for factions, species, locations (headers + known facts + open questions)
5. Create character files using `character-builder` skill template
6. Create series tracking files (overview, power-progression, thread-tracker)
7. Create style-guide in 05-Resources
8. Update titles/headers in moved files to reflect new series/book names
9. Delete old flat directory (with user confirmation)
10. Update memory with canonical vault path

### Consolidating duplicate trees

Projects often accumulate two manuscript trees — e.g. an early Obsidian vault with an old plot structure AND a pipeline `manuscript/{slug}/` directory with the current structure. When this happens:

1. **Identify which tree is canonical** — the one matching the user's latest premise/plot updates.
2. **Merge any unique content** from the stale tree (voice samples, reviews, outlines) into the canonical tree.
3. **Delete the stale tree** entirely. Two trees = guaranteed canon drift.
4. **Update memory** with the surviving canonical path so future sessions don't re-discover the old one.
5. **Report to user** what was kept, what was merged, what was deleted.

Never draft against a tree without confirming it's the only one.

See `references/skills-audit-guide.md` for the complete audit methodology and source URLs.
See `references/build-order-discipline.md` for the non-negotiable pre-draft sequence (characters → world → voice → draft).
See `references/character-complexity-scaling.md` for character sheet complexity tiers, working-document style rules, and the three-layer review system (doc-review / narrative-revisor / humanizer).

## Pitfalls

- **Hub search requires multi-word queries.** `hermes skills search "writing"` returns empty. Use `hermes skills search "creative writing"` or `"fiction storytelling"`.
- **Description ≠ substance.** Always `inspect` a skill and read the SKILL.md body before installing. Many descriptions are thin.
- **External GitHub repos may be unmaintained.** Check last commit date, issue open rate, and actual file count. Some popular repos have sparse codebases.
- **Chinese-language skills may have English READMEs but Chinese code/templates.** Verify language coverage matches your project language.
- **Don't over-install.** Test one skill per category. Keep only what you actually use. Bloat slows skill loading.
- **Duplicate manuscript trees.** User may have an old Obsidian vault AND a pipeline tree for the same project. Always check for multiple trees before drafting. Consolidate into ONE canonical path, delete the stale one, update memory.
- **Premise updates not propagated to all ledgers.** When the user drops new info, ALL files must re-sync in one pass (character-sheet → canon → plot-ledger → foreshadow-bank → worldbuilding → concept). Updating one file and forgetting the others creates silent canon drift.
- **Thin-draft trap (cross-ref: `narrative` skill).** When drafting chapters, hitting plot beats without hitting word count targets. Chapter outlines typically specify ~7,500 words each. If chapters land at <2,000 words, you're writing beat summaries instead of full scenes. Expand with sensory detail, dialogue, interiority, action. Run word count check before marking chapters `done`. The outline is the map, not the territory.
