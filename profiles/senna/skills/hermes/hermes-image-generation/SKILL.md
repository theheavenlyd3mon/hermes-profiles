---
name: hermes-image-generation
description: Configure, troubleshoot, and use Hermes image generation — all 5 built-in providers (FAL, OpenAI, OpenAI-Codex, xAI, Krea), model catalogs, env vars, and .env location gotchas.
triggers:
  - "image generation"
  - "generate image"
  - "fal"
  - "krea"
  - "gpt-image"
  - "grok imagine"
  - "image_gen"
  - "fal key"
  - "krea key"
  - "image gen provider"
version: 1.1.0
author: senna
metadata:
  hermes:
    tags: [hermes, image-gen, fal, krea, openai, xai, setup]
---

# Hermes Image Generation

5 built-in providers, registered as plugins under `$HERMES_HOME/plugins/image_gen/`.

## Providers

### FAL.ai (name: `fal`)
- **18 models** in the catalog — broadest range
- Auth: `FAL_KEY` env var OR Nous managed gateway (subscription)
- Default: `fal-ai/flux-2/klein/9b` (sub-1s, $0.006/MP)

| Model | Speed | Price | Best For |
|-------|-------|-------|----------|
| FLUX 2 Klein 9B | <1s | $0.006/MP | Fast, crisp text |
| FLUX 2 Pro | ~6s | $0.03/MP | Studio photorealism (auto-upscaled 2x) |
| Z-Image Turbo | ~2s | $0.005/MP | Bilingual EN/CN |
| Nano Banana Pro | ~8s | $0.15/img | Gemini 3 Pro, reasoning, text render |
| GPT Image 1.5 | ~15s | $0.034/img | Prompt adherence |
| GPT Image 2 | ~20s | $0.04–0.06 | SOTA text + CJK |
| Ideogram V3 | ~5s | $0.03–0.09 | Best typography |
| Recraft V4 Pro | ~8s | $0.25/img | Design, brand systems |
| Qwen Image | ~12s | $0.02/MP | LLM-based, complex text |

Upscaler: Clarity Upscaler (`fal-ai/clarity-upscaler`), 2x, auto-chained on FLUX 2 Pro only.

### OpenAI (name: `openai`)
- Model: `gpt-image-2` at 3 quality tiers (low/medium/high)
- Auth: `OPENAI_API_KEY`
- Sizes: 1024x1024, 1536x1024, 1024x1536

### OpenAI via Codex OAuth (name: `openai-codex`)
- Same `gpt-image-2` tiers — FREE, no API key needed
- Auth: ChatGPT/Codex OAuth via `hermes auth codex`
- Routes through ChatGPT backend

### xAI Grok (name: `xai`)
- Models: `grok-imagine-image` (~5-10s), `grok-imagine-image-quality` (~10-20s)
- Auth: `XAI_API_KEY` or xAI OAuth
- More aspect ratios (4:3, 3:2, 2:3, 3:4) + 1K/2K resolution

### Krea (name: `krea`)
- Models: `krea-2-medium` ($0.03), `krea-2-large` ($0.06)
- Auth: `KREA_API_KEY`
- Unique features: style references, moodboards, creativity knob (raw/low/medium/high)
- Async API (submit → poll), handled internally by the provider

## Environment Variables

Keys go in `$HERMES_HOME/.env` (e.g., `~/.hermes/profiles/senna/.env`).

```
FAL_KEY=fal-ai-key-here
KREA_API_KEY=krea-key-here
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
```

## .env Location Pitfall

⚠️ **Common mistake**: Users edit `~/.hermes/.env` (root) instead of `$HERMES_HOME/.env` (profile-specific). When `HERMES_HOME=/Users/<user>/.hermes/profiles/<profile>`, the profile `.env` is what gets loaded. The root `.env` is ignored by the profile gateway.

To check which `.env` hermes reads:
```
echo $HERMES_HOME   # then .env goes at $HERMES_HOME/.env
hermes status       # shows ".env file: ✓ exists"
```

## Setup Checklist (ALL 3 required)

Keys in .env alone are NOT enough. The tool and plugin providers must also be enabled in config.yaml.

### 1. API keys in `$HERMES_HOME/.env`
See Environment Variables section above.

### 2. `image_gen` in platform_toolsets
The tool must be listed in `platform_toolsets.cli` (and/or `platform_toolsets.telegram`, `platform_toolsets.discord`, etc.) in config.yaml. Without this, the tool is never loaded even if keys are present.

```bash
# Check current CLI toolsets:
grep -A20 'platform_toolsets:' ~/.hermes/profiles/<profile>/config.yaml

# Add image_gen to CLI toolsets:
hermes config set platform_toolsets.cli '["browser","clarify","code_execution","computer_use","cronjob","delegation","fabric","file","image_gen","memory","messaging","session_search","skills","terminal","todo","vision","web","web-search-plus"]'
```

### 3. Plugin providers in `plugins.enabled`
Each provider (fal, krea, openai, etc.) must be explicitly listed in `plugins.enabled` in config.yaml:

