# AI-Generated Asset Triage — Rubric & Reframes

How to evaluate a batch of AI-generated creative assets (art, comics, UI, infographics,
ASCII/pixel art) and decide what to post and how to frame it. Pairs with the workflow
in SKILL.md.

## The three tiers

- **Tier 1 — postable as-is.** Strong, readable concept; clean render; no embarrassing
  artifacts at social-feed scale. These are your hero images.
- **Tier 2 — good art, fix first.** Composition/mood/render are strong but a small
  defect would get screenshotted and mocked. Almost always TEXT. A 10–20 min lettering
  or touch-up pass promotes these to Tier 1.
- **Tier 3 — not showcase-ready.** Reads as an automated filter or generation artifact
  rather than craft. Including these as "look what it made" evidence is fine; leading
  with them is not.

## AI-artifact tells to scan for (vision_analyze each candidate)

Text is the #1 failure mode. Check it FIRST on anything with words:
- **Misspelled titles / key words** — e.g. a comic cover reading "WHAT IS A GHOLL?" or
  "TOKYOO GHOUL". Misspelling the core subject word kills an otherwise strong piece.
- **Stuttered / truncated captions** — e.g. "They wal / walk amoong us." (cut-off word,
  duplicated word, misspelling in one box). Conspicuous because captions are meant to be read.
- **Garbled body text / pseudo-script** — infographic body copy or book spines that mimic
  writing but spell nothing. An infographic with unreadable body text fails AS an infographic
  even if it looks slick from afar.
- **Nonsense credit/logo lines** — fake creator credits, malformed issue numbers, broken badges.

Other tells:
- **Hands** — ambiguous finger counts, claw-like fingers where they overlap detail.
- **"Pixel art" that's really a pixelated photo** — uniform flat color blocks, stair-step
  edges, muddy banded gradients, no clean outlines or intentional dithering. Reads as
  "downscaled-then-upscaled photo," not crafted sprites. Subject may still be recognizable.
- **ASCII art that doesn't resolve** — a smear of characters with no readable silhouette.
  If a viewer can't name the subject without a caption, it's Tier 3.

## Choosing the strategic frame

Two default angles for a "my AI agent made these" post:

1. **Quality showcase** ("look at this art"). Use ONLY when the assets are genuinely
   strong and uniform. Invites the audience to judge quality — risky with uneven batches.
2. **Build-in-public workflow** ("I gave my agent ONE prompt/theme and it ran ~N different
   skills — UI design, comics, illustration, pixel art, ASCII — and produced all this").
   Use when assets are uneven. The variety and the single-prompt-many-skills mechanism are
   the hook; rough pieces become proof of breadth, not liabilities. Plays to an
   AI-builder audience rather than art critics.

Default to (2) for skill-demo batches — it's the more honest and more defensible story.

## Output shape for the report

Lead with the honest quality read (tiers), call out what the folder's README got wrong,
then give the strategic recommendation (which images lead, which frame, which need a fix
first). End with options, not a posted artifact — triage is review-gated.
