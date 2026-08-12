---
name: writing
description: "Use this skill for any creative writing task involving narrative, character, story structure, or franchise development. Triggers: building or tracking characters, designing plots, writing scenes or chapters, organizing a story universe, developing motifs or themes, building a series or franchise bible, tracking character arcs, resolving plot gaps, or any request to write or develop fiction at any scale — from a single moment to a multi-story cluster. This skill operates like a narrative OS: it tracks state, identifies gaps, organizes hierarchy, and generates content that is consistent with the established world."
---

# WRITING — Narrative Operating System

## Philosophy

Story is a living system, not a sequence of events. This skill treats a narrative world the way an OS treats a file system: every element has a type, a location in the hierarchy, a set of relationships, and a state. Writing tasks are operations on that system — create, read, update, resolve, link.

The atomic unit of story is not the scene. It is the **gap** — the unresolved tension between what a character needs, what they do, and what the world gives back. All structure exists to surface, hold, and eventually close gaps.

---

## Hierarchy of Narrative Units

From smallest to largest:

```
MOMENT
  └─ INTERACTION
       └─ SCENE
            └─ SEQUENCE
                 └─ CHAPTER
                      └─ STORY
                           └─ STORY CLUSTER (franchise / series / universe)
```

### Definitions

| Unit | Definition | Key Property |
|---|---|---|
| **Moment** | A single beat of perception, action, or feeling | Has a before and after state |
| **Interaction** | Two or more entities in contact; causes at least one state change | Requires at least one character |
| **Scene** | A contained unit of space, time, and purpose | Has a single dramatic question |
| **Sequence** | A chain of scenes with a shared throughline | Has rising or falling pressure |
| **Chapter** | A named, bounded section of a story | Has an opening posture and closing posture |
| **Story** | A complete arc from imbalance to resolution | Has a protagonist with a want and a wound |
| **Story Cluster** | A franchise, series, or universe of related stories | Has a governing mythology and shared entity registry |

---

## System Components

### 1. CHARACTER REGISTRY

Every character is a record with the following fields:

```
CHARACTER
  id:               [unique slug, e.g. dime, penny, asha]
  full_name:        string
  role:             protagonist | antagonist | foil | catalyst | witness | ensemble
  wound:            the unhealed thing they carry into the story
  want:             what they are consciously pursuing
  need:             what would actually heal them (may conflict with want)
  fear:             what they will avoid at cost to themselves
  voice:            one sentence describing how they speak and think

  EMOTIONAL ARC:
    opening_state:  emotional/psychological condition at story start
    pressure_points: list of moments that force change
    transformation: what shifts (may be positive, negative, or ambiguous)
    closing_state:  emotional/psychological condition at story end

  THEMATIC RESONANCE TRACK:
    primary_theme:  the theme this character embodies or challenges
    motifs:         recurring images, phrases, or behaviors tied to this character
    symbolic_object: [optional] a physical thing that carries their meaning
    arc_color:      a one-word descriptor of the emotional register (e.g. "amber", "cold", "rust")

  INTERACTION LOG:
    [list of scene IDs where this character appears, auto-populated]

  GAP FLAGS:
    [auto-detected: scenes where this character should logically appear but doesn't]
```

---

### 2. SETTING REGISTRY

```
SETTING
  id:               string slug
  name:             string
  type:             interior | exterior | liminal | symbolic
  atmosphere:       dominant sensory and emotional texture
  history:          what happened here before the story begins
  thematic_charge:  what this place means in the world's symbolic logic
  associated_characters: [list of character IDs who belong to or are changed by this place]
  scenes_set_here:  [list of scene IDs, auto-populated]
```

---

### 3. MOTIF REGISTRY

```
MOTIF
  id:               string slug
  form:             image | phrase | gesture | sound | color | number | object
  description:      what it is
  first_appearance: scene ID where it enters
  recurrences:      [list of scene IDs and how it appears each time]
  resolution:       scene ID where it closes or transforms (may be open-ended)
  thematic_link:    which theme or character arc it serves
```

---

### 4. PLOT REGISTRY

Plots are tracked at two levels: **local** (within a story) and **overarching** (across stories in a cluster).

```
PLOT
  id:               string slug
  type:             local | overarching
  logline:          one sentence: [character] wants [X] because [Y] but [obstacle]
  status:           seeded | active | climaxing | resolved | abandoned
  open_in:          story ID (or list for overarching)
  closed_in:        story ID (null if unresolved)
  threads:          [list of scene IDs that advance this plot]
  gap_check:        [scenes where this plot should surface but doesn't — flagged for review]
```

#### Overarching Plot Board

When operating at story cluster scale, maintain a board of all active overarching plots:

```
OVERARCHING PLOT BOARD
  [plot_id]  |  [logline]  |  [status]  |  [stories touched]  |  [resolution target]
```

Plots are organized by their **interaction gap density** — overarching plots with the most characters who have never shared a scene are prioritized for development, since those gaps represent the highest-yield unwritten territory.

---

### 5. THEME MAP

```
THEME
  id:               string slug
  statement:        a full sentence, not a noun (e.g. "Loyalty is indistinguishable from control")
  characters_who_embody:    [list]
  characters_who_challenge: [list]
  motifs_serving:           [list]
  scenes_where_explicit:    [list — use sparingly; theme is usually better shown]
  resolution_posture:       affirmed | complicated | subverted | left open
```

