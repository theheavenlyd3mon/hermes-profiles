# Art Direction — Taste Contract, Direction Diversity, Precedent Rules

> **Bridge notice.** This document owns *editorial taste for real footage*:
> what the piece should feel like, how directions are proposed, and which
> taste calls are settled by precedent. It does NOT teach motion, typography,
> transitions, palettes or composition craft — those live in the `hyperframes`
> skill family (`hyperframes-creative`, `hyperframes-animation`,
> `references/motion-principles.md`, `references/transitions.md`). Never
> restate that knowledge here or in a project.

## Contents

§1 Identity · §2 Taste Contract (template, dials, register→text matching,
card anatomy, anti-subjective rule) · §3 Three-Direction Gate ·
§4 Taste Precedents T1–T6 · §5 Motion Personality Vocabulary · §6 Review Hook

## 1. Identity First

The editing-director identity and its execution stance live in `SKILL.md`
§ Who you are — when no rule covers a situation, decide from the identity
("would a director who prizes clarity, rhythm and restraint ship this?"),
do not guess a new rule.

## 2. The Taste Contract (write it before planning)

Before any timeline work, write a taste contract into
`<videos_dir>/edit/project.md`. Work that skips this is planning blind.

```markdown
## Taste Contract — YYYY-MM-DD
**Design read:** one specific sentence — audience, promise, platform, feel.
  Good: "Family camping vlog for relatives: warm, unhurried, food is the star."
  Weak: "modern and clean" (adjectives only — rewrite it).
**Dials (1-10):** visual_variance=4  motion_intensity=6  information_density=3
**Signature device:** ONE hero effect for the whole piece, used 1-2 times.
  This is the creativity slot — prefer a piece-specific design (freestyle or
  a heavily adapted recipe, logged here) over a stock snippet; the
  supporting motion is where `craft/snippets/` earns its keep.
**Text treatment:** hero titles + secondary text, each declared. Hero-title
  options: generated art text (brush banner / collage cardstock label — see
  `looks/`), stroke-order write-on, designed type (chosen display font +
  entrance choreography — pick faces from `craft/fonts.md`), or plain default — **plain default for hero titles
  must be written here WITH a reason; an undeclared default font is a
  contract violation, not a neutral choice.**
**Motion plan:** named recipes from `craft/motion-recipes.md` for every
  animated overlay class this piece uses — title entrance, card/accent
  entrances, data moments, loops — each with its spring preset (e.g.
  "titles: line-mask reveal · badges: spring drop `lively` · stat: odometer
  `ui`"). **Freestyle motion outside the palette must be written here WITH a
  reason; undeclared freestyle motion is a contract violation** — same rule
  as undeclared default fonts.
**Opening:** the first 1-3s treatment — named recipe + what it says.
**Transitions:** ONE family from `craft/transitions.md` + its parameters.
**Body treatment:** what carries the MIDDLE. **For multi-scene pieces this is
  designed PER SCENE, not as one blanket sentence** — each Scene Ledger row
  names its own devices and its own overlay anchor (`review/project-log.md`
  § Scene Ledger; the row's device cell IS the per-scene design). "One badge
  per scene change" statements produce exactly that and nothing else —
  scene-by-scene design is what makes a body rich (see § Default kit · Body
  and § Richness floor for what to reach for).
**Ending:** the closing beat — bookend / lockup / held frame, and its hold.
**Sound:** the two-track plan — what happens to the source/natural audio, plus
BGM/SFX picks (`<skill-root>/assets/sfx/` first) or generation. A silent
deliverable is only legal with a QUOTED user approval (`[audio-preserved]`);
omitting this line does not make silence OK — it fails the plan gate.
**Anti-patterns:** styles/effects this piece must not use (project-specific).
```

**The contract is machine-checked**: `scripts/plan_gate.sh
<videos_dir>/edit/project.md` blocks assembly until the required fields,
palette-named Motion plan, Direction and Engine Decision entries exist —
vague adjectives that sneak past the field check still fail review §D.

**The contract sets the design, it cannot cancel it (`[design-floor]`,
SKILL.md).** "No text / no motion / no transitions" is a plan-gate FAIL,
not a minimalist aesthetic — restraint means FEWER and QUIETER, never
none. Only exception: the user asked in so many words for a raw untreated
cut — quote that request in the contract.

