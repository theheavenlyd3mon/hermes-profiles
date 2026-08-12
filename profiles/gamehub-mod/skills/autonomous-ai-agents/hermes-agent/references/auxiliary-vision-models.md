# Auxiliary Vision Model Options (OpenRouter)

When the main model doesn't support vision, Hermes falls back to an auxiliary vision model configured under `auxiliary.vision` in `config.yaml`.

## Recommended Cheap Vision Models on OpenRouter

### Primary pick: GPT-4.1 Nano

| Field | Value |
|-------|-------|
| **Model ID** | `openai/gpt-4.1-nano` |
| **Input price** | $0.10 / 1M tokens |
| **Output price** | $0.40 / 1M tokens |
| **Context** | 1M tokens |
| **Provider** | OpenAI / Azure |

Confirmed image+text input. Fast, huge context, reliable routing. At $0.10/M input, ~10 full-page screenshots cost under a penny. Hermes Agent itself is listed as a top consumer of this model on OpenRouter.

### Runner-up: Reka Edge

| Field | Value |
|-------|-------|
| **Model ID** | `rekaai/reka-edge` |
| **Input price** | $0.10 / 1M tokens |
| **Output price** | $0.10 / 1M tokens |
| **Context** | 16K tokens |
| **Provider** | Reka AI |

Specialized 7B vision-language model. Cheapest output pricing. Small context window — may struggle with complex/large images.

### Budget option with balanced pricing: Llama 3.2 11B Vision

| Field | Value |
|-------|-------|
| **Model ID** | `meta-llama/llama-3.2-11b-vision-instruct` |
| **Input price** | $0.245 / 1M tokens |
| **Output price** | $0.245 / 1M tokens |
| **Context** | 131K tokens |
| **Provider** | DeepInfra |

Symmetric pricing, decent context for a vision model.

## Config

```bash
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model openai/gpt-4.1-nano
```

If using a custom provider (e.g., Nous Portal), set `auxiliary.vision.provider` to the custom provider name and ensure the base URL and API key are configured in the custom providers section.

### Nous Portal Setup

For OAuth-based setup via the Nous Portal (portal.nousresearch.com), see:
- `references/nous-portal-vision-setup.md` — full config guide

> **Note**: The Nous Portal provides the same model at `openai/gpt-4.1-nano` via their inference API at `https://inference-api.nousresearch.com/v1`. OAuth credentials are stored in `auth.json`. No API key or base_url needed in config.yaml — Hermes reads them from the auth store automatically.
