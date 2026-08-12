---
name: ai-video-editing
description: "Use when assembling AI clips into an edited video."
---

# AI Video Editing & Assembly

## Trigger
Any request to cut, assemble, re-time, or finish a set of (usually AI-generated)
video clips into an edited piece — especially syncing clips to a music track,
adding camera moves, or doing a QA review pass on generated footage. This is the
POST-PRODUCTION phase: it starts after clips exist on disk.

## Companions (other phases live elsewhere)
- Prompt craft / shot direction → `flux3-video-directing`
- Generation mechanics (tools, polling, rate limits) → `video-generation`
- Model routing / prompt engineering → `ai-video-generation`
This skill owns: inventory → beat grid → trim → moves → concat → audio mix → QA → deliver.

## The pipeline
1. **Inventory.** List every clip; note which are originals vs generated takes.
   Where a shot was regenerated, keep BOTH takes and mark the chosen one `FINAL`.
2. **Probe before you plan.** NEVER assume a clip's duration — generated clips are
   often 5.04s, not the round 5/6s you expect. Probe every source (recipe in
   `references/ffmpeg-recipes.md`). Build the beat grid on REAL durations or
   slow-mo/trim math will overshoot.
3. **Map the music.** Run an RMS energy envelope over the track to find drops and
   breakdowns; snap the key visuals to them (the drop hit, the breakdown's
   suspended moment). See `references/ffmpeg-recipes.md` for the analyze pattern.
4. **Trim + apply moves** per shot (Ken Burns push-in/out — recipe below).
5. **Concat** the segments (`-c copy` once they share codec/res/fps).
6. **Mix audio** — `atrim` the track to video length + a fade-out tail.
7. **QA** the assembled cut with `video_analyze` (mandatory prep in
   `references/video-analyze-qa.md` — strip audio and downscale first). For a
   multi-minute film that times out, QA via a keyframe contact sheet instead
   (failure mode 3). Always bright-pixel-check title/text cards (recipe 9).
8. **Deliver** + flag anything the director should rule on (e.g. baked-in
   letterbox bars, a repeated angle).

## Ken Burns / camera moves (the reliable way)
Drive a slow push-in with the **crop filter + the `n` (frame) variable**, then
scale back to the target res. ~15% over the shot reads as a subtle "slow punch-in"
(the feel directors want — "felt, not seen"). Exact recipe + a push-out variant
in `references/ffmpeg-recipes.md`.

```
crop=w='iw/(1+0.15*n/FRAMES)':h='ih/(1+0.15*n/FRAMES)',scale=W:H:flags=lanczos
```
where `FRAMES = duration_seconds * fps`. Apply a move to every shot to kill the
"static AI still" feel; vary direction (push-in for tension, push-out for an
exhale/outro) only on director approval.

## Director-led workflow (this user)
The user has a videography/photography background and DIRECTS the edit himself:
he gives the shot order and the beat map. Your job is to (a) map his calls to the
exact files, (b) surface inferences for confirmation, (c) execute precisely,
(d) flag — not silently fix — creative decisions.

**Editing-language pitfall:** when a director says "cut at the 6-second mark,"
that is the in/out TIMESTAMP, not a 6-second hold. A clip entering the timeline at
3s and cut "at the 6s mark" is a 3-SECOND clip (timeline 3–6s). Confirm any
ambiguous duration-vs-timestamp phrasing before building.

## Pitfalls
- **`zoompan` on a video input multiplies frames** (a 3s clip became 216s). It is
  designed for image→video. For moves on existing video, use the crop+`n` recipe.
- **`crop` has no `t` (time) variable** — expression error. It exposes `n` (frame
  number); drive moves off `n` with `frames = dur*fps`.
- **Assumed durations break slow-mo math.** Probe first; `setpts=k*PTS` over a
  clip longer than you thought overshoots the target.
- **Baked-in letterbox bars** on some generated clips shift aspect ratio mid-edit;
  crop them to match the rest of the frame if the director wants consistency.
  Measure the bars first with `cropdetect` (recipe #8 in ffmpeg-recipes.md).
- **Text-to-video wardrobe drift:** each generation re-rolls clothing color. If a
  jacket must stay one color across cuts, reinforce it explicitly in every prompt
  or anchor with image-to-video; verify each take and regenerate the offenders.

## References
- `references/ffmpeg-recipes.md` — verified commands: probe, crop-based push-in /
  push-out, slow-mo + trim, concat, audio mix with fade, downscale-for-review,
  RMS energy envelope for beat mapping.
- `references/video-analyze-qa.md` — the `video_analyze` failure modes (baked-in
  audio → "audio modality not enabled"; large files → timeout / 413; LONG films →
  timeout even downscaled, use a keyframe contact sheet) and the exact review-copy
  prep that fixes them, plus what to ask the model.
- `references/narrated-film-pipeline.md` — end-to-end flow for a multi-minute
  dialogue-driven film: time the VO first, stills-as-frame-0, cut clips to the
  dialogue timeline (not the reverse), title-card + contact-sheet QA.
