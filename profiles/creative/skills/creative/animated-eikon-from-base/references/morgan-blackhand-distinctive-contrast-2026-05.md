# Morgan Blackhand distinctive eikon — exact fal/GPT Image 2/Kling 3.0 method

This captures the distinctive Morgan Blackhand path Lucas approved after the low-res 48×24 experiment failed. Use this when the goal is not merely a generic animated avatar, but a terminal-readable, identity-preserving, distinctive eikon with strong facial landmarks.

> Historical note: this run used per-state plate files. The current production default is one `canonical_base_plate.png` reused as the start image for all six state videos, to prevent jarring state transitions from mismatched crops/poses.

## Why this branch exists

After testing exact 48×24 source images for Morgan Blackhand, Lucas judged the result bad: “48x24 sucked ass”. The correction was not to lower source resolution further. The real issue was feature distinctiveness and rasterizer readability.

Durable lesson:

- exact low-res source can make video models over-interpret the face and destroy fidelity
- high-res source plates survive better if they are designed as a glyph-survival signal map
- fix value separation and iconic landmarks before spending video credits
- inspect at 48×24, but generate from high-resolution plates

## Toolchain used

- fal.ai Python client for upload, image generation/editing, queue submit, polling, and downloads
- fal model for plates: `openai/gpt-image-2/edit`
- fal model for video: `fal-ai/kling-video/v3/pro/image-to-video` (Kling 3.0 Pro image-to-video)
- `ffprobe` for media receipts
- `ffmpeg` for frame strips/contact sheets and optional ping-pong loops
- `chafa` for 48×24 Braille/terminal preview when available
- Eikon Studio for final bake; do not hand-write `.eikon` unless explicitly requested

## Credentials

Prefer Agent Vault. Never print the key.

```bash
export FAL_KEY="$(agent-vault vault credential get --vault default FAL_AI_API_KEY | tr -d '\n')"
```

Fallbacks used in older sessions were env files such as `~/.hermes/.env` or `/home/lucas/projects/OpenMontage/.env`. If you load from files, source or parse silently and verify only that `FAL_KEY` is set, never echo it.

## Workspace shape

```bash
name="morgan-blackhand-distinctive"
ts=$(date +%Y%m%d-%H%M%S)
work="$HOME/.hermes/eikon-work/${name}-${ts}"
out="$HOME/.hermes/eikons/${name}/source"
mkdir -p \
  "$work/source-input" \
  "$work/bw-plates" \
  "$work/fal-gpt-image-2/payloads" \
  "$work/fal-gpt-image-2/results" \
  "$work/fal-kling/payloads" \
  "$work/fal-kling/queue_submits" \
  "$work/fal-kling/statuses" \
  "$work/fal-kling/results" \
  "$work/fal-kling/videos" \
  "$work/preview" \
  "$out"
cp "$BASE_IMAGE" "$work/source-input/base.png"
```

## Plate generation: fal.ai + GPT Image 2 edit

Use the base image as a strict identity reference and create six high-res square plates. The distinctive fix is not “more detail”; it is fewer, larger landmarks and stronger value separation.

### Core fal call shape

