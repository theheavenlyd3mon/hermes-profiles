# 48x24 source-image eikon test

Context: Lucas asked to test a separate Morgan Blackhand eikon whose source images were exact target resolution (48x24) rather than high-res plates.

## What worked

- Build exact 48x24 PNG state plates from the higher-quality face-contrast plates, then enlarge with nearest-neighbor only for inspection and video-provider start frames.
- Install both exact 48x24 PNGs and generated videos under a separate eikon name so Studio comparison is easy:
  - `~/.hermes/eikons/<name>-48x24-test/source/base.png`
  - `<state>.png` exact 48x24 state plates
  - `<state>.mp4` looped video state clips
- For video generation, tiny 48x24 images should be nearest-upscaled to a provider-friendly 2:1 frame first, e.g. 960x480, while keeping the original 48x24 PNGs as the actual test artifact.
- Use ping-pong forward+reverse loops after generation to make final clips loop cleanly.

## Important result

Exact 48x24 source images are useful as an experiment, but they generally hurt facial fidelity compared with high-res high-contrast plates. The face becomes more icon-like or mask-like, and video models may over-interpret the tiny pixel face, especially for high-motion states like `working` and `error`.

Default recommendation: keep high-res, face-first, high-contrast source plates as the production path. Use exact 48x24 source tests only when Studio/rasterization appears to be over-processing high-res sources or when Lucas explicitly wants a pre-baked pixel-art look.

## 48x24 plate generation pattern

1. Start from the best high-res face-contrast B/W plates, not the original cinematic base.
2. Use a tight face/collar crop so the face occupies enough pixels.
3. Resize to exactly 48x24 with antialiasing, then quantize to 3-4 tones.
4. Save exact plates as `<state>_bw_plate_48x24.png`.
5. Create nearest-neighbor enlarged contact sheet for QA.
6. Create nearest-neighbor upscaled versions, e.g. 960x480, for video-generation start frames.

## QA expectations

- A successful 48x24 test should make brow/eye band, nose bridge, mouth/beard, cigar, and collar readable after enlargement.
- Expect less identity fidelity than high-res plates.
- Compare against the high-res production eikon before recommending the 48x24 version.
