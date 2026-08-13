# Look — Brush & Calligraphy Banner

Ink-brush banners and calligraphic titles over real footage — artistic weight
for cultural, culinary and character content.

## Visual DNA

- Generated brush-stroke banners (single confident stroke, uneven ink edges)
  as text backplates; calligraphic or high-contrast display type on top.
- Strokes reveal by wipe/mask in the stroke's own direction (as if being
  painted), 0.5–0.8s, then hold.
- Ink elements live in the frame's negative space — off-center, anchored to
  an edge, sized to the text they carry.
- Palette: ink black + paper cream + ONE accent (vermilion seal-red is the
  classic); footage underneath gets at most a subtle warm correction.

## Preconditions

- Content with cultural/artisanal/culinary register; taste contract
  personality Premium or Playful-artistic.
- A brush-asset source: `qwen_image` (prompt for "single ink brush stroke,
  white background, high contrast" — white bg for clean matting).

## Not for

- Tech/product/corporate registers (mismatched vocabulary).
- **Center-screen ink-splash bursts.** Brush elements frame content from the
  edges; they never explode over the subject.

## Implementation (gen assets + HyperFrames)

1. Generate 2–3 brush strokes + optional seal stamp with `qwen_image`
   (white background), matte to transparency. For white-background brush
   matting, use the continuous de-white alpha recipe in
   `craft/character-intro-montage-techniques.md`.
2. Sample-first rule applies: generate ONE sample, verify edges/tone,
   then batch the remaining variants (`mcps/README.md`).
3. HyperFrames: banner reveals via `clip-path` inset wipe along stroke
   direction; text enters after the stroke lands (two-beat, T6); seal stamp
   pops last with an impact SFX.
4. **True write-on (stroke-order) alternative** for hero Chinese titles:
   per-stroke SVG paths from the Make Me a Hanzi / HanziWriter dataset
   (9000+ chars with stroke order), animated stroke-by-stroke via GSAP
   `stroke-dashoffset` — deterministic and seek-safe, reads as an
   invisible pen actually writing. Use when the brief wants visible
   "writing", not just a brush-textured reveal. Cheap fake for secondary
   text only: handwriting font + per-char stagger + ±2° rotation jitter
   (recognizable as a font up close — never for hero titles).
5. Keep brush elements to title/section moments — 2–3 appearances per
   piece maximum.

## Known pitfalls

- Ink-splash transitions covering the frame overwhelm the subject; directional
  slides or hard cuts usually remain the cleaner transition language.
- Generated strokes with gray halos ruin the paper illusion — re-matte or
  regenerate; check against both light and dark frames.
- Calligraphic fonts for CJK must actually ship the glyphs — verify no tofu
  at render.
- AI-generated Chinese calligraphy frequently draws wrong or malformed
  characters — `read_image` and verify EVERY generated glyph before
  compositing, or generate only the abstract stroke/banner and set real
  type on top.
