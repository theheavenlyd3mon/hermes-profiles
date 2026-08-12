# Fish Audio as a Hermes TTS provider (verified 2026-08-04)

Session: added Fish Audio to the senna profile as an optional command-type TTS provider. This is the condensed knowledge bank; the runnable script is `templates/fish_tts.py` (deployed live at `~/.hermes/scripts/fish_tts.py`).

## Fish Audio platform facts (docs.fish.audio, 2026-08)

- TTS models: `s2.1-pro` (production, TTFA/DPA guarantees), `s2.1-pro-free` (**same model at $0**, fair-use limits, no guarantees — right choice for assistant chatter/testing), `s2-pro` (open-source SGLang stack, ~100ms TTFA claim), `s1` (legacy, `(paren)` emotion tags).
- S2.x emotion control is free-form natural language in `[brackets]` — not a fixed tag set.
- 83 languages (s2.1-pro), voice cloning (instant from a clip, used via `reference_id`), STT with timestamps, WebSocket realtime streaming.
- Web app extras: Story Studio (multi-speaker long-form audiobook production — relevant to the book-writer pipeline), voice changer, music/SFX, stem separation.

## Integration-blocking quirks

1. **The cloud API is NOT OpenAI-compatible.** `POST https://api.fish.audio/v1/tts` with a custom JSON body; an OpenAI-compatible endpoint is an open feature request (fishaudio/fish-speech#1272). A `base_url` reroute of the built-in `openai` provider does NOT work — this is why the command-provider path was used.
2. **The model is a HEADER, not a body field:** `--header "model: s2.1-pro-free"`. Body carries `text`, `reference_id` (optional), `format`, `latency`, etc.
3. Auth: `Authorization: Bearer <FISH_API_KEY>` from the fish.audio dashboard. Stored in the profile `.env`; the provider config block must list it under `env_passthrough` or Hermes scrubs it from the child env.
4. Response is raw audio bytes (mp3 with `ID3` or `0xFFEx` magic when `format: mp3`). Non-2xx errors come back as JSON bodies — read `e.read()` on HTTPError for the real message (fair-use limit hits surface here).

## Deployed config (senna profile, `tts.provider` left as `openai` until A/B tested)

```yaml
tts:
  providers:
    fish:
      type: command
      command: "python3 ~/.hermes/scripts/fish_tts.py {text_path} {output_path} {voice} {model}"
      model: s2.1-pro-free
      format: mp3
      timeout: 60
      env_passthrough:
        - FISH_API_KEY
```

To activate: `hermes config set tts.provider fish`, then full process restart (provider changes need relaunch, `/reset` is not enough — see Pitfall 4 in SKILL.md). Voice cloning later = set the block's `voice:` to the Fish `reference_id`.

## Verification recipe

```bash
# resolution + env passthrough + template render (the layer that lies)
cd ~/.hermes/hermes-agent && ./venv/bin/python3 -c "
import sys; sys.path.insert(0,'.')
from hermes_cli.config import load_config
from tools.tts_tool import _resolve_command_provider_config, _command_provider_env_passthrough, _render_command_tts_template
cfg = load_config().get('tts', {})
prov = _resolve_command_provider_config('fish', cfg)
print('resolved:', bool(prov), '| passthrough:', _command_provider_env_passthrough(prov))
print(_render_command_tts_template(prov['command'], {'text_path':'/tmp/t.txt','output_path':'/tmp/o.mp3','voice':'','model':prov.get('model','')}))"

# live API proof (needs FISH_API_KEY in env)
FISH_API_KEY=... python3 ~/.hermes/scripts/fish_tts.py --selftest
```

## Related evaluation: hermes-talk plugin (TheSmokeDev/hermes-talk, v0.7.0)

Duplex voice-agent surface for Hermes built on OpenAI Realtime (gpt-realtime-2.1), auth via API key or Codex CLI OAuth (rides a ChatGPT subscription). Not a fit for "speak my replies" — that is the turn-based TTS leg this provider covers. Fish Audio has NO speech-to-speech model, so it cannot replace hermes-talk's duplex layer; its viable roles are (a) this TTSProvider/command slot, (b) voice cloning for a persistent assistant voice, (c) Story Studio for the book pipeline.
