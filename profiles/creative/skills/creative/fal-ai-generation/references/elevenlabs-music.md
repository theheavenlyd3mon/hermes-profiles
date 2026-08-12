# ElevenLabs Music on fal.ai — text-to-music via FAL_KEY

Verified 2026-07. The cleanest music-rendering path on this setup (no local GPU
needed; audiocraft/heartmula need CUDA). Use it to score multi-clip video edits —
generate the track FIRST, then energy-map it (see the `ai-video-generation` skill's
`references/music-driven-assembly.md` + `scripts/audio_energy_map.py`).

## Endpoint & auth
- Model id: `fal-ai/elevenlabs/music`
- Auth: `Authorization: Key <FAL_KEY>` (FAL_KEY in `~/.hermes/.env`)
- **Use the queue endpoint** `https://queue.fal.run/fal-ai/elevenlabs/music`
  (submit → poll `/requests/<id>` → result has `audio.url`). The sync `fal.run`
  POST works but blocks 30-90s and can time out the read.
- Run `scripts/fal_music.py` instead of hand-writing the HTTP.

## Input schema (probed from the OpenAPI)
| Field | Type | Notes |
|---|---|---|
| `prompt` | str (≤4100) | Text description of the music. |
| `music_length_ms` | int 3000–600000 | Optional; model picks a length if omitted. |
| `force_instrumental` | bool (default false) | Guarantees no vocals when true. Only with `prompt`. |
| `composition_plan` | object/null | Optional section-by-section plan (MusicCompositionPlan → MusicSection[]); `respect_sections_durations` controls strictness. |
| `output_format` | enum (default `mp3_44100_128`) | e.g. `mp3_44100_192` (needs Creator tier), `pcm_48000` (needs Pro). |

Output: `{"audio": {"url": "...mp3", "file_name", "file_size", "content_type"}}`.

## Pricing
**$0.80 per output audio minute, rounded UP.** A 100s track bills as 2 min ($1.60).
Keep `music_length_ms` modest while iterating; ~100s is a good "multiple builds/drops
to choose from" length for a 60-90s edit.

## Prompting for action-sports scoring (build → breakdown → drop)
For a skate/snow/sports commercial you want internal movement, not a flat loop, so
the edit has a spine. Spell out the structure in the prompt:
- "punchy beat drops in immediately at full energy" (no slow intro for full-energy pacing)
- "sustains a groovy head-nod" (the verse/energy section)
- "strips back into a brief DRUMLESS breakdown with just keys and bass" (the slow-mo apex slot)
- "the full beat SLAMS BACK IN harder for a triumphant finale that rides out and fades" (the drop + outro)
Add genre/mood/instrumentation: e.g. "upbeat boom-bap lo-fi hip-hop instrumental,
dusty breakbeat, warm vinyl crackle, jazzy Rhodes, bouncy sub-bass, crisp snare on
2 and 4, golden-hour summer feel. No vocals, purely instrumental."

Two-candidate workflow: render an upbeat boom-bap/lo-fi hybrid AND a warmer chill
lo-fi, both ~100s + `force_instrumental`, and pick by ear.

## Pitfalls
- The fal.ai model page / `llms.txt` sit behind a Vercel bot checkpoint — don't
  scrape them for the schema; probe the OpenAPI at
  `https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=fal-ai/elevenlabs/music`
  or just send a payload and read the validation error.
- `force_instrumental` only works with a `prompt` (not a `composition_plan`).
- Generated audio is never sample-accurate to a planned beat — map the ACTUAL track
  with the energy script, don't trust the prompt's implied timings.
