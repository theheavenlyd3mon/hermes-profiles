---
name: qwen-mm-plugins-omni-av
description: "Omni-model audio/video understanding MCP tools: segmented captioning with timestamps, ASR (plain / controllable-granularity / multi-speaker diarized), temporal grounding (locate a segment by text query), and event/action counting. Use for questions about WHAT is said/happens in an audio or video file and WHEN, on clips up to a few minutes."
---

# Qwen-MM-Plugins Omni-AV

You have `qwen-mm-plugins-omni-av` MCP tools. They call the **Qwen-Omni** model, which reads the
video frames **and** the embedded audio track together, so one call can reason over both. Prefer
these tools over manual ffmpeg/ffprobe scripting.

Check the `qwen-mm-plugins-omni-av` tools in your tool list for full schemas and parameters.

## When to Use Which Tool

- **Transcribe speech, plain text** → `omni_asr` (one continuous string, no timestamps).
- **Transcribe with timestamps** → `omni_asr_timestamped` (`granularity` = `sentence` or `word`;
  also returns SRT).
- **Who said what** → `omni_multi_speaker_asr` (diarization: speaker labels + timestamps + SRT;
  pass `num_speakers` if known).
- **Describe the content over time** → `omni_av_caption` (splits into spans, one description +
  start/end per span).
- **Find WHEN something happens** → `omni_av_grounding` (natural-language `query` → matching time
  segments). Temporal localization.
- **Count how many times** an event/object/action occurs → `omni_av_counting` (`target` → total +
  per-occurrence timestamps).
- **Analyze / caption a music track** → `omni_music_caption` (whole-track tags —
  genre / moods / instruments / key / time signature / vocal profile — plus a dense English
  caption for music generation; audio-only, no timestamps).

Every tool takes a local audio/video `file_path` (or an http/OSS URL) and supports `dry_run=true`
to preview the request without calling the API. The AV tools (`caption`/`grounding`/`counting`)
accept `fps` and `max_pixels` to trade temporal/spatial detail against token cost.

## Relationship to other capabilities (do NOT overlap)

- **`omni_asr*` vs core `transcribe_audio`**: core's `transcribe_audio` uses the dedicated
  qwen3-asr-flash service (fast, chunks long files, 27 languages). The `omni_asr*` tools here use the
  Omni model — pick them when you want Omni's understanding (multi-speaker diarization, controllable
  word/sentence granularity, or transcription fused with visual context). For a straight, long-file
  transcription, core's `transcribe_audio` is cheaper.
- **`omni_av_grounding` (temporal, WHEN) vs core `grounding` (spatial, WHERE)**: this tool locates a
  span in *time*; core's `grounding` draws a bounding box in a single *image*. They are different
  axes — don't substitute one for the other.
- **Long videos (30 min+)**: for whole-video QA over long content, use the
  `qwen-mm-plugins-video-memory` skill (hierarchical graph memory) instead of feeding the entire file
  to these per-call tools. These tools target clips up to a few minutes.

## Tips

- **Cost/latency**: sending video samples frames — raise `fps` only for fast or frequent events;
  keep `max_pixels` at the default (≈448²) unless fine visual detail matters. ASR-family tools send
  only the audio track (the video's audio is extracted first), so they are cheaper on video input.
- **Timestamps** are in seconds from the start of the media.
- **Language**: pass `language` as a hint (e.g. `zh`, `en`) for the ASR/caption tools when known;
  otherwise the model auto-detects.
- Requires `DASHSCOPE_API_KEY`. Default model `qwen3.5-omni-plus`; override per call with `model`.
