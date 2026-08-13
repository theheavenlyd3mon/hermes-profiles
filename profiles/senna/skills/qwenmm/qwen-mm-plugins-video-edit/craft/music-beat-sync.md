# Music Beat Sync — Grid Fit, Beat-Number Timeline, Post-Render Verify

> **Bridge notice.** This document owns *engineering the cut-to-beat loop*
> for real-footage edits with a strong-beat BGM. BGM sourcing/generation
> lives in `hyperframes-media` / `media-use`; rhythm *design* (which beats
> get energy) pairs with `craft/pacing-rhythm.md`.

For a strong-beat BGM, **every cut and key accent lands on the grid** — and
"on the grid" is measured, not felt. Target: post-render cut error ≤3 frames
(perception threshold); ideal ≤1.5f. A shipped 70s/18-shot piece hit
≤2.2f with this exact loop.

## When to run this

- User supplied or approved a BGM before cutting → run steps 1–4.
- No BGM chosen yet → cut to content rhythm first; source BGM later and only
  then decide whether to re-align key seams.
- **No BGM obtainable at all** (network-restricted, nothing suitable) →
  invert the problem: generate the music FROM the timeline. Write the
  timeline's key moments (freeze/land/slide windows) into a shared metadata
  JSON, then programmatically synthesize BGM (numpy/scipy — chord bed +
  whooshes on slide windows + a bell/impact drop on each freeze time). Cut
  error is ≈0ms by construction because video and audio read one source of
  truth; see `craft/character-intro-montage-techniques.md` for the shared
  beat metadata pattern.

## 1. Measure the grid (never trust the tempo scalar)

```bash
python3 scripts/beat_grid.py bgm.mp3 --json edit/beat-grid.json
```

The script runs librosa `beat_track`, then least-squares-fits an equal-spacing
grid `t_i = t0 + i*T` over the whole beat sequence — the fitted BPM is the
truth (raw tempo scalar drifts 2%+; validated here: raw 119.68 vs fitted
120.00 exactly). Read the output:

- `residual ≤ ±15ms` → machine-steady drums, grid TRUSTABLE.
- Large residual → tempo changes; fit per section (rerun on trimmed ranges).

## 2. Pin the big moments to the strongest kicks

The script band-passes the kick range (40–160Hz) and ranks integer beats by
onset energy. The 2–3 biggest slams of the piece (open, climax, close) go ON
those beats. Strong-beat music accents integer beats — never pin a slam on a
half-beat without energy data proving it.

Also extract structure for the energy skeleton: where the drums enter, where
the breakdown/quiet section sits (that's the natural home for a breathing
card or brand moment).

## 3. Write the timeline in beat numbers, not seconds

Constants first, everything derived:

```
t0 = 36.0597   # phase (s), from the grid fit
T  = 0.50000   # beat interval (s)
beat(n) = t0 + n*T          → cut times, accent times, SFX times
```

In HyperFrames, compute `data-start` values from `beat(n)`; in FFmpeg, trim
offsets likewise. Shots last whole beats (4/8 per shot); accelerando runs use
half/quarter-beat ladders. When the BGM's own drums are dense, keep SFX
sparse — pin only picture-unique actions.

Swap the track later = change two constants, entire timeline re-derives.

## 4. Post-render verification (the loop is not closed without this)

Measure the RENDERED file, not the source track — this catches encoder/mux
offset too:

```bash
python3 scripts/beat_grid.py final_v2.mp4 --cuts 2.0,4.5,8.0,12.5 --fps 30
```

| Verdict | Error |
|---|---|
| IDEAL | ≤1.5f |
| PASS | ≤3f |
| FAIL — fix and re-render | >3f |

Any FAIL: adjust that cut's beat number or frame offset, re-render, re-verify.
Record the final error table in `project.md` as review evidence.

## Self-check

- Grid fitted (not eyeballed), residual recorded?
- Big slams sitting on measured strongest kicks?
- Timeline expressed in beat numbers with t0/T constants?
- Post-render error table produced from the delivered file, all ≤3f?
