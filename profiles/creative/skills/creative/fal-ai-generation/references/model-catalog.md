# fal.ai Model Catalog — Condensed Reference

Researched 2026-07 from fal.ai docs/pricing. Condensed for model selection; check https://fal.ai/models for the live catalog (1,000+ models).

## Calling patterns

- **Direct `run`** — sync HTTP to `fal.run`, result in response. Good for scripts/prototyping.
- **`subscribe`** — queue under the hood, client polls for you. Feels synchronous.
- **Async `submit`** — full queue control: submit → poll status / webhook. Recommended for production/parallel.
- **Streaming** — progressive output (LLM tokens, progress UIs).
- **`realtime()`** — WebSocket, sub-100ms, only on models with explicit realtime endpoints.

Base URLs: sync `https://fal.run/<model-id>`; queue `https://queue.fal.run/<model-id>`. Auth header `Authorization: Key <FAL_KEY>`. Outputs are JSON with CDN media URLs.

## Image generation / editing (top models)

| Model | Endpoint | Notes |
|---|---|---|
| Seedream 4.5 (ByteDance) | `fal-ai/bytedance/seedream/v4.5/text-to-image` | Unified gen+edit; top anime/stylized adherence; ~$0.03–0.04/img |
| Nano Banana 2 / Pro (Google) | `fal-ai/nano-banana-2`, `fal-ai/nano-banana-pro` | Fast / SOTA realism+typography; edit variants at `/edit` |
| FLUX.2 Pro / Flex | `fal-ai/flux-2-pro`, `fal-ai/flux-2-flex` | BFL flagship editing; Flex = typography |
| FLUX.1 [dev] / [schnell] | `fal-ai/flux/dev`, `fal-ai/flux/schnell` | 12B flow transformer; schnell = 4-step fast |
| FLUX + LoRA | `fal-ai/flux-lora` | Custom LoRA weights via URL, `loras: [{path, scale}]` |
| Krea 2 turbo LoRA | `fal-ai/krea-2/turbo/lora` | User's Loratlas skins endpoint (see ~/cheonma/scripts/fal_generate.py) |
| FLUX Kontext Pro | `fal-ai/flux-pro/kontext` | Targeted edits, scene transforms, $0.04/img |
| GPT-Image 1.5 | `fal-ai/gpt-image-1.5` | Strong prompt adherence, composition/lighting fidelity |
| Gemini 3 Pro Image | `fal-ai/gemini-3-pro-image-preview` | = Nano Banana Pro |
| Qwen-Image | `fal-ai/qwen-image` | $0.02/MP |
| Z-Image Turbo | `fal-ai/z-image/turbo` | Tongyi 6B, very fast |
| Ideogram V3 | text-to-image | Exceptional typography, posters/logos |
| Recraft V4 Pro | `fal-ai/recraft/v4/pro/text-to-image` | Design/marketing visuals |
| Grok Imagine | `fal-ai/xai-grok-imagine-image` | xAI editing |
| SANA | `fal-ai/sana` | 4K generation |

## Utility image models

- Upscale: SeedVR2 (`seedvr-upscale-image`), Topaz, ESRGAN (`fal-ai/esrgan`)
- Background removal: BiRefNet (`fal-ai/birefnet`), Bria RMBG 2.0 (licensed-data safe), generic remove-bg
- Caption/VLM: Florence-2 Large (prompt-based vision tasks)
- Face swap: `fal-ai/face-swap`

## Video

Veo 3.1 (audio, $0.4/s), Kling 2.5 Turbo Pro ($0.07/s), Kling O3 (start+end frame), Sora 2 / Sora 2 Pro (audio), LTX-2 19B (img2video+audio), Wan 2.5 ($0.05/s), Ovi ($0.2/video), Stable Video Diffusion. Billed per second or per video.

## Audio / speech / music

Chatterbox TTS, MiniMax Speech-02 HD, Dia TTS (multi-speaker + voice cloning), ElevenLabs Music, Beatoven Music (royalty-free instrumental), Beatoven SFX.

## Pricing shape

- Images: per-image or per-megapixel (normalized to 1MP on pricing page); higher res scales proportionally.
- Video: per output second or per video.
- Some models GPU-time billed. Serverless GPU fleet (H100 from $1.89/h) for custom deployments.

## Session-verified params (Seedream 4.5)

```json
{
  "prompt": "...",
  "image_size": {"width": 1440, "height": 1920},
  "num_images": 1,
  "enable_safety_checker": true
}
```
`image_size` custom range 1280–4096/side; also accepts presets (`portrait_4_3`, `landscape_16_9`, `square_hd`...). Response: `{images: [{url}], seed}` synchronously from `fal.run` (~17s observed).
