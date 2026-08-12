# QA with video_analyze — required prep

`video_analyze` sends a video to a multimodal model (Gemini) for review. Two
failure modes bit us repeatedly; both are fixed by preparing a review copy first.

## Failure mode 1: "Audio input modality is not enabled for this model"
Triggered when the clip has an audio track (e.g. FLUX 3 bakes audio in by default;
silent originals pass fine). The model can't ingest the audio modality.
**Fix:** strip audio into the review copy: `ffmpeg -i in.mp4 -an -c:v copy review.mp4`.

## Failure mode 2: "Download multimodal file timed out" / HTTP 413 RequestTooLarge
Triggered by large files (>~20MB slow, >~50MB rejected). Retrying the SAME bytes
just loops. **Fix:** downscale to a light copy (`scale=640:-2`, crf 30). If a
specific file keeps timing out while others pass, re-encode it smaller rather than
retrying — that changes what's uploaded.

## The reliable prep (do both)
```bash
ffmpeg -y -v error -i in.mp4 -an -vf "scale=640:-2" -c:v libx264 -crf 32 -preset fast review.mp4
```
Audio-free + tiny. Run reviews in small batches (3–4 parallel); expect occasional
transient download timeouts and retry those individually.

## What to ask the model (per-clip review)
- What happens in it (shot type, action)?
- Wardrobe/color continuity — is the jacket the right color and consistent?
- Morphing / warping / glitches — name the specific elements to watch (board,
  hands, body). For a hero shot, make stability the CRITICAL question.
- Rate usability 1–10 for its intended role in the edit.
- "Be concise" keeps responses usable in batch.

## What to ask on the assembled edit
- List shots in order as they appear (confirms your cut map survived).
- Are the camera moves subtle and smooth, or jarring?
- Are cuts hard and clean? Does pacing build?
- Any broken / morphed / out-of-place shot? (Distinguish deliberate devices like
  powder white-out wipes from real artifacts.)
- Rate overall 1–10.

## Limits to remember
- The model sees SILENT frames even when audio is present — it CANNOT verify music
  sync or sound design. Confirm beat alignment yourself from the cut map + durations.
- It samples a handful of frames; subtle single-frame glitches may be missed.

## Failure mode 3: a LONG film (>~60s) times out even downscaled
`video_analyze` on a multi-minute edit returns "Request timed out" regardless of
size — the model won't process minutes of footage in one call. Don't retry.
**Fix: QA by keyframe contact sheet.** Pull one frame per shot/beat, tile them
into a single grid image, and run ONE `vision_analyze` on the grid. This verifies
era/subject progression, the color-grade arc, and that title cards rendered — the
things that matter for a long film — in a single cheap call.
```bash
# Pull a keyframe at each beat timestamp, small, then tile 4x4
for t in 0.9 8 20 30 40 52 70 90 115 130 152 166 176 188 205 217.5; do
  ffmpeg -y -v error -ss $t -i final.mp4 -frames:v 1 -vf "scale=480:-2" -q:v 5 kf_$t.jpg
done
ffmpeg -y -v error -i kf_*.jpg -filter_complex \
  "[0][1][2][3]hstack=inputs=4[r0];[4][5][6][7]hstack=inputs=4[r1];\
[8][9][10][11]hstack=inputs=4[r2];[12][13][14][15]hstack=inputs=4[r3];\
[r0][r1][r2][r3]vstack=inputs=4,scale=1200:-1" contact_sheet.jpg
```
Ask the model to read the grid in order and report: does each frame match its
intended subject, does the grade progress as designed, and do any title/text cards
show readable text (a blank cell = the text failed to render — see ffmpeg recipe 9).
Note: a single keyframe can land on a transitional moment (dark screen, mid-motion
blur) and look wrong while the clip plays fine — judge the SET, and re-pull a
specific timestamp if one cell looks off.
