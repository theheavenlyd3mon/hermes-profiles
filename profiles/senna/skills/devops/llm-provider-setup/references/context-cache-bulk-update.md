# Context Length Cache — Bulk Update Procedure

## Problem
`context_length_cache.yaml` only has entries for models that have been manually
added or auto-discovered. Many models across providers are missing, causing
silent fallback to wrong defaults (often max_output_tokens, not context window).

## Data Source
`~/.hermes/profiles/<profile>/models_dev_cache.json` — the authoritative source.
Structure: `{provider_id: {models: {model_id: {limit: {context: N, output: N}}}}}`

**PITFALL**: The context length is at `limit.context`, NOT `context_length`,
`context_window`, or `max_context`. Those keys do not exist. Always check
`mdata.get('limit', {}).get('context')`.

## Cache File Format
`~/.hermes/profiles/<profile>/context_length_cache.yaml`:
```yaml
context_lengths:
  model_id@base_url: context_window
  model_id@base_url/: context_window   # trailing-slash variant (Hermes checks both)
```

## Procedure
1. Read `models_dev_cache.json` — iterate all providers, extract `limit.context` per model.
2. Map each provider to its base URL(s) from `config.yaml` (`model.base_url`, `providers.*.base_url`).
3. For each model+URL pair, write `model@url: N` and `model@url/: N`.
4. Sort keys alphabetically, write YAML.
5. Verify: parse the file, count entries, confirm key models present.
6. Takes effect on next session (`/new`).

## Base URL Mapping (senna profile, as of 2026-07)
| Provider | Base URL |
|----------|----------|
| alibaba (token-plan) | `https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1` |
| nous (inference API) | `https://inference-api.nousresearch.com/v1` |
| openrouter | `https://openrouter.ai/api/v1` |
| local (qwen3.6-27b) | `http://100.121.222.33:8001/v1` |

## Notable Context Windows (quick reference)
| Model | Context |
|-------|---------|
| qwen3.8-max-preview | 1,000,000 |
| qwen3.7-max/plus | 1,000,000 |
| qwen3.6-plus/flash | 1,000,000 |
| qwen3.5-plus | 1,000,000 |
| qwen3-coder-plus | 1,048,576 |
| kimi-k3 | 1,048,576 |
| deepseek-v4-pro/flash | 1,048,576 |
| claude opus-4.7/4.8, sonnet-5/4.6/4.5, fable-5 | 1,000,000 |
| claude haiku-4.5 | 200,000 |
| glm-5.2 | 1,000,000 |
| minimax-m3 | 1,048,576 |
| grok-4.3 | 1,000,000 |
| grok-4.5 | 500,000 |
| GPT-5.5/5.6 family | 1,050,000 |
| gemini-3.1-pro/3.5-flash | 1,048,576 |
| nemotron-3-super/ultra | 1,000,000 |

## Script
See `scripts/rebuild_context_cache.py` — reads models_dev_cache.json + config.yaml,
generates the full context_length_cache.yaml.
