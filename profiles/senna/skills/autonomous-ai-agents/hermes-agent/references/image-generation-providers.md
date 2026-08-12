# Image Generation Providers

Hermes has 5 built-in image generation providers in `plugins/image_gen/`.
All are auto-discovered — add the API key and restart the gateway.

## Provider Summary

| Provider | Name in config | Auth | Badge | Key env var |
|----------|---------------|------|-------|-------------|
| FAL.ai | `fal` | `FAL_KEY` | paid | `FAL_KEY` |
| OpenAI | `openai` | `OPENAI_API_KEY` | paid | `OPENAI_API_KEY` |
| OpenAI Codex | `openai-codex` | ChatGPT/Codex OAuth | **free** | none (uses `hermes auth codex`) |
| xAI Grok | `xai` | `XAI_API_KEY` or xAI OAuth | paid | `XAI_API_KEY` |
| Krea | `krea` | `KREA_API_KEY` | paid | `KREA_API_KEY` |

## FAL.ai

- **18 models**: FLUX 2, Z-Image, Nano Banana, GPT Image 1.5, Recraft, Imagen 4, Qwen, Ideogram, etc.
- Auth: `FAL_KEY` env var OR Nous managed gateway (auto-resolves without a key)
- Get key: https://fal.ai/dashboard/keys
- Largest model catalog of any provider

## OpenAI (API key)

- **Model**: `gpt-image-2` at 3 quality tiers
  - `gpt-image-2-low` ~15s — fast iteration
  - `gpt-image-2-medium` ~40s — balanced (default)
  - `gpt-image-2-high` ~2min — highest fidelity
- Auth: `OPENAI_API_KEY` env var
- Get key: https://platform.openai.com/api-keys

## OpenAI Codex (FREE — no API key needed)

- Same `gpt-image-2` tiers as the API key variant
- Routes through ChatGPT/Codex OAuth instead of REST API
- Auth: `hermes auth codex` (or `hermes setup` → Codex)
- Badge: **free** — no API key or billing needed
- Uses Codex Responses API `image_generation` tool under the hood

## xAI Grok

- **Models**:
  - `grok-imagine-image` ~5-10s — fast, high quality
  - `grok-imagine-image-quality` ~10-20s — higher fidelity
- Auth: `XAI_API_KEY` or xAI OAuth (`hermes model` → xAI)
- Extras: more aspect ratios (4:3, 3:4, 3:2, 2:3), 1K/2K resolution
- Get key: https://console.x.ai

## Krea

- **Models**:
  - `krea-2-medium` ~15-25s — $0.03/img — illustration, anime, painting
  - `krea-2-large` ~25-60s — $0.06/img — photorealism, raw textured looks
- Auth: `KREA_API_KEY` env var
- Get key: https://www.krea.ai/settings/api-tokens
- Extras: style references (up to 10), moodboards (1), creativity knob (raw/low/medium/high)
- Async API: submit → poll → result (provider handles this transparently)

## Where to put keys

Keys go in `~/.hermes/.env` (root — canonical source for all profiles).
See `references/env-architecture.md` for root vs profile `.env` rules.

```
# ~/.hermes/.env
FAL_KEY=your-fal-key
KREA_API_KEY=your-krea-key
XAI_API_KEY=your-xai-key
# OPENAI_API_KEY already covers OpenAI image gen if set
```

After adding keys, restart the gateway. The image_gen toolset auto-detects
available providers at startup.

## Config overrides (optional)

In `config.yaml` under `image_gen:`:

```yaml
image_gen:
  model: krea-2-medium          # default model across providers
  krea:
    model: krea-2-large
    creativity: high
  openai:
    model: gpt-image-2-high
  xai:
    model: grok-imagine-image-quality
    resolution: 2k
```

## Pitfalls

### 1. Don't confuse root and profile .env
The user may put keys in `~/.hermes/.env` (root) or `~/.hermes/profiles/<name>/.env`.
Both work — root is shared across profiles, profile is override-only. Verify with
`hermes config` → "Secrets:" path to confirm which `.env` is active.

### 2. OpenAI Codex provider is often overlooked
It's the only **free** option — no API key needed, just `hermes auth codex`.
Users with a ChatGPT account can generate images without paying for API access.

### 3. FAL works without a key via Nous gateway
If the user has a Nous Portal subscription, FAL may resolve through the managed
gateway even without `FAL_KEY` set. Check `is_available()` logic — it checks both
`FAL_KEY` and the managed gateway origin.

### 4. Krea is async — don't expect instant results
Krea submits a job and polls. The provider handles this transparently, but
generation takes 15-60s depending on model. This is normal, not a hang.

### 5. xAI OAuth shares auth with TTS/video
xAI image gen, TTS, and video gen all use the same xAI OAuth or `XAI_API_KEY`.
Setting up one sets up all three.
