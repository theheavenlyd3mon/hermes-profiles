---
name: riso
description: High-fidelity ASCII/Braille rendering via the Risomorphism-1911 pipeline — edge-aware downsampling, presets, quality gates, and eikon mirror workflows
version: 1.2.0
author: Senna
tags: [ascii, braille, rendering, eikon, mirror, quality-gate, scaling, creative, preprocessing]
related_skills: [ascii-art, ascii-video, animated-eikon-from-base]
---

# RISO — Risomorphism-1911 ASCII Pipeline

**Package:** `ascii-art-pipeline` (installed at `~/riso/`)
**CLI:** `ascii-pipeline`
**Base grid:** 48×24 (Herm avatar default)

Pure-Python ASCII rendering with edge-aware downsampling, four curated presets, and automatic quality verdicts. No external binaries required. See `references/preprocessing.md` for the session-specific image preprocessing patterns.

---

## Preset Quick Reference

| Preset | Charset | Best for | Quality gate |
|--------|---------|----------|-------------|
| `stroke-clarity` | 12 glyphs (`@$#MHAGXS532;:,`) | High-contrast silhouettes, portraits, safe default | `high-contrast` |
| `d30-dense` | 68 glyphs (extended D30) | Dense cyber-noir texture, HUD aesthetic | `high-contrast` (edge-aware at scale≥8) |
| `braille-detail` | Unicode Braille (U+2800–U+28FF) | Maximum detail, halftone effect | `braille-dominant` |
| `eikon-motion` | D30 charset | Video → animated eikon for mirror/avatar | `high-contrast` per frame |

### When to use what

| You want... | Use... |
|-------------|--------|
| Clean readable ASCII from a photo | `stroke-clarity` — default, fastest, always works |
| Dense moody ASCII (cyber-noir look) | `d30-dense` — richer texture, slower at high scales |
| Character portrait with legible face | `stroke-clarity` — the 12-glyph charset produces cleaner silhouettes than d30-dense face detail at scale ≤2 |
| Maximum detail in the cell grid | `braille-detail` — needs terminal Braille support |
| Animated avatar for mirror | `eikon-motion` via `build-eikon-from-video` |

---

## Preprocessing for Clean Backgrounds

**CRITICAL: The pipeline maps pure black (0,0,0) to `@` (the darkest character), NOT to spaces.** The converter at `converter.py:_map_intensity` maps pixel brightness 0–255 linearly to charset indices with `floor(pixels * n)`. Black → index 0 → `@`. There is no special handling for black-as-background.

If you send an image with a black background, the output fills with `@`, `$`, `#` — the background looks like solid dense character fill, not empty space.

**Fix: set background to white (255) before running through the pipeline.** White maps to the lightest characters (`.` / `,` / `;`) which are visually near-invisible. The autocontrast preprocess then stretches the character's contrast range independently, so the subject stays crisp.

### Preprocessing Workflow for Subject Isolation

1. **Crop tight** to the subject — remove background at the image level first
2. **Analyze brightness histogram** — find the valley between background peak and subject peak
3. **Threshold** — create a boolean mask with the threshold set at that valley:
   ```python
   gray = np.mean(arr, axis=2)
   mask = gray > threshold  # True = subject, False = background
   ```
4. **Set background to white** — replace background pixels with (255,255,255):
   ```python
   result = np.full_like(arr, 255)  # all white
   for c in range(3):
       result[:,:,c] = np.where(mask, arr[:,:,c], 255)
   ```
5. **Median filter** — smooth mask boundary artifacts:
   ```python
   Image.fromarray(result).filter(ImageFilter.MedianFilter(3))
   ```
6. **Run through pipeline** — `stroke-clarity` at scale 2 (96×48) is a good starting point for portraits

### Quality Check

After rendering, inspect `fill_ratio` in the diagnostics JSON:
- **0.65–0.75**: clean result — ~25–35% background rendered as space
- **~1.0**: background wasn't removed — redo the threshold with a higher value
- **Heavy ratio > 0.50 with fill near 1.0**: likely `@`/`$`/`#` background fill, not character

---

## Commands

### Render a still image

```bash
ascii-pipeline render-image \
  --input <image> \
  --preset <preset> \
  --out <output.txt> \
  [--preview-out preview.png] \
  [--diagnostics-out metrics.json] \
  [--scale N]           # default 1, range 1–16
  [--fullsize]          # alias for --scale 4 (192×96)
```

**Workflow:**
1. Preprocess image if background needs isolation (see above)
2. Run with `--diagnostics-out` to get quality verdict
3. Check verdict: `high-contrast` → ship; `low-contrast-garble-risk` → increase scale or switch preset
4. Use `--preview-out` for side-by-side visual QA

