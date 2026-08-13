# Look — Editorial Paper Collage / Sticker

Editorial collage treatment adapted to this plugin's toolchain
(segmentation MCP + HyperFrames + qwen_image + wan_t2v/happyhorse).

## Visual DNA

- Strong, flat, uniform color field as the backdrop — the hue carries
  meaning (see semantic palette below), never a gradient wash.
- Subjects as **photographic cut-outs**: crisp machine-cut edges, warm-cream
  keylines (2–4px), soft low-opacity paper shadows, optional torn-paper
  edges and tape corners on secondary elements.
- Black-and-white halftone texture on backgrounds/secondary cut-outs;
  **never on faces** — faces stay photographic.
- Colored cardstock accents (cards, labels, arrows) serve information
  hierarchy — never colored for color's sake.
- Motion is **assemble-from-empty**: pieces slide in, snap into place,
  connect — stop-motion timing (steps easing, hard landings). Not drift,
  not slow zoom, not crossfade.
- 3–6 large separable groups per frame; more reads as confetti.

Semantic color-field palette (adapt per taste contract):

| Field | Meaning |
|---|---|
| burnt orange / red | time, labor, urgency |
| mustard yellow | tools, warnings, leaks |
| ink green | cognition, reset, judgment |
| deep purple | rules, memory, permanence |
| teal | collaboration, automation |

## Preconditions

- The piece tolerates a graphic, editorial register (vlog intro, concept
  beat, explainer section, personality-driven content).
- For sticker treatment: subject is well-separated from background
  (segmentation quality gate — run a test frame first).

## Not for

- Documentary/realism-first pieces where any stylization breaks trust.
- Whole-piece application on long footage edits — use it for intros,
  chapter cards, PiP and B-roll beats; the footage itself stays footage.
- Precise layered timeline control needs → plain HyperFrames composition.

## Route A — Real-footage sticker treatment (deterministic, preferred)

Keeps the person's real performance; no generation needed; uses tools this
plugin already has.

1. Pick the moment (freeze frame or short clip). `segmentation` (SAM3) cuts
   the subject; verify the mask on a contrasting background
   (`mcps/segmentation-matting.md` quality gates — hair/hands intact).
2. In HyperFrames: subject PNG/alpha-video gets keyline (solid outline or
   double-border), paper drop shadow, slight rotation (±2–4°); color field
   behind; halftone dot texture (CSS radial-gradient pattern) on background
   panels only; cardstock labels/arrows as separate timed elements.
   For pixel-exact keylines, use the alpha-dilation outline recipe in
   `craft/character-intro-montage-techniques.md`.
3. Animate assembly with GSAP: field first → structure pieces → subject
   snaps in (`back.out` or stepped easing) → labels land last. Hard
   landings, 0.5s stillness after the set completes (T2 precedent).
4. SFX: card-snap/paper taps per landing, pinned per frame
   (`craft/sound-mix.md`).

Uses: character intro cards, sticker PiP over footage, chapter cards,
before/after panels.

## Route B — Generated collage B-roll (for concept beats with no footage)

Use a three-gate sample-first pipeline (`mcps/README.md`):

1. **Gate 1 — metaphor:** compress the line into ONE visual
   proposition, 3–6 key objects, color field from the semantic palette.
   User confirms before any generation.
2. **Gate 2 — still:** `qwen_image` renders the finished collage
   poster (flat field + halftone cut-outs + cardstock accents, no text, no
   logos). User confirms the still.
3. **Gate 3 — motion:** first frame = empty color field, last
   frame = approved still; `wan_t2v`/`happyhorse` animates the
   piece-by-piece assembly (prompt: locked camera, no zoom, no morphing, no
   new objects). Strip audio for B-roll use. Verify with a per-second
   contact sheet: starts empty, assembles progressively, final frame matches
   the approved still.

## Known pitfalls

- Faces must never be halftoned or redrawn — keep faces photographic.
- Fake lettering appears in generated stills → regenerate the still; never
  patch text at the video stage.
- Weak assembly feeling → reduce element count and prompt explicit
  piece-order (structure → subject → labels).
- A flyer element crossing frame is a great occasional punch, not a
  per-shot formula.
