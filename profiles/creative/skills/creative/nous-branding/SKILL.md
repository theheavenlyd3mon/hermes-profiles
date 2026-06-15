---
name: nous-branding
description: "Nous Research brand identity guide with reference-image generation — cyber-classical style, Nous Girl mascot, color palette, typography, texture system, and img2img via generate-with-ref.py."
version: 1.0.0
author: Magnus Hedemark
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [branding, image-generation, nous-research, mascot, style-guide, cyber-classical]
    category: creative
    source: https://git.brandyapple.com/magnus/agent-skills
prerequisites:
  commands: ["python3"]
  packages: ["Pillow"]
---

# Nous Research Branding Guide

Adapted from [magnus/agent-skills](https://git.brandyapple.com/magnus/agent-skills) for local use.

## Core Brand Identity

- **Style**: "Cyber-classical" — fusion of neo-classical statuary, cyberpunk/industrial grunge, and retro 1970s-80s anime/manga
- **Tagline**: "The AI accelerator company"
- **Key phrases**: "Advance human rights and freedoms", "Open source language models", "Unrestricted availability and use"
- **Vibe**: Intellectual but gritty — a cutting-edge research lab operating in the shadows

## Color Palette

### Hero Palette

| Color | Hex | Usage |
|-------|-----|-------|
| **Electric Blue** | `#3847FF` | Primary accent, mascot hair highlights, key brand color |
| **Soft Lavender** | `#BDA6FF` | Secondary accent, gradient blends |
| **Burnt Orange** | `#D6825A` | Geometric overlay lines, HUD elements |
| **Deep Teal** | `#2E706B` | Secondary backgrounds |
| **Off-White** | `#E6E6E6` | Text on dark backgrounds |
| **Near Black** | `#00000E` | Primary background |

### Extended Palette

| Color | Hex | Usage |
|-------|-----|-------|
| **Deep Navy** | `#003681` | Secondary brand color, headers |
| **Medium Blue** | `#0051c3` | Interactive elements, links |
| **Coral Red** | `#fc574a` | Alerts, emphasis accents |
| **Gold** | `#E6C666` | Constellation lines, geometric overlays |
| **Charcoal** | `#1d1d1d` | Dark UI backgrounds |

### Palette Principles

- **High contrast is mandatory** — near-black backgrounds against electric blue accents
- **Grunge textures over solid colors** — never use flat, clean color blocks
- **Color reserved for hero content** — brand booklet is >95% grayscale
- **Gold/orange geometric lines** for HUD-style overlays and constellation motifs

## The Nous Girl Mascot

- **Style**: Retro 1970s-80s manga/anime cel-shaded, pure black/white (no gray)
- **Pose**: Three-quarter profile, looking upward-left, large expressive eyes
- **Features**: Voluminous bob hair with straight bangs, white over-ear headphones, white collared shirt
- **Expression**: Neutral, calm, attentive — "neutral, perhaps slightly surprised or attentive"
- **Critical details**:
  - White headphones ONLY (black headphones are incorrect)
  - NO facial markings (no tattoo, tear, scar)
  - Pure black ink on white paper — no shading, no gradients

### Official Pose Variants

1. **Primary Badge** (three-quarter profile facing up-left) — main logo lockup
2. **Headphone ¾ Profile** (facing right) — tech contexts
3. **Headphone Profile Left** (full profile) — social media
4. **Headphone Small Profile** (smaller profile) — watermarks

## Typography

| Role | Font | Treatment |
|------|------|-----------|
| **Display/Headline** | Heavy sans-serif (Druk Condensed style) | Massive, uppercase, distressed/grunge texture |
| **Body/Supporting** | Inter or IBM Plex Sans | Clean sans-serif, uppercase with loose tracking |
| **Code/Technical** | JetBrains Mono | Small, compact, monospace |

## Texture System

Five essential textures for all visuals:

1. **Risograph Grain** — coarse halftone dots for backgrounds
2. **Photocopy Noise** — speckled static for shadow areas
3. **CRT/Scan Lines** — horizontal lines for screen elements
4. **Paper Fiber** — subtle texture for backgrounds
5. **Ink Smudge** — irregular bleed for type edges

**Key rule**: Textures must feel **raw, analog, and imperfect**.

## Art Style Attributes

- **Medium**: Digital mixed media: renders + photomontage + hand-drawn illustration
- **Technique**: Photomontage with digital overlays, blueprint drawings, cel-shaded anime
- **Shading**: High-contrast chiaroscuro
- **Lighting**: Dramatic spot lighting, light beams from eyes, neon edge highlights
- **Composition**: Multi-panel grid layouts (system sheets); dramatic offset subjects (hero images)

**What the style is NOT**: Flat vector, corporate minimalist, purely photographic, bright/cheerful

## Reference Assets

Source: [magnus/agent-skills assets](https://git.brandyapple.com/magnus/agent-skills/src/branch/main/nous-branding/assets)

| File | Description | Primary Use |
|------|-------------|-------------|
| `palette-typography-reference.png` | Brand identity card with 6-color palette, typography specimens | Color/typography style reference |
| `nous-girl-official.webp` | High-res (2669×2709) official mascot, pure b&w manga | Primary mascot reference |
| `nous-girl-official-badge.png` | Official badge portrait (5760×7454) | Badge/primary variant |
| `nous-girl-sketch-sheet.png` | All 4 canonical poses | Pose reference |
| `nous-girl-philosophy.png` | Philosophy page with mission statement | Brand context |
| `nous-girl-style-reference.png` | Generated portrait with "NOUS" on headphones, electric blue accents | Color-application reference |
| `brand-collage-reference.png` | Cyber-classical collage with Theia marble statue, targeting reticle, CRT overlay | Multi-panel layout reference |

## Image Generation

### With Reference Images (img2img)

The `scripts/generate-with-ref.py` script bypasses the text-only `image_generate` tool by directly hitting OpenAI's `/v1/images/edits` endpoint with reference image upload.

```bash
python3 scripts/generate-with-ref.py \
  --prompt "A cyber-classical hero image with marble statue and CRT overlay" \
  --reference assets/brand-collage-reference.png \
  --aspect landscape \
  --quality high
```

**Options:**
- `--prompt TEXT`: Generation prompt (required)
- `--reference PATH`: Path to reference image (required)
- `--aspect RATIO`: `landscape|portrait|square` (default: `landscape`)
- `--quality Q`: `low|medium|high` (default: `medium`)
- `--output PATH`: Output file path (default: auto-named in cache)
- `--provider NAME`: Force provider (default: read from config)
- `--dry-run`: Print what would be sent without executing
- `--debug`: Print full request/response details

**Requires:** `OPENAI_API_KEY` in `~/.hermes/.env`

### Text-Only Generation

Use standard `image_generate` with detailed prompts incorporating the style guide elements:

**Prompt template:**
```
[Subject description] in cyber-classical style. Neo-classical statuary meets cyberpunk grunge. 
High-contrast chiaroscuro lighting with dramatic spot lights. 
Electric blue (#3847FF) accents on near-black (#00000E) background.
Risograph grain texture, CRT scan lines, photocopy noise.
Multi-panel grid composition with gold geometric overlay lines.
Retro 1970s-80s manga cel-shaded rendering. Raw, analog, imperfect textures.
```

### ComfyUI Workflows

For advanced generation (img2img, inpainting, ControlNet, video), use the `comfyui` skill with reference images from `assets/`.

## Prompt Construction Examples

### Hero Image
```
A marble bust of Athena emerging from circuit boards and cables, cyber-classical style. 
Electric blue (#3847FF) light emanating from her eyes, gold (#E6C666) constellation lines 
connecting floating geometric shapes. CRT scan lines overlay, risograph grain texture. 
Near-black background with burnt orange (#D6825A) HUD targeting reticle. 
Dramatic chiaroscuro lighting, raw imperfect textures.
```

### Mascot Portrait
```
Retro 1970s-80s manga cel-shaded portrait, pure black ink on white paper. 
Three-quarter profile looking upward-left, voluminous bob hair with straight bangs. 
White over-ear headphones, white collared shirt. Neutral calm attentive expression. 
Large expressive eyes. No gray tones, no shading, no gradients. 
Clean linework, analog imperfections.
```

### System Sheet
```
Technical system sheet layout with multi-panel grid. Cyber-classical aesthetic. 
Blueprint-style line drawings with gold (#E6C666) geometric overlay lines. 
JetBrains Mono monospace labels. CRT scan lines, photocopy noise texture. 
Near-black background, electric blue accent highlights. 
Raw industrial grunge feel, imperfect analog textures.
```

## Brand Compliance Checklist

- [ ] High contrast: near-black backgrounds with electric blue accents
- [ ] Textures present: at least 2 of 5 (risograph, photocopy, CRT, paper fiber, ink smudge)
- [ ] No flat/clean color blocks — always textured
- [ ] Color reserved for hero content, rest is grayscale
- [ ] Typography: distressed heavy sans-serif for headlines, clean sans for body
- [ ] Mascot: white headphones only, no facial markings, pure b&w manga style
- [ ] Geometric overlays: gold/orange lines for HUD and constellation motifs
- [ ] Style is NOT: flat vector, corporate minimalist, purely photographic, bright/cheerful
