# Loratlas × Cheonma Discovery Notes
Source site: https://www.loratlas.com/
Brand: Cheonma (천마) — X handle @theHeavenlyD3mon, display name "Cheonma (천마)".

## Context
Loratlas indexes ~1500 Krea 2 Style LoRAs and supports browser generation via a FAL key, plus direct Hugging Face weight links per style page.

## Direct Cheonma-adjacent tiers
Tier 1: Dark Victorian Oil / Cobalt Nightglow Lantern / Crimson Dark Victorian Oil / Dark Swirling Gothic Whimsy / Golden Deco Fable
Tier 2: Warm Golden Hour Film / Open Sky Anime / Monochrome Green Surreal / Hazy Golden Oilpaint / Retro Japanese Noir Illustration
Tier 3: Crimson Midnight Inkline / Midnight Blue Gilded / Retro Anime Cel Dusk / Dreamy Lavender Bloom / Vivid Tropical Gouache

## Prompt protocol
Subject-only prompts are preferred; many styles use a fixed short prompt across styles to isolate style transfer. Style trigger is auto-injected on style pages. Default style weight is ~1.0; raise to ~1.3 for stronger identity.

## Selected skins (2026-07-02)
- Primary: Crimson Dark Victorian Oil — trigger `crimson dark victorian oil style`, scale 1.15
- Secondary: Midnight Blue Gilded — trigger `midnight blue gilded style`, scale 1.0
- Reserve anime: Open Sky Anime — trigger `open sky anime style`, scale 1.0
- Mural/old-art: Hazy Golden Oilpaint + Dark Victorian Oil — triggers as listed above, scale 1.0–1.1

## Prompt discipline rules
- Lead: trigger token first, then 1–4 concrete nouns only.
- Avoid: mood adjectives like intense, defiant, elegant, majestic, stunning, gorgeous.
- Never restate medium/style after the trigger.
- Skip filler unless image-critical.

## Brand system files
- `~/cheonma/brand/BRAND_SYSTEM.md` — core identity, archetypes, scene grammar, post formats
- `~/cheonma/brand/BRAND_GUIDE.md` — visual identity, voice, content pillars, posting strategy
- `~/cheonma/brand/ARCHETYPES.md` — 6 archetype blocks with DNA blocks
- `~/cheonma/brand/SCENE_GRAMMAR.md` — slot formula and modular blocks
- `~/cheonma/brand/CONSISTENCY_RULES.md` — mandatory anchors, prohibited elements, seed discipline
- `~/cheonma/brand/loratlas-templates/` — 5 approved skins + 4 subject banks