```python
import json, os, time, requests
from pathlib import Path
import fal_client

os.environ["FAL_KEY"] = os.environ["FAL_KEY"]  # already loaded without printing

work = Path(os.environ["WORK"])
base = work / "source-input" / "base.png"
base_url = fal_client.upload_file(str(base))

states = {
    "idle": "cold forward glare, neutral menace, head and shoulders centered",
    "listening": "slight lean-in and head turn, attentive skeptical posture",
    "thinking": "head tilted down slightly, heavy brow, clenched jaw, pensive tension",
    "speaking": "mouth and jaw clearly open as if delivering a short cutting line",
    "working": "focused aggressive posture, sharp scan, high-collar operator silhouette",
    "error": "controlled angry grimace/recoil, subtle glitch shape behind silhouette only",
}

global_prompt = """
Use the supplied image as strict identity reference. Create a terminal eikon source plate optimized for Herm rasterization: high-resolution black/white/very-light-gray poster, pure black background, face with strong value separation and large readable planes. Preserve Morgan Blackhand identity: swept-back hair with bright white front streak, hard brow/eyes, strong nose bridge, beard/jaw block, cigar with small bright ember or bright dot, massive high leather collar silhouette. Make face readable via contrast and clean shapes rather than adding new accessories. Use bold black facial landmarks on bright face planes; keep collar dark with white edge highlights. No tiny hatch noise, no smoky face, no city lights, no scenery, no text, no logos, no HUD. Avatar-only close-up, head and shoulders large in frame.
""".strip()

for state, nudge in states.items():
    prompt = f"{global_prompt}\n\nState: {state}. {nudge}. Keep identity consistent with every other state."
    payload = {
        "image_urls": [base_url],
        "prompt": prompt,
        "image_size": "square",
        "quality": "medium",
        "num_images": 1,
        "output_format": "png",
    }
    (work / "fal-gpt-image-2" / "payloads" / f"{state}.json").write_text(json.dumps(payload, indent=2))
    result = fal_client.subscribe("openai/gpt-image-2/edit", arguments=payload, with_logs=True)
    (work / "fal-gpt-image-2" / "results" / f"{state}.json").write_text(json.dumps(result, indent=2))
    image_url = result["images"][0]["url"]
    data = requests.get(image_url, timeout=120).content
    (work / "bw-plates" / f"{state}_bw_plate.png").write_bytes(data)
    time.sleep(1)
```

Notes:

- `quality: "medium"` was enough for distinctive plates and keeps cost/latency sane; use `high` only if plate fidelity is still insufficient.
- Do not include UI sheets, dashboards, arrows, labels, HUD, city lights, or smoke in the generated plates.
- A tiny warm cigar ember may appear; acceptable if the rasterizer treats it as bright value. If color survives badly, regenerate with “pure white ember/dot, no color”.

## Distinctive prompt deltas that mattered

Bad/vague:

```text
make it higher contrast and more detailed
```

Good/specific:

```text
face with strong value separation and large readable planes; deep black brow/eye sockets; strong nose bridge; mouth slash; beard/jaw block; swept white hair streak; cigar bar plus bright ember dot; massive high black collar with white rim highlights; fewer tiny hatch lines; pure black background; no smoke over face
```

The winning correction was:

- bright face mask/planes
- black brow/eye/nose/mouth slashes
- beard/jaw as one hard dark block
- cigar as a thick clean bar plus dot
- 2–3 big hair highlight chunks, not wispy hair texture
- oversized high-collar silhouette
- clean negative-space background

## Plate QA before Kling spend

Make a contact sheet:

```bash
python3 - <<'PY'
from PIL import Image, ImageDraw
from pathlib import Path
folder=Path('$work/bw-plates')
states=['idle','listening','thinking','speaking','working','error']
imgs=[]
for s in states:
    im=Image.open(folder/f'{s}_bw_plate.png').convert('RGB').resize((240,240))
    imgs.append((s,im))
sheet=Image.new('RGB',(720,560),'white')
d=ImageDraw.Draw(sheet)
for i,(s,im) in enumerate(imgs):
    x=(i%3)*240; y=(i//3)*280
    sheet.paste(im,(x,y+25)); d.text((x+8,y+5),s,fill='black')
sheet.save(folder/'contact_sheet.png')
print(folder/'contact_sheet.png')
PY
```

Preview representative plates at terminal scale:

```bash
chafa --size=48x24 --symbols=braille --colors=none --format=symbols --stretch "$work/bw-plates/idle_bw_plate.png" || true
chafa --size=48x24 --symbols=braille --colors=none --format=symbols --stretch "$work/bw-plates/speaking_bw_plate.png" || true
```

