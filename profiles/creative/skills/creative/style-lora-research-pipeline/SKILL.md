---
name: style-lora-research-pipeline
description: Discover, curate, and batch-test external style LoRAs for brand-custom image generation. Covers Loratlas-style libraries, FAL LoRA inference, and async polling patterns.
---

# Style LoRA Research Pipeline

Use when: the user wants to mine external style LoRA libraries, curate a brand-aligned shortlist, or batch-test styles against real scene prompts.

## Trigger conditions

- "curate style LoRAs", "test styles on FAL", "batch test LoRAs", "style library", "Loratlas", "Krea 2 LoRAs"
- User wants to find new visual styles aligned with a brand aesthetic before deciding whether to hybrid-fit locally or inference via API

## Workflow

1. **Discover**: load the external library homepage and navigate to the indexed view (Library/All).
2. **Filter by brand DNA**: match palette, lighting, cinematic density, and genre overlap. Use subjective fit ranking, not like-counts alone.
3. **Shortlist tiers rather than one flat list**: core dramatic skin, secondary ornate skin, reserve anime/lighter skin, and mural/old-artwork fallback family.
4. **Deep-dive each page**: extract the trigger phrase, the Hugging Face weight path, and the developer-call prompt template. Pause before generating — read the page’s prompt guide first.
5. **Author test prompts**: brand-themed subjects, stripped to concrete nouns + minimal action/setting. Never redefine medium; let the LoRA carry it.
6. **Batch-submit via `fal.run` endpoint** `fal-ai/krea-2/turbo/lora` (or equivalent). Use async polling. See `references/fal-lora-testing.md` for the stdlib-only fallback and the exact poll loop, and `references/cheonma-fal-batch-notes.md` for the brand-local batch CLI and synchronous-response behavior.
7. **Collect outputs**: save image URLs + request IDs locally under `~/cheonma/loratlas_test_runs.json` or brand-equivalent path.
8. **Evaluate**: rank tested styles by visual fidelity to brand prompts, not just novelty.
9. **Formalize**: save chosen skins as template files, subject prompts as JSON banks, and generate via a repeatable brand CLI instead of one-off scripts.

## Brand-fit filter rubric

- Palette overlap with brand DNA
- Cinematic lighting density (chiaroscuro, backlight, golden hour, noir)
- Depth of field and texture grain behavior
- Consistency across varied subjects
- Scalability — can the style survive 1.0–1.3 scale without collapse

## Pitfalls

- Don’t generate before reading the page-level prompt guide — each LoRA has a distinct ideal prompt shape.
- FAL’s `image_generate` tool is FLUX-only and cannot run custom LoRA weights. Use direct `https://fal.run` calls instead.
- `requests` is not guaranteed in the session venv. Use `urllib.request` + polling loop; see `references/fal-lora-testing.md` for the complete drop-in pattern.
- Some HF links reported broken; verify the `v3b.fal.media/...safetensors` URL is present on the style page before testing.
- This endpoint is sometimes synchronous: a completed response can appear as `response.images[0].url` while the top-level `request_id` is absent. Treat a missing request ID as “read the image from the response directly,” not as a hard failure requiring another submit.
- Async endpoints need polling — do not treat a 202/queued response as success.
- **Markdown patch hygiene**: when updating prompt template `.md` files, always inspect the fenced block afterward. Small replace patches can bisect code fences or duplicate headings.
- **Subject bank sizing**: 4–8 entries per archetype is too few for a recurring weekly feed. Formalize step should expand each bank to 12–15 concrete noun prompts before treating the template system production-ready.

## Environment discovery for FAL auth

Preferred key lookup order:
1. `~/.hermes/.env`
2. `<brand root>/.env`
3. profile-local `~/.hermes/profiles/<name>/.env` only if explicitly configured
4. Do not assume `~/.env`, `/root/.env`, or the active shell’s exports

The fallback script in `references/fal-lora-testing.md` hardcodes `~/.hermes/.env`.
Override that path only when brand setup explicitly differs.

## Output expectations

- JSON array: one entry per style × subject.
- Fields: `style`, `subject`, `prompt`, `request_id`, `final_status`, `image_url`.
- Print summary counts by style at end.

## Session package target

After testing, create one index doc next to `references/fal-lora-testing.md`, e.g. `references/<brand>-style-shortlist.md`, containing:
- Tiered shortlist
- Direct style-page URLs
- Trigger phrases
- Final style-URL pairs for future hybrid fitting
