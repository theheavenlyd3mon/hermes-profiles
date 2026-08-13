# Footage Grading — Bounded Correction First, Creative Looks Opt-In

> **Bridge notice.** This document owns *color treatment of real footage*.
> Designed-scene color/palette decisions live in `hyperframes-creative`
> (design spec, palettes); this file never defines brand palettes.

## Mental model

Two entirely different operations — never conflate them:

1. **Correction (default, automatic):** make each clip look clean without
   looking graded. Bounded, per-clip, no hue shifts, no LUTs.
2. **Creative look (opt-in only):** teal/orange, filmic curves, vintage —
   an art-direction decision recorded in the taste contract and approved.
   Never applied by default.

Under the hood corrections follow the ASC CDL intuition: slope ≈ highlights,
offset ≈ shadows, power ≈ midtones, then global saturation.

## Correction workflow

```bash
python3 scripts/auto_grade.py analyze CLIP          # stats + judgment + filter
python3 scripts/auto_grade.py apply CLIP -o OUT.mp4 # bounded eq, audio copied
```

The script samples signalstats, measures luma mean / luma range / saturation,
and emits an `eq` correction clamped to roughly ±8% per axis. It fixes only:
under-exposure (gamma lift), flatness (gentle contrast), mild desaturation.
Already-balanced clips get a near-noop. Apply **per clip during extraction**,
not on the assembled timeline (avoids double re-encode and lets each source
get its own correction).

## Multi-source consistency

When cutting clips from different cameras/sessions together:

- Correct each clip first, then compare representative frames side by side
  (`ffmpeg -ss T -frames:v 1` + hstack) across sources.
- One look for the whole piece — never switch grades between scenes unless
  the narrative demands it (and then it goes in the taste contract).

## Creative looks (when approved)

- Apply on top of corrected footage, never on raw.
- Intensity below full: 0.6–0.85 blend is the usable range; 1.0 reads as
  overdone.
- **Skin is the tripwire:** never push saturation above ~1.2 on footage with
  people; after grading, check a frame with visible skin — orange/green/
  magenta cast means pull back. If skin fights the look, the look loses.
- Slightly lifted shadows and rolled-off highlights read as premium; crushed
  blacks and clipped whites read as broken.

## Self-check

- Is every clip corrected (or explicitly judged "no correction needed")?
- Same-scene clips from different sources: do they match side by side?
- Any creative look: is it in the taste contract, approved, and blended <1.0?
- Skin tones checked on a real frame after any grade?
