# STT (Speech-to-Text) Quickstart

This file is the practical "just do it" guide. The SKILL.md body documents options;
this file gives exact commands to go from zero to speaking.

## What you need

STT turns your voice messages into text the agent can read. It's the input side.
The output side (TTS — agent speaks back) uses Edge TTS and needs no setup.

Two paths:

| Path | Cost | Latency | Setup |
|------|------|---------|-------|
| **Groq Whisper** | Free (rate-limited) | Fast (cloud GPU) | One API key |
| **faster-whisper (local)** | Free, no API key | Slower on CPU | pip install + model download |

## Quickstart: Groq (recommended, free tier)

```bash
# 1. Set the API key in root .env so all profiles inherit it
#    Append rather than inline to avoid exposing the key:
#    echo "GROQ_API_KEY=gsk_..." >> ~/.hermes/.env

# 2. Switch provider from default (local) to groq
hermes config set stt.provider groq

# 3. Verify
hermes config | grep -A2 "stt:"
# Expect: stt.enabled → true, stt.provider → groq

# 4. Restart
# CLI: exit and relaunch
# Gateway: /restart
```

The config already has `stt.enabled: true` by default on new installs. If it
doesn't, set it: `hermes config set stt.enabled true`.

## Quickstart: local faster-whisper (backup / no cloud)

```bash
# 1. Install into Hermes venv
#    The pip binary may be named pip3 or pip3.11, not pip.
#    Always specify the full version suffix:
~/.hermes/hermes-agent/venv/bin/python3 -m pip install faster-whisper

# 2. Set provider
hermes config set stt.provider local

# 3. Verify model level (tiny/base/small/medium/large-v3)
#    Default is 'base' — good balance for Intel Macs (CPU-only)
hermes config set stt.local.model base
```

### Intel Mac note

faster-whisper runs on Intel Macs via CPU-only mode (no Apple Silicon neural
engine). It works fine for voice messages — just slower than on M-series.
The 'base' model is recommended; 'tiny' is fastest but less accurate, 'small'
is accurate but noticeably slower.

## How to use it once configured

- **CLI**: `/voice on` enters voice-to-voice mode. Speak, I transcribe,
  respond with audio. `/voice tts` makes all replies spoken.
- **Telegram**: Send a voice message — it auto-transcribes via the configured
  STT provider. I read the transcription and reply.
- **Any platform**: Explicit `<voice-message>` attachments are transcribed.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Voice message arrives but I don't react | STT not enabled or wrong provider | Check `hermes config \| grep stt.` — set `stt.enabled: true` and correct provider |
| "No module named faster-whisper" | Not installed in Hermes venv | `cd ~/.hermes/hermes-agent && . venv/bin/activate && pip install faster-whisper` |
| Groq returns error | Key not set, wrong key, or exceeded rate limit | Check `grep GROQ ~/.hermes/.env` |
| `/voice on` does nothing in CLI | The command toggles output too, but STT requires the mic input path — only works if `stt.enabled` is true AND `/voice on` was typed (not just `/voice tts`) | Confirm `stt.enabled: true` first, then use `/voice on` (not `/voice tts`) for bidirectional voice |
| `stt.provider: groq` in config, `GROQ_API_KEY` is set, but STT doesn't work | `openai` Python package missing — Groq STT uses it under the hood as the HTTP client | `~/.hermes/hermes-agent/venv/bin/python3 -c "import openai; print(openai.__version__)"` — if it fails, install: `~/.hermes/hermes-agent/venv/bin/python3 -m pip install openai` |
| Changed `stt.provider` config but still using old provider | Config changes require a full process restart — `/reset` is not enough | CLI: exit and relaunch. Gateway: send `/restart` in the chat |

## Deeper Diagnosis (config looks right, still broken)

When the config and API key both check out but STT still won't fire, the
provider-selection logic in `tools/transcription_tools.py` has specific
guards. Diagnose from most-accessible checks first.

### 1. Check the error log first (fastest signal)

The `_get_provider()` function logs a `logger.warning()` when it rejects a
configured provider — this tells you the exact reason without any imports:

```bash
grep -i "stt\|groq\|transcri" ~/.hermes/profiles/senna/logs/errors.log | tail -10
```

Common messages and their meaning:
```
STT provider 'groq' configured but GROQ_API_KEY not set  →  key missing from os.environ
STT provider 'groq' configured but unavailable            →  openai package not importable
STT is disabled in config.yaml                            →  stt.enabled is false
```
If the log is clean (no matches), STT never tried to activate — likely a
config load issue or the provider auto-detect path.

### 2. Verify the config is readable

`hermes config` doesn't display the `stt:` section in its summary output.
Check the raw config file directly:

```bash
grep -A4 '^stt:' ~/.hermes/profiles/senna/config.yaml
# Expect: enabled: true  /  provider: groq
```

If the profile config has no `stt:` section, check the root config:
```bash
grep -A4 '^stt:' ~/.hermes/config.yaml
```

### 3. Verify the API key in the raw .env file (not process env)

```bash
grep '^GROQ_API_KEY=' ~/.hermes/.env | wc -c
# Expect >20 (key is present and non-empty)
```

**Important:** The error `GROQ_API_KEY not set` can happen even when the
key is in `.env` if the running process started before the key was added.
The `.env` is loaded once at Hermes startup — editing it mid-session has no
effect until restart. Verify by checking for duplicate keys in the file:
```bash
grep -c '^GROQ_API_KEY=' ~/.hermes/.env
# Should be exactly 1. More than 1 means the last one wins.
```

### 4. Check the openai package (Groq STT depends on it)

From a regular terminal (the openai package MUST be in the Hermes venv):
```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "import openai; print(openai.__version__)"
```
If it fails with `ModuleNotFoundError`, install it:
```bash
~/.hermes/hermes-agent/venv/bin/python3 -m pip install openai
```

### 5. Check the env var loading chain (for the running process)

The `echo $GROQ_API_KEY` trick from a subprocess can give FALSE NEGATIVES
— the agent's subprocess does NOT inherit the Hermes CLI's loaded `.env`
vars, so it will always show as empty even when the Hermes process has the
key. Do NOT rely on a bare `echo` to determine if the key is loaded.

Instead, check from within the Hermes venv (this tests the actual
`get_env_value()` path the STT code uses):

```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "
import os
print('in os.environ:', 'GROQ_API_KEY' in os.environ)
"
```

If this returns `True` but STT still doesn't work, the `.env` loading is
fine — move to step 6.

### 6. Trace the provider-resolve path directly

```bash
cd ~/.hermes/hermes-agent
./venv/bin/python3 -c "
import sys; sys.path.insert(0, '.')
from importlib.util import find_spec
from hermes_cli.config import load_config
from tools.transcription_tools import is_stt_enabled, _get_provider

# Check openai availability
print('openai importable:', find_spec('openai') is not None)

# Check stt config
cfg = load_config().get('stt', {})
print('stt config section:', cfg)
print('stt enabled:', is_stt_enabled(cfg))
resolved = _get_provider(cfg)
print('resolved provider:', resolved)
if resolved == 'none':
    print('→ check errors.log for the warning message')
"
```

If `resolved provider` shows `none`, the exact guard that tripped is in
the warning at step 1. If it shows `groq`, the provider resolved correctly
and the issue is downstream (transcription call itself).
