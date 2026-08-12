#!/usr/bin/env python3
"""Fish Audio TTS command provider for Hermes.

Usage: fish_tts.py <text_path> <output_path> [reference_id] [model]
       fish_tts.py --selftest
Env:   FISH_API_KEY (required, passed via env_passthrough in config.yaml)

Copy to ~/.hermes/scripts/fish_tts.py, chmod +x, and point a
tts.providers.fish command block at it (see references/fish-audio-tts-provider.md).
"""
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
import uuid

API = "https://api.fish.audio/v1/tts"
DEFAULT_MODEL = "s2.1-pro-free"  # $0 tier; switch to s2.1-pro in config for production


def synthesize(text, output_path, reference_id="", model="", fmt="mp3"):
    key = os.environ.get("FISH_API_KEY")
    if not key:
        raise SystemExit("FISH_API_KEY not set")
    body = {"text": text, "format": fmt, "latency": "normal", "normalize": True}
    if reference_id:
        body["reference_id"] = reference_id
    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "model": model or DEFAULT_MODEL,  # Fish takes the model as a header, not a body field
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=55) as r:
            data = r.read()  # ponytail: whole-file read, chunked streaming if TTFA ever matters
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Fish API {e.code}: {e.read()[:300].decode(errors='replace')}")
    if len(data) < 100 or not (data[:3] == b"ID3" or data[0] == 0xFF):
        raise SystemExit(f"unexpected response ({len(data)} bytes): {data[:200]!r}")
    with open(output_path, "wb") as f:
        f.write(data)


def main():
    if sys.argv[1:2] == ["--selftest"]:
        out = os.path.join(tempfile.gettempdir(), f"fish-tts-selftest-{uuid.uuid4().hex[:8]}.mp3")
        synthesize("Fish Audio self test for Hermes.", out)
        assert os.path.getsize(out) > 1000, "suspiciously small audio"
        print(f"OK {out} {os.path.getsize(out)} bytes")
        return
    text_path, output_path = sys.argv[1], sys.argv[2]
    reference_id = sys.argv[3] if len(sys.argv) > 3 else ""
    model = sys.argv[4] if len(sys.argv) > 4 else ""
    with open(text_path, encoding="utf-8") as f:
        synthesize(f.read(), output_path, reference_id, model)


if __name__ == "__main__":
    main()
