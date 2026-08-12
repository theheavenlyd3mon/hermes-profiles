#!/usr/bin/env python3
"""3-model character sheet comparison test.

Renders the same character prompt on GPT-Image 1.5, Ideogram V3, and Seedream 4.5,
saving labeled PNGs to an output directory for side-by-side QA.

Usage:
    python3 character_sheet_test.py --character "description" --outdir ~/character\ designs/model-test-foo
    python3 character_sheet_test.py --prompt-file prompt.txt --outdir ./results

If --character is given, it's inserted into the standard character-sheet template.
If --prompt-file is given, it's used as the full prompt verbatim (overrides template).
"""
import argparse, json, os, sys, time, urllib.request, urllib.error

def load_fal_key():
    env_path = os.path.expanduser("~/.hermes/.env")
    with open(env_path) as f:
        for line in f:
            if line.startswith("FAL_KEY="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("FAL_KEY not found in ~/.hermes/.env")

TEMPLATE = """Professional AAA video game concept art character sheet. Official character design reference document for 3D modeling. Clean flat light gray background. Neutral even studio lighting. Grid layout with labeled sections separated by thin hairline rules.

PANEL LAYOUT (top to bottom, left to right):

TOP LEFT — Information panel with uppercase serif labels: Character Name, Race, Age, Height, Build, Occupation, Alignment. Below it: a 3x3 grid of color palette swatches matching the character's tones.

CENTER (largest area) — Two full-body orthographic views side by side: front view (left) and rear view (right). Character standing upright, arms relaxed at sides. Both views show identical proportions, costume, and equipment.

RIGHT COLUMN — Detail studies stacked vertically with small uppercase labels:
HEAD STUDIES: three portrait busts (frontal, three-quarter, profile)
HAIR DETAIL: two cropped views showing construction, braids, undercut
EYE CLOSE-UP: extreme macro of iris color and shape
WEAPONS: isolated weapon designs in a row (sheathed and drawn)

BOTTOM LEFT — CLOTHING/DETAIL: three square close-up panels showing material textures (collar closure, belt hardware, bracer lacing).

STYLE DIRECTIVES:

Highly realistic fantasy concept art. Digital painting with crisp linework. Muted desaturated color palette. Flat neutral lighting with soft contact shadows only. Static standing pose. Plain background with zero scenery. Production-ready character turnaround. Proportionally consistent panels. Accurate anatomy. Visible construction details: clothing seams, stitching, belts, buckles, material textures, wear marks. Composition matching official Blizzard, Riot Games, CD Projekt Red, or Naughty Dog concept sheets.

CHARACTER:

{character}

QUALITY:

Professional entertainment industry character design. Sharp focus throughout. Every element fully contained within its panel. Clean readable text labels. Pristine presentation."""

MODELS = [
    {"name": "gpt-image-1.5", "endpoint": "fal-ai/gpt-image-1.5",
     "payload_fn": lambda p: {"prompt": p, "image_size": {"width": 1536, "height": 1024}}},
    {"name": "ideogram-v3", "endpoint": "fal-ai/ideogram/v3",
     "payload_fn": lambda p: {"prompt": p, "resolution": "1536x1024"}},
    {"name": "seedream-4.5", "endpoint": "fal-ai/bytedance/seedream/v4.5/text-to-image",
     "payload_fn": lambda p: {"prompt": p, "image_size": {"width": 1920, "height": 1440}}},
]

def call_fal(fal_key, endpoint, payload):
    url = f"https://fal.run/{endpoint}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Key {fal_key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())

def poll_result(fal_key, endpoint, request_id):
    url = f"https://fal.run/{endpoint}/requests/{request_id}"
    for _ in range(60):
        req = urllib.request.Request(url, headers={"Authorization": f"Key {fal_key}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        if data.get("status") == "COMPLETED":
            return data
        if data.get("status") in ("FAILED", "ERROR"):
            raise RuntimeError(f"Failed: {data}")
        time.sleep(3)
    raise TimeoutError(f"Timed out polling {endpoint}/{request_id}")

def download(url, path):
    with urllib.request.urlopen(urllib.request.Request(url), timeout=60) as resp:
        with open(path, "wb") as f:
            f.write(resp.read())

def main():
    parser = argparse.ArgumentParser(description="3-model character sheet comparison")
    parser.add_argument("--character", help="Character description to insert into template")
    parser.add_argument("--prompt-file", help="Full prompt file (overrides template)")
    parser.add_argument("--outdir", required=True, help="Output directory for PNGs")
    args = parser.parse_args()

    if args.prompt_file:
        with open(args.prompt_file) as f:
            prompt = f.read().strip()
    elif args.character:
        prompt = TEMPLATE.format(character=args.character)
    else:
        print("ERROR: provide --character or --prompt-file", file=sys.stderr)
        sys.exit(1)

    fal_key = load_fal_key()
    os.makedirs(os.path.expanduser(args.outdir), exist_ok=True)
    outdir = os.path.expanduser(args.outdir)

    results = {}
    for m in MODELS:
        name = m["name"]
        print(f"\n{'='*50}\nRendering: {name} ...")
        t0 = time.time()
        try:
            resp = call_fal(fal_key, m["endpoint"], m["payload_fn"](prompt))
            if "request_id" in resp and "images" not in resp:
                print(f"  Queued: {resp['request_id']}, polling...")
                resp = poll_result(fal_key, m["endpoint"], resp["request_id"])
            elapsed = time.time() - t0
            img_url = None
            if "images" in resp and resp["images"]:
                img_url = resp["images"][0].get("url")
            elif "image" in resp:
                img_url = resp["image"].get("url") if isinstance(resp["image"], dict) else resp["image"]
            if not img_url:
                results[name] = {"status": "error", "detail": f"No image URL. Keys: {list(resp.keys())}"}
                continue
            out_path = os.path.join(outdir, f"sheet_{name}.png")
            download(img_url, out_path)
            seed = resp.get("seed", "N/A")
            print(f"  Done in {elapsed:.1f}s | seed={seed} | saved: {out_path}")
            results[name] = {"status": "ok", "path": out_path, "seed": seed, "time": f"{elapsed:.1f}s"}
        except Exception as e:
            print(f"  FAILED after {time.time()-t0:.1f}s: {e}")
            results[name] = {"status": "error", "detail": str(e)}

    print(f"\n{'='*50}\nSUMMARY:\n{json.dumps(results, indent=2)}")

if __name__ == "__main__":
    main()
