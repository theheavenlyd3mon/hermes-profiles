# Video Generation Models — 2026 Landscape

Last updated: May 2026. Research from Atlas Cloud, Scenario, Spheron, WhiteFiber, ComfyUI docs.

## Open-Source Models (run locally via ComfyUI)

| Model | Params | Min VRAM | Quality | Speed | Modes | License |
|-------|--------|----------|---------|-------|-------|---------|
| **Wan 2.2 5B Hybrid** | 5B | ~8 GB | Very Good | Fast | T2V + I2V (single model) | Apache 2.0 |
| **Wan 2.2 14B T2V** | 14B | ~80 GB | Excellent | ~10min | T2V | Apache 2.0 |
| **Wan 2.2 14B I2V** | 14B | ~80 GB | Excellent | ~10min | I2V | Apache 2.0 |
| **Wan 2.1 T2V-14B** | 14B | ~40-80 GB | Excellent | ~4-12min | T2V | Apache 2.0 |
| **LTX-Video 2.3** | - | ~24-32 GB | Good | Very Fast | T2V, I2V | - |
| **HunyuanVideo** | 13B+ | ~60-80 GB | Best OSS | ~20min | T2V | - |
| **AnimateDiff v3** | - | ~18-24 GB | Decent | ~30-60s | T2V (short) | - |
| **CogVideoX-1.5-5B** | 5B | ~16-24 GB | Good | ~5min | T2V | - |

## Wan 2.2 Deep Dive (Recommended)

MoE (Mixture of Experts) architecture with high-noise and low-noise expert models.

### Models (from Comfy-Org/Wan_2.2_ComfyUI_Repackaged)

**5B Hybrid (TI2V) — consumer GPU sweet spot:**
```
wan2.2_ti2v_5B_fp16.safetensors          # Diffusion model (~10 GB)
umt5_xxl_fp8_e4m3fn_scaled.safetensors   # Text encoder (shared with 2.1)
wan2.2_vae.safetensors                   # VAE
```
- Single model handles both T2V and I2V
- ~8 GB VRAM with native offloading
- Enable Load Image node for I2V mode

**14B T2V — MoE dual-pass:**
```
wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors
wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors
umt5_xxl_fp8_e4m3fn_scaled.safetensors
wan_2.1_vae.safetensors
```

**14B I2V — MoE dual-pass:**
```
wan2.2_i2v_high_noise_14B_fp16.safetensors
wan2.2_i2v_low_noise_14B_fp16.safetensors
umt5_xxl_fp8_e4m3fn_scaled.safetensors
wan_2.1_vae.safetensors
```

### Capabilities
- Cinematic-level aesthetic control (lighting, color, composition)
- Professional camera language support (dolly, pan, crane, orbit, tracking)
- Complex motion handling with enhanced controllability
- LoRA support (character consistency across videos)
- First/last frame interpolation (FLF2V)
- Chinese + English text generation in video

### Camera Language Prompts
Wan 2.2 understands cinematic terminology:
- "slow dolly forward through misty forest"
- "orbital pan around glowing crystal, neon reflections"
- "tracking shot following subject against dawn sky"
- "crane shot rising above clouds, golden hour lighting"
- "static tripod shot, subject walks through frame"
- "handheld camera, slight shake, documentary feel"

## VRAM Requirements (Practical)

| Resolution | Duration | Wan 2.2 5B | Wan 2.1 14B | HunyuanVideo |
|------------|----------|------------|-------------|--------------|
| 480p | 3-5s | ~8 GB | ~40 GB | ~60 GB |
| 720p | 5s | ~12 GB | ~65-80 GB | ~80 GB |
| 1080p | 5s | OOM | ~80 GB+ | ~100-120 GB |

**Quantization helps:** fp8 reduces 14B model requirements significantly.
**Torch compile:** Reduces VRAM and speeds up generation for Wan models.

## Closed-Source / Cloud APIs

| Model | Price/sec | Max Duration | Audio | Best For |
|-------|-----------|-------------|-------|----------|
| Seedance 2.0 | $0.022 | 8s | No | Best value, production scale |
| Wan 2.6 (cloud) | $0.07 | 15s | Yes | Fast drafts (~20s) |
| Kling Video O3 | $0.15 | 10s | Yes | Maximum fidelity |
| Veo 3.1 | $0.09 | 8s | Yes | Cinematic + native audio |
| Sora 2 | $0.15 | 10s | No | Narrative/cinematic |
| PixVerse V4.5 | - | - | - | Anime/stylized |

## Image-to-Video Workflow (3D/AI Pipeline)

Best approach for users with Blender/3D background:

```
1. Create scene in Blender → render still frame or short camera pass
2. Feed still into Wan 2.2 I2V via ComfyUI
3. AI adds: atmosphere, organic motion, particles, life
4. Optionally bring back into Blender for compositing
5. Final output: AI-enhanced 3D scene with cinematic motion
```

Benefits:
- Full control over composition, lighting, camera angle from 3D
- AI adds the "organic life" that's hard to keyframe
- Blender handles hard-surface precision, AI handles atmosphere
- Loitering shot → AI can extend with subtle camera drift

## Hardware Tiers

| Tier | GPU | Wan 2.2 5B | Notes |
|------|-----|-----------|-------|
| Budget | RTX 3060 12GB | 480p-720p, ~5-10s clips | Minimum viable |
| Mid | RTX 4080/5070 Ti 16GB | 720p, good quality | Sweet spot for local |
| Serious | RTX 4090 24GB | 720p-1080p | Tight but works |
| Datacenter | H100 80GB | 14B models, 720p-1080p | Full quality |
| Cloud | Comfy Cloud / Spheron | All models | $2.50/hr for H100 |

## Post-Processing

ComfyUI video outputs use yuv444p (not Discord/browser compatible). Re-encode:
```bash
ffmpeg -y -i input.mp4 \
  -c:v libx264 -profile:v main -preset medium -crf 13 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  output.mp4
```

Multi-video crossfade stitch:
```bash
ffmpeg -y -i a.mp4 -i b.mp4 -i c.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=1:offset=3.04[v1];[v1][2:v]xfade=transition=fade:duration=1:offset=6.08[vout];[0:a][1:a]acrossfade=duration=1:c1=tri:c2=tri[a1];[a1][2:a]acrossfade=duration=1:c1=tri:c2=tri[aout]" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -profile:v main -crf 13 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  output_stitched.mp4
```

## Sources
- Atlas Cloud comparison (Feb 2026)
- Scenario "How to Choose the Right Video Model" (2026)
- Spheron GPU Cloud VRAM Guide (Mar 2026)
- WhiteFiber open-source model comparison (May 2026)
- ComfyUI official Wan 2.2 docs
