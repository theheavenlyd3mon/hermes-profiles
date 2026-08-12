# Single canonical plate animation pipeline

Use this when generating animated Herm eikons from one base image.

## Problem

Generating six independent still plates for `idle`, `listening`, `thinking`, `speaking`, `working`, and `error` gives each video a different first frame: different crop, pose, face geometry, lighting, and sometimes identity. Herm state transitions then snap between unrelated starting points. At sidebar size this reads as jitter, not animation.

## Current default

1. Generate one high-contrast `canonical_base_plate.png` from the supplied base image.
2. QA that single plate for 48×24 glyph survival.
3. Upload that same plate once to the video provider.
4. Generate all six state videos with the same `start_image_url`.
5. Put the state difference in the motion prompt only.
6. Ask the model to return to the canonical pose by the final frame, then ping-pong loop if needed.

## Acceptance

- All six video payloads use the same `start_image_url`.
- `~/.hermes/eikons/<name>/source/base.png` is copied from `bw-plates/canonical_base_plate.png`.
- State files are videos: `idle.mp4`, `listening.mp4`, `thinking.mp4`, `speaking.mp4`, `working.mp4`, `error.mp4`.
- No static `idle.png`, `listening.png`, etc. remain in the active source folder unless Lucas explicitly asks for static state overrides.
- State motion is readable but starts from the same identity/crop/silhouette.

## Exception

Separate state plates are allowed only as labeled experiments or emergency fallbacks. Store them under `bw-plates/optional_rejected_state_plates/` and do not install them as production state sources without saying so in the handoff.
