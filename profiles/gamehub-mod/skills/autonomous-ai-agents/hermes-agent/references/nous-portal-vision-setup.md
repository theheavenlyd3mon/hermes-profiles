# Nous Portal + Auxiliary Vision Model

## Overview

The Nous Portal (`portal.nousresearch.com`) provides OpenAI-compatible inference via OAuth authentication. When the main model doesn't support vision, Hermes falls back to an auxiliary vision model. This reference documents using the Nous Portal as the auxiliary vision provider.

## OAuth Setup

Run from the target profile:

```bash
hermes login --provider nous
```

This completes a device-code OAuth flow. Credentials are stored in the profile's `auth.json`:

```json
{
  "providers": {
    "nous": {
      "access_token": "eyJ...",
      "refresh_token": "rt_...",
      "client_id": "hermes-cli",
      "portal_base_url": "https://portal.nousresearch.com",
      "inference_base_url": "https://inference-api.nousresearch.com/v1",
      "token_type": "Bearer",
      "agent_key": "sk-nou...",
      "agent_key_expires_at": "2026-05-15T01:35:15.623Z"
    }
  }
}
```

The `inference_base_url` is the actual API endpoint. The agent key is auto-minted.

## Configuring the Auxiliary Vision Model

```bash
hermes config set auxiliary.vision.provider nous
hermes config set auxiliary.vision.model openai/gpt-4.1-nano
```

Result in `config.yaml`:

```yaml
auxiliary:
  vision:
    api_key: ''
    base_url: ''
    download_timeout: 30
    extra_body: {}
    model: openai/gpt-4.1-nano
    provider: nous
    timeout: 120
```

The `api_key` and `base_url` fields are left empty — Hermes reads the credentials from `auth.json` (OAuth token + inference base URL) automatically.

## Recommended Model: GPT-4.1 Nano

| Property | Value |
|----------|-------|
| Model ID | `openai/gpt-4.1-nano` |
| Input price | $0.10 / 1M tokens |
| Output price | $0.40 / 1M tokens |
| Context | 1,047,576 tokens |
| Modalities | text, image, file |

Available through the Nous Portal's inference API. Confirmed via `GET /v1/models`. Supports image analysis at ~10 full-page screenshots per penny.

## How It Works

When the main agent model (e.g., `deepseek-v4-flash`) receives a `vision_analyze` call and doesn't support images natively, Hermes:
1. Routes the image to the auxiliary vision model
2. The model ID `openai/gpt-4.1-nano` is sent to the Nous inference base URL
3. The OAuth Bearer token from `auth.json` is attached automatically
4. Returns a text description to the main agent

## Available Vision Models on Nous Portal

The Nous inference API hosts many vision-capable models. The cheapest ones (under $0.50/M input) include:

- `openai/gpt-4.1-nano` — $0.10/M, 1M ctx
- `openai/gpt-5-nano` — $0.05/M, 400K ctx
- `google/gemini-3.1-flash-lite` — $0.25/M, 1M ctx
- `qwen/qwen3.5-flash-02-23` — $0.065/M, 1M ctx
- `rekaai/reka-edge` — $0.10/M, 16K ctx
