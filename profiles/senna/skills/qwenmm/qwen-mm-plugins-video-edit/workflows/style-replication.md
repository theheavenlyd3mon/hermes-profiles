# Style Replication Workflow

Use this when the task is: "make a new video in the style of this reference video." The reference dictates HOW to edit (opening, transitions, effects, color, typography, pacing); all content comes from the new footage. Never copy footage from the reference.

**Reference effects are requirements, not options.** Every effect present in
the reference (a subject cutout with keyline, a panel wipe, a title treatment)
is a MUST-replicate item — never deliver a version missing one and then ask
"do you want it?". Precedent: a reference had a person-cutout
keyline effect; the agent shipped a no-cutout version and asked afterwards —
wrong on both counts. If a required capability is unavailable, stop BEFORE
assembly and resolve it (see Phase 3 capability gate).

This workflow builds on `review/source-review.md` (source review) and `review/final-review.md` (verification). It adds the style-replication-specific steps and the failure modes we have actually hit. Note: the reference IS the direction — the three-direction gate is skipped, but the taste contract is still written (distilled FROM the reference) so the final review has something to grade against.

## Phase 1 — Deep Reference Analysis

Do not plan the edit from a few thumbnails. A style replication is only as good as the reference analysis.

1. **Broad pass** — `read_video` at ~1fps to map the overall structure: sections, shot order, pacing, where effects happen.
2. **High-FPS pass on effect windows** — for every segment that contains a motion effect (opening, transitions, collages, title reveals), re-read with `read_video` at **2–4fps** and `budget="large"`. Watch the effect *move*, not just its start/end states.
3. **Write timestamped reconstruction notes** — for each effect record:
   - Exact time range
   - What elements are present (panels, text, dividers, overlays)
   - The *motion behavior* (how it animates: direction, easing, sequencing)
   - What persists vs what changes
   - Typography, color, layout details

## Phase 2 — Identify the Motion Architecture

This is where most replications fail. Two effects can look similar in a still frame but use completely different animation architectures. **Name the architecture before writing code.**

| Visual effect | Correct architecture | Wrong architecture (common mistake) |
|---------------|---------------------|-------------------------------------|
| Venetian blind / panel multiplication | Continuous footage + **multiplying black dividers** overlaid on top | Discrete panels scaling/appearing from nothing |
| Slit reveal / wipe | `clip-path` inset animation on a full element | Element width/scale animation |
| Filmstrip band | Horizontal strip with `clip-path` vertical inset | Stacked separate strips |
| Collage expand | Panels already placed, revealed by mask | Panels growing via `scaleX` |

Rule of thumb: if the reference shows footage that is *continuous* while lines/gaps appear, the footage is a base layer and the dividers are an overlay — not separate panels.

**Check the looks/ library before implementing from scratch.** After writing the reconstruction notes, scan `looks/README.md`: if the reference's style DNA matches a card (e.g. photographic cut-outs + keylines + flat color field → `looks/paper-collage.md`; freeze + punch zoom on a subject → `looks/freeze-punch-intro.md`; scrolling clip band → `looks/film-reel-carousel.md`), read that card in full and use its implementation route and known pitfalls as the baseline — then adapt to the reference's specifics. Re-deriving a look we already have a tuned recipe for throws away accumulated calibration. The reconstruction notes still win on any conflict: the card is the starting point, the reference is the ground truth.

Once named, look the architecture up in the `hyperframes` skill's transition catalog rather than inventing the GSAP from scratch — see the routing table in Phase 4.

## Phase 3 — Asset Preparation

**Capability gate first:** for each effect named in Phase 2, verify the tools
it needs are actually available NOW (subject cutout → `segmentation` (SAM3)
reachable, or local rembg fallback per `mcps/segmentation-matting.md`;
generated assets → the generation MCP tools registered). A missing capability
stops the workflow HERE — report it and agree on a path with the user before
any timeline assembly. Building first and asking afterwards is a
`[no-silent-downgrade]` violation even if you eventually ask.

