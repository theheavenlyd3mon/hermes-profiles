# Core Perception Tools

Use these before content-driven editing, reference matching, key-window timing, overlay placement, and final evidence-based review.

## Role

Core perception tools are the agent's eyes. They provide visual/audio evidence so the agent does not make edit decisions from filenames, assumptions, or low-detail thumbnails.

## Tools

| Tool | Primary Use |
|------|-------------|
| `read_video` | Inspect video frames over a time window at chosen fps/resolution budget |
| `read_image` | Inspect images or saved frames |
| `visualize` | Inspect non-video files or mixed media inputs |
| `transcribe_audio` | Understand speech and produce timestamps |
| `save_view` | Save exact frames for evidence or follow-up analysis |
| `vision_chat` | Ask a general visual assistant for an independent second opinion on sampled frames/videos |

## Use When

- Reviewing source footage before editing
- Analyzing a reference video style or timing
- Selecting cuts or hero moments
- Checking fast motion, UI changes, gestures, lip-sync, or transitions
- Verifying subtitles, overlays, text readability, and final output
- Asking `vision_chat` for an objective second-opinion review on important/style-sensitive outputs
- Capturing visual evidence for checkpoint/final review

## Do Not Use As A Substitute For

- FFmpeg technical probing (`ffprobe` still checks streams, fps, duration, codec)
- Full final render validation
- User approval when changing direction

Perception tools complement engineering checks; they do not replace them.

## Inspection Strategy

1. **Technical probe first** — know duration, fps, resolution, audio streams.
2. **Overview pass** — use `read_video` at moderate fps/budget to understand structure.
3. **Key-window pass** — re-read critical windows at higher fps and larger budget.
4. **Second-opinion pass** — for important, style-sensitive, reference-driven, or ambiguous outputs, ask `vision_chat` to review sampled frames/video windows against concrete criteria.
5. **Evidence recording** — write what was observed with timestamps.

## Recommended `read_video` Patterns

Viewing-depth requirements per source type (short/long/reference/critical
windows) live in `review/source-review.md` — the owning doc. Tool-side rule
of thumb: overview at ~1fps normal budget; edit-critical windows re-read at
2–8fps `budget="large"` with tight `start_time`/`end_time`; increase fps
when motion timing matters, budget when visual detail matters.

## `vision_chat` Second-Opinion Pattern

Use `vision_chat` after the agent has already inspected the media itself. It is a second opinion, not a substitute for direct review.

Good prompts are specific and adversarial:

```text
Review these sampled frames from the rendered video. Check for: black frames, garbled text, unreadable subtitles, abrupt transitions, overlay occlusion, weak visual hierarchy, and whether the edit feels like a coherent video rather than a slideshow. Return concrete issues with timestamps/frame references if visible.
```

For reference-style work:

```text
Compare the reference sample and output sample. Focus on pacing, transition timing, shot order, motion density, typography, and overall style similarity. Identify the biggest mismatches.
```

Record any `vision_chat` finding in the final review. If it finds an issue the agent missed, treat that as evidence to revise or explicitly justify why it is acceptable.

## Evidence Template

```markdown
**Perception evidence:**
- `read_video` / 1fps / normal / 0:00-0:30 — identified 5 scene boundaries
- `read_video` / 6fps / large / 0:12.0-0:14.0 — cursor lands at 0:13.2; cut should happen after 0:13.3
- `read_image` / frame 0:18.0 — subtitle is readable and does not cover face
```

## Failure Handling

If required perception tools are unavailable:

1. State the missing tool/server explicitly (perception ships with the
   `qwen-mm-plugins-core` plugin — usually it just needs installing).
2. Do not claim the media was visually reviewed.
3. **Standard degraded mode** (real visual evidence — NOT a `[perception-first]`
   violation, but MUST be disclosed in the project log): extract frames with
   ffmpeg and read them with the agent's native image input —
   `ffmpeg -i IN.mp4 -vf fps=1 frames/f_%04d.jpg` for overview,
   `-ss <t> -vf fps=6 -frames:v 12` re-reads for critical windows, plus
   `scripts/contact_sheet.sh` for full-duration evidence. `transcribe_audio`
   missing ⇒ speech-led edits lose their basis — say so.
4. If not even frame extraction + image reading is possible, stop and ask
   before making content-driven decisions.
