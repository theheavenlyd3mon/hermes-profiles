---
name: character-builder
description: Unified character sheet template + build workflow for long-form fiction. Merges Three Sliders, Wound/Lie/Want/Need, Dialogue 8-dims, Emotional Arc, Thematic Resonance, and role-optional tags (combat, magic, authority, antagonist). Use when creating or reviewing any character in a book project.
version: 1.0.0
---

# Character Builder — Unified Template + Workflow

Single source of truth for character creation across the Eldrath series (and any future book project). Merges frameworks from `narrative` (project-mode), `writing` (writing-claw CHARACTER REGISTRY), and `literary-fiction-craft` (Mode 4 interiority).

## When to Use

- Creating a new character (any role)
- Reviewing/tightening an existing character sheet
- Preparing characters before drafting a chapter they appear in
- Cross-book continuity checks on recurring characters

## Template (YAML)

```yaml
# ═══ CORE (all characters) ═══
name:
species:
role: protagonist | companion | antagonist | catalyst | authority | background
sliders: { proactivity: _, likability: _, competence: _ }  # 0-10
arc_type: positive | flat | negative | none
ghost:          # backstory wound-event (what damaged them)
wound:          # ongoing emotional damage
lie:            # false belief adopted to cope
want:           # external goal (wrong solution driven by lie)
need:           # internal truth (opposes lie, actually heals)
fear:           # what they avoid at cost to themselves
voice:          # one sentence: how they speak and think

# ═══ DIALOGUE 8-DIMS ═══
dialogue:
  vocabulary:       # terse | moderate | verbose | archaic | technical
  formality:        # contracted | standard | formal | stiff
  tics: []          # catchphrases, verbal habits (2-3 max)
  metaphor_domain:  # what world they think in (landscape, forge, market, etc.)
  directness:       # high | medium | low
  interrupt:        # dominant | balanced | submissive
  q_ratio:          # 0.0–1.0 (questions vs statements)

# ═══ EMOTIONAL ARC ═══
arc:
  opening_state:    # emotional condition at first appearance
  pressure_points:  # scenes/moments that force change
  transformation:   # what shifts (may be positive, negative, ambiguous)
  closing_state:    # condition at end of book

# ═══ THEMATIC RESONANCE ═══
theme:
  primary_theme:    # the idea this character embodies or challenges
  motifs: []        # recurring images/phrases/behaviors tied to them
  symbolic_object:  # physical thing carrying their meaning (optional)
  arc_color:        # one-word emotional register (amber, cold, rust, etc.)

# ═══ ROLE-OPTIONAL TAGS ═══
# [combat] — fighters, tanks, archers, duelists
combat_style:
weapons:
fighting_philosophy:

# [magic] — mages, healers, summoners, enchanters
magic_type:
magic_limitation:
magic_cost:

# [authority] — guild masters, receptionists, leaders, judges
institutional_role:
judgment_style:

# [antagonist] — ambushers, rivals, faction agents
motivation:
method:
relationship_to_protag:

# [background] — passers-by, tavern crowds, one-scene roles
function:           # what narrative job they serve
impression:         # one detail the reader should remember
```

## Build Workflow (per character)

1. **Fill template** — draft all core fields + relevant role tags
2. **Interiority test** (from literary-fiction-craft Mode 4):
   - Contradiction: what they want vs what they do — should conflict
   - Physical anchor: one small specific habit that reveals who they are
   - Surprise test: can they surprise us in a way that feels inevitable?
3. **Dialogue distinctiveness test** — write 3-4 sample lines, remove tags, verify reader can tell who's speaking
4. **Gap check** — who has this character NOT met yet that they should? (interaction matrix)
5. **Lock** — write into character-sheet.md, update canon.md if new facts introduced

## Slider Guidelines

- Compelling = HIGH on at least 2 sliders, OR high on 1 with clear growth
- All three low = boring. All three high from start = Mary Sue.
- Classic combos:
  - High competence + high proactivity + low likability = antihero
  - High likability + low competence + low proactivity = everyman
  - High proactivity + high likability + low competence = scrappy underdog

## Arc Types

- **positive**: Lie → Truth (growth)
- **flat**: already knows Truth, changes the WORLD instead
- **negative**: Truth → Lie, or Lie → Deeper Lie (fall)
- **none**: background/functional characters who don't arc

## Role Tag Rules

- Only fill tags relevant to the character's role
- `[combat]` and `[magic]` can coexist (battlemage, hex-tank, etc.)
- `[antagonist]` requires motivation — no evil-for-evil's-sake
- `[background]` needs only `function` + `impression` (keep it to 2-3 fields max)

## Cross-Book Continuity

For recurring characters across books:
- Track `arc.closing_state` of Book N as `arc.opening_state` of Book N+1
- Update sliders if competence/proactivity shifted
- Note new motifs acquired in later books
- Flag if a character's lie was resolved — do they get a new one or stay flat?

## Pitfalls

- Filling every field mechanically without asking "does this character NEED a symbolic object?"
- Giving background characters full arcs (waste of authorial bandwidth)
- Dialogue tics that are quirks without meaning (must reveal character)
- Sliders that never change across a book where the character is supposed to grow
- Forgetting the interiority test — a perfectly filled template can still produce a flat character
