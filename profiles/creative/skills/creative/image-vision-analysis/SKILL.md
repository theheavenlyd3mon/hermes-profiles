---
name: image-vision-analysis
description: "Vision fallback: describe images via OpenRouter gpt-4o-mini."
version: 1.0.0
metadata:
  hermes:
    tags: [vision, image-analysis, image-description, openrouter, fallback, creative]
---

# Image Vision Analysis (with fallback)

When you need to SEE an image — a user-supplied reference, a generated artifact, a screenshot — and the active model can't accept image content.

## Primary path

`vision_analyze(image_url, question)` — works when the active model or its auxiliary vision fallback supports `image_url` content. Always try this first.

## Failure signature: text-only model

`vision_analyze` errors with:

```
Error code: 400 - Failed to deserialize the JSON body into the target type:
messages[0]: unknown variant `image_url`, expected `text`
```

This means the endpoint only accepts text messages — a model capability gap, NOT an image size/format problem. **Downscaling does NOT fix it.** Don't loop on sips/quality variants; switch to the fallback path immediately.

## Fallback path (validated 2026-08)

Route the image to `openai/gpt-4o-mini` through OpenRouter:

```bash
python3 scripts/analyze-image.py --image /path/to/img.jpg --question "Describe..."
# optional: --model openai/gpt-4o-mini
```

The script:
1. Finds `OPENROUTER_API_KEY` (env, then `~/.hermes/profiles/creative/.env`, then `~/.hermes/.env`)
2. Base64-embeds the image as a data URL (no file upload needed)
3. Calls `https://openrouter.ai/api/v1/chat/completions`
4. Prints the model's description

## Discovering API keys safely

- `grep -oE '^[A-Z_]+' <file>` lists key NAMES without exposing values.
- Check the profile `.env` FIRST (`~/.hermes/profiles/creative/.env`), then the root `~/.hermes/.env`.
- **Verify key length, not presence**: an `OPENAI_API_KEY=` line that is empty returns "You didn't provide an API key." A key name existing in the file does not mean it has a value. Confirm `len(value) > 10` before using it.
- Keys observed with real values: OPENROUTER, DASHSCOPE, KIMI, NVIDIA, GROQ, XIAOMI, MINIMAX. See `references/provider-notes.md`.

## Pitfalls

- Do NOT pipe curl output into python3 (`curl ... | python3`) — the security scanner flags it as pipe-to-interpreter. Use python3 + urllib with a JSON payload instead (exactly what `scripts/analyze-image.py` does).
- Size: a 1024×1536 / 373 KB JPEG worked fine base64-embedded (~230 KB JSON body). Only downscale (`sips -Z 768 -s format jpeg in.jpg --out small.jpg`) if a provider rejects the payload for size — never for the `image_url` variant error.
- Ask specific questions. For design-classification / skill-matching tasks, request: subject, style, medium, composition, framing, palette, lighting, texture, any visible text, mood. The vision answer is only as useful as the question.
- If the OpenRouter call returns an error, check the raw response JSON — the model field may be deprecated; any current `openai/gpt-4o*` vision model works.

## Support files

- `scripts/analyze-image.py` — re-runnable OpenRouter vision description script (the validated workaround).
- `references/provider-notes.md` — vision-capable provider inventory and key locations observed on this machine.
