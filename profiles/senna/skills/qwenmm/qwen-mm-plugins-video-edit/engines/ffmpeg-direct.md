# FFmpeg — Prep & Finishing Engine

FFmpeg is the deterministic engineering engine for **preparing footage and
finishing deliverables**. Designed deliverables are assembled in HyperFrames
(see `hyperframes.md`); FFmpeg owns everything before and after that.

## Best For

- Probing (`ffprobe`) and technical QA
- Golden-segment extraction; re-encode for frame-accurate seeking
- Per-clip bounded color correction (`craft/footage-grading.md`)
- Audio extraction, mixing, ducking, loudness work (`craft/sound-mix.md`)
- Subtitle burn-in after timing is final
- Format/codec conversion, speed changes, crop/scale/pad
- Mechanical-only deliverables (exact trims, conversions — no design)

## Not For

- Assembling watchable designed deliverables (montages, vlogs, promos) —
  concat+xfade timelines read as slideshows; hand off to HyperFrames
- Titles, kinetic text, PiP choreography, masks, designed transitions

Use HyperFrames (via the handoff protocol) for those.

## Environment Requirements

Required binaries:

- `ffmpeg`
- `ffprobe`

Install examples:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

Verify:

```bash
ffmpeg -version
ffprobe -version
```

Probe an input:

```bash
ffprobe -v quiet -print_format json -show_format -show_streams /abs/path/input.mp4
```

If either binary is missing, report the blocker and do not pretend an FFmpeg operation was tested.

## Cheap-Probe Patterns

Before full execution:

- Test trims on a short range and inspect first/last frames
- Test filter chains on ~3 seconds
- Test subtitle burn-in on one caption window
- Test crop/scale with a single frame or very short clip
- Test every transition recipe on a tiny two-clip sample before applying it to the full timeline
- After concat/crossfade, sample seam windows (±0.5s) before continuing downstream

## Common Pitfalls

- `-ss` before `-i` is fast but keyframe-imprecise; after `-i` is slower but more accurate
- `-c copy` is lossless but cannot apply filters and may cut only at keyframes
- Concat demuxer requires matching codec, resolution, fps, timebase, and audio parameters
- Normalize ALL clips to the single delivery resolution/fps once, at prep re-encode — mixed-resolution sources cover-cropped at assembly time produce a different effective zoom per shot (the "picture breathes at every cut" defect); an upscaled low-res clip also reads as a sudden softness change
- **Keep the audio track at prep re-encode** (`-c:a aac`, never `-an`) — natural sound is edit material for the two-track mix; stripping it at extraction produces a silent deliverable (`[audio-preserved]`)
- Audio and video stream durations may differ; check before concat
- Subtitle burn-in should happen after timing/crop/scale decisions are final
- Filter order matters: crop/scale before subtitle burn-in; color grade before final text only when text is rendered separately later
- Re-encoding can shift colors; compare representative frames when fidelity matters
- Bad subtitle/font encoding can show as mojibake or tofu boxes; verify text-bearing frames, especially CJK text and punctuation
- Crossfade/xfade offsets are easy to miscompute; wrong offsets create hard cuts, flash frames, or black frames
- Missing stream mapping (`-map`) can silently drop audio or subtitles
- Mixed pixel formats or alpha overlays can produce black backgrounds where transparency was expected

## Low-Level Failure Checks

These are cheap, common, and unacceptable in final delivery:

| Problem | Typical Cause | How to Judge |
|---------|---------------|--------------|
| Mojibake / garbled subtitles | wrong subtitle encoding, missing font, wrong ASS escaping | inspect text-bearing frames; for CJK verify actual glyphs, not boxes |
| Black frames | bad trim range, wrong xfade offset (must be A_duration - fade_duration), failed decode, blank generated segment | `scripts/black_check.sh` on the output (exit 2 = interior black); then sample the flagged seam windows |
| Harsh transition | wrong transition duration/offset, no motivated motion, audio not crossfaded | inspect ±0.5s around seams and listen for clicks/pops |
| Audio dropped | missing `-map`, mux mistake, filter_complex output not mapped | ffprobe output stream list; audio stream must exist when expected |
| Duration drift | mismatched audio/video durations, concat parameter mismatch | compare expected duration with ffprobe duration |

## Output Verification

After producing output:

- ffprobe output file
- Confirm duration, fps, resolution
- Confirm audio stream when expected
- Inspect frames near cuts, subtitle moments, first frame, and ending
- For concat/crossfade, inspect seam windows ±0.5s
- Specifically check for mojibake/tofu text, black frames, hard/flash transitions, dropped audio, and unexpected duration drift
- Record evidence in checkpoint/final review
