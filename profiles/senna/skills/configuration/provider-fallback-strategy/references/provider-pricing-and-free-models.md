# Provider Pricing & Free Model Lists

**Last verified:** 2026-05-27

Prices change. Free models come and go. Re-verify before making config changes.

## How to Check OpenRouter Free Models

1. Browse: https://openrouter.ai/models — search "free", filter by Text
2. API: GET https://openrouter.ai/api/v1/models — filter where pricing.prompt == "0" and pricing.completion == "0"
3. Direct URL: https://openrouter.ai/deepseek/deepseek-v4-flash:free — check if still $0/$0

## OpenRouter Free Text Models (as of May 2026)

24 free text models available. Best picks for agent use:

| Model | Context | Notes |
|-------|---------|-------|
| DeepSeek V4 Flash (free) | 1.05M | Best general-purpose free model. 284B/13B active. |
| NVIDIA Nemotron 3 Super | 1M | Strong reasoning, large context. |
| Qwen3 Coder 480B A35B (free) | ~262K | Huge MoE, coding-focused. |
| Qwen3 Next 80B A3B (free) | 262K | General purpose, thinking model. |
| Google Gemma 4 31B (free) | 262K | Google's open model. |
| Google Gemma 4 26B A4B (free) | 262K | Smaller Gemma variant. |
| MiniMax M2.5 (free) | 205K | Chinese provider, good quality. |
| OpenAI gpt-oss-120b (free) | ~128K | OpenAI's open-source model. |
| OpenAI gpt-oss-20b (free) | ~128K | Smaller open-source. |
| NVIDIA Nemotron 3 Nano 30B A3B (free) | 256K | Multimodal (text/image/video/audio). |
| NVIDIA Nemotron Nano 9B V2 (free) | ~128K | Small, fast. |
| Poolside Laguna XS.2 (free) | 128K | Coding-focused. |
| Poolside Laguna M.1 (free) | 128K | Coding-focused. |
| Z.ai GLM 4.5 Air (free) | ~128K | ZhipuAI model. |
| Venice Uncensored (free) | ~128K | Uncensored variant. |
| LiquidAI LFM2.5-1.2B Thinking/Instruct (free) | 33K | Tiny models, limited context. |

**Going away soon:** Baidu CoBuddy (free) — May 29, 2026.

## DeepSeek API Pricing (direct, not via OpenRouter)

| Model | Input (cache miss) | Input (cache hit) | Output | Notes |
|-------|-------------------|-------------------|--------|-------|
| V4 Flash | $0.14/M | $0.0028/M | $0.28/M | 284B/13B active, 1M ctx |
| V4 Pro | $0.435/M (promo) | $0.003625/M | $0.87/M (promo) | 1.6T/49B active, 1M ctx |

**V4 Pro promo:** 75% off until May 31, 2026. After that: $1.74/M in, $3.48/M out.

At $10 budget:
- V4 Flash: ~71M input tokens or ~35M output tokens
- V4 Pro (promo): ~23M input tokens or ~11.5M output tokens
- V4 Pro (after promo): ~5.7M input tokens or ~2.9M output tokens

## OpenRouter Paid Model Pricing (popular, as of May 2026)

| Model | Input/M | Output/M | Context |
|-------|---------|----------|---------|
| Qwen3.7 Max | $1.25 | $3.75 | 1M |
| Grok Build 0.1 | $1.00 | $2.00 | 256K |
| Gemini 3.5 Flash | $1.50 | $9.00 | 1.05M |
| DeepSeek V4 Pro | $0.435 | $0.87 | 1.05M |
| DeepSeek V4 Flash | $0.10 | $0.20 | 1.05M |
| GPT-5.4 | $2.50 | $15.00 | 1.05M |
| GPT-5.4 Mini | $0.75 | $4.50 | 400K |
| Claude Opus 4.7 | $5.00 | $25.00 | 1M |
| Claude Sonnet 4.5 | $3.00 | $15.00 | 1M |

## Budget Longevity Estimates

For a typical agent session (~50K input + 20K output tokens per turn, ~20 turns/session = ~1M input + 400K output per session):

| Provider | Budget | Sessions (approx) |
|----------|--------|--------------------|
| MiMo v2.5 Pro (82B grant) | ~82B tokens | ~82,000 sessions (effectively unlimited for one user) |
| DeepSeek API $10 (V4 Flash) | $10 | ~89 sessions |
| DeepSeek API $10 (V4 Pro promo) | $10 | ~28 sessions |
| OpenRouter free | $0 | Unlimited (rate-limited, queue-based) |
| Nous Portal $9 | $9 | Depends on model used |
