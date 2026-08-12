---
name: narrative-revisor
description: Separate reviewer stage for fiction — runs 3-pass craft/anti-slop/stability-trap critique on scenes without generating net-new plot. Emits JSON handoff for the drafting agent. Use after a scene is drafted in the book-writer pipeline; never self-review the draft you just wrote.
version: 1.0.0
---

# Narrative Revisor — Stage 2/3 of the book loop

**You critique. You do not invent plot.** Fresh context only: ledger + canon + voice + the single scene under review. Never the generator's chain-of-thought.

Rule sources (load via parent `narrative` skill if needed):
- CRAFT: `narrative/references/autonovel-craft.md`
- ANTI-SLOP: `narrative/references/autonovel-anti-slop.md`
- Playbook: `book-pipeline/references/style-revision-playbook.md`
- Project schemas: `narrative/references/project-mode.md`

## When to use
- After `status: drafted` on a scene/chapter in `manuscript/{project}/chapters/`
- Book-end stability pass across the whole arc
- Voice drift check against `voice-profile.md`

## Procedure

1. **Load state (only):**
   - target scene file
   - `plot-ledger.md`, `foreshadow-bank.md`, relevant character blocks
   - `voice-profile.md`, `canon.md` (skim)
   - Do NOT load other full chapters unless checking continuity on a specific claim

2. **Pass 1 — Craft / structure** (playbook §2 Pass 1)
   - Beat fit, try-fail tag, character sliders, Want/Need tension, show-don't-tell at peaks, foreshadow linkage
   - Emit issues with `severity: blocker|major|minor` and `rule_ref`

3. **Pass 2 — Anti-slop mechanical**
   - Tier-1 zero; Tier-2 clusters; Tier-3 filler; em-dash cap; "not just X but Y"; fiction AI tells
   - Prefer running `narrative/scripts/check_manuscript.py` for mechanical counts when whole book available

4. **Pass 3 — Stability trap (mandatory, all 7)**
   - Real change, bad stays bad, irreversible loss, withheld info, moral ambiguity, emotional range, real cost
   - Any rounded edge → blocker

5. **Write handoff JSON** to `manuscript/{project}/reviews/{scene_id}.pass{N}.json`

```json
{
  "scene_id": "ch01-sc02",
  "pass": 3,
  "status": "fail",
  "metrics": {
    "tier1_banned": 0,
    "em_dash_per_page": 1.2,
    "not_just_x_but_y": 0,
    "sentence_len_cv": 0.4
  },
  "issues": [
    {
      "id": "p3-001",
      "category": "stability",
      "rule_ref": "CRAFT §7 real cost",
      "severity": "blocker",
      "quote": "…",
      "suggestion": "…"
    }
  ]
}
```

6. **Loop control**
   - `blocker` / `major` → reviser must fix; re-run failed passes
   - All three passes `status: pass` → set scene frontmatter `status: reviewed`
   - Update `plot-ledger.md` beat row when the scene completes its assigned beat

## Revise role (same agent or drafting agent)
Apply only listed issues. No new subplots. Re-emit scene; re-request review.

## Gates
- [ ] Handoff JSON written under `reviews/`
- [ ] No net-new plot invented in review comments (suggestions only)
- [ ] Stability 7 checked explicitly in Pass 3 output
- [ ] Scene status advanced only on full pass

## Pitfalls
- Softening the draft further ("make nicer") — that *is* the stability trap
- Reviewing without ledger (misses foreshadow / beat skips)
- Merging draft + review in one generation call
