# Verified Model Specifications

Current provider specs as of July 2026. Verify against official docs before use — specs change.

## Alibaba Cloud DashScope (Qwen)

Source: `help.aliyun.com/zh/model-studio/` + Qwen Cloud integration metadata

| Model ID | Context | Max Output | Availability |
|---|---|---|---|
| `qwen3.8-max-preview` | 983,616 | 131,072 | Token Plan only |
| `qwen3.7-max` | 262,144 | — | General |
| `qwen3.7-plus` | 1,000,000 | — | General |
| `qwen3.6-plus` | 1,000,000 | — | General |

**Notes:**
- qwen3.8-max-preview has always-on reasoning (`low`/`high`/`xhigh`, default `xhigh`)
- Generic `"qwen"` catch-all in `DEFAULT_CONTEXT_LENGTHS` = 131,072
- Newer models not explicitly listed will hit the catch-all and show wrong context

## How to verify

1. Check provider's official documentation
2. Query provider's `/v1/models` endpoint if available
3. Test with actual API calls to confirm limits
4. Update this file when specs change

## Common errors to avoid

- **Don't guess model IDs** — fabricating `qwen3.8`, `qwen3.8-max`, `qwen3.8-plus` when the actual ID is `qwen3.8-max-preview`
- **Don't round context lengths** — 983,616 is not 1,000,000
- **Don't assume newer = larger** — qwen3.7-max (262K) < qwen3.7-plus (1M)