- Re-encode source footage with dense keyframes for frame-accurate seeking: `ffmpeg -i in.mp4 -c:v libx264 -r 30 -g 30 -keyint_min 30 -movflags +faststart -an out.mp4`
- Verify each clip's duration with `ffprobe`. **`data-media-start` + `data-duration` must not exceed the source duration**, or the clip renders 0 frames.
- Symlink or copy clips into the project's `assets/` directory.

## Phase 4 — Composition (HyperFrames)

Follow the handoff protocol in `engines/hyperframes.md` — run the real `hyperframes` pipeline, do not skip straight to writing GSAP. Route the Phase 2 architecture name to the specific reference before implementing:

| Named architecture (Phase 2) | Read in the `hyperframes` skill (external — NOT files of this skill) |
|-------------------------------|----------------------------------|
| Venetian blind / panel multiplication | hyperframes skill: `references/transitions/catalog.md` § Cover (staggered blocks, blinds) |
| Slit reveal / wipe | hyperframes skill: `references/transitions/catalog.md` § Radial/Shape, or its `css-radial.md` |
| Filmstrip band / collage expand | hyperframes skill: `references/transitions/catalog.md` § Cover or Dissolve, whichever matches the reveal mechanism |
| Any transition not in Phase 2's table | hyperframes skill: `references/transitions.md` energy/mood tables, then the matching `css-*.md` in its `transitions/catalog.md` |
| Overall pacing / rhythm across the whole edit | hyperframes skill: `references/beat-direction.md` |

These paths live inside the `hyperframes` skill family and may move when it
restructures — if a referenced file is missing, search that skill for the
named concept (e.g. "transition catalog, Cover family") instead of treating
the route as dead.

Key contracts that break renders:

- Every `<video>` needs `class="clip"`, `data-start`, `data-duration`, `data-track-index`, a unique `id`, and `src` (not `data-src`).
- Videos must be **direct children** of the root — never nested inside another timed `div`.
- Overlapping elements (panels, overlays, dividers) need **distinct track indices**. Wrap a group of same-timed elements in one container `div` if they share a track.
- Animate `clip-path` / transforms via GSAP `fromTo` (seek-safe). Avoid CSS `transform` on the same property GSAP animates.
- Add `tl.set()` hard-kills where a fade ends exactly on a clip boundary.
- For fast-cut compositions set `HF_VIDEO_COVERAGE_THRESHOLD=0.8` (or 0.9) when rendering.

## Phase 5 — Verify Against the Reference (mandatory)

Do not declare done after a clean render. A render can be technically valid and still miss the effect.

1. Extract frames at the effect timestamps (`ffmpeg -ss <t> -frames:v 1`).
2. `read_video` the output at 2–3fps across the effect window.
3. For an independent check, use `vision_chat` with a targeted question: *"Does a black vertical line appear in the center, then multiply into 4/6/8 panels? YES/NO per step."*
4. Compare against the Phase 1 reconstruction notes, not against memory of the reference.
5. If an effect is missing or wrong, return to Phase 2 — the architecture is likely wrong, not the timing.

## Checklist Before Delivery

- [ ] Reference analyzed at high FPS, reconstruction notes **saved to a file** (e.g. `<videos_dir>/edit/reference_notes.md`) — not just reasoned about in chat
- [ ] Each effect's motion architecture named and matched to a `hyperframes` transition catalog entry (Phase 4 routing table)
- [ ] `looks/` library scanned against the reference's style DNA; any matching card read and used as implementation baseline
- [ ] All `data-media-start` values within source durations
- [ ] `hyperframes lint` and `hyperframes check` both pass (0 errors) before render
- [ ] Rendered with coverage threshold appropriate for cut density
- [ ] `<videos_dir>/edit/project.md` updated with the taste contract and decisions (`[log-or-it-didn't-happen]`)
- [ ] Final review planned and executed as its own step(s) — self-review pass + independent tool-verified pass, per `review/final-review.md` (`[review-independence]`)
- [ ] Output audio stream explicitly checked; any muted/dropped source audio disclosed and approved (`[audio-preserved]`)
- [ ] Output verified at effect timestamps via `read_video` / `vision_chat`
- [ ] Deliverable uses a versioned filename on re-render