Pass only if face/cigar/collar are readable at thumbnail scale. If it only looks good full-size, regenerate before video.

## Video generation: fal.ai + Kling 3.0 Pro

Upload each plate and use `fal-ai/kling-video/v3/pro/image-to-video`.

### Core queue call shape

Use direct queue/subscribe if wrappers expose stale schemas. The critical field is `start_image_url`, not `image_url`.

```python
import json, os, time, requests
from pathlib import Path
import fal_client

work = Path(os.environ["WORK"])
states = ["idle", "listening", "thinking", "speaking", "working", "error"]

state_prompts = {
    "idle": "Animate as idle: visible but controlled breathing, slight shoulder rise and fall, cold forward glare, calm menace.",
    "listening": "Animate as listening: clear lean-in, small head turn, one visible restrained nod, attentive skeptical posture. No speaking.",
    "thinking": "Animate as thinking: clear slow downward head tilt, heavy brow, tiny jaw clench, then return forward.",
    "speaking": "Animate as speaking: obvious natural mouth and jaw movement like delivering a short cutting line. Mouth opens clearly and closes. No subtitles.",
    "working": "Animate as working: head dips forward slightly, sharp scanning eye-line behind sunglasses, tense jaw, subtle abstract pulse behind silhouette only. No readable code or HUD.",
    "error": "Animate as error/failure: sharp controlled recoil, angry grimace, jaw tightens, subtle glitch around silhouette only, then return to cold glare. Face remains stable and readable.",
}

suffix = """
Short seamless loopable close-up head-and-shoulders terminal avatar animation. Preserve the supplied high-contrast black-and-white plate composition and identity exactly. Make the motion more exaggerated than subtle so it reads at 48x24, but return to the starting pose by the final frame for looping. Locked camera, no cuts, no zooming out, no text, no logos, no subtitles, no HUD, no extra characters. Keep face high contrast and easy to read. Pure black background. Natural controlled motion only.
""".strip()

for state in states:
    plate = work / "bw-plates" / f"{state}_bw_plate.png"
    plate_url = fal_client.upload_file(str(plate))
    payload = {
        "start_image_url": plate_url,
        "prompt": f"{state_prompts[state]}\n\n{suffix}",
        "duration": "3",
        "generate_audio": False,
        "cfg_scale": 0.65,
        "negative_prompt": "blur, distort, low quality, text, logo, subtitle, hud, extra character, camera cut, zoom out, face melting, low contrast, smoky face",
    }
    (work / "fal-kling" / "payloads" / f"{state}.json").write_text(json.dumps(payload, indent=2))

    # subscribe is simplest when available; queue submit/status files are still required receipts.
    result = fal_client.subscribe("fal-ai/kling-video/v3/pro/image-to-video", arguments=payload, with_logs=True)
    (work / "fal-kling" / "results" / f"{state}.json").write_text(json.dumps(result, indent=2))

    video_url = result["video"]["url"] if isinstance(result.get("video"), dict) else result["video_url"]
    data = requests.get(video_url, timeout=300).content
    (work / "fal-kling" / "videos" / f"{state}.mp4").write_bytes(data)
    time.sleep(2)
```

If using explicit queue endpoints, persist:

- `fal-kling/queue_submits/<state>.json`
- `fal-kling/statuses/<state>-<n>.json`
- `fal-kling/results/<state>.json`
- `fal-kling/videos/<state>.mp4`

Never claim a state is done until the MP4 exists and `ffprobe` can read it.

## Looping: ping-pong the raw Kling clips

Kling clips can visibly snap at loop boundaries. For installed state clips, make forward+reverse loops:

```bash
for st in idle listening thinking speaking working error; do
  raw="$work/fal-kling/videos/${st}.mp4"
  fwd="$work/fal-kling/videos/${st}_fwd.mp4"
  rev="$work/fal-kling/videos/${st}_rev.mp4"
  list="$work/fal-kling/videos/${st}_concat.txt"
  loop="$work/fal-kling/videos/${st}_loop.mp4"
  ffmpeg -y -hide_banner -loglevel error -i "$raw" -an -vf "fps=24,scale=1440:1440,format=yuv420p" -c:v libx264 -preset medium -crf 18 "$fwd"
  ffmpeg -y -hide_banner -loglevel error -i "$fwd" -vf reverse -an -c:v libx264 -preset medium -crf 18 "$rev"
  printf "file '%s'\nfile '%s'\n" "$fwd" "$rev" > "$list"
  ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i "$list" -c copy "$loop"
  cp "$loop" "$work/fal-kling/videos/${st}.mp4"
done
```

In the Morgan run this turned ~3.04s raw clips into ~6.08s loopable state clips.

## Media receipts

Probe everything:

```bash
python3 - <<'PY'
import json, subprocess
from pathlib import Path
work=Path('$work')
out={}
for p in sorted((work/'fal-kling'/'videos').glob('*.mp4')):
    if p.stem.endswith(('_fwd','_rev','_loop')):
        continue
    cmd=['ffprobe','-v','error','-show_entries','stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_frames,duration','-show_entries','format=duration,size,format_name','-of','json',str(p)]
    out[p.name]=json.loads(subprocess.check_output(cmd))
(work/'fal-kling'/'media_probe.json').write_text(json.dumps(out,indent=2))
print(work/'fal-kling'/'media_probe.json')
PY
```

Make video strips/contact sheet:

```bash
mkdir -p "$work/preview/strips"
for st in idle listening thinking speaking working error; do
  ffmpeg -y -hide_banner -loglevel error -i "$work/fal-kling/videos/${st}.mp4" -vf "fps=1,scale=240:240,tile=6x1" "$work/preview/strips/${st}_strip.jpg"
done
```

QA for:

- identity stable across frames and states
- face/cigar/collar readable at thumbnail scale
- no text/logos/HUD
- no face melting
- no smoke or glitch covering face
- state motion visible at 48×24
- background remains clean

## Install to Eikon Studio source folder

Back up existing sources and remove state PNGs that can shadow videos:

```bash
target="$HOME/.hermes/eikons/morgan-blackhand-distinctive/source"
ts=$(date +%Y%m%d-%H%M%S)
mkdir -p "$target/backups-$ts" "$target/static-state-backup-$ts"
cp "$target"/* "$target/backups-$ts"/ 2>/dev/null || true
for st in idle listening thinking speaking working error; do
  [ -f "$target/$st.png" ] && mv "$target/$st.png" "$target/static-state-backup-$ts/$st.png"
  cp "$work/fal-kling/videos/${st}.mp4" "$target/${st}.mp4"
done
cp "$work/bw-plates/idle_bw_plate.png" "$target/base.png"
python "$HOME/.hermes/skills/creative/animated-eikon-from-base/scripts/verify_eikon_source.py" "$target"
```

## Final Studio step

Tell Lucas:

```text
Open Herm → Eikon tab → morgan-blackhand-distinctive.
Tune zoom/pan/contrast/invert/symbols in Studio.
Ctrl+S to bake the .eikon and studio.json.
```

Do not say the `.eikon` is baked unless you see Studio wrote it.

## Known scars

- Do not animate the raw cinematic portrait directly; it turns into a ghost/noise eikon.
- Do not “solve” weak face readability with exact 48×24 sources by default; use high-res distinctive plates and inspect at 48×24 instead.
- Do not let state PNGs remain next to MP4s in active source; Studio/source resolution may prefer static PNGs and make states look non-animated.
- If fal balance dies mid-run, label partial/static placeholder states honestly and rerun missing Kling states later. Do not imply all six are animated.
- If wrapper schema fails, use direct fal queue/API with `start_image_url` for Kling 3.0 Pro.
