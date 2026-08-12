# Manuscript scaffold — copy per project

Prefer: `python scripts/init_manuscript.py <slug> --root manuscript --title "…"`.

```
manuscript/{project}/
  manuscript.yaml
  concept.md
  canon.md
  character-sheet.md
  plot-ledger.md
  foreshadow-bank.md
  worldbuilding.md
  voice-profile.md
  chapters/ch01.md …
  outlines/synopsis.md
  reviews/
  exports/
```

## concept.md
- Logline (1 sentence: who, wants, because, but)
- Tone anchor (dread / restraint / melancholy / bright action)
- MICE mix + thread close order
- Target length (short novel = 40–50k default; novella = 20–40k)

## character-sheet.md
- Name / role
- Three Sliders: proactivity / likability / competence (0–10)
- Ghost → Wound → Lie → Want → Need (Want vs Need in tension)
- Dialogue signature: vocabulary, length, tics, metaphor domain
- Arc type: positive / flat / negative

## plot-ledger.md
| Beat | % Mark | Status | Chapter | Scenes | Notes |
|------|--------|--------|---------|--------|-------|
| Opening Image | 0–1% | planned | | | |
| Catalyst | ~11% | planned | | | EXTERNAL |
| Break Into Two | ~23% | planned | | | CHOICE |
| Midpoint | ~50% | planned | | | reverse |
| All Is Lost | ~68% | planned | | | death-whiff |
| Final Image | ~99% | planned | | | mirror |

Status: `planned` | `drafted` | `reviewed` | `done`

## foreshadow-bank.md
| ID | Plant (ch) | Element | Type | Payoff (ch) | Status |
|----|------------|---------|------|-------------|--------|

## worldbuilding.md
- Pillars (physical / cultural / magical) — pick 1–2
- Magic: Three Laws + costs that drive plot
- 2–3 societal implications per speculative element
- Iceberg hints

## voice-profile.md
- See style-revision-playbook §1 YAML template
- Calibrate from 500-word sample before drafting chapter 1 for real

## chapters/*.md frontmatter
```yaml
---
scene_id: ch01-sc01
beat: catalyst
try_fail: no-and
pov: Jin
status: planned   # planned | drafted | reviewed | done
---
```

## reviews/
JSON from `narrative-revisor` — one file per scene pass.
