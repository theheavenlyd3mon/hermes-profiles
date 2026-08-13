# HyperFrames — Handoff Protocol (Not a Knowledge Copy)

HyperFrames is not an "engine" this skill drives with a few reference reads —
it is a **full creative production line** owned by the `hyperframes` skill
family. This file defines the handoff: what video-edit contributes, what
it hands over, and what it is forbidden to re-implement.

## The ownership rule

For any designed deliverable, run the ACTUAL `hyperframes` pipeline — invoke
the `hyperframes` entry skill and let it route:

```
hyperframes (entry) → BRIEF/intent → owning workflow (general-video, ...)
→ hyperframes-core (composition contract, STORYBOARD.md)
→ hyperframes-creative (design spec: palette, type, beat plan)
→ hyperframes-registry (installed pro blocks: captions, transitions, VFX)
→ hyperframes-media (BGM/SFX/TTS via the shared audio engine)
→ hyperframes-cli (lint → check → snapshot / grade-compare → render)
```

**Forbidden:** skipping this pipeline and hand-writing a composition from
memory; re-teaching transitions/motion/typography inside this skill or a
project; skipping design spec and storyboard because "it's just an edit".
Bypassing the pipeline is exactly how outputs end up worse than plain
hyperframes usage.

## What video-edit hands over (its added value)

Before the handoff, this skill produces the inputs the pipeline can't invent:

- **Taste contract + chosen direction/look** (`craft/art-direction.md`,
  `looks/`) → feeds BRIEF/design-spec decisions.
- **Footage package:** selected golden segments, re-encoded for
  frame-accurate seeking (`ffmpeg -c:v libx264 -r 30 -g 30 -keyint_min 30
  -movflags +faststart`), per-clip corrected (`craft/footage-grading.md`),
  with a footage log.
- **Rhythm plan:** declared pacing pattern, energy skeleton, and (for
  beat-cut pieces) the measured beat grid constants t0/T
  (`craft/music-beat-sync.md`) for `data-start` computation.
- **Cut/segment assets:** subject mattes from `segmentation` when the look
  needs them (sticker/text-behind-subject).
- **Motion-language references (borrow the style, never the runtime):**
  external animation ecosystems — motion.dev (Framer Motion) examples,
  Motion UI sections, similar catalogs — are legitimate TASTE sources for
  spring feel, stagger rhythm, layout-morph and exit choreography. Cite the
  pattern + parameters in the design spec, then implement in the pipeline's
  own adapters: springs are pre-sampled into CSS keyframes or a GSAP
  CustomEase (a sampled spring is a fixed curve — seek-safe and cold-render
  safe by construction); staggers map to `gsap.stagger`; layout morphs to
  GSAP Flip. The user-approved recipe palette with production spring presets
  lives in `craft/motion-recipes.md`, with seek-safe reference
  implementations per recipe in `craft/snippets/` — hand the named recipes +
  parameters over in the design spec, and paste/adapt from the snippet
  instead of re-deriving the GSAP. Importing the Motion runtime (or any
  non-adapter
  animation engine) into a composition is forbidden — it drives its own rAF
  loop and breaks deterministic rendering.

After the pipeline renders, this skill takes the output back through
`review/final-review.md`.

## Video-edit-specific composition gotchas

Kept here because they bit real footage projects (not general HF teaching):

- Every `<video>`: `class="clip"`, `data-start`, `data-duration`,
  `data-track-index`, unique `id`, `src` (not `data-src`); videos are direct
  children of the composition root.
- `data-media-start + data-duration` must not exceed the source clip's real
  duration — the clip renders 0 frames otherwise. Verify with ffprobe.
- **No timeline gaps.** Before render, sum every visual element's
  `data-start`/`data-duration` and confirm the full composition duration is
  covered — any instant with no element on any track renders as a black gap
  at the transition. After render, `scripts/black_check.sh` on the output is
  the objective catch (exit 2 = interior black).
- Overlapping elements need distinct track indices; same-timed groups share
  one container.
- Fast-cut footage compositions: render with
  `HF_VIDEO_COVERAGE_THRESHOLD=0.8` (or 0.9).
- Cold-render frame 0 differs from preview when animations start
  unregistered — verify first frame on the render, not the preview.
- **Black frames from the SECOND video source onward ⇒ try
  `render --workers 1` FIRST.** Multi-worker rendering (default 4) has a
  frame-injection race at the switch between video sources; the second source
  renders black from a few seconds in. Verified by minimal repro:
  one clip renders clean, any two clips fail identically regardless of order,
  file, or monolithic-vs-modular structure, pre-extracted frame cache is
  intact (luma normal), and `--workers 1` fixes it completely. Re-encoding
  the footage does NOT help — five attempts (fps, keyframes, baseline
  profile, audio strip, duration alignment) all failed because the cause is
  the renderer, not the media.

## Scene-loop assembly — the default for multi-scene pieces

Never write one giant composition and let the full render be the first
time anyone SEES it — that feedback loop is how broken closings and
absent devices shipped, and a full re-render is exactly the cost pressure
that produces "PASS with notes". Build scene by scene against the Scene
Ledger (`review/project-log.md`); single-scene loops and mechanical jobs
are exempt.

