---
name: fal-ai-generation
description: Generate images, video, and audio via fal.ai Model APIs directly using the user's FAL_KEY — model selection, sync/queue call pattern, LoRA endpoints, pricing. Use when the built-in image_generate tool (gateway-pinned to FLUX 2 Klein) is a poor fit for the brief, when the user asks for a specific fal.ai model, or for anime/stylized/LoRA/upscale/background-removal work on fal.ai.
---

# fal.ai Generation

Direct access to fal.ai's full model catalog (1,000+ models) using the user's own API key. The built-in `image_generate` tool routes through the Nous gateway and is pinned to whatever model the user configured (currently FLUX 2 Klein — a generalist that leans illustration/render, weak for strict anime). For anything model-specific, call fal.ai directly.

## Auth

`FAL_KEY` lives in `~/.hermes/.env` (line `FAL_KEY=...`). Parse it like `~/cheonma/scripts/fal_generate.py` does. Header: `Authorization: Key <FAL_KEY>`.

## Core call pattern (no SDK needed, stdlib only)

1. `POST https://fal.run/<model-id>` with JSON payload (model-specific params).
2. Response is usually the finished result synchronously (image gens ~10–60s). If it returns `request_id` instead, poll `GET https://fal.run/<model-id>/requests/<id>` until `status == COMPLETED`.
3. Result media are CDN URLs under `*.fal.media` — download to `~/Downloads/` (user convention: VisualOutput→SaveToDownloads).
4. Always record and report the returned `seed` for reproducibility.

Use `scripts/fal_txt2img.py` in this skill for text-to-image instead of hand-writing the HTTP each time.

## Workflow

1. **Survey models first** — the user expects a shortlist with a recommendation before rendering, not an immediate generate. Present 3–5 candidates with a one-line why/why-not each (see `references/model-catalog.md`).
2. Confirm or pick the top recommendation, then render.
3. QA the output with vision before presenting; flag missed traits honestly and offer targeted re-rolls (same seed for composition, fresh seed for variety, or batch of 4).

## Model selection (quick map — full notes in references/model-catalog.md)

- **Anime / stylized illustration:** `fal-ai/bytedance/seedream/v4.5/text-to-image` (top pick — excellent multi-trait prompt adherence, ~$0.04/img, ~17s) > Z-Image Turbo (fast/cheap, weaker detail) > Qwen-Image > Nano Banana Pro (polished digital-art lean, less "anime").
- **Anime via LoRA:** `fal-ai/krea-2/turbo/lora` or `fal-ai/flux-lora` with a style LoRA. User's curated LoRA skins (incl. `open-sky-anime`) live in the SKINS dict of `~/cheonma/scripts/fal_generate.py`.
- **Photoreal / flagship:** FLUX.1/2 Pro, GPT-Image 1.5, Imagen 4.
- **Multi-panel layouts / character sheets / structured documents:** Nano Banana Pro (top pick — best instruction-following for complex layouts) > GPT-Image 1.5 (best text) > Seedream 4.5 (cheapest). See `references/character-sheet-model-rankings.md`.
- **Editing:** FLUX Kontext Pro, Nano Banana 2 Edit, Seedream (unified gen+edit).
- **Upscale / bg removal / caption:** SeedVR2, Topaz, ESRGAN / BiRefNet, Bria RMBG / Florence-2.
- **Video / audio:** Veo 3.1, Kling, Sora 2, LTX-2 / Chatterbox, MiniMax Speech, ElevenLabs Music (per-second or per-video billing).
- **Text-to-music (score a video edit):** `fal-ai/elevenlabs/music` via FAL_KEY — no local GPU needed (audiocraft/heartmula need CUDA). Queue endpoint, `force_instrumental`, $0.80/output-minute rounded up. Full schema, pricing, action-sports build→breakdown→drop prompting, and `scripts/fal_music.py` in `references/elevenlabs-music.md`. Generate the track FIRST, then energy-map it (see the `ai-video-generation` skill).

## Model performance for character rendering (session-verified 2026-07)

**Tested models:** FLUX Pro Ultra v1.1, Ideogram V3, Recraft V4, Seedream 4.5, GPT-Image 1.5, Nano Banana Pro, FLUX.2 Pro, Recraft V4 Pro

| Use case | Best model | Why |
|----------|-----------|-----|
| Complex character specs (wings, multi-part anatomy) | **Ideogram V3** | Best prompt adherence — nailed 2-pair wings when others failed |
| Group shots (4+ distinct characters) | **Seedream 4.5** | Only model that kept all 5 characters distinct in one frame |
| Photorealistic portraits | **Recraft V4** or **FLUX Pro Ultra** | Recraft = gritty/cinematic; FLUX = heroic fantasy |
| Anime style | **Seedream 4.5** | By design, excellent cel-shaded aesthetic |
| **Multi-panel character sheets** | **Nano Banana Pro** | Only model delivering ALL panels with clean text + consistency (8/10). See `references/character-sheet-model-rankings.md` |
| Character sheet text/labels | **GPT-Image 1.5** | Best typography (9.5/10), crisp serif labels, no garbling |
| Character sheet budget iteration | **Seedream 4.5** | Cheapest (~$0.03), most complete layout, but text typos + hair inconsistency |

