# Step 3: Voice Generation

Generate standard Mandarin TTS audio with sentence-level timestamps. Audio and timestamps are produced in a single step — **no Whisper transcription needed**.

## TTS Strategy — DashScope Qwen-TTS (`qwen3-tts-flash`), synthesized per-sentence in parallel

**用 DashScope SDK 调用 Qwen-TTS（`dashscope.MultiModalConversation`，模型 `qwen3-tts-flash`），面向用户交付，音质优先。**

这是面向用户的产品路径：直接用官方 DashScope SDK 调 Qwen-TTS，无需自己部署 TTS 节点、无需拼推理 URL、
无需管理推理服务器。相比本地引擎，Qwen-TTS 的中文自然度、停顿和多音字处理明显更好，适合成品视频。

> **为什么用 `qwen3-tts-flash`（HTTP）而不是 `tts_v2.SpeechSynthesizer`（WebSocket）？**
> `qwen3-tts-flash` 走 HTTP `MultiModalConversation.call`，返回一个音频 URL（WAV，~24h 有效），
> 稳定、无需 WebSocket 通道。`dashscope.audio.tts_v2.SpeechSynthesizer` 走 wss，部分环境的
> 出网策略会拦截 WebSocket 导致 `ConnectionError`。因此这里统一用 HTTP 的 `qwen3-tts-flash`。

**速度与分句准确率如何兼得？** 逐句串行请求会慢，因此这里**按句并发合成**：用线程池同时发起所有
句子的合成请求，再按原顺序把返回的音频拼接起来。整段耗时约等于 *最慢的一句*，而不是所有句子耗时
之和（实测 3 句并发约 1s）。时间戳直接由**每句返回音频的真实时长**测得（不是按字数估算），因此保持
100% 精确的分句时间轴。

- **Official SDK, no self-hosting.** 用 `MultiModalConversation.call(model="qwen3-tts-flash", ...)`，不请求任何自建 `http://.../tts`。
- **Parallel per-sentence.** 线程池并发（默认 8 worker），墙钟时间 ≈ 最慢一句。
- **Accurate timestamps.** 每句时长来自返回音频实测，分句时间轴精确。

Each sentence's exact duration is measured from its returned audio clip, producing both `narration.wav` and `transcript.json` in one pass with 100% accurate timestamps.

## 1. Environment Setup

Install dependencies if not already present:

```bash
pip install dashscope requests soundfile numpy
```

Audio decoding/assembly uses **`soundfile`** (Qwen-TTS returns WAV, which soundfile reads natively — no `pydub`/`audioop`, so this works on Python 3.13). ffmpeg is still needed for the loudness-normalization step below.

**DashScope API key.** The synthesis script (`scripts/generate_voice.py`) reads `DASHSCOPE_API_KEY` itself via `env_config.get_env` — precedence **environment → `~/.qwen-mm-plugins/config` → default**. So set it **either** way:

```bash
export DASHSCOPE_API_KEY="sk-xxx"            # shell-launched setups
# ── or, for GUI-launched harnesses that don't inherit shell exports: ──
echo 'DASHSCOPE_API_KEY=sk-xxx' >> ~/.qwen-mm-plugins/config
```

> **Do NOT `cat`/`echo` the key or paste it into the script** — the script reads it at runtime, so the plaintext key never has to enter the conversation. If synthesis fails with a missing-key error, add the key to the config file above; don't inline it.

**No `sherpa-onnx`, `openai-whisper`, `torch`, `pydub`, or `opencc` dependency.**

## 2. Model & Voice

| Item | Value | Notes |
|------|-------|-------|
| `model` | `qwen3-tts-flash` | HTTP `MultiModalConversation`; returns a WAV URL (~24h validity). |
| `voice` | `Cherry` | System voices: `Cherry` (young female), `Serena` (female, professional), `Ethan` (male), `Chelsie` (female, warm), +40 others. |
| `language_type` | `Chinese` | Specifying the language significantly improves synthesis quality. |

## 3. Prepare Narration Text