**Verified mechanics (field-tested against CLI 0.7.81):**

- One file per scene: `compositions/sceneN.html`. Single-scene render:
  `npx hyperframes render -c compositions/sceneN.html --workers 1`
  — 30-40s per 6-12s scene; keep outputs in `renders/sceneN.mp4` (they
  are the board previews and the ledger evidence).
- `check` / `lint` / `snapshot` only read `index.html`: copy the scene in
  to validate, and **restore or overwrite `index.html` deliberately before
  any master-level command** — field accident: a scene-check `cp` left a
  scene in `index.html` and the master sync script silently edited the
  wrong file. Author the master as `compositions/master.html`, promote it
  to `index.html` only at the global pass, and verify WHICH file occupies
  `index.html` before every check/render.

**Per scene:** build → lint/check clean → snapshot the device timestamps
(cheap pre-render look: fonts real, type above floor, no tofu, placement)
→ render the scene → **scene review, six checks on the render**
(`review/scene-review.md`) → fix and re-render locally until it passes →
update the ledger row → LOCKED.

**Global pass (ONLY after the scene gate passes):** first run
`bash <skill-root>/scripts/scene_gate.sh <videos_dir>/edit/project.md`
and paste its verbatim block into the project log — it FAILs while any
ledger row is unLOCKED or any scene file lacks a real `## iter N` entry,
and a master rendered without a passing SCENE GATE block is a skipped
workflow ([hyperframes-handoff]). A monolithic `index.html` authored in
one shot never satisfies this gate: there are no scene renders to log.
Then assemble the master on the full
timeline; cross-scene transitions ride the seams here (overlapping clips
live at this layer only); unified grade, sound design, opening↔ending
bookend — each a G row. Then ONE full render → `review_gate.sh` → verdict
(device ledger aggregates from the Scene Ledger; re-confirm timestamps on
the final mp4, since master-layer bugs — z-order, seam timing — do not
exist at scene level).

## Render troubleshooting — diagnose before downgrading

A render failure is a bug to isolate, not a verdict on the engine
(`[no-silent-downgrade]`). Before proposing ANY engine or treatment
downgrade:

1. **Minimal repro in `<videos_dir>/edit/repro/`** — strip to the smallest
   composition that still fails; change ONE variable per run (clip count,
   order, same-vs-different file, worker count, structure).
2. **Check the pipeline stage** — is the pre-extracted frame cache intact
   (measure luma, e.g. ffmpeg `signalstats`)? Clean cache + black output
   means the fault is in injection/capture, not the media or the browser.
3. **Try the known switches** — `--workers 1`, `HF_VIDEO_COVERAGE_THRESHOLD`.
4. **Log the repro table** in `project.md`; only then discuss options.

Attributing a failure to a component you have not isolated is a violation
of this section (black frames blamed on "an inherent Chrome decode
flaw", engine abandoned — the real cause was the worker race above).

Headless-render pitfalls that keep recurring:

- **Vendor GSAP locally** (`assets/gsap.min.js`), never a CDN `<script src>`
  — CDNs time out in headless runs.
- **No emoji glyphs in render-path content** — headless Chromium has no
  color emoji font; structural imagery (photos, icons) must be an actual
  footage frame, SVG, or image file. Emoji only as frame-verified
  decoration.
- **`class="clip"` belongs on a `div`** — an `<svg>` (and likely any
  non-div element) carrying the timing attributes is NOT hidden outside its
  window: it keeps painting over later scenes. Wrap it:
  `<div class="clip" data-start…><svg>…</svg></div>`. Field leak:
  a freeze-punch ellipse bled 3s past its window onto the next
  scene and the ending card; div clips and a sibling caption div behaved
  correctly, only the svg leaked.
- **Master audio assembly can MISPLACE a source — verify the mix after
  every multi-source master render.** Field case: the master
  placed one scene's audio at offset ~0s instead of its scene offset — the
  scene's own region went silent AND its speech played doubled under the
  opening scenes; `--workers 1` did not prevent it (audio-domain analog of
  the frame-injection race). A silent region and a doubled region are the
  SAME bug — finding one means checking for the other. Post-master audio
  check (before review, speech-led pieces especially): compare per-scene
  RMS of each scene render vs the same window in the master (a window at
  rms≈0 while the scene render has voice = misplaced source); confirm with
  envelope cross-correlation — each scene's audio must match the master
  EXACTLY ONCE, at its ledger offset. Repair without touching reviewed
  video: discard the master's audio, rebuild deterministically in ffmpeg
  (`adelay` each scene render's audio to its ledger offset, + SFX events,
  `amix=normalize=0` + limiter), mux with `-c:v copy` — video stays
  byte-identical, output gets the next version suffix, review invalidation
  re-runs the gate on the new file.

## Environment gate

`node -v` (≥22) · `npx hyperframes doctor` · ffmpeg/ffprobe present. All
compositions pass `lint` then `check` (0 errors) before `render` — rendering
a failing composition is never acceptable. If the environment cannot resolve
hyperframes, report the blocker and get approval before any FFmpeg-only
fallback (`[no-silent-downgrade]`).