**Character sheet 6-model shootout (2026-07-29):**
1. 🥇 Nano Banana Pro — 8/10 (complete layout, clean text, strong consistency, 25s)
2. 🥈 GPT-Image 1.5 — 7.5/10 (best text, missing eye panel, 52s)
3. 🥉 Seedream 4.5 — 7.5/10 (complete but typos + hair conflicts, 25s)
4. Recraft V4 Pro — 7/10 (garbled label, 3 conflicting sword designs, 24s)
5. FLUX.2 Pro — 6.5/10 (ignored multi-panel brief, only front/back + palette, 34s)
6. Ideogram V3 — 5.5/10 (garbled captions, missing palette/stats, 16s)

**Key insight:** Strong single-image models (FLUX.2 Pro, Ideogram V3) fail at structured multi-panel layouts. Nano Banana Pro's instruction-following is what makes it win for character sheets. Recommended workflow: draft with Seedream (cheap) → finalize with Nano Banana Pro or GPT-Image 1.5.

**Group shot reality:** 5+ distinct characters in one frame is hard for most models. Seedream was the only one that got all 5 identifiable. FLUX and Ideogram dropped to 4 or merged characters. Consider per-character renders + composite if strict accuracy needed.

## Payload format differences (verified endpoints)

Each model uses different parameter names — don't assume uniformity:

```python
# FLUX Pro Ultra v1.1
{"prompt": "...", "image_size": {"width": 1024, "height": 1536}, "num_images": 1, "scheduler": "k_euler"}

# Ideogram V3
{"prompt": "...", "resolution": "1024x1536"}  # string format, not dict

# Recraft V4 / V4 Pro
{"prompt": "...", "image_size": {"width": 1024, "height": 1536}}  # dict format

# Seedream 4.5
{"prompt": "...", "image_size": {"width": 1024, "height": 1536}}  # dict format

# GPT-Image 1.5
{"prompt": "...", "image_size": "1536x1024"}  # STRING, not dict! Only accepts: "1024x1024", "1536x1024", "1024x1536"

# Nano Banana Pro
{"prompt": "...", "image_size": {"width": 1536, "height": 1024}}  # dict format

# FLUX.2 Pro
{"prompt": "...", "image_size": {"width": 1536, "height": 1024}}  # dict format
```

**Endpoint patterns:**
- `fal-ai/flux-pro/v1.1-ultra` ✅
- `fal-ai/ideogram/v3` ✅ (NOT `/v3/text-to-image`)
- `fal-ai/recraft/v4/text-to-image` ✅ (NOT `/v4`)
- `fal-ai/recraft/v4/pro/text-to-image` ✅
- `fal-ai/bytedance/seedream/v4.5/text-to-image` ✅
- `fal-ai/gpt-image-1.5` ✅ — **422 if image_size is a dict; must be string**
- `fal-ai/nano-banana-pro` ✅
- `fal-ai/flux-2-pro` ✅

## Batch rendering workflow

For 10+ images, foreground `execute_code` hits the 300s timeout. Use background process:

```python
# Write script to /tmp, run with background=true + notify_on_complete=true
terminal("python3 /tmp/batch_render.py", background=True, notify_on_complete=True, timeout=600)
```

Typical throughput: ~15-20s per image. 24 images ≈ 6-8 minutes total.

## Troubleshooting Authentication & 403 Errors

When encountering 403 Forbidden errors during image generation:

0. **Read the error body FIRST — a 403 is not always a key problem.** If the JSON
   `detail` reads `"User is locked. Reason: Exhausted balance. Top up your balance
   at fal.ai/dashboard/billing."`, the account BALANCE is empty — the key is valid
   and nothing is misconfigured. Diagnose with a tiny probe (a minimal payload
   returns the JSON detail instantly, no generation cost):
   ```bash
   curl -s -X POST "https://fal.run/fal-ai/bytedance/seedream/v4.5/text-to-image" \
     -H "Authorization: Key $(grep '^FAL_KEY' ~/.hermes/.env | cut -d'=' -f2-)" \
     -H "Content-Type: application/json" -d '{"prompt":"x","num_images":1}'
   ```
   On exhausted balance: don't burn retries (the lock is account-wide and persists
   until billing is resolved at fal.ai/dashboard/billing). Route work elsewhere —
   Suno web UI for music, local ComfyUI/HeartMuLa, or the gateway `image_generate`
   tool. **The gateway `image_generate` bills through the Nous subscription, NOT the
   FAL_KEY balance**, so it keeps working for image work when direct fal.run calls
   are locked. Ask the user to top up before relying on fal.ai again.

