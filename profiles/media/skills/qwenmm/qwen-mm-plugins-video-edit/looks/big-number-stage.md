# Look — Big-Number / Big-Word Stage

Distilled from a "黑底巨型数字剧场" study and Neo-Swiss billboard
styles: one word or one number owns the whole screen. For stat moments,
section titles and cold-open hooks inside footage edits.

## Visual DNA

- Near-black (#0A0A0A, never pure #000) or paper-cream field; huge
  geometric-sans type filling 60–80% of the width; ONE accent color for the
  single highlighted token.
- Numbers roll/settle (digit-roll with tabular figures), words slam with a
  two-beat entrance; then a small annotation line lands beneath.
- Vast negative space is the point — nothing else on screen; optional
  hairline rule or tiny mono label as structure.
- Card holds ≥1s after the annotation lands (T2), then hard cut back to
  footage — the contrast IS the transition.

## Preconditions

- The number/word genuinely deserves the stage (a real stat, a turning
  point, the piece's thesis) — staging a filler word cheapens everything.
- ≤3 such cards per piece; each with different content type (number, word,
  question).

## Not for

- Pieces with information_density dial ≥7 (competes with dense overlays).
- Replacing actual footage storytelling — this is punctuation, not prose.

## Implementation (HyperFrames)

- Full-bleed color field on its own track between footage clips; type sized
  with viewport units; digits use `font-variant-numeric: tabular-nums`.
- Digit-roll: per-digit vertical wheel (GSAP y-keyframes, stepped or
  expo-out), landing staggered right-to-left; final settle + 0.5s stillness.
- Accent token gets the piece's single accent color; everything else stays
  monochrome.
- SFX: riser into the card, impact on the slam/settle, silence during the
  hold (`craft/sound-mix.md`).

## Precedents & known pitfalls

- Pure #000/#FFF fields read as "nothing loaded" — tint the neutral
  (shared precedent with the hyperframes skill family).
- Fade-out ending on the card kills its authority — hard cut out while
  it's still sharp.
- Breathing cards in the energy skeleton (`craft/pacing-rhythm.md` §2) are
  the low-energy cousin of this look: same layout, calmer entrance.
