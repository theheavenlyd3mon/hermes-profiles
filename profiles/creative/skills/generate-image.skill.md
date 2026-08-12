---
name: image-studio-generate
description: "Generate AI images with style presets using Hermes Image Studio. Use when the user wants a single image for social media, articles, or creative projects."
---

# Image Studio: Generate a Single Image

Load this skill when the user asks to generate an image. Works with the
Hermes Image Studio plugin (tools: `image_studio_generate`,
`image_studio_presets`).

## Workflow

1. **Ask what they want.** If the user hasn't described the scene, ask:
   - Subject (what/who is in the image)
   - Setting (where/when)
   - Mood or lighting
   - What it's for (Twitter, article, personal)

2. **Pick a preset** using `image_studio_presets` if you're unsure which
   style fits. Explain your choice in one sentence.

3. **Build a strong prompt.** Be specific:
   - "A cowboy riding through a desert at sunrise" is weak
   - "A lone cowboy on horseback silhouetted against the rising sun, dust
     kicking up from hooves, warm golden light, distant red rock mountains"
     is strong

4. **Call `image_studio_generate`** with the prompt, preset, aspect ratio,
   and optionally a seed for reproducibility.

5. **Present the result.** Include the file path and seed so they can
   re-generate with tweaks.

## Defaults

- Preset: `cinematic` (good all-around)
- Aspect ratio: `landscape` (16:9 for Twitter)
- Seed: `-1` (random)

For Twitter images, `landscape` (16:9) works best for most posts.
`square` (1:1) works better for images that will be preview cards.

## Preset Quick Reference

| Preset | Best for |
|--------|----------|
| cinematic | Scenes, landscapes, action, portraits with drama |
| photorealistic | Products, environments, anything needing realism |
| vintage | Historical, retro, nostalgic, old-days aesthetic |
| fantasy | Concept art, magical scenes, epic landscapes |
| minimalist | Clean branding, editorial, modern compositions |
| illustration | Bold artistic style, social media graphics |
| noir | Moody, shadowy, dramatic black-and-white |
| studio | Product shots, portraits, clean commercial looks |
