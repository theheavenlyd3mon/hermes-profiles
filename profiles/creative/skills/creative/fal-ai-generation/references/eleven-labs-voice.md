# ElevenLabs Voice Pipeline (cross-reference)

**Context:** This session used ElevenLabs for the podcast VO in "The Evolution" short film. The FAL skill covers general API patterns; ElevenLabs has its own quirks worth noting.

## Authentication
- Key: `ELEVEN_LABS_API_KEY` — lives in profile dotenv (`~/.hermes/profiles/creative/.env`), NOT global `~/.hermes/.env`
- Header: `xi-api-key: <KEY>`
- Base: `https://api.elevenlabs.io/v1/`

## Caveat: /v1/user/subscription returns 401
Many standard keys are scope-limited. The endpoint returns 401 Unauthorized. Test TTS endpoints directly — they work fine. This is normal.

## Voice casting for podcast duos
| Role | Voice | Character |
|------|-------|-----------|
| Male anchor (warm, reflective) | George (JBFqnCBsd6RMkjVDRZzb) | Warm British storyteller |
| Female co-host (expressive) | Jessica (cgSgspJ2msm6clMCkdW9) | Playful, bright, warm American |

## VO pipeline (proven)
1. **Cast & write dialogue JSON** with line IDs and speaker tags
2. **Render via ElevenLabs API** (not edge-tts) for personality:
   ```python
   payload = {"text": text, "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": 0.5, "similarity_boost": 0.75,
                                 "style": 0.35, "use_speaker_boost": True}}
   POST /v1/text-to-speech/{voice_id} → audio/mpeg
   ```
3. **Probe durations**: `ffprobe -v error -show_entries format=duration file.mp3`
4. **Build timeline JSON** mapping dialogue start/end to video beats
5. **Assemble**: `ffmpeg -f concat -safe 0 -i concat.txt -c:a libmp3lame -q:a 2 out.mp3`

## Rate considerations
- No public rate limit published; batch rendering works sequentially with ~1s/line
- 1200-char dialogue = ~3:40 spoken, ~$0.36 at standard rates
- Always probe real durations — generated clips vary from targets

## Integration with FLUX 3 workflow
- Generate VO FIRST, measure timeline
- Then generate video clips to match exact beat lengths
- This reverse order (audio→visual) prevents time-stretching artifacts

## Pitfalls
- "no music" in voice_settings is critical — ElevenLabs adds ambience otherwise
- Long monologues (>30s) can drift; chunk into paragraphs
- Male voices with high "style" become preachy; keep style ≤ 0.4