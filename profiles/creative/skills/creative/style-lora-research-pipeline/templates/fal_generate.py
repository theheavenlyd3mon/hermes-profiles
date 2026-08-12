#!/usr/bin/env python3
"""Cheonma-style brand-ready FAL LoRA generator for approved skins."""
import argparse, json, os, time, urllib.request, urllib.error, ssl

HERE = os.path.expanduser("~/.hermes/.env")
FAL_KEY = None
with open(HERE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == "FAL_KEY":
            FAL_KEY = v.strip()
            break
if not FAL_KEY:
    raise SystemExit("FAL_KEY not found in ~/.hermes/.env")

HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
API_BASE = "https://fal.run"
CTX = ssl.create_default_context()

SKINS = {
    "crimson-dark-victorian-oil": {
        "trigger": "crimson dark victorian oil style",
        "scale": 1.15,
        "lora": "https://v3b.fal.media/files/b/0a9fd22e/EdJ7fln3ZByCyGZfHo_8K_krea2_lora_step_100.safetensors",
    },
    "dark-victorian-oil": {
        "trigger": "dark victorian oil style",
        "scale": 1.0,
        "lora": "https://v3b.fal.media/files/b/0a9fcfe7/pk2mv-F9ht86CiLZFvWNW_krea2_lora_step_100.safetensors",
    },
    "midnight-blue-gilded": {
        "trigger": "midnight blue gilded style",
        "scale": 1.0,
        "lora": "https://v3b.fal.media/files/b/0a9f9b3f/ZfcixyTk354QkyV7496X0_krea2_lora_step_100.safetensors",
    },
    "open-sky-anime": {
        "trigger": "open sky anime style",
        "scale": 1.0,
        "lora": "https://v3b.fal.media/files/b/0a9fc127/kkePDUsHtvjfX6jztxgFE_krea2_lora_step_100.safetensors",
    },
    "hazy-golden-oilpaint": {
        "trigger": "hazy golden oilpaint style",
        "scale": 1.1,
        "lora": "https://v3b.fal.media/files/b/0a9fa057/IYD3s4RQiQEXDJJKUC1X6_krea2_lora_step_100.safetensors",
    },
}


def submit(prompt, lora, scale, seed=None, width=1024, height=1280):
    payload = {
        "prompt": prompt,
        "loras": [{"path": lora, "scale": scale}],
        "image_size": {"width": width, "height": height},
    }
    if seed is not None:
        payload["seed"] = seed
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/fal-ai/krea-2/turbo/lora", data=data, headers=HEADERS, method="POST"
    )
    with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def poll(request_id, timeout=240):
    deadline = time.time() + timeout
    last = {}
    while time.time() < deadline:
        req = urllib.request.Request(
            f"{API_BASE}/fal-ai/krea-2/turbo/lora/requests/{request_id}",
            headers=HEADERS,
            method="GET",
        )
        with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
            last = json.loads(r.read().decode("utf-8"))
        if last.get("status") == "COMPLETED":
            return last
        time.sleep(1.2)
    return last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skin", required=True, choices=list(SKINS.keys()))
    ap.add_argument("--subject", required=True)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--save-json", default=None)
    args = ap.parse_args()

    skin = SKINS[args.skin]
    prompt = f"{skin['trigger']}, {args.subject}"
    rec = {"skin": args.skin, "subject": args.subject, "prompt": prompt}
    data = submit(prompt, skin["lora"], skin["scale"], seed=args.seed)

    reqid = data.get("request_id") or data.get("id")
    if not reqid:
        rec["error"] = "no request id"
        rec["response"] = data
    else:
        rec["request_id"] = reqid
        rec["seed"] = args.seed
        done = poll(reqid)
        rec["final_status"] = done.get("status")
        rec["used_seed"] = done.get("seed")
        imgs = done.get("images") if isinstance(done.get("images"), list) else []
        rec["image_url"] = imgs[0].get("url") if imgs else None

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(rec.get("image_url") or "")
        print("saved image file path:", args.out)
    if args.save_json:
        os.makedirs(os.path.dirname(args.save_json) or ".", exist_ok=True)
        with open(args.save_json, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        print("saved json:", args.save_json)
    print("image_url:", rec.get("image_url"))
    print("used_seed:", rec.get("used_seed"))


if __name__ == "__main__":
    main()
