#!/usr/bin/env python3
"""fal.ai text-to-image CLI — any model, direct API, stdlib only.

Usage:
  python3 fal_txt2img.py --model fal-ai/bytedance/seedream/v4.5/text-to-image \
      --prompt "..." --width 1440 --height 1920 --seed 123 --out ~/Downloads/img.png

Handles both sync results and async request_id polling. Prints image path + seed.
Reads FAL_KEY from the Hermes env file (~/.hermes/.env).
"""
import argparse, json, os, sys, time, urllib.request, urllib.error, ssl

def load_key():
    env_path = os.path.expanduser("~/.hermes/.env")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "FAL_KEY":
                    return v.strip()
    sys.exit("FAL_KEY not found in ~/.hermes/.env")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="fal-ai/bytedance/seedream/v4.5/text-to-image")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--num", type=int, default=1)
    ap.add_argument("--out", default=None, help="Output path (default ~/Downloads/fal_<seed>.png)")
    ap.add_argument("--extra-json", default=None, help="Extra model-specific params as JSON, merged into payload")
    args = ap.parse_args()

    key = load_key()
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}
    ctx = ssl.create_default_context()

    payload = {
        "prompt": args.prompt,
        "image_size": {"width": args.width, "height": args.height},
        "num_images": args.num,
    }
    if args.seed is not None:
        payload["seed"] = args.seed
    if args.extra_json:
        payload.update(json.loads(args.extra_json))

    req = urllib.request.Request(
        f"https://fal.run/{args.model}",
        data=json.dumps(payload).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=300) as r:
            result = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:1500]}")

    # Async fallback: poll if we got a request_id instead of a result
    if "images" not in result and ("request_id" in result or "id" in result):
        rid = result.get("request_id") or result.get("id")
        deadline = time.time() + 600
        while time.time() < deadline:
            time.sleep(2)
            q = urllib.request.Request(
                f"https://fal.run/{args.model}/requests/{rid}", headers=headers)
            with urllib.request.urlopen(q, context=ctx, timeout=30) as r:
                result = json.loads(r.read().decode())
            if result.get("status") == "COMPLETED" or "images" in result:
                break

    imgs = result.get("images", [])
    if not imgs:
        sys.exit(f"No images returned. Response keys: {list(result.keys())}\n{json.dumps(result)[:1200]}")

    seed = result.get("seed")
    url = imgs[0]["url"]
    out = args.out or os.path.expanduser(f"~/Downloads/fal_{seed or int(time.time())}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    urllib.request.urlretrieve(url, out)
    print(f"seed: {seed}")
    print(f"saved: {out}")
    print(f"url: {url}")

if __name__ == "__main__":
    main()
