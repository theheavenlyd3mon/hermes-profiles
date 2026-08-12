#!/usr/bin/env python3
"""Text-to-music via fal-ai/elevenlabs/music using the user's FAL_KEY (queue API).

Usage:
  python3 fal_music.py --prompt "upbeat boom-bap lo-fi instrumental..." \
      --length-ms 100000 --out ~/Downloads/track.mp3 [--instrumental]

- Submits to the queue endpoint, polls to COMPLETED, downloads the mp3.
- FAL_KEY is read from ~/.hermes/.env (line FAL_KEY=...).
- Pricing: $0.80 per output audio MINUTE, rounded UP to the nearest minute
  (a 100s generation bills as 2 minutes). Keep length-ms modest while iterating.
- Sync `fal.run` POST works but blocks ~30-90s and can time out the read; the
  queue endpoint is the reliable path.
"""
import argparse, json, time, os, urllib.request, urllib.error

ENDPOINT = "fal-ai/elevenlabs/music"
QBASE = f"https://queue.fal.run/{ENDPOINT}"


def load_key():
    env = os.path.expanduser("~/.hermes/.env")
    with open(env) as f:
        for line in f:
            if line.startswith("FAL_KEY="):
                return line.strip().split("=", 1)[1]
    raise SystemExit("FAL_KEY not found in ~/.hermes/.env")


def submit(key, payload):
    req = urllib.request.Request(
        QBASE, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
    return d["request_id"]


def poll(key, rid, interval=8, timeout=600):
    url = f"{QBASE}/requests/{rid}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        req = urllib.request.Request(url, headers={"Authorization": f"Key {key}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
        st = d.get("status")
        print(f"  [{rid[:8]}] status={st}", flush=True)
        if st == "COMPLETED":
            return d  # contains {"audio": {"url": ...}}
        if st in ("FAILED", "ERROR"):
            print("  FAILED:", json.dumps(d)[:500])
            return None
        time.sleep(interval)
    print("  poll timeout")
    return None


def download(url, path):
    path = os.path.expanduser(path)
    with urllib.request.urlopen(urllib.request.Request(url), timeout=60) as r:
        data = r.read()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  saved {path} ({len(data)//1024} KB)")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--length-ms", type=int, default=100000,
                    help="3000-600000; model picks if omitted")
    ap.add_argument("--out", default="~/Downloads/music_generated.mp3")
    ap.add_argument("--instrumental", action="store_true",
                    help="force instrumental (no vocals)")
    ap.add_argument("--format", default="mp3_44100_128")
    args = ap.parse_args()

    key = load_key()
    payload = {
        "prompt": args.prompt,
        "music_length_ms": args.length_ms,
        "force_instrumental": args.instrumental,
        "output_format": args.format,
    }
    print("Submitting...")
    rid = submit(key, payload)
    print("  request_id:", rid)
    res = poll(key, rid)
    if res and "audio" in res:
        download(res["audio"]["url"], args.out)
        print("DONE")
    else:
        raise SystemExit("generation did not complete")


if __name__ == "__main__":
    main()
