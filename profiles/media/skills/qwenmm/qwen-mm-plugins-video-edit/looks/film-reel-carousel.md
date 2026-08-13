# Look — Film-Reel Carousel Opening

Workspace-proven recipe (film-reel carousel montage series): a horizontal
filmstrip of clips scrolls like a reel, then one frame "lands" as a PiP or
takes over full-screen — structure and nostalgia in one move.

## Visual DNA

- A horizontal band of 16:9 frames (sprocket-hole borders optional) scrolls
  across the screen; each cell is a *moving* clip, not a still.
- Scroll uses a parametric timeline: accelerate in, glide, decelerate onto
  the chosen frame (never uniform speed — T2/R2 discipline).
- The chosen cell scales out of the band and lands into the layout (PiP
  corner or full-screen takeover) — landing is a real slot in the
  composition, not a float above it.
- Band and background stay muted (dim/desaturate) so the landing cell owns
  the color.

## Preconditions

- ≥6 visually distinct clips (no repetition — T4); landscape or square
  canvas (a horizontal band on 9:16 feels cramped — rotate the concept to a
  vertical strip if needed).
- Clips pre-trimmed to their golden segments so every visible cell moves.

## Not for

- Pieces with <5 usable clips (the band looks like a patch).
- Solemn registers — the reel reads playful/nostalgic.

## Implementation (HyperFrames)

1. Re-encode cells with dense keyframes for frame-accurate seeking
   (`workflows/style-replication.md` Phase 3 command).
2. Band = one container track, cells as direct-child clips with distinct
   track indices; scroll via GSAP `x` keyframes (parametric ease).
3. Landing: FLIP-style — cell's end position measured in layout, animate
   transform to it, then swap z-index so it embeds (Q9 precedent: flown-in
   elements land in real slots).
4. Dim non-chosen cells with brightness/saturate filters + slight blur —
   not opacity alone.

## Precedents & known pitfalls

- Cells that don't move read as a static grid screenshot — every cell must
  be a playing clip or Ken Burns still.
- One carousel per piece (T1); a second pass of the same band is filler.
- Verify the landing seam at high FPS — the transform-to-slot moment is the
  shot's make-or-break frame.
