#!/usr/bin/env python3
"""Describe an image using a vision-capable model via OpenRouter.

Validated workaround for when vision_analyze fails with:
    unknown variant `image_url`, expected `text`
(active/fallback model is text-only — downscaling does NOT fix it).

Usage:
    python3 analyze-image.py --image /path/to/img.jpg
    python3 analyze-image.py --image /path/to/img.jpg --question "Describe the art style"
    python3 analyze-image.py --image /path/to/img.jpg --model openai/gpt-4o-mini --max-tokens 800

Key discovery order: env var OPENROUTER_API_KEY, then
~/.hermes/profiles/creative/.env, then ~/.hermes/.env.
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request

ENV_FILES = [
    os.path.expanduser("~/.hermes/profiles/creative/.env"),
    os.path.expanduser("~/.hermes/.env"),
]


def find_key(name):
    """Return the value of an env key, checking process env then .env files."""
    val = os.environ.get(name, "").strip().strip('"').strip("'")
    if len(val) > 10:
        return val
    for path in ENV_FILES:
        if not os.path.isfile(path):
            continue
        with open(path, "r", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                if k == name:
                    v = v.strip().strip('"').strip("'")
                    if len(v) > 10:
                        return v
    return None


def main():
    ap = argparse.ArgumentParser(description="Vision analysis via OpenRouter")
    ap.add_argument("--image", required=True, help="Path to image file")
    ap.add_argument("--question", default=(
        "Describe this image in meticulous detail for an AI artist: the subject, "
        "art style, medium (photoreal? anime? 3D render? painting? pixel art?), "
        "composition, framing, color palette, lighting, depth of field, texture, "
        "notable rendering techniques. Note any visible text. What mood does it "
        "convey? Be specific and concrete."
    ))
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--max-tokens", type=int, default=800)
    args = ap.parse_args()

    if not os.path.isfile(args.image):
        sys.exit(f"Image not found: {args.image}")

    key = find_key("OPENROUTER_API_KEY")
    if not key:
        sys.exit(
            "No OPENROUTER_API_KEY found (env or " + ", ".join(ENV_FILES) + ")."
        )

    mime = mimetypes.guess_type(args.image)[0] or "image/jpeg"
    with open(args.image, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    payload = {
        "model": args.model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": args.question},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        }],
        "max_tokens": args.max_tokens,
    }

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:1500]}")
    except Exception as e:
        sys.exit(f"Request failed: {e}")

    content = data.get("choices", [{}])[0].get("message", {}).get("content")
    if not content:
        sys.exit("No content in response: " + json.dumps(data)[:1500])
    print(content)


if __name__ == "__main__":
    main()
