
# Cheonma FAL Batch Notes (2026-07-02)

## Brand-local generator

Preferred CLI: `~/cheonma/scripts/fal_generate.py`
- Loads `FAL_KEY` from `~/.hermes/.env`
- Submits to `https://fal.run/fal-ai/krea-2/turbo/lora`
- Saves JSON with `--save-json` and the absolute local PNG path with `--out`
- Supports skin, subject, seed, width, height

## Known endpoint behavior

- `fal-ai/krea-2/turbo/lora` sometimes returns synchronous completion.
- When that happens, the response body contains `images[0].url`, but top-level `request_id` may be absent.
- Do not re-submit on missing `request_id`; read `response.images[0].url` and download the image directly.
- Seeds are loose anchors; identical requested seeds do not guarantee identical outputs. Prefer unique seeds unless a specific poster frame is locked.

## Batch pattern

Use `subprocess.run` with `capture_output=True, text=True, timeout=240` in `execute_code` rather than taking a dependency on `requests`. Collect results in a dict keyed by scene ID, then optionally rename basenames to canonical scene filenames afterward.
  