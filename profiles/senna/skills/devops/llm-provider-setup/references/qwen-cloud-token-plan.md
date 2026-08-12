# Qwen Cloud Token Plan — Provider Setup

Source: https://docs.qwencloud.com (reviewed 2026-07-21)

## Key Distinction (most common failure)

Token Plan keys (`sk-sp-*`) ≠ regular Qwen Cloud/DashScope keys (`sk-*`).
Separate billing, separate base URLs. Mixing key+URL across the two gives
auth errors that look like "invalid key" but are really "wrong endpoint."
Token Plan / Coding Plan / pay-as-you-go are three fully separate systems.

## Base URLs

| Protocol | Base URL |
|----------|----------|
| OpenAI compatible | `https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1` |
| Anthropic compatible | `https://token-plan.ap-southeast-1.maas.aliyuncs.com/apps/anthropic` |

Regular (pay-as-you-go) DashScope URL for comparison:
`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## Models & Context Windows (Token Plan)

| Model | Context | Max Output | Notes |
|-------|---------|------------|-------|
| qwen3.8-max-preview | 983,616 | 131,072 | Token Plan ONLY. Thinking always on. Min temp 0.6. reasoning_effort: xhigh/high/low |
| qwen3.7-max | 1,000,000 | 65,536 | |
| qwen3.7-plus | 1,000,000 | 65,536 | Vision (text+image) |
| qwen3.6-flash | 1,000,000 | 32,768 | Vision (text+image) |
| glm-5.2 | 1,000,000 | 16,384 | Third-party |
| deepseek-v4-pro | 163,840 | 32,768 | Third-party |

## 1M Context — No Special Config Needed

The 1M context is the model's native window. Just send up to the limit in one
request (system + messages + tools combined). No header, parameter, or opt-in.

## Hermes Context Cache Fix (silent context loss)

**Symptom**: A model reports a context window equal to its max *output* tokens
(e.g. qwen3.8-max-preview shows 131.1k instead of ~1M), causing early
compaction / context truncation.

**Root cause**: Hermes resolves a model's context window from
`~/.hermes/profiles/<profile>/context_length_cache.yaml`. If the model+base_url
has NO entry there, it falls back to a default that can equal the model's max
output tokens — NOT its real context window. The cache is keyed by
`<model_id>@<base_url>`, so a model served from a NEW base URL (like Token Plan)
won't match entries cached for the same model on a different endpoint.

**Fix**: add the correct context window to the cache under `context_lengths:`.
Add both with and without a trailing slash on the base URL (Hermes keys both):

```yaml
context_lengths:
  qwen3.8-max-preview@https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1: 983616
  qwen3.8-max-preview@https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/: 983616
```

Use the real context value from the table above (983616 for qwen3.8-max-preview,
1000000 for the qwen3.7/3.6 line). Takes effect on next session start (`/new`).

**Diagnose**: `grep -A30 'context_lengths:' ~/.hermes/profiles/<profile>/context_length_cache.yaml`
and confirm the active model+base_url pair is present. If absent, that's the bug.

## qwen3.8-max-preview Specifics

- **Token Plan exclusive** — not available via pay-as-you-go API
- Thinking mode: always enabled, cannot disable
- Temperature: defaults to 0.6, values below 0.6 auto-adjusted up
- `reasoning_effort`: xhigh (default), high, low
- Preview status: model may be replaced or taken offline after preview ends

## Personal Edition Tiers (limited-time pricing, July 2026)

| Tier | Price | 5hr Quota | 7-day Quota | Concurrent Agents |
|------|-------|-----------|-------------|-------------------|
| Lite | $6/mo | 700 credits | 2,500 | 1-2 |
| Standard | $18/mo | 3,000 credits | 10,000 | 3-4 |
| Pro | $68/mo | 12,000 credits | 40,000 | 6-8 |

Quota is sliding-window (5hr + 7-day), NOT monthly — service pauses when either
caps. Team Edition uses monthly quotas, no sliding window, higher per-seat cost.

Preview promo: qwen3.8-max-preview costs 10% of normal credits (10x capacity).
Night discount (22:00–08:00): additional 80% off on top of existing 90% off.

## Hermes Config Template

```yaml
model:
  provider: alibaba
  default: qwen3.8-max-preview
  base_url: https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
```

## Quick Test (OpenAI SDK)

```python
from openai import OpenAI
client = OpenAI(
    api_key="sk-sp-...",
    base_url="https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1",
)
resp = client.chat.completions.create(
    model="qwen3.8-max-preview",
    messages=[{"role": "user", "content": "Hello"}],
)
```

## Links

- Hermes integration: https://docs.qwencloud.com/developer-guides/clients-and-developer-tools/hermes-agent
- API keys console: https://home.qwencloud.com/api-keys
- Token Plan purchase: https://home.qwencloud.com/token-plan
