#!/usr/bin/env python3
"""MiniMax H3 video generation — submit -> poll -> download.

Reads MINIMAX_API_KEY from ~/.hermes/.env. Global host by default;
set MINIMAX_API_HOST=https://api.minimaxi.com for a mainland key.

Modes:
  t2v  text-to-video            (requires --ratio)
  i2v  image-to-video           (requires --image as first frame)
  flf  first + last frame       (requires --image and --last-image)
  ref  reference-to-video       (one or more --ref images)

Examples:
  minimax_video.py --mode t2v --prompt "..." --ratio 16:9 --duration 5 --out ~/Downloads/h3.mp4
  minimax_video.py --mode i2v --prompt "..." --image https://.../frame.png --duration 5
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

ENV_FILES = [
    os.path.expanduser("~/.hermes/profiles/creative/.env"),  # active profile
    os.path.expanduser("~/.hermes/.env"),                     # global fallback
]


def load_key():
    key = os.environ.get("MINIMAX_API_KEY")
    if key:
        return key.strip()
    for env_file in ENV_FILES:
        if not os.path.exists(env_file):
            continue
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("MINIMAX_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("MINIMAX_API_KEY not found in env or " + ", ".join(ENV_FILES))


def http_json(url, key, payload=None, method=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        sys.exit(f"HTTP {e.code} from {url}\n{body}")


def build_content(args):
    content = [{"type": "text", "text": args.prompt}]
    if args.mode == "i2v":
        if not args.image:
            sys.exit("i2v requires --image (first frame URL)")
        content.append({"type": "image_url", "image_url": {"url": args.image}, "role": "first_frame"})
    elif args.mode == "flf":
        if not (args.image and args.last_image):
            sys.exit("flf requires --image and --last-image URLs")
        content.append({"type": "image_url", "image_url": {"url": args.image}, "role": "first_frame"})
        content.append({"type": "image_url", "image_url": {"url": args.last_image}, "role": "last_frame"})
    elif args.mode == "ref":
        if not args.ref:
            sys.exit("ref requires at least one --ref URL")
        for u in args.ref:
            content.append({"type": "image_url", "image_url": {"url": u}, "role": "reference_image"})
    return content


def main():
    p = argparse.ArgumentParser(description="MiniMax H3 video generation")
    p.add_argument("--mode", required=True, choices=["t2v", "i2v", "flf", "ref"])
    p.add_argument("--prompt", required=True)
    p.add_argument("--image", help="first-frame image URL (i2v, flf)")
    p.add_argument("--last-image", help="last-frame image URL (flf)")
    p.add_argument("--ref", action="append", help="reference image URL (ref); repeatable")
    p.add_argument("--duration", type=int, default=5, help="seconds, 4-15 (default 5)")
    p.add_argument("--resolution", default="2K", help="2K (public) | 768P (closed beta)")
    p.add_argument("--ratio", help="aspect ratio for t2v only, e.g. 16:9 (required for t2v)")
    p.add_argument("--out", default=os.path.expanduser("~/Downloads/minimax_h3.mp4"))
    p.add_argument("--poll", type=int, default=10, help="poll interval seconds (default 10)")
    args = p.parse_args()

    if args.mode == "t2v" and not args.ratio:
        sys.exit("t2v requires --ratio (e.g. 16:9); it cannot be 'adaptive'")

    key = load_key()
    base = os.environ.get("MINIMAX_API_HOST", "https://api.minimax.io").rstrip("/")

    payload = {
        "model": "MiniMax-H3",
        "content": build_content(args),
        "duration": args.duration,
        "resolution": args.resolution,
    }
    if args.mode == "t2v":
        payload["ratio"] = args.ratio

    print(f"Submitting {args.mode} task to {base} ...", flush=True)
    resp = http_json(f"{base}/v2/video_generation", key, payload)
    task_id = resp.get("task_id")
    if not task_id:
        sys.exit(f"No task_id in response: {json.dumps(resp)[:500]}")
    print(f"task_id = {task_id}", flush=True)

    query_url = f"{base}/v2/query/video_generation/{task_id}"
    while True:
        time.sleep(args.poll)
        task = http_json(query_url, key).get("task", {})
        status = task.get("status")
        print(f"status: {status}", flush=True)
        if status == "succeeded":
            url = task["content"]["url"]
            break
        if status in ("failed", "cancelled", "expired"):
            sys.exit(f"Task did not succeed: status={status} error={task.get('error')}")

    out = os.path.expanduser(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    print(f"Downloading -> {out}", flush=True)
    urllib.request.urlretrieve(url, out)
    print(f"DONE: {out}")


if __name__ == "__main__":
    main()
