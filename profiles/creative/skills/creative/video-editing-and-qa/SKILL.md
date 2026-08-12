---
name: video-editing-and-qa
description: "Use when assembling/reviewing clips into a finished edit."
---

# Video Editing & QA (Post-Production)

## Trigger
Any task that takes EXISTING clips (AI-generated or source footage) and turns them
into a finished video: reviewing/QA'ing footage, cutting to a music beat grid,
applying subtle motion (Ken Burns / punch-in), mixing audio, concatenating, and
exporting. This is the POST phase — distinct from generating clips (`video-generation`)
and from writing prompts (`flux3-video-directing`). Load those for earlier phases.

## The QA loop (review footage before you commit it to an edit)
Use the `video_analyze` tool (deferred — load via tool_describe/tool_call) to actually
WATCH clips, not guess from filenames. Two gotchas bite every time — see
`references/ffmpeg-video-gotchas.md` for transcripts:

1. **Strip audio first.** FLUX 3 (and most generators) bake an audio track in. Gemini's
   video backend rejects audio with `Audio input modality is not enabled for this model`.
   Fix: `ffmpeg -i in.mp4 -an -c:v copy review.mp4` before analyzing.
2. **Downscale big/oversized files.** Failures `Download multimodal file timed out` and
   `Request body size exceeds maximum` mean the file is too heavy. Fix: make a light
   proxy: `ffmpeg -i in.mp4 -an -vf "scale=640:-2" -c:v libx264 -crf 30 -preset fast proxy.mp4`
   (a few hundred KB). Analyze the proxy.
- Batch reviews in parallel (4 at a time). Transient download timeouts happen — retry
  ONCE; if the same file fails again, re-encode it lighter rather than retrying identical bytes.
- Ask focused questions: what happens / jacket-color continuity / morphing & glitches /
  a 1–10 usability rating for the shot's intended role.

## Continuity across generations (the recurring defect)
Text-to-video re-rolls wardrobe/color on EVERY independent generation — a prompt can
only suggest a color, not lock it. Expect drift (e.g. an "orange-red" jacket coming out
olive or dark on some clips). Fixes, weakest→strongest:
- Reinforce in the prompt: name the color 3×, anchor it ("vivid orange-red like a traffic
  cone"), and add an explicit prohibition ("MUST be orange-red, never green/dark").
- Re-generate the offenders with the reinforced prompt (cheap, usually works for small
  visible areas like sleeves/cuffs).
- Anchor with image-to-video: feed a frame where the color is correct so pixels, not text,
  define the wardrobe. Use this when text reinforcement keeps failing.
QA every clip for the continuity color before assembly; flag mismatches to the user.

## Cutting to a beat grid
1. Get the song's structure first — don't guess. Decode to PCM and run an RMS energy
   envelope to find drops/breakdowns (`scripts/` in the project, or `04_audio/analyze.py`
   pattern: 0.5s windows, normalize, report quietest/loudest windows + sharp onsets).
2. Map one shot per beat. Put the biggest action on the drops, a slow/suspended shot in
   the breakdown, calm shots in the intro/outro. The song's own spine does the pacing.
3. Trim each segment (`-ss` in-point, `-t` duration), concat via a filelist, then lay the
   music under with a fade-out. Template: `templates/build_edit.sh`.

## Subtle motion (Ken Burns / slow punch-in)
Static AI clips feel dead; a very slow push-in (~15%, "feel not see") gives them life.
**Do NOT use `zoompan` on video** — it's image-oriented and multiplies frames per input
frame (a 3s clip becomes 216s). Use a crop-based push driven by frame number `n`
(the crop filter does NOT expose time `t`):
```
crop=w='iw/(1+0.15*n/FRAMES)':h='ih/(1+0.15*n/FRAMES)',scale=W:H:flags=lanczos
```
where FRAMES = duration_seconds × fps. Push IN on most shots; push OUT (invert the sign)
on an outro for an "exhale." Full gotcha transcripts in `references/ffmpeg-video-gotchas.md`.

## Project organization (deliverable hygiene)
For a multi-clip project, organize by numbered purpose folders and document it:
`01_raw_clips/` (ALL clips for user review, clearly named, both takes kept with the chosen
one marked FINAL), `02_final_edits/`, `03_references/`, `04_audio/`, `05_scripts/`,
`_scratch/` (proxies/intermediates), plus a `README.md` (folder map + song structure +
clip inventory + continuity notes). Before deleting any original during a reorg,
md5-verify its organized copy is byte-identical.

## Pitfalls
- Don't review clips by filename — watch them with video_analyze; content and quality
  (morphing!) are invisible otherwise.
- Don't feed generator audio tracks to video_analyze — strip first.
- Don't trust a single text prompt for cross-clip color — QA and reinforce/re-generate.
- Don't use zoompan for video Ken Burns — crop+scale on `n`.
- A clip that morphs at normal speed can read CLEAN when slowed (e.g. 2.4×) with minimal
  rotation — slow-mo is a valid way to rescue a weak aerial for a suspended beat.
- Letterbox bars are sometimes BAKED into a generated take (aspect shifts mid-edit).
  Flag to the user; crop them out if they want frame consistency.
