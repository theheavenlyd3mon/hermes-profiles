# Auxiliary Vision Model Configuration

## What It's For

When the active model doesn't support native vision (like `deepseek-v4-flash`),
the `vision_analyze` tool is supposed to fall back to a configured auxiliary
vision model. Without one configured, it fails with:

```
unknown variant `image_url`, expected `text`
```

This means the fallback resolved to a text-only model.

## The Config

The relevant section in `config.yaml`:

```yaml
auxiliary:
  vision:
    api_key: ''           # Uses main provider key if blank
    base_url: ''
    provider: auto        # "auto" resolves to the main provider (often text-only)
    model: ''             # Empty → uses provider default (often text-only)
    timeout: 120
```

With `provider: auto` and `model: ''`, the fallback tries the same provider
as the main model — which almost certainly doesn't support images.

## The Fix

Set a vision-capable provider and model explicitly:

```bash
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model openai/gpt-4o
```

Or for Anthropic via OpenRouter:
```bash
hermes config set auxiliary.vision.model anthropic/claude-sonnet-4
```

Or if you have an Anthropic key configured directly:
```bash
hermes config set auxiliary.vision.provider anthropic
hermes config set auxiliary.vision.model claude-sonnet-4-20250514
```

## Verifying It Works

After configuring, test with any image:

```bash
hermes config | grep -A5 "vision"
# Expect: auxiliary.vision.provider → openrouter
# Expect: auxiliary.vision.model → openai/gpt-4o
```

Then call `vision_analyze` on a known-good image URL. The main model still
handles the conversation; only the image payload routes to the auxiliary model.

## Common Providers for Vision Fallback

| Provider | Model (example) | Notes |
|----------|-----------------|-------|
| OpenRouter | `openai/gpt-4o` | Works if OpenRouter API key is configured |
| OpenRouter | `anthropic/claude-sonnet-4` | Also via OpenRouter |
| Anthropic | `claude-sonnet-4-20250514` | Requires ANTHROPIC_API_KEY |
| OpenAI | `gpt-4o` | Requires OPENAI_API_KEY |
| Google | `gemini-2.5-pro` | Requires Google AI API key |

## Pitfalls

- **`provider: auto` is rarely what you want for vision** — it inherits the
  main provider, which is probably text-only. Always set explicitly.
- **The auxiliary vision model must accept `image_url` in messages.** Not all
  providers handle this format — test after configuring.
- **Changes take effect on next agent turn**, not mid-conversation. Restart
  or /reset after changing the config.
- **Cost:** Vision model calls count against that provider's billing. If using
  OpenRouter, image analysis will appear in OpenRouter usage, not the main
  provider's usage.