---

## Gap Analysis Engine

The most important function of this skill is **gap detection** — finding the unwritten interactions that the story needs.

### Character Interaction Matrix

When working at story or cluster scale, build a matrix of all characters and flag pairs who have never shared a scene:

```
          | CHAR_A | CHAR_B | CHAR_C | CHAR_D |
CHAR_A    |   —    |   ✓    |   ✗    |   ✓    |
CHAR_B    |   ✓    |   —    |   ✓    |   ✗    |
CHAR_C    |   ✗    |   ✓    |   —    |   ✗    |
CHAR_D    |   ✓    |   ✗    |   ✗    |   —    |
```

`✗` cells = **gap candidates**. When suggesting new scenes or chapters, prioritize pairings from the ✗ cells — especially when both characters share a thematic resonance or are on collision-course arcs.

### Plot Gap Check

For every active plot, verify:
- Has it been seeded in a scene? If not → write the seed.
- Has it been complicated? If not → find the right moment.
- Has it been resolved or consciously left open? If neither → flag.

### Emotional Arc Continuity Check

For every character, verify their emotional arc has:
- A legible opening state
- At least one scene that applies pressure
- A transformation that is *earned* (has visible cause in the scene log)
- A closing state that differs meaningfully from the opening

---

## Writing Operations

### `CREATE CHARACTER [name]`
Populate all CHARACTER fields. Generate emotional arc and thematic resonance track. Add to registry. Run gap analysis to find existing scenes where this character could or should appear.

### `WRITE SCENE [dramatic question]`
Before writing: identify which characters are present, which plot thread this advances, which motifs should appear, and what the scene's opening and closing postures are. After writing: update interaction logs, plot thread lists, and motif recurrences.

### `WRITE SEQUENCE [throughline]`
Chain scenes with a shared escalation. Label the pressure curve: where does tension peak, where does it release, and what new gap does it open?

### `WRITE CHAPTER [name]`
Define opening posture (what the reader/audience carries in) and closing posture (what they carry out). Chapters should end with a state change — not necessarily resolution, but a shift.

### `PLAN STORY [title]`
- Define protagonist want, wound, need, fear
- Map overarching plot position
- Build chapter spine (opening posture → closing posture for each)
- Run character interaction matrix
- Identify top 3 gap-priority scenes to develop first

### `EXPAND STORY CLUSTER [universe name]`
- Audit all existing stories for unresolved overarching plots
- Run full interaction matrix across all characters
- Identify which character pairings have the highest thematic charge and have never met
- Propose next story based on gap density + overarching plot advancement

---

## Narrative Consistency Rules

1. **Characters do not change without cause.** Every transformation must have a traceable scene that triggered it.
2. **Motifs earn their meaning through repetition and variation.** A motif that appears once is decoration. One that appears three times with variation is architecture.
3. **Every scene has a dramatic question.** If you cannot state it in one sentence, the scene lacks a spine.
4. **Overarching plots are not subplots.** They run beneath the local plot like groundwater — felt but rarely surfaced directly.
5. **Gap is not absence.** A character who never meets another character is an unspent charge. The story is incomplete until it discharges or consciously holds.
6. **Theme is a pressure, not a message.** The theme map describes what the story is wrestling with, not what it concludes.

---

## Output Formats

| Request | Default Output |
|---|---|
| New character | Filled CHARACTER record + emotional arc + thematic resonance track |
| New scene | Scene prose + updated interaction log entries + motif notes |
| Plot planning | Plot record + thread list + gap check |
| Gap analysis | Interaction matrix + top 5 gap-priority pairings with rationale |
| Chapter planning | Opening/closing postures + scene list + arc notes per character present |
| Story planning | Full spine with chapter postures + interaction matrix + top gap scenes |
| Cluster expansion | Overarching plot board + gap matrix + next story proposal |

---

## Example: Character Record

```
CHARACTER
  id:               dime
  full_name:        Dime
  role:             protagonist
  wound:            Was given shape before she was given a name — defined by function, not self
  want:             To be the one who decides what things are worth
  need:             To be seen without being useful
  fear:             That she only matters in relation to something larger
  voice:            Precise, economical, slightly formal — as if every word costs something

  EMOTIONAL ARC:
    opening_state:  Contained. Certain. Privately lonely.
    pressure_points:
      - First encounter with Penny (Scene: the_splitting)
      - The moment she is asked to choose without context (Scene: tbd)
      - The scene where someone values her for the wrong reason
    transformation:  Learns the difference between being known and being needed
    closing_state:  Softer. Still precise. No longer alone in the precision.

  THEMATIC RESONANCE TRACK:
    primary_theme:  Value is not the same as worth
    motifs:         Silver edges, the word "exactly", things split cleanly in two
    symbolic_object: A coin that is no longer currency
    arc_color:      silver-cold → warming

  GAP FLAGS:
    - Has not shared a scene with [supporting_character_3] — thematic charge: high
```

---

## Notes

- This skill does not overwrite authorial voice. It surfaces structure so the author can make informed choices.
- When in doubt, **surface the gap** rather than fill it. The author decides when a gap becomes a scene.
- Character records should be treated as living documents — updated after every scene is written.
- Overarching plots should be reviewed at the start of every new story in the cluster.
