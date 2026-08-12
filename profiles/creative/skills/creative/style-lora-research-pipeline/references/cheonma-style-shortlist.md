# Cheonma Loratlas Selections (2026-07-02)

Saved run indexes:
- `~/cheonma/loratlas_test_runs.json`
- `~/cheonma/loratlas_test_runs_tier23.json`
- `~/cheonma/loratlas_crimson_fixed_seed_series.json`

## Confirmed primary skin
- **Crimson Dark Victorian Oil**
  - Style page: https://www.loratlas.com/style/crimson-dark-victorian-oil
  - Trigger: `crimson dark victorian oil style`
  - Scale: `1.15` start; `1.2–1.35` for stronger chiaroscuro
  - Weight: https://huggingface.co/ilkerzgi/krea-2-crimson-dark-victorian-oil-lora
  - Direct: `https://v3b.fal.media/files/b/0a9fd22e/EdJ7fln3ZByCyGZfHo_8K_krea2_lora_step_100.safetensors`
  - Best for: main manhwa panels, demon lord reveals, cliff fights, crimson fog scenes

## Secondary skin
- **Midnight Blue Gilded**
  - Style page: https://www.loratlas.com/style/midnight-blue-gilded
  - Trigger: `midnight blue gilded style`
  - Scale: `1.0`
  - Weight: https://huggingface.co/ilkerzgi/krea-2-midnight-blue-gilded-lora
  - Direct: `https://v3b.fal.media/files/b/0a9f9b3f/ZfcixyTk354QkyV7496X0_krea2_lora_step_100.safetensors`
  - Best for: regal portraits, thumbnail alternates, ornate close-ups

## Reserve skin
- **Open Sky Anime**
  - Style page: https://www.loratlas.com/style/open-sky-anime
  - Trigger: `open sky anime style`
  - Scale: `1.0`
  - Weight: https://huggingface.co/ilkerzgi/krea-2-open-sky-anime-lora
  - Direct: `https://v3b.fal.media/files/b/0a9fc127/kkePDUsHtvjfX6jztxgFE_krea2_lora_step_100.safetensors`
  - Best for: announcements, lighter threads, montage transitions, softer hero frames

## Mural / old-artwork skins
- **Hazy Golden Oilpaint** — golden haze / DOF treatment
  - Trigger: `hazy golden oilpaint style`, scale `1.1`
  - Weight: https://huggingface.co/ilkerzgi/krea-2-hazy-golden-oilpaint-lora
  - Direct: `https://v3b.fal.media/files/b/0a9fa057/IYD3s4RQiQEXDJJKUC1X6_krea2_lora_step_100.safetensors`
- **Dark Victorian Oil** — darker panel feel than crimson variant
  - Trigger: `dark victorian oil style`, scale `1.0`
  - Weight: https://huggingface.co/ilkerzgi/krea-2-dark-victorian-oil-lora
  - Direct: `https://v3b.fal.media/files/b/0a9fcfe7/pk2mv-F9ht86CiLZFvWNW_krea2_lora_step_100.safetensors`

## Prompt discipline
- `<trigger>, <subject>` — trigger first, then subject, then action/setting only if it matters.
- Concrete nouns only. No filler adjectives. No invented props/costumes/backstory. No full sentences. Never redefine medium; the LoRA carries it.
- Style strength: 1.0 default; 1.0–1.35 only for stronger cinematic emphasis.

## Selection doctrine
- Core brand skins first: palette overlap with Heavenly Demon identity, screenshot-grade cinematic behavior, consistency across 3+ varied subjects.
- Maintain 4 roles: primary drama, secondary ornate, reserve anime, mural/old-artwork.
- Use `style-lora-research-pipeline` CLI or brand-local generator for reruns, not ad-hoc scripts.

## Reusable brand assets
- Templates: `brand/loratlas-templates/templates/*.md`
- Subjects: `brand/loratlas-templates/subjects/*.json`
- Generator: `~/cheonma/scripts/fal_generate.py`
- Outputs: `~/cheonma/outputs/`
