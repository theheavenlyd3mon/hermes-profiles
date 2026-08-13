# Engines — Ownership and Routing

Two engines, one ownership rule:

| Engine | Role |
|--------|------|
| **HyperFrames** | Assembles the *deliverable* for any user-facing designed output — full creative pipeline, handed off, not re-implemented (see `hyperframes.md`) |
| **FFmpeg** | Prep and finishing: probing, re-encode for seeking, per-clip correction, audio mux, mechanical trims (see `ffmpeg-direct.md`) |

**Default:** if the deliverable is meant to be watched (vlog, montage, intro,
promo, recap — anything with designed motion, text or structure), the final
timeline is assembled in HyperFrames via the full `hyperframes` skill
pipeline. FFmpeg-only assembly is reserved for mechanical deliverables.

## Routing

| Task shape | Route |
|------------|-------|
| Exact trim / concat / format conversion, no design | FFmpeg only |
| Subtitle burn onto an otherwise-finished file | FFmpeg (after timing final) |
| Per-clip color correction, re-encode for frame-accurate seeking | FFmpeg prep |
| Audio mix / loudness / mux | FFmpeg finishing (`craft/sound-mix.md`) |
| ANY designed deliverable: montage, vlog, intro, promo, recap, styled edit | **HyperFrames handoff** |
| Designed sections + long plain footage passages | Hybrid: FFmpeg preps/trims the footage; HyperFrames owns the assembled timeline |

Why the default: `concat`+`xfade` assembly produces slideshows — the beauty
ceiling lives in the HyperFrames pipeline, so watchable deliverables go
there (`hyperframes.md` owns the handoff and its environment gate).

## Availability

FFmpeg: `ffmpeg -version` / `ffprobe -version` run. HyperFrames: env gate in
`hyperframes.md`. If an approved engine becomes unavailable: stop, report,
get approval before downgrading (`[no-silent-downgrade]`).

## Cheap-probe rule (both engines)

Before full renders: FFmpeg — test risky filter chains on ~3s slices and
every transition recipe on a two-clip sample; HyperFrames — lint → check →
snapshot a representative scene before rendering the piece.
