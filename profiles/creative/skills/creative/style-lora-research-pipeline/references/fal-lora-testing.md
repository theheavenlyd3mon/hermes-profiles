# FAL LoRA batch testing (stdlib-only fallback)

Context: `fal.run` `fal-ai/krea-2/turbo/lora` may return either an immediate completion payload with `images` or an async submission object with `request_id`. This template handles both shapes. Do not treat a successful body as a failure just because `request_id` is absent — the result can already contain `images`.

```python
import json, os, time, urllib.request, urllib.error, ssl

# Preferred auth: root Hermes env
HERE=os.path.expanduser("~/.hermes/.env")
# If brand setup differs, override to brand-local .env here.
with open(HERE, "r", encoding="utf-8") as f:
    for line in f:
        line=line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k,v=line.split("=",1)
        if k.strip()!="FAL_KEY":
            continue
        FAL_KEY=v.strip()
        break
    else:
        raise SystemExit("Set FAL_KEY in ~/.hermes/.env")

API_BASE="https://fal.run"
CTX=ssl.create_default_context()
HEADERS={"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

def submit(payload):
    data=json.dumps(payload).encode("utf-8")
    req=urllib.request.Request(f"{API_BASE}/fal-ai/krea-2/turbo/lora", data=data, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))

def poll(request_id, timeout=360):
    deadline=time.time()+timeout; last={}
    while time.time() < deadline:
        req=urllib.request.Request(f"{API_BASE}/fal-ai/krea-2/turbo/lora/requests/{request_id}", headers=HEADERS, method="GET")
        with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
            last=json.loads(r.read().decode("utf-8"))
        if last.get("status")=="COMPLETED":
            return last
        time.sleep(1.2)
    return last
```

## Brand generator wrapper

For repeated brand use, prefer a local CLI over ad-hoc scripts.
Example: `~/cheonma/scripts/fal_generate.py`

Args:
- `--skin` — slug from `brand/loratlas-templates/templates/`
- `--subject` — concrete subject phrase
- `--seed` — optional int
- `--save-json` — record path
- `--out` — optional image-path write

Record shape:
```json
{
  "skin": "...",
  "subject": "...",
  "prompt": "<trigger>, <subject>",
  "seed": 123,
  "request_id": "...",
  "final_status": "COMPLETED",
  "used_seed": 123,
  "image_url": "https://..."
}
```

## Known responses observed

- Krea 2 Turbo can return `images` directly from the submit response, even when `request_id` is absent. Capture the image URL from `response.images[0].url` rather than waiting for poll state.
- Identical requested seeds are not guaranteed to reproduce identical outputs for this endpoint. Treat seed as family anchor, not exact clone. For reproducible series, use unique seeds by default and lock only when a specific poster frame is selected.

## Prompt discipline

- Lead with `<trigger>, <subject>`.
- Subject should be concrete nouns + minimal action/setting.
- No filler adjectives. No invented props/costumes/backstory. No full sentences.
- Never restate medium or style after the trigger; the LoRA carries it.

## Output expectation

- JSON array or single record: one entry per style × subject.
- Fields: `style`, `subject`, `prompt`, `seed`, `request_id` or `response`, `image_url`.
- Print or save under brand output path, do not rely on stdout alone.

## Notes

- Prefer `data=json.dumps(payload).encode("utf-8")` over third-party clients.
- Poll 1.2s cadence is usually enough to stay under rate limits; bump if needed.
- Save results under brand test path.
- `image_generate` tooling is FLUX-only and cannot run custom LoRA weights. Use direct `https://fal.run` calls instead.
- Some HF repo links on Loratlas pages are broken; always use the `v3b.fal.media/...safetensors` URL present on the style page when available.