1. **Verify API Key Scope**: If the detail is NOT an exhausted-balance lock, ensure
   your FAL_KEY has access to the specific model you're using. Check https://fal.ai/docs/api-reference/platform-apis/authentication for required scopes.

2. **Test Key Validity**: Run this diagnostic command:
   ```bash
   curl -H "Authorization: Key $(grep '^FAL_KEY' ~/.hermes/.env | cut -d'=' -f2-)" https://fal.run/fal-ai/bytedance/seedream/v4.5/text-to-image -I
   ```
   Should return 200 OK. A 403 means the key lacks model access.

3. **Model-Specific Access**: Some models require additional permissions (e.g., "image generation" scope). Check the model's documentation on fal.ai.

4. **Common Fixes**:
   - Regenerate API key with proper scopes
   - Wait 5-10 minutes for key propagation
   - Use fallback models that don't require premium access
   - Check for key expiration (fal.ai keys don't expire but can be revoked)

5. **Debug Workflow**:
   - First: Check `~/.hermes/.env` for valid FAL_KEY
   - Second: Test key with curl command above
   - Third: Try model access verification via browser at https://fal.ai/models
   - Fourth: Consult skill's `references/model-catalog.md` for model-specific permissions

## Character sheet / reference sheet workflow

User keeps prompt templates at `~/character designs/` (original ChatGPT template + fal-optimized version). Test renders go under `~/character designs/model-test-*/` with filenames labeled by model.

**Prompt adaptation for fal.ai models:**
- Front-load layout structure — early tokens carry more weight on fal models
- Convert negation to positive directives ("show X" not "no Y") — Seedream especially mishandles negation
- Use explicit spatial language ("top left", "stacked vertically", "side by side") for panel placement
- Consolidate redundant quality tokens ("8k" + "ultra-high detail" → pick one; dilution hurts)

**Recommended sizes:** Landscape sheet 1536×1024 or 1920×1440; portrait 1440×1920; square 1536×1536.

**3-model comparison test:** Use `scripts/character_sheet_test.py` — renders the same prompt on GPT-Image 1.5, Ideogram V3, and Seedream 4.5 sequentially, saves labeled PNGs to an output dir. Run via background terminal (~2–3 min total).

See `references/character-sheet-prompts.md` for the full original and optimized prompt templates.

## Prompt-Craft Pitfalls (Updated)

- **Body types need explicit weight language**. "Plump" alone collapses to standard anime proportions — write "soft round belly, full hips, thick thighs, plump figure" and avoid hourglass-implying words. (Confirmed: Seedream 4.5 rendered "plump" as merely voluptuous without this.)
- **Multi-trait specificity works on Seedream 4.5** — split-tone hair ("left half jet black, right half snow white") and heterochromia ("one amber-orange eye, one sapphire-blue eye") landed cleanly when spelled out spatially.
- Keep suggestive-but-tasteful phrasing ("draped off shoulders, tastefully hinting at curves") to stay inside safety checkers; Seedream's `enable_safety_checker` defaults true.
- Seedream `image_size` accepts `{"width": W, "height": H}` in the 1280–4096 range per side; ~1440×1920 is a good portrait default (~2.8MP).

## Support files

- `references/model-catalog.md` — condensed fal.ai coverage: top models per category, calling patterns (run/subscribe/submit/stream/realtime), pricing normalization.
- `references/character-sheet-model-rankings.md` — 6-model shootout results for character sheets: per-model QA notes, scores, payload quirks, recommended workflow.
- `references/character-sheet-prompts.md` — original ChatGPT character sheet prompt + fal-optimized variant with model-specific notes and recommended sizes.
- `scripts/fal_txt2img.py` — CLI: `--model --prompt --width --height --seed --out`; handles sync result or request_id polling; downloads image.
- `scripts/character_sheet_test.py` — 3-model comparison runner (GPT-Image 1.5, Ideogram V3, Seedream 4.5) for character sheets; saves labeled PNGs to an output dir.
- `scripts/fal_music.py` — CLI text-to-music via `fal-ai/elevenlabs/music` (queue submit→poll→download): `--prompt --length-ms --out --instrumental --format`. See `references/elevenlabs-music.md`.

## Related skills

Sibling provider umbrellas: `comfyui` (local/cloud ComfyUI pipelines), `higgsfield-generate` (Higgsfield credits/MCP). Route: quick gateway render → built-in image_generate; specific fal.ai model or LoRA → this skill; full pipeline control → comfyui; Higgsfield account features → higgsfield-*.