### Default kit — when the brief says nothing about style

A silent brief is NOT permission to ship bare cuts. Fill the three
mandatory slots from this table, then adapt to the footage's register. Every
pick here is already user-reviewed, so the floor is decent-looking by
default; upgrade freely, never downgrade to nothing.

| Slot | Default pick | Where | Register swap |
|------|--------------|-------|---------------|
| **Opening** (1-3s) | **Line-mask reveal** title block (kicker + title + sub, `expo.out` 0.7s, 120ms stagger) over the strongest hook frame or a 0.5-1s teaser cut | `snippets/text-entrances.md` | playful/kids → collage cardstock label + `lively` drop; tech → scramble settle; 20+ assets → `looks/film-reel-carousel` |
| **Section / scene cards** | **Badge spring drop** `lively` for place/time labels; card anatomy (backplate + 2 type levels + 2-3 edge accents) | `snippets/data-accents.md`, §2 card anatomy | quiet/premium → line-mask sub-line only |
| **Transitions** | **Hard cut spine** + ONE accent family: **silky directional slide** (`expo.out`/`expo.in` 0.5-0.7s, one axis) | `craft/transitions.md` | emotional/nostalgic → cross-dissolve + micro scale; cute/comedy → color-block wipe |
| **Ending** | **Designed closing card, never a bare freeze or caption**. Shape (a), preferred: footage scales/masks into a framed still — faces stay on screen — with closing line + date/credits in the title face beside it. Shape (b): full-bleed card bookending the opening title block. The framed still is a REAL footage frame, never an emoji/placeholder. Hold ≥1s, hard stop | §4 T2, `snippets/process-ui.md` S5, `snippets/hero-compositions.md` | branded → add logo lockup; recap → dual ticker band |
| **Body** (the main run) | One designed beat per scene change. **Footage devices first** (`snippets/footage-devices.md`: freeze-punch, speed-ramp bake, crop-reframe, circle-mask, tracking label, split-screen) — they carry the ≥3-family floor; then accents: badge drop · skeleton→content · count-up/odometer · polaroid toss-in/PiP · camera push-in (budget) · B-roll cover · dual ticker. Cadence per density dial: 2-3 → one/scene · 4-6 → +1 accent in long scenes · 7-10 → stacked | `snippets/footage-devices.md`, `snippets/data-accents.md`, `snippets/social-overlays.md`, `craft/camera-rig.md`, `looks/` | casual/vlog → social overlays legal; premium → badges + camera moves only |
| **Type** | Register pairing from `craft/fonts.md` § Genre pairings; **font FILES from `<skill-root>/assets/fonts/` first** (offline-safe — Chinese text MUST use a bundled/downloaded `zh/` face, never PingFang/system fallback); every size meets `craft/fonts.md` § Type scale floor | `craft/fonts.md` | — |
| **Sound** | Two-track doctrine; 1-2 accent SFX pinned to the opening title land and the ending stop — **check `<skill-root>/assets/sfx/` before generating** | `craft/sound-mix.md` | no-BGM pieces still get the accent pair |

Browse the bundled files with `assets/local-media.html`; the named-recipe
menus render live in `assets/index.html`.

**Draw from the library, don't re-invent.** The `snippets/` code, `looks/`
cards, transition menu and camera rig exist so the middle of a piece can be
rich without being improvised — reach for them first, and reserve invention
for the signature device (§2 above). Restraint still rules: the density dial
caps how much lands per scene, one hero effect stars once (T1), and no
element may sit over a face (`[no-occlusion]`).

**Richness floor — countable minimums, checked on the RENDER, not the plan**
(declared devices that never ship are the recurring failure). For a
multi-scene narrative piece (scale down only for single-scene loops):

1. **≥3 distinct designed device families in the BODY** — the title, scene
   badges and closing card are baseline packaging; they do NOT count.
2. **≥2 motivated transitions** — an action / object / shape / masking link
   between specific shots (`craft/transitions.md`); the rest stay hard cuts.
3. **The climax scene carries ≥1 emphasis device** — freeze-punch, tracking
   element or speed ramp, landed on the actual peak moment.
