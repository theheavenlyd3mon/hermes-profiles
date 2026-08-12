---
name: hermes-model-config
description: Diagnose and fix Hermes model configuration issues — context length display errors, provider setup, custom_providers overrides, and model ID verification. Use when model picker shows wrong context length, provider endpoints fail, or you need to add new models to Hermes configuration.
version: 1.0.0
---

# Hermes Model Configuration

Diagnose and fix model configuration issues in Hermes: context length display errors, provider setup, custom_providers overrides, and model ID verification.

## When to use
- Model picker shows wrong context length (e.g., 128K instead of 1M)
- Adding new model providers to Hermes
- Troubleshooting provider endpoint failures
- Need to override default context lengths for specific models

## Context-length resolution chain

Hermes resolves context length via `get_model_context_length()` in `agent/model_metadata.py`:

1. **`model.context_length`** in config.yaml (global override — affects ALL models, use carefully)
2. **`custom_providers[].models.<id>.context_length`** (per-model override — preferred)
3. Persistent cache (`~/.hermes/context_length_cache.yaml`)
4. Endpoint `/v1/models` probe (queries provider's live metadata)
5. Provider-aware lookups (Anthropic, Nous, Copilot, models.dev)
6. OpenRouter live API
7. **`DEFAULT_CONTEXT_LENGTHS`** table (hardcoded fallback, line ~211 in `model_metadata.py`)
8. Default fallback: 256K

## Diagnosis steps

1. **Check `DEFAULT_CONTEXT_LENGTHS`** — is the model ID present? Generic catch-alls (e.g., `"qwen": 131072`) fire via longest-substring match and often give wrong values for newer models.

2. **Check endpoint's `/v1/models`** — does it return `context_length` metadata? Some providers (Alibaba DashScope, some local servers) don't include it.

3. **Verify actual context length from official provider docs** — never guess.

## Fix: custom_providers per-model override

```yaml
# In config.yaml (profile-level)
custom_providers:
  - name: alibaba
    base_url: https://<workspace>.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
    models:
      qwen3.8-max-preview:
        context_length: 983616
```

## Critical rule: verify before adding

**Always verify exact model IDs and context lengths from official provider documentation before adding config entries.**

Fabricated IDs or guessed values create silent misbehavior:
- Wrong compression thresholds
- Premature context cuts
- Provider endpoint failures

Check:
- Official provider API docs
- Model catalog/marketplace pages
- Provider's `/v1/models` endpoint (if available)

## Verified specs (Alibaba DashScope / Qwen Cloud, July 2026)

| Model ID | Context | Max Output | Notes |
|---|---|---|---|
| `qwen3.8-max-preview` | 983,616 | 131,072 | Token Plan only; always-on reasoning |
| `qwen3.7-max` | 262,144 | — | General availability |
| `qwen3.7-plus` | 1,000,000 | — | General availability |
| `qwen3.6-plus` | 1,000,000 | — | General availability |

Source: Qwen Cloud Codex integration metadata + `help.aliyun.com/zh/model-studio/` docs.

## Common pitfalls

- **Generic catch-alls** — `"qwen"` in `DEFAULT_CONTEXT_LENGTHS` = 131,072. Newer Qwen models not explicitly listed will hit this.

- **Global overrides** — `model.context_length` in config.yaml applies to every model, not just the default. Use `custom_providers` for per-model control.

- **Missing endpoint metadata** — Some providers' `/v1/models` doesn't include `context_length` field, so probes return no data.

- **Guessing values** — Never fabricate model IDs or context lengths. Verify against official docs first.

## Workflow

1. User reports wrong context length display
2. Check if model ID exists in `DEFAULT_CONTEXT_LENGTHS`
3. If missing or wrong, verify correct specs from official provider docs
4. Add `custom_providers` entry with verified values
5. Restart Hermes for changes to take effect

## Support files

See `references/verified-model-specs.md` for current provider model specs.
