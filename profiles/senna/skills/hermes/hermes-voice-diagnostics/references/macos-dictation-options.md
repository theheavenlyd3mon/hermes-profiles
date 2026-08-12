# macOS system-wide dictation options (researched 2026-07-27)

Context: user wanted a free/FOSS replacement for Wispr Flow (paid subscription
dictation) on an Intel MacBook Pro (i7-9750H, x86_64). Hermes STT/TTS only works
inside Hermes voice mode — it is NOT a system-wide dictation replacement.

## Apple Silicon requirement kills most polished options

| App | Open source | Intel Mac | Notes |
|---|---|---|---|
| OpenWhispr (openwhispr.com) | yes | YES (explicit) | Local Whisper tiny→turbo, hotkey push-to-talk, works in all apps. Direct Wispr Flow replacement that fits Intel hardware. |
| Dictara (github.com/vitalii-zinchenko/dictara) | yes | yes | Local Whisper or BYO OpenAI key. Smaller project. |
| VoiceInk | yes (GPLv3) | NO — Apple Silicon + macOS 14.4 required | whisper.cpp based, otherwise well-regarded |
| Superwhisper | no | NO — Apple Silicon | local Whisper, paid |
| MacWhisper | no | limited | best modes need Apple Silicon |
| Apple Dictation | n/a (built-in) | yes | free, zero install, weaker accuracy than Whisper, clunky long-form |
| whisper.cpp CLI | yes | yes (CPU/AVX2) | no system-wide integration without glue tooling |

## Hardware reality for local Whisper on Intel

- No CoreML/ANE acceleration. CPU (AVX2) only; whisper.cpp Metal may help on
  models with discrete AMD GPUs.
- Whisper base ≈ real-time on i7-9750H; small ≈ 2-3x slower than speech.
  Usable for dictation, not instant.
- faster-whisper (CTranslate2) and piper-tts both have x86_64 macOS support.
- Fallback for speed: Groq free tier (cloud, Whisper large-v3-turbo) — $0 but
  not FOSS and audio leaves the device.
