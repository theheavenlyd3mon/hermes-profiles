# Look — Freeze-Frame Punch-Zoom Intro

A workspace-proven recipe (character intro montage series) for introducing a
person or subject with high energy.

## Visual DNA

- Action plays at speed → **hard freeze** on the subject's strongest
  front-facing frame → **punch zoom** (fast scale step, e.g. 1.0 → 1.15 in
  2–3 frames, expo-out settle) onto the frozen frame.
- Name/label card slams in beside the face during the freeze — two-beat
  entrance (name slams, descriptor follows), always in face-safe negative
  space.
- Optional beat-synced decorations around (not over) the subject: speed
  lines, geometric pops, spark dots — comic energy, 0.3–0.5s lifetime each.
- Freeze holds ≥1s after text lands, then action resumes or hard-cuts on.

## Preconditions

- A genuinely strong front-facing frame exists (T5 precedent: front-facing,
  instantly readable). Verify at high FPS with `read_video` before choosing.
- The piece's motion_intensity dial ≥5 — this look is loud.

## Not for

- Calm, premium or documentary registers; grief/serious subjects.
- Introducing more than ~4 subjects back-to-back (repetition kills it —
  vary the freeze framing/decoration per person, or switch structure).

## Implementation (HyperFrames on footage)

1. Extract the freeze frame (`ffmpeg -ss T -frames:v 1`), optionally cut the
   subject with `segmentation` for a text-behind-subject layer.
2. Composition: video clip plays → freeze image takes over on the exact
   frame → GSAP punch (scale keyframes, `expo.out`) → text two-beat entrance
   → decorations stagger in on the beat grid → resume.
3. SFX: whoosh-fast leading the freeze by 1–2 frames + impact on the punch
   landing (`craft/sound-mix.md` pinning rules).

## Precedents & known pitfalls

- Decorations belong to the *card zone*, never over the face
  (portrait-area minimalism precedent; T3).
- Freeze frame must be sharp — motion-blurred freezes read as mistakes;
  scan ±3 frames for the sharpest.
- Punch without hold reads as glitch: always ≥1s settled hold with text
  readable (T2).
