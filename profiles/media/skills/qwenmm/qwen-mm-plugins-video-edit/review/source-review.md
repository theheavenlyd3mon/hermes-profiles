# Source Review — See the Material Before Cutting It

Run before content-driven editing decisions. The agent must understand the
source media before cutting, overlaying, grading, generating support assets,
or choosing a visual treatment.

Core perception MCP tools (`read_video`, `read_image`, `visualize`,
`transcribe_audio` — see `mcps/core-perception.md`) are the agent's eyes.
Before claiming a video was inspected, verify the tool is actually registered
in the current runtime. If `read_video` is unavailable, say so — do not
pretend the visual review happened.

## Required technical probe

For every input media file record: absolute path, duration, resolution, FPS,
codec/pixel format, audio stream presence + sample rate + channels, file
size, and known mismatches across files (fps/resolution/sample-rate/codec).
Use `ffprobe`. If probing fails, record the failure — never pretend.

## Required content review

Viewing depth scales with duration:

- **Short video (≤5min):** inspect the whole video at ≥1fps,
  `budget="normal"` or higher. Zoom into text/UI/gesture/transition moments
  with higher fps or larger budget.
- **Reference videos:** broad pass first (structure, style, pacing, shot
  order, key beats), then re-read the moments that drive the edit at higher
  FPS. Before planning, write timestamped reconstruction notes: shot list,
  camera/motion behavior, transitions, on-screen text, layout, typography,
  color, audio/beat cues (`workflows/style-replication.md`).
- **Critical windows:** cuts, gestures, UI changes, fast motion, lip-sync,
  subtitle timing → tight `start_time`/`end_time`, 2–8fps,
  `budget="large"` when detail matters. Record observations with timestamps.
- **Long video (>5min):** sample by windows for an overview, then fully
  inspect the windows the task touches.
- **Speech-led footage:** transcribe when edit decisions depend on speech
  (`craft/audio-first-cutting.md`).

Before planning, know and record: scene/shot boundaries; on-screen text and
UI regions; faces/subjects/focal actions; usable vs unusable stretches;
black frames, silence, stutters, glitches, watermarks, chrome; audio content
and speaker structure when relevant.

## Footage log (multi-clip projects)

For a pile of clips, memory fails as volume grows — build
`<videos_dir>/edit/footage_log.md` before any selection/ordering decision.
Field table, selection order and utilization norms:
`workflows/vlog-multi-source.md` Phase 1-2 (the owning doc).

## Artifact

Record the review in `<videos_dir>/edit/project.md`:

```markdown
## Source Review — YYYY-MM-DD HH:MM
**Inputs:** /abs/path/input.mp4 — 60.0s, 1920x1080, 30fps, h264, audio=yes
**Content understanding:**
- 0:00-0:05 opening title and UI chrome (read_video 2fps, normal)
- 0:12.0-0:14.0 fast transition re-read at 6fps, large budget
**Risks:** browser chrome top; mixed fps with second source
**Implications:** avoid subtitles over lower third; normalize fps at prep
```

## Stop conditions

Stop and ask/report before proceeding if: the file cannot be probed or read;
required perception tooling is unavailable with no equivalent; the media is
not what the user described; required audio is missing; source parameters
make the operation unsafe (e.g. concat with mismatched fps/codecs); the
requested edit would hide key content.
