---
name: slp-scene-art
description: 'Generate and QA picture scenes for the SLP WH-question app.'
---

# SLP Scene Art Pipeline

Canonical style contract lives in the repo: `~/Desktop/SLP-App/content/STYLE-SPEC.md`
(read it first — palette table, composition slots, QA gate). This skill is the
execution playbook around it. Pilot reference: `content/playground/scene.png`
(seed 20260804).

## Pipeline

1. `fal-ai-generation` skill script:
   `python3 <skill>/scripts/fal_txt2img.py --width 1536 --height 1152 --seed <N> --out content/<scene-id>/scene.png --prompt "<template>"`
2. Prompt template (STYLE-SPEC §5): "Flat children's picture-book illustration
   of <SCENE>, soft matte colors, clean bold rounded shapes, subtle paper
   grain, calm low-clutter composition for a kids' learning app. <ELEMENT LIST
   with color + position slot + relation; girl in red dress, boy in blue
   shirt>. Wide shot, eye level, flat ground plane, elements clearly
   separated, small soft shadows, no text, no words, no letters, no numbers
   anywhere."
3. Vision-QA the PNG against STYLE-SPEC §6 before shipping; re-roll fresh seed
   on any failure; record passing seed.
4. Drop a per-scene `README.md` with the anchor inventory (element, normalized
   rect draft, relation proved, suggested WH-questions, distractor list) so
   the questions.json author works from what was actually drawn.

## Pitfalls (session-verified)

- **Seedream 4.5 ignores requested pixel size on disk**: request 1536×1152,
  file lands 2560×1920 (4:3, same as pilot on disk). The scene JSON
  `image_size` records the REQUEST size (1536×1152) and hotspots are
  normalized 0–1, so nothing breaks — don't "fix" either number.
- **Do not ship `<scene-id>/<scene-id>.json` until questions are final.**
  ContentStore.sceneIDs() picks up any folder containing `<id>.json`
  immediately (strict validation: exactly 5 questions, A–D choices at L1,
  unique non-overlapping hotspot rects). Art-only folders are invisible to
  the app — safe to land art first.
- **One accent hue per object.** Two red round objects break "where is the
  red ball". Clothing may share a hue with one object (pilot precedent).
- **Negation phrases degrade Seedream output** — write positive directives
  ("blank white board") not "no text". Still, always keep the explicit
  "no text, no letters, no numbers anywhere" tail; it works.
- **Relation pairs need headroom**: UNDER = visible gap above the animal,
  IN = container rim clearly around the object, or the preposition question
  becomes ambiguous. Re-roll, don't ship.
- **Probe calls cost money**: even a minimal-payload POST to fal.run renders
  an image (~$0.04). Use it only as a balance probe when a 403 says
  exhausted-balance.
- **Calm faces only**: small smiles, no open mouths/tears — autism-friendly
  low-arousal rule from DESIGN.md.

## QA gate (must pass before kanban_complete)

All planned anchors present with correct color + relation · exactly one
object per accent hue · zero text/numerals anywhere (boards, books, banners,
blocks) · anchors non-overlapping with ≥40% quiet space · calm faces ·
style matches playground pilot family · per-scene README anchor notes written.
