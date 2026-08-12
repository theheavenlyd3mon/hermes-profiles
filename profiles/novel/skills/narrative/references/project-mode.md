# Narrative project mode — schemas & gates

Companion to `narrative` SKILL.md v2. Concrete file shapes the generator and reviewer must honor.

## Directory tree

```
manuscript/{project}/
  manuscript.yaml         # optional bind
  concept.md
  canon.md                # truth ledger
  plot-ledger.md
  foreshadow-bank.md
  character-sheet.md      # or characters/<name>.md
  worldbuilding.md
  voice-profile.md
  chapters/
    ch01.md               # or ch01/scene01.md …
  outlines/
    synopsis.md
  reviews/                # JSON handoffs per scene
    ch01-sc01.pass1.json
  exports/                # CLI-only write target
```

## manuscript.yaml (optional)

```yaml
title: "The Glass Concord"
author: "A. Writer"
framework: StC          # StC | Harmon | PPP
target_words: 45000
voice_profile: voice-profile.md
genre: dark-fantasy-murim
status: drafting        # planning | drafting | revising | done
```

## Character block (YAML frontmatter or fenced yaml)

```yaml
name: Jin
sliders: { proactivity: 3, likability: 8, competence: 4 }
arc_type: positive
ghost: "quit handwriting class; nothing he starts finishes"
wound: "chronic irrelevance"
lie: "I only matter if I'm useful to someone stronger"
want: "survive the war / be a useful weapon"
need: "choose something that is his, not the King's"
dialogue_profile:
  vocabulary: terse
  formality: contracted
  tics: ["I was at work.", "What's the plan?"]
  metaphor_domain: warehouse / industrial
  directness: high
  interrupt: submissive
  q_ratio: 0.4
```

## plot-ledger.md shape

| Beat | % Mark | Status | Chapter | Scenes | Notes |
|------|--------|--------|---------|--------|-------|
| Opening Image | 0-1% | done | ch01 | ch01-sc01 | warehouse quiet |
| Catalyst | ~11% | drafted | ch01 | ch01-sc02 | summon |
| Break Into Two | ~23% | planned | | | must be CHOICE |
| Midpoint | ~50% | planned | | | reverse trajectory |
| All Is Lost | ~68% | planned | | | whiff of death |
| Final Image | ~99% | planned | | | mirror opening |

Status enum: `planned` | `drafted` | `reviewed` | `done`

## foreshadow-bank.md shape

| ID | Plant (ch) | Element | Type | Payoff (ch) | Status |
|----|------------|---------|------|-------------|--------|
| f-001 | ch01 | memory-eating sword | action | ch18 | planted |
| f-002 | ch01 | closed-eye banner | symbolic | ch12 | open |

Status: `open` | `planted` | `payoff` | `dangling` | `red-herring`

Hard fails at export:
- any `dangling`
- any payoff with no plant (deus ex)
- red-herring without explanation

## Chapter gate checklist

Before `status: done` on a chapter:

- [ ] All scenes in chapter have reviewer pass (zero blocker/major)
- [ ] New facts written into `canon.md`
- [ ] Ledger beat rows updated
- [ ] Foreshadow bank updated for plants/payoffs this chapter
- [ ] Try-fail tags present; middle chapters aim ≥60% yes-but / no-and
- [ ] Stability-trap 7/7 at chapter grain
- [ ] Tier-1 banned words = 0 in assembled text

## Export gate

Export CLI may run only if every chapter is `done` and foreshadow has zero `dangling`.
