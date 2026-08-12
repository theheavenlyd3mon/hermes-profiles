# Unicode raster base-image guidelines for Herm eikons

Session source: Morgan Blackhand eikon iteration, May 2026. Lucas asked for research on what makes a good Unicode raster base image, then requested a new `morgan-blackhand-glyphbase` variant using fal.ai GPT Image 2 plates and Kling animation.

## Core finding

A good eikon source is not a good illustration. It is a glyph-survival signal map.

Herm eikons are baked down to a 48×24 monochrome text avatar using Unicode/Braille/block-style rasterization. Fine illustration detail, subtle gradients, hair strands, smoke, and small facial texture mostly collapse into noise. Large value-separated shapes survive.

## Unicode/Braille implications

- Unicode Braille encodes dots in a 2×4 grid per character cell.
- Rendering is effectively threshold/dither driven; it chooses dot clusters, not literal photographic pixels.
- Terminal font aspect ratios are not square. Shape exaggeration is safer than relying on exact portrait proportions.
- Block/half-block/braille renderers reward clean silhouette, hard edges, and large light/dark fields.

## Source design doctrine

Prefer high-resolution source plates. Do not make the source itself exact 48×24 unless explicitly running an experiment; that caused the Morgan Blackhand features to become mask-like and low-fidelity.

Build the source as a high-res poster with:

- pure black background
- light subject on black
- three-value design: black, light gray, white
- large close-up head and shoulders
- face filling the frame
- simple strong silhouette
- big facial landmarks
- no smoke over the face
- no scenery, city lights, text, logos, HUD, or tiny hatch lines
- minimal coat/leather detail; collar/shoulder silhouette beats texture

## Feature hierarchy for Morgan Blackhand-style faces

The renderer should be able to read these in order:

1. hair mass / bold white front streak
2. hard black brow or eye slash
3. strong black nose bridge
4. mouth line / speaking mouth as one clean shape
5. beard/jaw block
6. cigar line + ember dot
7. oversized high-collar V/triangle silhouette

## Prompt pattern

Use this concept in GPT Image 2 edit prompts:

```text
Use the supplied image as strict identity reference. Create a high-resolution source plate for a 48x24 monochrome Unicode/Braille terminal eikon. This must be a glyph-survival poster, not a detailed illustration. Pure black background. Light subject on black. Three-value design only: black, light gray, white. Large close-up head and shoulders; face fills the square frame. Preserve identity with bold readable landmarks: hair mass/white streak, hard brow/eye slash, strong nose bridge, mouth line, beard/jaw block, visible cigar line with ember dot, and oversized angular high collar silhouette. No smoke over face, no scenery, no gradients, no text/logos/HUD, no tiny hatch lines, no realistic skin texture. Every important feature must remain readable after conversion to one-color braille/block glyphs at 48x24.
```

## QA gate before video spend

Before Kling/video generation, inspect:

- normal contact sheet at thumbnail scale
- harsh manual 48×24 Braille/threshold preview if `chafa` is unavailable
- whether the face still reads when the plate is small
- whether state differences are obvious at a glance
- whether the collar/hair/cigar survive without relying on color

Do not spend Kling credits on a plate that only looks good as a full-size illustration.

## Animation notes

Kling can preserve these plates well if prompted to preserve the three-value composition exactly. Still use ffmpeg ping-pong loops after raw output.

Recommended video prompt suffix:

```text
Short seamless loopable close-up head-and-shoulders terminal avatar animation. Preserve the supplied three-value black/gray/white poster plate exactly: pure black background, bright face planes, hard black brow/eye/nose/mouth cuts, white hair streak, clean cigar line with ember dot, angular high collar silhouette. Motion must be readable at 48x24 but controlled. Return to starting pose by final frame. Locked camera, no cuts, no zoom out, no text, no logos, no subtitles, no HUD, no extra characters. No smoke over face, no fine texture, no face melting, no new accessories.
```

## Pitfall captured

Lucas corrected the approach: the bad 48×24 experiment showed the problem was not literal output resolution. It was feature distinctiveness and value separation. Fix with high-res glyph-survival plates, not lower-resolution source images.
