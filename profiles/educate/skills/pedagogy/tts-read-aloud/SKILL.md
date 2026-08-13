---
name: tts-read-aloud
description: Use when the user wants text read aloud via TTS.
version: 1.0.0
author: Senna (for educate profile)
license: MIT
platforms: [macos, linux]
tags: [tts, audio, voice, read-aloud, hands-free]
metadata:
  hermes:
    tags: [tts, audio, voice, read-aloud]
    related_skills: [adaptive-teaching, beginner-friendly-writeup]
---

WHENUSE: {UserAsksToReadAloud,ListenWhileWorking,AudioReviewOfPastLesson,VoiceMemo}. ESPECIALLY:{LongDocument,UserMultitasking}.

# TTS Read-Aloud Delivery

Turn written material (lessons, guides, notes, past-session reviews) into spoken audio the user can listen to while working. The durable skill here is two-part: (1) a reliable local synthesis+playback pipeline, and (2) converting written text into a *spoken* script — markdown does not survive being read verbatim.

## Choose the route

1. Check what's configured: `hermes config get voice` and `hermes config get tts`. The voice subsystem supports many providers (openai, edge, elevenlabs, gemini, piper, etc.).
2. If the current session's toolset includes a text-to-speech tool, prefer it — it honours the configured provider.
3. If not (e.g., a TUI session without the tts toolset loaded), use the local pipeline below. edge-tts is free, needs no API key, and has high-quality neural voices.

## Setup (one-time)

```bash
pip3 install edge-tts --quiet --break-system-packages   # macOS system Python: plain `pip` may not exist; --break-system-packages needed on PEP 668 systems
edge-tts --list-voices | grep en-US | head              # pick a voice
```

Voices proven good for long-form narration:

| Voice | Character |
|-------|-----------|
| en-US-AriaNeural | Female — positive, confident; news/novel tone (default pick) |
| en-US-GuyNeural | Male — passionate, news/novel |
| en-US-JennyNeural | Female — friendly, considerate, comfortable |

## Procedure

1. **Gather the material — and check its freshness.** For past-topic reviews: `session_search()` (browse) to list sessions, let the user pick via `clarify`, then read the artifact (session transcript or saved guide file). If the artifact is a technical guide written a while ago, ask whether to refresh it against the current version BEFORE narrating — reading a stale guide aloud locks in outdated info. If refreshing: audit every falsifiable claim in the doc against the actual source at the current version (grep/ripgrep the checked-out install; record CONFIRMED/STALE/CHANGED per claim), update the file, then narrate from the updated version.
2. **Offer a short test first.** Synthesize one sentence, play it, let the user confirm they can hear it *before* generating the full piece:
   ```bash
   edge-tts --voice en-US-AriaNeural --text "Test line." --write-media /tmp/tts-test.mp3
   afplay /tmp/tts-test.mp3   # macOS
   ```
3. **Convert to a spoken script** (see rules below). Never feed raw markdown to the synthesizer.
4. **Generate and play in chunks** using `scripts/tts_read.py` (bundled with this skill): splits into ~3500-char paragraph chunks, synthesizes each to MP3, plays sequentially with progress lines. Run it in the background (`terminal background=true`) so the user isn't blocked; poll for progress if they ask where it is.
5. **Offer scope choice for long material** — full vs. core sections vs. highlights — before generating. ~160 words/min is a good length estimate.

## Spoken-script conversion rules

| Written form | Spoken replacement |
|--------------|--------------------|
| Markdown tables | Prose: "There are three options: first..., second..., third..." |
| Code blocks / config YAML | Describe intent ("you'd set the backend to docker in your config") or skip; never read syntax aloud |
| Headings with symbols (##, ✅, 🥇) | Signposting phrases: "Section two, delegation. The key point is..." |
| URLs, file paths, flag soup | Name them once in plain words or omit; listeners can read the written doc later |
| Commit hashes, version strings, hex IDs | Replace with plain language ("at our current commit") or spell out letter-by-letter — never read raw hex aloud |
| Bullet lists | Full sentences joined with connectives |

Good example: table `{local: development | docker: security | ssh: sandboxing}` → "There are several terminal backends. Local is the default for development. Docker gives you security and reproducibility. And SSH keeps the agent away from your own code."

Bad example: reading "pipe local, docker, ssh, modal, daytona" as a bare list with no context.

## Pitfalls

- **Don't promise audio before the test playback succeeds.** Speakers, volume, and output device vary — the one-sentence test catches all of it.
- **Don't narrate a stale document as-is.** When asked to review an old guide, check whether the system it documents has moved on (versions, renamed flags, relocated paths). Refresh first, read second.
- **Don't read markdown verbatim.** Pipe characters, backticks, and emoji names are noise in audio.
- **afplay is macOS-only.** Linux: `mpv` or `aplay`. Windows: `start` or PowerShell MediaElement. The chunk script's player command is the only OS-specific line.
- **Long single synthesis calls can time out or get monotone.** Chunking at ~3500 chars keeps each call bounded and lets playback start early.
- **The voice subsystem's `use_gateway` setting routes TTS through the gateway** — in sessions without that path, the local pipeline is the dependable route.

## Verification

- Test clip played and user confirmed audibility.
- Reader script prints `▶ part N/M playing` lines as it progresses and `DONE` at the end.
- Ask the user at the end whether pacing/voice worked; adjust voice or speed (`edge-tts --rate=+10%`) for next time.

## Support files

- `scripts/tts_read.py` — chunked narrator: paragraph-split → edge-tts per chunk → sequential afplay with progress. Usage: `python3 scripts/tts_read.py /tmp/narration.txt [--voice en-US-AriaNeural]`. Components (edge-tts synthesis, afplay playback) verified live; adjust CHUNK_SIZE/VOICE as needed.
