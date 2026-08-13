#!/usr/bin/env python3
"""Read a narration script aloud with a selectable TTS provider (macOS).

Usage:
  python3 tts_read.py narration.txt --provider edge      --voice en-US-AriaNeural
  python3 tts_read.py narration.txt --provider openai    --voice nova
  python3 tts_read.py narration.txt --provider elevenlabs --voice <voice_id>
  python3 tts_read.py narration.txt --provider say       --voice Samantha

Providers:
  edge       - free neural TTS (edge-tts package, no API key)
  openai     - gpt-4o-mini-tts via REST (needs OPENAI_API_KEY in env or ~/.hermes/.env)
  elevenlabs - eleven_multilingual_v2 via REST (needs ELEVENLABS_API_KEY; voice_id
               via --voice, ELEVENLABS_VOICE_ID env, or tts config)
  say        - offline macOS `say` fallback (robotic, zero deps)

Chunks text at ~3500 chars, synthesizes each chunk (retry once on failure),
plays sequentially with afplay, prints progress.
"""
import json
import os
import re
import subprocess
import sys

CHUNK_SIZE = 3500
OUT_DIR = "/tmp/tts_chunks"

DEFAULTS = {
    "edge": "en-US-AriaNeural",
    "openai": "nova",
    "elevenlabs": "pNInz6obpgDQGcFmaJgB",  # Rachel (Hermes config default voice_id)
    "say": "Samantha",
}


def load_dotenv_key(name: str) -> str | None:
    """Read KEY=value from ~/.hermes/.env without printing values."""
    if os.environ.get(name):
        return os.environ[name]
    env_path = os.path.expanduser("~/.hermes/.env")
    try:
        for line in open(env_path):
            line = line.strip()
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return None


def chunk_text(text: str) -> list[str]:
    paras = re.split(r"\n\s*\n", text.strip())
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 2 > CHUNK_SIZE and cur:
            chunks.append(cur.strip())
            cur = p
        else:
            cur = (cur + "\n\n" + p).strip()
    if cur.strip():
        chunks.append(cur.strip())
    return chunks


def synth_edge(chunk: str, voice: str, mp3: str) -> None:
    r = subprocess.run(
        ["edge-tts", "--voice", voice, "--text", chunk, "--write-media", mp3],
        capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"edge-tts failed: {r.stderr[:300]}")


def synth_openai(chunk: str, voice: str, mp3: str) -> None:
    key = load_dotenv_key("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY not found (env or ~/.hermes/.env)")
    payload = json.dumps({
        "model": "gpt-4o-mini-tts",
        "input": chunk,
        "voice": voice,
        "response_format": "mp3",
    })
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "120", "-X", "POST",
         "https://api.openai.com/v1/audio/speech",
         "-H", f"Authorization: Bearer {key}",
         "-H", "Content-Type: application/json",
         "-d", payload, "-o", mp3],
        capture_output=True, text=True, timeout=140)
    if r.returncode != 0 or not os.path.exists(mp3) or os.path.getsize(mp3) < 100:
        err = open(mp3, errors="replace").read()[:300] if os.path.exists(mp3) else r.stderr[:300]
        raise RuntimeError(f"openai TTS failed: {err}")


def synth_elevenlabs(chunk: str, voice: str, mp3: str) -> None:
    key = load_dotenv_key("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY not found (env or ~/.hermes/.env)")
    if voice == DEFAULTS["elevenlabs"] and os.environ.get("ELEVENLABS_VOICE_ID"):
        voice = os.environ["ELEVENLABS_VOICE_ID"]
    payload = json.dumps({"text": chunk, "model_id": "eleven_multilingual_v2"})
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "120", "-X", "POST",
         f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
         "-H", f"xi-api-key: {key}",
         "-H", "Content-Type: application/json",
         "-d", payload, "-o", mp3],
        capture_output=True, text=True, timeout=140)
    if r.returncode != 0 or not os.path.exists(mp3) or os.path.getsize(mp3) < 100:
        err = open(mp3, errors="replace").read()[:300] if os.path.exists(mp3) else r.stderr[:300]
        raise RuntimeError(f"elevenlabs TTS failed: {err}")


def synth_say(chunk: str, voice: str, mp3: str) -> None:
    aiff = mp3 + ".aiff"
    r = subprocess.run(["say", "-v", voice, "-o", aiff, chunk],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"say failed: {r.stderr[:200]}")
    os.replace(aiff, mp3)  # afplay handles aiff fine under any extension


SYNTH = {"edge": synth_edge, "openai": synth_openai,
         "elevenlabs": synth_elevenlabs, "say": synth_say}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    provider = "edge"
    voice = None
    if "--provider" in sys.argv:
        provider = sys.argv[sys.argv.index("--provider") + 1]
    if "--voice" in sys.argv:
        voice = sys.argv[sys.argv.index("--voice") + 1]
    if provider not in SYNTH:
        sys.exit(f"Unknown provider '{provider}'. Choose: {', '.join(SYNTH)}")
    voice = voice or DEFAULTS[provider]

    text = open(path, encoding="utf-8").read()
    chunks = chunk_text(text)
    os.makedirs(OUT_DIR, exist_ok=True)
    words = sum(len(c.split()) for c in chunks)
    print(f"Provider: {provider} | Voice: {voice} | {len(chunks)} chunks | ~{words/160:.0f} min", flush=True)

    tag = f"{provider}-{voice}".replace(" ", "_")
    for i, chunk in enumerate(chunks, 1):
        mp3 = f"{OUT_DIR}/{tag}-part-{i:02d}.mp3"
        ok = False
        for attempt in (1, 2):
            try:
                SYNTH[provider](chunk, voice, mp3)
                ok = True
                break
            except Exception as e:
                print(f"  [chunk {i}, try {attempt}] FAILED: {e}", flush=True)
        if not ok:
            print(f"  ✗ skipping chunk {i} after 2 failures", flush=True)
            continue
        print(f"  ▶ part {i}/{len(chunks)} playing ({len(chunk)} chars)...", flush=True)
        subprocess.run(["afplay", mp3], check=True)
    print("DONE — finished reading.", flush=True)


if __name__ == "__main__":
    main()
