#!/usr/bin/env python3
"""generate_voice.py — Step 3 TTS: DashScope Qwen-TTS (qwen3-tts-flash) narration + timestamps.

Synthesizes every sentence of the narration concurrently via the DashScope SDK, then assembles
`narration.wav`, `transcript.json`, and `captions.json` in one pass with exact per-sentence
timestamps (measured from each returned clip's real duration — not estimated).

Why this is a shipped script and not an inline snippet: the DashScope API key is read INSIDE this
script via `env_config.get_env` (precedence: environment > ~/.qwen-mm-plugins/config > default), so

  1. GUI-launched harnesses (Claude desktop / Codex GUI) that don't inherit a shell's exports still
     find the key in the shared config file, and
  2. the plaintext key never has to pass through the calling agent's context / transcript / logs.

NEVER print the key. On a missing key this exits non-zero with an instruction only — no value.

Invoke from the project root (the parent of dist/), same convention as precheck.py:

    python3 scripts/generate_voice.py [narration-script.txt]

Optional flags: --voice --language --model --pause --workers --wav --transcript --captions.
Loudness normalization (ffmpeg loudnorm) is a separate step — see step-3-voice-generation.md §4b.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from env_config import get_env

DEFAULT_BASE_HTTP_API_URL = "https://dashscope.aliyuncs.com/api/v1"


def clean_for_tts(text: str) -> str:
    """Strip parenthetical/quote punctuation TTS shouldn't voice; normalize colon to comma."""
    return re.sub(r"[（）()\"']", "", text).replace("：", "，")


def split_sentences(raw: str) -> list[str]:
    """Split narration into sentences on 。！？, preserving any trailing remainder."""
    parts = re.split(r"(?<=[。！？])", raw)
    sentences = [s.strip() for s in parts if s.strip()]
    remainder = raw
    for s in sentences:
        remainder = remainder.replace(s, "", 1)
    remainder = remainder.strip()
    if remainder:
        sentences.append(remainder)
    return sentences


def main() -> int:
    ap = argparse.ArgumentParser(description="DashScope Qwen-TTS narration + timestamps (Step 3).")
    ap.add_argument(
        "script", nargs="?", default="narration-script.txt", help="narration text file (default: narration-script.txt)"
    )
    ap.add_argument("--voice", default="Cherry", help="Cherry / Serena / Ethan / Chelsie / ...")
    ap.add_argument("--language", default="Chinese", help="language_type hint (improves quality)")
    ap.add_argument("--model", default="qwen3-tts-flash")
    ap.add_argument("--pause", type=float, default=0.3, help="silence between sentences (s)")
    ap.add_argument("--workers", type=int, default=8, help="parallel synthesis workers (mind QPS)")
    ap.add_argument("--wav", default="narration.wav")
    ap.add_argument("--transcript", default="transcript.json")
    ap.add_argument("--captions", default="captions.json")
    args = ap.parse_args()

    # Read the key at call time — env first, then the shared config file. Never echo it.
    api_key = get_env("DASHSCOPE_API_KEY")
    if not api_key:
        print(
            "ERROR: DASHSCOPE_API_KEY not found. Export it in this shell, OR add it to "
            "~/.qwen-mm-plugins/config as `DASHSCOPE_API_KEY=sk-...`. "
            "Do NOT paste the key into the conversation.",
            file=sys.stderr,
        )
        return 1

    try:
        with open(args.script, encoding="utf-8") as f:
            raw = f.read().strip()
    except OSError as e:
        print(f"ERROR: cannot read narration file {args.script!r}: {e}", file=sys.stderr)
        return 1

    sentences = split_sentences(raw)
    if not sentences:
        print(f"ERROR: no narration text found in {args.script!r}", file=sys.stderr)
        return 1

    # Heavy deps imported only after the key/text checks pass, so the guidance above stays cheap.
    import dashscope
    import numpy as np
    import requests
    import soundfile as sf

    dashscope.api_key = api_key
    dashscope.base_http_api_url = DEFAULT_BASE_HTTP_API_URL

    def synth_one(idx_text):
        """Synthesize a single sentence via DashScope; download the WAV. Returns (idx, wav_bytes)."""
        idx, text = idx_text
        clean = clean_for_tts(text)
        for attempt in range(3):  # brief retry for transient network / QPS errors
            try:
                resp = dashscope.MultiModalConversation.call(
                    model=args.model,
                    api_key=dashscope.api_key,
                    text=clean,
                    voice=args.voice,
                    language_type=args.language,
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"[{resp.code}] {resp.message}")
                url = resp.output["audio"]["url"]
                audio = requests.get(url, timeout=60).content
                print(f"  Qwen-TTS [{idx + 1}/{len(sentences)}] {len(audio)} bytes: {text[:25]}...")
                return idx, audio
            except Exception as e:  # noqa: BLE001 — retry any transient failure, re-raise on last
                if attempt == 2:
                    raise
                print(f"  retry {idx} ({attempt + 1}/3): {e}")

    # ── Synthesize all sentences concurrently (wall-clock ≈ slowest single sentence) ──
    clips_bytes = [None] * len(sentences)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for idx, audio in ex.map(synth_one, list(enumerate(sentences))):
            clips_bytes[idx] = audio

    # ── Assemble in order; measure each clip's real duration for exact timestamps ──
    all_samples, sr, transcript, current_time = [], None, [], 0.0
    for text, audio in zip(sentences, clips_bytes):
        data, rate = sf.read(io.BytesIO(audio), dtype="float32")
        if data.ndim > 1:  # collapse to mono if stereo
            data = data.mean(axis=1)
        sr = rate
        duration = len(data) / rate  # measured from the actual audio
        transcript.append({"text": text, "start": round(current_time, 2), "end": round(current_time + duration, 2)})
        all_samples.extend(data.tolist())
        all_samples.extend([0.0] * int(args.pause * rate))
        current_time += duration + args.pause

    sf.write(args.wav, np.array(all_samples, dtype=np.float32), sr, subtype="PCM_16")
    with open(args.transcript, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    with open(args.captions, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    total_dur = transcript[-1]["end"] if transcript else 0
    print(f"\n>>> TTS engine: dashscope qwen-tts ({args.model} / {args.voice})")
    print(
        f">>> Generated {args.wav} ({total_dur:.1f}s) + {args.transcript} + "
        f"{args.captions} ({len(transcript)} segments)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