### Diagnose an existing file

```bash
ascii-pipeline diagnose --input <file.txt> --pretty
```

Checks dimensions, glyph diversity, fill ratio, heavy/light balance. Verdict is authoritative.

### Render preview from text/eikon

```bash
ascii-pipeline render-preview --input <file.txt> --out preview.png
```

### Build animated eikon from video (mirror workflow)

```bash
ascii-pipeline build-eikon-from-video \
  --video <input.mp4> \
  --fps 24 \
  --states 3 \
  --id <eikon-name> \
  [--grid 192x96] \
  [--charset d30-dense]
```

Outputs: `<id>.eikon` + `<id>-player.html` (offline HTML5 canvas player).

**Workflow for mirror deployment:**
1. Use `build-eikon-from-video` with source video
2. Output `.eikon` file can be served to the mirror
3. HTML player is self-contained (base64-encoded, no server needed)

---

## Scaling Guide

| Scale N | Grid (W×H) | Name | When |
|---------|-----------|------|------|
| 1 | 48×24 | avatar | Default, Herm avatar size, chat-friendly |
| 2 | 96×48 | compact | Slightly more detail, good for portraits |
| 4 | 192×96 | fullsize | Showcase, poster, eikon master |
| 8 | 384×192 | large | High-fidelity showcase |
| 16 | 768×384 | max | Archival, print — **only with `stroke-clarity`** |

**Performance:** `d30-dense` at scale ≥8 is slow and memory-heavy (up to ~4GB at N=16). `stroke-clarity` stays fast at all scales (~0.3s at N=16). Prefer `stroke-clarity` for quick previews, then switch to `d30-dense` for the final render.

---

## Quality Gates

| Verdict | Meaning | Action |
|---------|---------|--------|
| `high-contrast` | Production-safe | Ship |
| `low-contrast-garble-risk` | Edge washout detected | Increase scale or switch to `stroke-clarity` |
| `braille-dominant` | Braille preset, 4× resolution achieved | Accept (Braille mode) |

Always run `--diagnostics-out` before shipping to mirror or avatar. Don't ship `low-contrast-garble-risk`.

---

## Integration with Other Skills

- **`ascii-art` skill** — Use `riso` instead of `jp2a`/`ascii-image-converter` when you want quality-gated output with preset control. The `ascii-art` skill handles text banners, cowsay, and borders — this handles high-fidelity image → ASCII.
- **`ascii-video` skill** — `riso`'s `build-eikon-from-video` is a lighter alternative to the full ascii-video pipeline when you just need an animated eikon for the mirror (no scene composition, shaders, or audio reactivity needed).
- **`animated-eikon-from-base` skill** — Upstream pipeline that generates real animated video clips (idle/listening/thinking/speaking/working/error) from a single base image via fal.ai/Kling. Once you have the MP4s, either feed them through `riso`'s `build-eikon-from-video` for ASCII eikon conversion, or install them directly into Herm Studio source at `~/.hermes/eikons/<name>/source/` for native rendering. riso handles ASCII/braille eikons; animated-eikon-from-base handles real video eikons — complementary, not competing.
- **`animated-eikon-from-base` skill** — Use this upstream to generate animated video clips from a single base image via fal.ai/Kling (idle/listening/thinking/speaking/working/error). Once you have those MP4s, feed them into `riso`'s `build-eikon-from-video` for ASCII eikon conversion, or install them directly into Herm Studio's source folder (`~/.hermes/eikons/<name>/source/`) for native rendering.

---

## Pitfalls

- **Black background → `@` fill, NOT spaces** — The core converter maps black (0) → index 0 → `@`. If the output is `@`-dense with fill_ratio ~1.0, the background is pure black. Set it to white (255) instead. This is the #1 gotcha.
- **`d30-dense` at scale ≥8 can memory-spike** — intermediate grid goes to 6144×3072 at N=16. Use `stroke-clarity` at N=16 instead.
- **`stroke-clarity` beats `d30-dense` for portraits** — The 12-glyph charset produces cleaner face silhouettes. `d30-dense` with 68 glyphs adds texture noise that obscures facial features at scale ≤2.
- **Edge-aware downsampling is automatic** for `d30-dense` at scale ≥8 — don't try to override it, it's wired into the preset.
- **`braille-detail` needs a Braille-capable terminal** — standard terminals don't render U+2800+ well. Use for file output / preview PNG, not terminal display.
- **Eikon videos require source MP4 to be high-contrast, well-lit, minimal motion blur** — the ASCII pipeline amplifies noise.
- **Clean up temp frames** after `build-eikon-from-video`: `rm -rf tmp/` in the working directory.
