# Morgan Blackhand facecut pass — 2026-05

Session learning from iterating Lucas's Morgan Blackhand eikon.

## User corrections that changed the workflow

- Exact 48×24 source images were a bad path. They made the icon look like pixel mush and caused video models to over-interpret the face. The correct fix was not lower source resolution; it was stronger high-resolution source design.
- “More contrast” was not enough. Lucas specifically needed facial features to remain distinctive after Herm/Unicode rasterization.
- Same-name state PNGs (`idle.png`, `listening.png`, etc.) in the active source folder can make Studio show static states instead of the intended videos. Active source folders for animated state eikons should be clean: `base.png` plus six `<state>.mp4` files.

## Effective visual doctrine

When face features get lost, escalate to an extreme facecut/stencil pass:

- Treat the source as a combat patch / glyph survival map, not a portrait.
- Use a much tighter crop: head + high collar fill the square.
- Make the face a large white mask with huge black cuts.
- Mandatory landmarks:
  - thick black angry brow/eye band
  - bold black nose wedge
  - heavy mouth slash/wedge
  - beard/jaw as one dark geometric block
  - cigar as a thick clean bar plus bright ember dot
  - hair as 2–3 large white chunks/flames, not strands
  - collar as a simple angular V
- Remove subtle eyes, wrinkles, hatching, smoke, leather texture, small facial detail, and realistic shading.

## Plate prompt pattern

```text
Use supplied image as identity reference but redesign as an EXTREME face-landmark icon for 48x24 one-color Unicode/Braille rasterization. Crop MUCH tighter: head and collar fill almost entire square; face is 65-75% of the icon height. This is a combat patch / stencil mask, not a portrait. Pure black background. Only massive, simple, readable shapes. Use mostly white face mask with huge black graphic cuts.
Mandatory giant facial landmarks: one thick black angry eyebrow/eye band, one bold black nose wedge, one heavy black mouth slash, beard/jaw as one dark geometric block, cigar as a thick clean white/gray bar with bright ember dot, hair as two huge white flame chunks, high collar as simple angular black/white V shape. No subtle eyes, wrinkles, cheek shading, fine lines, realistic hair, small face details, smoke over face, scenery, gradients, hatching, leather texture, text, logos.
```

## Animation prompt pattern

Use lower `cfg_scale` around `0.55` to keep Kling from adding illustration detail back in.

```text
Short seamless loopable close-up terminal avatar animation. Preserve the supplied extreme black-and-white stencil icon exactly: huge brow band, nose wedge, mouth slash, beard block, cigar bar, white hair flame, angular collar V. Do not add detail. Do not soften into portrait shading. Locked camera, pure black background, no text/logos/HUD, no extra characters, no smoke over face. Motion visible but small enough that landmarks stay readable. Return to starting pose by final frame.
```

## Recovery pattern after partial animation

If only some states complete, do not claim the eikon is fully animated. Either:

1. Install partial outputs honestly and label placeholders as static MP4s; or
2. After credits/service recover, rerun only the missing states from their existing plates, then rebuild ping-pong loops and reinstall all six MP4s.

## Verification checklist

- Active source folder contains only `base.png` and six state MP4s.
- No `idle.png`, `listening.png`, etc. remain at the active source root.
- `ffprobe` confirms each MP4 is readable, 24fps, and ~6s after ping-pong.
- Contact sheet visually confirms every row changes over time and face landmarks survive motion.