```bash
hermes config set plugins.enabled '["image_gen/fal","image_gen/krea","...existing plugins..."]'
```

### 4. (Optional) `image_gen.enabled` in config
```bash
hermes config set image_gen.enabled true
```

### Verification
```bash
hermes config show 2>&1 | grep -i "FAL\|image"   # FAL key should show masked
hermes status 2>&1 | grep -i "image"              # should say "✓"
```

## Configuration in config.yaml

Optional overrides under `image_gen:` key:
```yaml
image_gen:
  enabled: true
  use_gateway: true
  model: flux-2-klein-9b        # default model
  openai:
    model: gpt-image-2-medium   # OpenAI tier
  xai:
    model: grok-imagine-image
    resolution: 1k
  krea:
    model: krea-2-medium
    creativity: medium
```

## Multi-Profile Setup

When enabling image gen on a non-default profile (e.g., designer), ALL THREE
steps must target the correct profile. `hermes config set` writes to the
**current** profile (usually senna), NOT the profile you intend.

**Reliable method — edit the target config directly:**

```bash
TARGET=~/.hermes/profiles/<name>/config.yaml

# 1. Add image_gen to platform_toolsets.cli (if not present)
# Edit $TARGET directly

# 2. Add plugin providers to plugins.enabled
# Must include image_gen/fal and/or image_gen/krea

# 3. Add image_gen config section
# image_gen:
#   use_gateway: true
#   enabled: true
```

**Pitfall:** `hermes config set plugins.enabled '["image_gen/fal"]'` writes to
the CURRENT profile's config, not the target. Always verify with:
```bash
hermes config path   # confirms which config file is being edited
```

For profiles without their own FAL key, `use_gateway: true` routes through the
Nous managed gateway. The FAL key in the gateway's .env covers all profiles on
the same machine.

## Gateway Restart

After adding/changing API keys, restart the gateway for the agent to pick them up:
```bash
# Find senna gateway PID
ps aux | grep "senna.*gateway" | grep -v grep
# Kill it — s6/auto-restart brings it back
kill <PID>
```

## Troubleshooting: Keys Set But Tool Not Available

If `image_generate` doesn't appear in your tool list:

1. **Check platform_toolsets** — most common cause. `image_gen` must be in the platform's toolset list (see Setup Checklist above).

2. **Check plugins.enabled** — plugin providers (fal, krea, openai, xai) must be explicitly listed. The in-tree FAL backend only needs FAL_KEY + fal_client SDK; plugin providers need their entry in `plugins.enabled`.

3. **Check .env loading** — verify with:
   ```bash
   hermes config show 2>&1 | grep FAL   # should show masked key
   ```
   If the key doesn't show, the .env path is wrong. The CLI loads `$HERMES_HOME/.env` via `get_hermes_home()` from `hermes_constants.py`.

4. **Session restart required** — toolset and plugin changes take effect on next CLI/gateway start. Current session won't pick them up.

5. **Check requirement function** — from the hermes-agent venv:
   ```python
   from tools.image_generation_tool import check_image_generation_requirements
   check_image_generation_requirements()  # True = tool should register
   ```
   If False: fal_client SDK missing AND no plugin providers available.

## Plugin Architecture

Hermes has a **plugin-based image generation system**. Providers live at:
```
~/.hermes/hermes-agent/plugins/image_gen/
```
Each subdirectory is a self-registering plugin that implements the `ImageGenProvider` ABC from `agent/image_gen_provider`.

The toolset name is `image_gen`. It checks available providers at runtime based on auth state AND config. Providers must be listed in `plugins.enabled` in config.yaml to be discovered — just having the key in .env is not sufficient.

## Verification (Quick Health Check)

```bash
# 1. Overall status — look for "Image generation ✓ active" under Nous Tool Gateway
hermes status 2>&1 | grep -A1 "Image generation"

# 2. Confirm image_gen is in the CLI toolset
grep "image_gen" "$(hermes config path)"

# 3. Confirm providers are in plugins.enabled
grep "image_gen/" "$(hermes config path)"

# 4. Confirm image_gen section exists and is enabled
grep -A2 "^image_gen:" "$(hermes config path)"

# 5. Check .env for the actual key entry
grep -n "FAL_KEY\|KREA_API\|XAI_API" "$(hermes config env-path)"
```

All five should pass. If (1) says active but (2)-(4) fail, the gateway is providing image gen via Nous subscription without local plugin config — works but limits model selection.

## Aspect Ratios

| Hermes | FAL (preset) | Krea | xAI | OpenAI |
|--------|-------------|------|-----|--------|
| landscape | landscape_16_9 | 16:9 | 16:9 | 1536x1024 |
| square | square_hd | 1:1 | 1:1 | 1024x1024 |
| portrait | portrait_16_9 | 9:16 | 9:16 | 1024x1536 |

Krea additionally supports: 4:3, 3:2, 2.35:1, 4:5, 2:3.
xAI additionally supports: 4:3, 3:4, 3:2, 2:3.