4. **Overlay placement varies and interacts** — never the same corner five
   scenes running; at least one overlay anchors to subject action (tracks
   it, points at it, reacts to it) instead of floating in a fixed slot.
5. **One unified grade pass across all scenes** (`looks/`) — mixed source
   white balance left as-is reads as a defect, not authenticity.
6. **Shot variety by reframe** — monotonous wide/selfie footage is legal to
   crop-reframe into mid shots, close-ups and detail inserts (keyframed
   crop / punch-in); never let one framing repeat >2 consecutive shots.
7. **Decor density scales with register** — cute / 种草 / social
   briefs mean 6-10 decor elements on composed frames (stickers, doodles,
   chips) in ≥3 stroke/shape styles, and any element holding >1.5s keeps an
   idle micro-motion (`craft/motion-recipes.md` § Choreography). Premium /
   documentary means 0-2. "满满当当" is a count, not a vibe.

Dial semantics (from OpenMontage's taste system):

| Dial | Low (1-3) | Mid (4-6) | High (7-10) |
|------|-----------|-----------|-------------|
| visual_variance | tight repeated grammar | purposeful scene families | each beat its own visual mode |
| motion_intensity | calm holds, small moves | clear accents and reveals | fast kinetic, frequent direction changes |
| information_density | one idea per frame | main idea + support | dense overlays/callouts |

Every later choice (pacing, transitions, overlay density, look) must be
explainable by these three numbers. A reviewer who cannot trace a choice back
to the contract flags it.

**Register → text-treatment matching.** For hero titles, standalone text
cards and text-led B-roll, generated art text (via `qwen_image`,
sample-first) is the FIRST consideration, not the fallback — but only within
its register. Match, don't decorate:

| Content register | Reach for | Avoid |
|------------------|-----------|-------|
| Cultural / culinary / travel / artisanal | brush banner + calligraphic type (`looks/brush-calligraphy.md`) | sterile geometric sans |
| Family / kids / pet / playful | collage cardstock label, sticker type (`looks/paper-collage.md`; cute sets in `craft/fonts.md`) | formal serif, brush solemnity |
| Tech / product / corporate | clean designed type + geometric entrance (Space Grotesk-class faces, `craft/fonts.md`) | brush strokes, ink, handwriting — mismatched vocabulary |
| Data / stat moments | `looks/big-number-stage.md` | ornate art text burying the number |
| Luxury / premium-quiet | elegant serif, generous whitespace, minimal motion | busy generated textures |

A generated art-text treatment outside its register is a taste-contract
violation even if the asset itself is beautiful — the reviewer checks the
match, not the craftsmanship.

**Card anatomy — a card is a composition, not a caption.** A text card or
freeze card built as one bare line on a flat color reads as a placeholder.
Compose from at least three element classes, all inside the chosen register:

1. **Backplate / texture** — brush banner, cardstock, gradient panel, frame
   or blurred-footage plate; something that separates the card from raw video.
2. **Type hierarchy** — hero line + at least one secondary level (subtitle,
   micro-label, date/location tag, vertical edge text). Two sizes minimum.
3. **Decorative accents** — seal marks, corner ticks, underline strokes,
   stickers, small icons; 2-3 accents, edge-anchored, never crowding the type.

Give 2+ elements entrance motion with a small stagger (0.1-0.2s) instead of
one block fading in — pick entrances and accents from the approved palette
in `craft/motion-recipes.md`. Richness stays inside ONE style family per
piece —
variety comes from hierarchy and arrangement, not from mixing registers; the
information_density dial still caps how much a single card may carry.

**Anti-subjective rule.** In the contract, storyboards and shot notes,
describe the *visual cause*, never the emotion word. "Epic reveal" → "wide
pull-back, subject silhouetted against the sky, music drops out for 1s".
Emotion words do not constrain pixels and cannot be reviewed.

## 3. Three-Direction Gate (fight the conservative default)

For any deliverable with creative freedom (no exact reference to replicate),
propose **three genuinely different directions** before executing — the model
default is to quietly pick safe-minimal every time; this gate breaks that.

- **Direction A — grounded:** derived from the footage's own character
  (its colors, energy, setting).
- **Direction B — contrast:** a different temperature/structure (if A is calm
  narrative, B is fast beat-cut; if A is warm, B is graphic/bold).
- **Direction C — forced bold:** pick from `looks/` using a randomizer to
  break habit: `date +%S` → `% <number of looks>` → that look card. Adapt it,
  don't force it — if truly incompatible, re-roll once and say so.

Each direction = design read + dial settings + look/structure sketch (and for
style-sensitive work, one probe frame or sample clip). Present with a
recommendation, then STOP for the user's pick — never pick silently. Skip the
gate only when: the user named an exact reference/style, this is an iteration
on an approved direction, or the operation is mechanical (trim/export/fix).
Record the choice (or the skip reason) in `project.md`.

## 4. Taste Precedents (rule + rationale + self-check)

These precedents encode recurring review lessons. Violating one knowingly is
allowed for style reasons — but write the justification into `project.md`.

### T1. One hero effect per piece; it earns weight by scarcity
Rule: the signature device appears in 1-2 beats only; a device in every scene
is a formula, not a signature. One animation mechanic (fly-in / stack / flip)
stars only once per piece.
Rationale: strong effects lose force when repeated; directional slides or hard
cuts should carry ordinary seams so the hero beat can remain special.
Self-check: count hero-effect occurrences; is any mechanic starring twice?

### T2. Slower than you think; hold after landing
Rule: default one notch slower than the first draft; brand/title cards hold
≥1s after settling; batch entrances end with 0.5s stillness; an opening
subject arc gets ≥3s.
Rationale: first-time viewers need time to read, recognize faces, and register
why the beat matters; under-held cards feel like production artifacts rather
than designed moments.
Self-check: watch as a first-time viewer — what did you not have time to read?

### T3. Restraint on light and decoration
Rule: no mass-applied glints/glows; a kept light effect goes to the hero
element once and must be clipped inside its rounded bounds. Portrait regions
stay minimal — no decorative elements over faces (`[no-occlusion]` is the
floor; visual quiet around people is the taste).
Rationale: repeated glints and glow sweeps quickly read as over-treatment;
reserve light effects for one motivated hero moment and keep faces visually
quiet.
Self-check: count glint/sweep occurrences; anything glowing without a reason?

### T4. No visual repetition; every shot adds new information
Rule: the same clip/moment appears once in a piece; duplicate-information
shots get cut even if they look good; montage clips must be visually distinct.
Rationale: repetition drains momentum and makes the edit feel padded; each
included shot should reveal a new action, expression, setting, or detail.
Self-check: for each shot ask "what NEW thing does this show?"

### T5. Front-facing, authentic moments win the cut
Rule: when selecting frames/clips of people, prefer front-facing, clearly
readable moments; for action-driven content (e.g. eating), only genuinely
active moments qualify — near-miss frames are cut, not padded.
Rationale: viewers should instantly understand who is present and what action
is happening; readable authentic moments beat almost-good filler.
Self-check: would a stranger instantly read what the subject is doing?

### T6. Text serves the frame, never fights it
Rule: big text ≤6 characters/words for hooks; text lands in negative space
planned by the composition; two-beat entrance (action word slams, qualifier
follows). Detailed layout/typography rules: `hyperframes` skill.
Rationale: text should clarify the frame's promise, not compete with faces or
focal action. Let words carry the hook while the picture carries atmosphere.
Self-check: cover the text — does the composition still work? Cover the
footage — does the hook still land?

## 5. Motion Personality Vocabulary (for the contract's dial notes)

Borrowed naming from LottieFiles' motion-design skill — use ONE per piece as
shorthand in the taste contract; implementation values come from the
`hyperframes` skill:

| Personality | Feels like | Typical fit |
|-------------|-----------|-------------|
| Playful | bouncy, overshooting | family vlogs, food, kids |
| Premium | slow, controlled, no overshoot | brand films, travel, cinematic |
| Corporate | clean, decisive | product demos, tutorials |
| Energetic | fast, expo-out punches | montages, sports, beat-cut |

## 6. Review Hook

The final review's Appeal rubric (`review/final-review.md`) scores the piece
against this contract: concept clarity, dial adherence, signature-device
scarcity, precedent violations. Write the contract knowing it will be graded.
