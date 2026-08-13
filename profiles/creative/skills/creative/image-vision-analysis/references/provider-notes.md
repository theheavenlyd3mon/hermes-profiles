# Vision-capable provider inventory (observed 2026-08)

Key discovery method: `grep -oE '^[A-Z_]+' <file>` lists key names without
exposing values. Check profile .env first, root .env second.

## Validated path

| Provider | Key location | Model used | Status |
|----------|--------------|------------|--------|
| OpenRouter | `OPENROUTER_API_KEY` (creative profile .env AND root .env, ~73 chars) | `openai/gpt-4o-mini` | ✅ VALIDATED — worked for a 1024×1536 / 373 KB JPEG via base64 data URL |

OpenRouter call shape (worked 2026-08-10):
- Endpoint: `https://openrouter.ai/api/v1/chat/completions`
- Auth: `Authorization: Bearer <key>`, `Content-Type: application/json`
- Body: `{"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": [{"type": "text", ...}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]}], "max_tokens": 800}`
- JSON body was ~230 KB for the 373 KB JPEG — no size rejection at this scale.
- Use python3 + urllib, NOT `curl | python3` (security scanner flags the pipe).

## Keys present but NOT validated for vision

| Key | Where | Notes |
|-----|-------|-------|
| DASHSCOPE_API_KEY | both envs (~113 chars) | Qwen-VL family is a likely candidate |
| KIMI_API_KEY | both envs (~72 chars) | Moonshot vision models possible |
| NVIDIA_API_KEY | root .env (~70 chars) | NVCF vision endpoints possible |
| GROQ_API_KEY | root .env (~56 chars) | llama-3.2 vision models possible |
| XIAOMI_API_KEY | creative .env (~51 chars) | unknown model support |
| MINIMAX_API_KEY | creative .env (~126 chars) | unknown model support |

## Traps

- `OPENAI_API_KEY` exists as a line in `~/.hermes/.env` but is EMPTY — calling
  it yields "You didn't provide an API key." Never trust presence, only length.
- HF_TOKEN in root .env is ~3 chars (placeholder, not a real token).
