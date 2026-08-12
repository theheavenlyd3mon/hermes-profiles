# Hermes Context Length Resolution Chain

Diagnostic recipe for "model shows wrong context window in Hermes."

## Resolution order (agent/model_metadata.py::get_model_context_length)

0. `model.context_length` in config.yaml (explicit override — always wins)
0b. `custom_providers[i].models.<model>.context_length` (per-model override)
0c. Endpoint-scoped metadata (hardcoded per endpoint+model pairs, e.g. k3@kimi.com/coding → 1M)
1. Persistent cache: `~/.hermes/profiles/<profile>/context_length_cache.yaml`
2. Active endpoint `/models` probe (for custom base_urls)
3. Local server query (LM Studio, Ollama, vLLM)
4. Anthropic `/v1/models` API
5. Provider-specific: Copilot, Nous live probe, Codex OAuth, GMI, Ollama native, models.dev
6. OpenRouter live API metadata
7. Local server query (second pass, before hardcoded defaults)
8. **Hardcoded substring-match defaults** (the usual culprit for wrong values)
9. Final fallback: 256K

## The hardcoded table (step 8)

Located in `~/.hermes/hermes-agent/agent/model_metadata.py` ~line 250-350.
Substring matching, longest-key-first. Current Qwen entries (2026-07-28):

```python
"qwen3.8-max-preview": 1000000,  # 1M context (Token Plan only)
"qwen3.7-plus": 1048576,
"qwen3.7-max": 1000000,
"qwen3.6-plus": 1048576,
"qwen3-coder-plus": 1000000,
"qwen3-coder": 262144,
"qwen3-max": 262144,          # qwen3-max-2026-01-23 snapshot, Coding Plan
"qwen": 131072,               # CATCH-ALL — any unmatched qwen model
```

**Substring trap**: `"qwen3-max"` does NOT match `"qwen3.8-max-preview"` because
the match requires the key to appear as a contiguous substring. The `.8` breaks it.
Any new Qwen model without an explicit entry hits `"qwen": 131072`.

## Diagnostic recipe

```bash
# 1. What does Hermes think the context is?
grep "qwen3.8" ~/.hermes/profiles/<profile>/context_length_cache.yaml

# 2. Is it in the hardcoded table?
grep -n "qwen3.8\|qwen3\.8" ~/.hermes/hermes-agent/agent/model_metadata.py

# 3. What does the provider docs say?
# Qwen: https://docs.qwencloud.com/developer-guides/getting-started/text-generation-models

# 4. Fix — seed the cache (immediate):
cat >> ~/.hermes/profiles/<profile>/context_length_cache.yaml << 'EOF'
  <model_id>@<base_url>: <context_window>
  <model_id>@<base_url>/: <context_window>
EOF

# 5. Fix — patch the hardcoded table (durable across cache clears):
# Add entry in the Qwen section of model_metadata.py, BEFORE the "qwen" catch-all.
# Longest-key-first ordering means more specific keys automatically win.

# 6. Fix — config override (per-profile, wins over everything):
# hermes config set model.context_length 1000000
```

## Qwen context windows (verified from docs.qwencloud.com, 2026-07-28)

| Model | Context | Max Output | Notes |
|-------|---------|------------|-------|
| qwen3.8-max-preview | 1M | 64k | Token Plan only |
| qwen3.7-max | 1M | 64k | |
| qwen3.7-plus | 1M | 64k | |
| qwen3.7-flash | 1M | 64k | |
| qwen3.6-flash | 1M | 64k | |
| qwen3.6-max-preview | 256k | 64k | |
| qwen3.6-plus | 1M | 64k | |
| qwen3-coder-plus | 1M | 64k | |
| qwen3-coder-flash | 1M | 64k | |
| qwen3-coder-next | 256k | 64k | |
| qwen3-max | 256k | 64k | Legacy |
| qwen3-235b-a22b | 128k | 16k/32k | Open source |
| qwen3-32b | 128k | 16k | Open source |

## Pitfalls

- **`hermes update` overwrites model_metadata.py** — hardcoded table patches are
  lost on update. The persistent cache (context_length_cache.yaml) survives.
  After update, verify new/preview models still resolve correctly.
- **Token Plan endpoint `/models` may not report context_length** — the Alibaba
  token-plan API returns model IDs but not always context metadata, so the
  endpoint probe (step 2) returns nothing and you fall through to step 8.
- **Both trailing-slash and no-slash variants needed** in the cache file —
  Hermes normalizes base_urls inconsistently across code paths.
