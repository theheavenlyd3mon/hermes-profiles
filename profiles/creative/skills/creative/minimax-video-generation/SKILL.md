---
name: minimax-video-generation
description: Use when generating video with MiniMax H3.
---

# MiniMax H3 Video Generation

Direct access to MiniMax's flagship video model **MiniMax-H3** (launched 2026-07-31, successor to the Hailuo line) using the user's own API key. Open-weight, multimodal, native stereo sound. Ranked #1 video editing / #2 text-to-video / #3 image-to-video (Artificial Analysis). Specs: up to 15s at native 2K, native stereo audio in one pass.

## When to use this vs siblings
- **MiniMax H3 (this skill):** native 2K + stereo sound in one pass, reference-to-video (feed subject images/video/audio), first+last-frame morphs. Strong cinematic motion.
- **fal-ai-generation:** broader model catalog (Veo, Kling, Sora), image gen, LoRA. Note: fal balance was exhausted as of 2026-07 — confirm before routing there.
- **higgsfield-generate:** separate general-creative slate, credits/MCP. Do NOT inject Cheonma palette into video prompts unless the user names the brand.
- **Built-in bfl_flux3_* tools:** first-party Flux 3 (runtime-native). H3 is a separate, parallel option — pick per brief.

## Auth
`MINIMAX_API_KEY` is set in `~/.hermes/profiles/creative/.env` (the active profile's env — this is where the user put it). The script also falls back to `~/.hermes/.env` and the shell env. Bearer auth.
**Region matters — key and host MUST match or you get `invalid api key`:**
- Global: host `https://api.minimax.io` (key from minimax.io platform)
- Mainland China: host `https://api.minimaxi.com` (key from minimaxi.com)
Default to global. Get a key: https://platform.minimax.io → user-center → interface-key. New accounts get starter credits.

## Call pattern (async, like fal.ai's queue)
1. `POST {BASE}/v2/video_generation` with JSON `{model:"MiniMax-H3", content:[...], duration, resolution, ratio?}` → returns `task_id`.
2. Poll `GET {BASE}/v2/query/video_generation/{task_id}` every ~10s. `task.status`: `succeeded` → `task.content.url` is the direct download URL; terminal fails are `failed`/`cancelled`/`expired`.
3. Download the mp4 to `~/Downloads/` (user convention: VisualOutput→SaveToDownloads).

### The `content[]` structure (multimodal)
Each element has a `type` and optional `role`:
- `{"type":"text","text":"..."}` — required; defines content + motion.
- `{"type":"image_url","image_url":{"url":"..."},"role":"first_frame"}` — opening frame (i2v).
- `{"type":"image_url","image_url":{"url":"..."},"role":"last_frame"}` — ending frame.
- `{"type":"image_url","image_url":{"url":"..."},"role":"reference_image"}` — subject reference (also `reference_video` / `reference_audio`).

### The four modes
| Mode | content[] | ratio |
|------|-----------|-------|
| text-to-video (t2va) | text only | **required**, not 'adaptive' (e.g. "16:9") |
| image-to-video (i2va) | text + first_frame | adaptive — omit ratio (set by image) |
| first+last frame | text + first_frame + last_frame | adaptive — omit ratio |
| reference-to-video (r2va) | text + reference_image(s) | adaptive — omit ratio |

### Params
- `duration`: 4–15 (seconds).
- `resolution`: `"2K"` (the public tier). `"768P"` exists but is **closed beta** — contact sales; don't default to it.
- `ratio`: only for t2v. e.g. "16:9", "9:16", "1:1".

## Pricing (pay-as-you-go, 2K)
- Video: **$0.13/sec** (5s ≈ $0.65, 15s ≈ $1.95). 768P would be $0.09/sec but is beta.
- Input audio: free. Input images: first 5 free, then $0.04 each. Input video: billed at output resolution rate.

## Usage
```bash
python3 scripts/minimax_video.py --mode t2v --prompt "..." --ratio 16:9 --duration 5 --out ~/Downloads/h3.mp4
python3 scripts/minimax_video.py --mode i2v --prompt "..." --image https://.../frame.png --duration 5
python3 scripts/minimax_video.py --mode flf --prompt "..." --image https://.../first.png --last-image https://.../last.png
python3 scripts/minimax_video.py --mode ref --prompt "..." --ref https://.../subject.png --ref https://.../style.png
```
Runs submit→poll→download. Poll interval 10s; generation takes minutes — run via background terminal with notify_on_complete for long clips.

## Pitfalls
- **Image inputs must be public URLs** in v1 — the API's `image_url` wants a URL, not a local path. Host local frames somewhere public first (or use MiniMax's file-upload endpoint — not yet wired into the script). Text-only t2v needs no images.
- **ratio is mandatory for t2v and forbidden ('adaptive') for the image modes.** Getting this wrong → 400.
- **Region mismatch = `invalid api key`** — it's almost always host/key region, not a bad key.
- Don't burn retries on a failed task — read `task.error`; content-policy rejections won't succeed on retry.
- Generation is slow (minutes). Poll, don't hammer; 10s interval is the documented recommendation.

## Support files
- `scripts/minimax_video.py` — CLI: submit→poll→download for all four modes. Reads MINIMAX_API_KEY from ~/.hermes/.env.

## Related skills
`fal-ai-generation` (catalog/LoRA/images), `higgsfield-generate` (credits slate), `ai-video-editing` + `ai-video-generation` (assembly/pacing — the user directs edits himself; defer to his eye), `comfyui` (local pipelines; H3 open-weights may run locally later).
