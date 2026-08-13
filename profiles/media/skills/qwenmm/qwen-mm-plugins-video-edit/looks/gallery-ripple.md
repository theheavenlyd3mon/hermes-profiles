# Look — Gallery Ripple + Multi-Focus

Distilled from a hero case study: when you have MANY uniform
assets and the story is "breadth × depth" — stun with scale, then dwell on
quality.

## Visual DNA

- A large tilted 3D grid (canvas ~2.25× the viewport) filled with the
  assets; cards **ripple in from the center outward** (entrance delay ∝
  distance from center, ~0.8s max delay, expo-out) while the camera zooms
  out to reveal scale.
- Then 3–4 **focus passes** (~1.7s each, 0.6s breathing gaps): background
  dims AND desaturates AND blurs (never opacity alone) while one card
  enlarges center-frame with a keyline ring.
- Continuous slow pan underneath (sine + linear drift, different X/Y
  frequencies) so stillness never reads as frozen.
- Depth via 2–3 shadow tiers, not true 3D per-card transforms (10× cheaper,
  <5% visual difference).

## Preconditions

- **≥20 visually uniform assets** (same aspect, same register) — below 20
  the ripple looks sparse; 30+ is ideal. Cells can be frames pulled from the
  piece's own clips.
- Each focused asset must survive enlargement (sharp at ~960px wide).
- Landscape or square canvas (the tilt needs horizontal room).

## Not for

- Telling a sequential story (this is a parallel structure).
- Data/reading content — focus passes are too fast to read dense text.
- Vertical 9:16 output.

## Implementation (HyperFrames)

1. Grid container on its own track, cells as stills (or muted micro-clips);
   ripple = per-cell `fromTo` with distance-based delay; simultaneous
   container scale 1.25 → 0.94.
2. Focus pass: chosen cell clones to an overlay layer, scales to center;
   grid gets `brightness(0.68) saturate(0.65) blur(2px)`.
3. Ambient pan on the container: `x = sin(t·0.12)·220 − t·8` (clamped),
   distinct Y frequency.
4. End: either collapse the grid into the title (converge morph) or fade
   the piece's opening shot back in as a bookend.

## Precedents & known pitfalls

- Dim-only backgrounds keep stealing attention — desaturate + blur is what
  makes the focus card pop (late-iteration finding).
- Uniform linear pan reads as mechanical; the sine+drift mix is the fix.
- Don't run more than 4 focus passes — the structure overstays its welcome.
