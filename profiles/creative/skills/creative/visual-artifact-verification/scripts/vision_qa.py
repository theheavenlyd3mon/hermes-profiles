#!/usr/bin/env python3
"""Vision QA for an image via OpenRouter (fallback when the session's vision model is text-only).

Usage:
    python3 vision_qa.py /path/to/image.png ["QA question"]
    python3 vision_qa.py /tmp/sketch.png "Any overflow, clipping, broken images, cut-off sections? Are all 6 cards visible?"

Reads OPENROUTER_API_KEY from ~/.hermes/.env (or ~/.hermes/profiles/<profile>/.env via --env).
Sends the image as a base64 data URL to openai/gpt-4o-mini and prints the model's answer.
"""
import base64, json, os, sys, urllib.request, urllib.error

DEFAULT_MODEL = "openai/gpt-4o-mini"

def read_key(env_path):
    try:
        for line in open(env_path):
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return None

def vision_qa(path, question, model=DEFAULT_MODEL, env_path=None):
    env_path = env_path or os.path.expanduser("~/.hermes/.env")
    key = read_key(env_path)
    if not key:
        raise SystemExit(f"OPENROUTER_API_KEY not found in {env_path}")
    if not os.path.exists(path):
        raise SystemExit(f"image not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp", "gif": "image/gif"}.get(ext, "image/png")
    b64 = base64.b64encode(open(path, "rb").read()).decode()

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": question},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        ]}],
        "max_tokens": 700,
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
            return d.get("choices", [{}])[0].get("message", {}).get("content") or json.dumps(d)[:1500]
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode()[:1500]}"

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    img = args[0]
    q = args[1] if len(args) > 1 else (
        "Describe this image in detail. Report any visual bugs: text overflow, overlapping or "
        "clipped content, cut-off sections at edges, unstyled elements, broken images. "
        "Then state whether every expected section/component is visible and give an overall legibility verdict."
    )
    print(vision_qa(img, q))
