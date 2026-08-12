---
name: flux3-video-directing
description: "Use when writing or critiquing FLUX 3 video prompts."
---

# FLUX 3 Video Directing

## Trigger
Any request to write, improve, storyboard, or critique a FLUX 3 video prompt.
This skill owns the CRAFT layer only: prompt anatomy, cinematography language,
scene/beat direction, and the example library.

## Companion — mechanics live elsewhere
Tool selection, rate limits, polling, keyframe-index math, and contest workflow
live in the `video-generation` skill. Load it for generation mechanics; do not
restate them here. This skill tells you WHAT to write; that one tells you HOW to
run it. (That skill cross-links back here for prompt craft.)

## The prompt anatomy (THE template)
The cross-source consensus shape. Write plain prose in this order — the harness
is a reasoning model, not a tag encoder, so keyword tricks and word-order hacks
do nothing:

```
[Shot type / camera movement] of [subject] in [setting].
[Subject action over time, with timing beats].
[Environmental motion over time].
Audio: [ambience + event-tied SFX + music direction, or "no music"].
Style: [cinematic style, lens, lighting, texture / film stock].
Constraints: [identity lock, no text, no logos, no extra characters, realistic motion].
```

### The 9 rules (condensed)
1. **One clip = one shot.** Write a shot direction, not a scene idea: who's in
   frame, where the camera is, what moves, what changes over time, what's heard.
2. **Timing beats.** FLUX 3 follows timelines: "0–5s: … 5–10s: …", "after three
   seconds, a red light begins pulsing", "at the 2-second mark…".
3. **Audio section is mandatory** (it's on by default — silence must be asked
   for). Layer it: ambience + SFX bound to visible events with "as/when" +
   music direction or explicit "no music".
4. **Camera language + pace.** Use standard terms (push-in, dolly, truck, pan,
   tilt, orbit/arc, crane, rack focus, handheld, locked-off, whip pan) and add
   pace + what each phase reveals. For static: "the camera is entirely
   motionless for the duration; movement occurs only from the subject."
5. **Anti-artifact phrasing is standard practice for video** — see the tension
   note below. "One true unbroken continuous shot, no cuts, no morphing",
   "seamless throughout, consistent characters and world", "preserve face".
6. **Iterate one variable at a time.** Keep a reusable style prefix identical
   across clips for sequence consistency.
7. **Duration: 5–8s default** (establishing/cutaway/insert/reaction/texture).
   10–20s only when the subject stays stable and the action has a
   beginning-middle-end. Don't default to 20s.
8. **Dialogue:** quote exact lines, name a speaker visible on camera, give voice
   qualities (accent, pace, "Beat." pauses, tone), "one at a time, never
   overlapping" for multi-speaker — or let the model improvise from a situation.
9. **Split-screen works exceptionally well:** "15-second split-screen, two equal
   vertical halves, one continuous take, no cuts, perfectly frame-synchronized"
   + per-half visibility rules + timed beats + matching rules.

## Directing workflow
1. **Brief.** One sentence: subject, mood, the single thing the viewer should
   feel. Grounding: research anything with a real checkable appearance and put
   camera-visible specifics (silhouette, materials, colors, era) in the prompt.
2. **Pick beats.** For suspense/reveal/trailer work, choose beats from
   `references/suspense-and-trailer-structure.md` (8-beat ominous-reveal table +
   trailer templates). One beat = one clip.
3. **Write per-clip prompts** with the anatomy above. Pull shot/movement/lighting
   terms from `references/cinematography-vocabulary.md`; steal proven phrasing
   from `references/prompt-library.md`.
4. **Lock a reusable style prefix** (e.g. "hyper realistic blockbuster cinematic,
   anamorphic 35mm, heavy film grain, deep blacks") and repeat it verbatim in
   every clip + continuation so the world never resets.
5. **Generate** via the `video-generation` skill's mechanics.

Two principles to hold throughout:
- **Withhold ratio < 15%.** The subject is visible for under 15% of total
  runtime; everything else is evidence and reaction. Imagination out-scares pixels.
- **Sound precedes image.** The threat exists in audio before it exists visually
  (wing beats, distant roar, stone cracking). Let the next shot's sound enter
  before its picture (J-cut) to stitch clips seamlessly.

## The negative-prompt tension (read this)
BFL's FLUX.2 **image** docs say "no negative prompts — describe what you want."
FLUX 3 **video** power users consistently use explicit prohibitions successfully
("no morphing, no timing offset, no extra characters"). For video, the constraint
line wins: treat "no X" prohibitions as standard practice. Both can coexist —
phrase the positive goal AND forbid the specific artifact.

## Failure modes (top 8) + fixes
| Failure | Fix |
|---|---|
| Invented/unwanted music | Audio is on by default — always write an Audio: section; say "no music" explicitly |
| Quoted dialogue burns in as text/subtitles | Make a speaker visible on camera; describe them; add "no on-screen text, no subtitles" |
| Multi-shot prompt blends into one take | Consecutive shots must contrast in scale, location, or color |
| Morphing/drift mid-clip | "one true unbroken continuous shot, no cuts, no morphing"; strong refs; identical style prefix; explicit physics + timing |
| Character inconsistency across clips | Turnaround sheets; reference everywhere; video refs > stills; identical style prefix |
| Split-screen / multi-view desync | "perfectly frame-synchronized", per-half visibility rules, matching rules, "no timing offset" |
| Overlong clip loses coherence | 5–8s unless the action has a full arc and a stable subject |
| Vague one-line prompt → generic output | Director-style specificity: fill all six anatomy slots (camera + subject motion + environment motion + timing + audio + style + constraints) |

## References
- `references/cinematography-vocabulary.md` — lookup tables: 15 shot types,
  16 movements, 14 lighting terms, 10 lens/DOF terms, each with emotional effect.
- `references/prompt-library.md` — verbatim proven prompts (flick.art, X power
  users, fluxproai templates, Runway/Sora/Kling/Veo fragments), each annotated
  with why it works. Keep source attributions.
- `references/suspense-and-trailer-structure.md` — 8-beat ominous-reveal table,
  Derek Lieu 4-act + 30–60s teaser templates sized for chained FLUX clips,
  pacing mechanics. Makes a creature teaser repeatable for any creature.

## Pitfalls
- Don't write a scene idea — write a shot. "A scary forest" is not a prompt.
- Don't leave text/logos ambiguous: explicitly request (quoted, placed) or forbid
  ("no readable text, no logos").
- Don't pile unrelated sounds — audio mush. One ambience + event-tied SFX + optional score.
- Don't confirm a full reveal for suspense work — user taste is restraint with ONE
  clear glimpse held for a beat, then gone. Confirm glimpse level before locking beats.
- Don't restate mechanics here; if a rule about rate limits/polling/keyframe indices
  is needed, that belongs in `video-generation`.