Extract plain narration text from `SCRIPT.md` into `narration-script.txt` — strip all markdown headers (`##`), horizontal rules (`---`), and timing annotations (parenthetical notes like `(3-5s)`). Keep only the spoken Chinese text.

## 4. Generate TTS Audio + Timestamps

Run the shipped synthesis script from the project root (the parent of `dist/`):

```bash
EDU_SKILL_ROOT="<absolute directory containing qwen-mm-plugins-edu-agent/SKILL.md>"
python3 "$EDU_SKILL_ROOT/scripts/generate_voice.py" narration-script.txt
```

It synthesizes every sentence concurrently via the DashScope SDK, downloads each clip, then assembles `narration.wav`, `transcript.json`, and `captions.json` in one pass with exact per-sentence timestamps (measured from each returned clip's real duration). **The script reads `DASHSCOPE_API_KEY` itself** (environment → `~/.qwen-mm-plugins/config` → default) — so it works in GUI-launched harnesses, and you never handle the plaintext key. Do not re-author this as an inline snippet; the logic (sentence split, parallel synthesis, duration-measured timestamps) is fixed and tested.

**Flags** (all optional):

| Flag | Default | Notes |
|------|---------|-------|
| `--model` | `qwen3-tts-flash` | HTTP path; returns a WAV URL |
| `--voice` | `Cherry` | Keep one consistent voice per video (`Serena` / `Ethan` / `Chelsie` / ...) |
| `--language` | `Chinese` | Improves synthesis quality |
| `--workers` | `8` | Parallel sentence synthesis; raise to go faster, but stay under the account QPS limit |
| `--pause` | `0.3` | Silence (s) inserted between sentences |
| `--wav` / `--transcript` / `--captions` | `narration.wav` / `transcript.json` / `captions.json` | Output paths |

> **Rate limits:** if failures come in bursts, lower `--workers`. A per-sentence retry (3 attempts) handles transient errors.
>
> **Missing key:** if the script exits with `DASHSCOPE_API_KEY not found`, add it to `~/.qwen-mm-plugins/config` (`DASHSCOPE_API_KEY=sk-...`) or export it.

## 4b. Normalize Audio Volume

Apply EBU R128 loudness normalization using ffmpeg to ensure consistent volume throughout the narration.

```bash
ffmpeg -i narration.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 44100 narration_normalized.wav -y
mv narration.wav narration_original.wav
mv narration_normalized.wav narration.wav
```

## 5. Map Timestamps to Scenes

After generation, map the sentence timestamps to scene boundaries from `SCRIPT.md`. Update `STORYBOARD.md` with actual timing:

```markdown
| Scene | Start | End | Duration |
|-------|-------|-----|----------|
| 开场引入 | 0.0s | 4.2s | 4.2s |
| 题目朗读 | 4.2s | 12.8s | 8.6s |
| 思路分析 | 12.8s | 22.1s | 9.3s |
| 解题步骤一 | 22.1s | 33.5s | 11.4s |
| ...   | ...   | ... | ... |
```

Locate scene boundaries by matching the first sentence of each section in `transcript.json`.

## Quality Check

1. Verify `narration.wav` exists and is non-empty.
2. Verify `transcript.json` has reasonable sentence boundaries (one segment per sentence).
3. If a math term is mispronounced, adjust `narration-script.txt`:
   - Spell out terms more explicitly (e.g., "x的平方" instead of "x平方")
   - Replace unsupported symbols with spoken equivalents
   - Re-run `python3 "$EDU_SKILL_ROOT/scripts/generate_voice.py" narration-script.txt` after adjustments

## Gate

Before proceeding to Step 4:
- [ ] `narration.wav` exists and is non-empty Mandarin audio
- [ ] `transcript.json` exists with sentence-level timestamps (one segment per sentence)
- [ ] `captions.json` exists (same content as transcript.json — original script text with precise timestamps)
- [ ] Caption text matches `narration-script.txt` exactly
- [ ] Scene boundaries mapped with actual timestamps
