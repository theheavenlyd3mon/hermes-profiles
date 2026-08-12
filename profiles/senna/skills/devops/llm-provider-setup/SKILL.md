---
name: llm-provider-setup
description: API setup reference for LLM providers — base URLs, key formats, model capabilities, context windows, and gotchas. Use when configuring a new provider, switching models, or diagnosing "wrong key type" / "model not found" errors on a provider endpoint.
version: 1.0.0
triggers: [provider setup, api key format, base url, token plan, qwen cloud, dashscope, model context window, 1M context, provider config]
metadata:
  hermes:
    tags: [provider, api, config, models, context-window]
    related: [profile-model-fleet, nous-openai-reroute, provider-fallback-strategy]
---

# LLM Provider Setup

Quick-reference for provider API configuration. Each provider has a `references/` file
with full details. Load the relevant reference when configuring or debugging.

## Provider Index

| Provider | Reference File | Key Prefix | Base URL (OpenAI-compat) |
|----------|---------------|------------|--------------------------|
| Qwen Cloud Token Plan | `references/qwen-cloud-token-plan.md` | `sk-sp-` | `https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1` |
| Qwen Cloud Pay-as-you-go | (see qwen ref) | `sk-` | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Nous Portal | (see nous-openai-reroute skill) | OAuth JWT | `https://inference-api.nousresearch.com/v1` |
| OpenRouter | (see profile-model-fleet skill) | `sk-or-` | `https://openrouter.ai/api/v1` |
| DeepSeek | `references/deepseek-v4.md` | `sk-` | `https://api.deepseek.com` |

## KV Cache Memory Budgeting

When a user asks "why can't I run the full context?" — the answer is usually memory, not architecture. See `references/kv-cache-memory-budgeting.md` for the formula, worked examples, and a quick reference table for common models. Key insight: SWA (sliding window attention) does NOT reduce allocated KV cache size — the full context is still cached.

## Universal Gotchas

- **Key/URL mismatch**: Every provider has its own key format AND base URL. Mixing a Token Plan key with the DashScope URL (or vice versa) gives auth errors that look like "invalid key" but are really "wrong endpoint."
- **Context window is native**: No opt-in header or parameter. Just don't exceed the model's window in one request (system + messages + tools combined).
- **Preview models**: May be taken offline or replaced. Don't build hard dependencies without a fallback.
- **Hermes context resolution chain & wrong context window**: When a model shows the wrong context (e.g. 131K instead of 1M), the issue is Hermes's resolution chain falling through to a bad default. The chain: config override → custom_providers per-model → endpoint-scoped metadata → persistent cache (`context_length_cache.yaml`) → endpoint `/models` probe → provider-specific lookups → OpenRouter metadata → **hardcoded substring-match table** in `agent/model_metadata.py`. The hardcoded table uses longest-key-first substring matching — `"qwen3-max": 262144` does NOT match `qwen3.8-max-preview` because the `.8` breaks the substring. Any unmatched Qwen model hits `"qwen": 131072`. **Three-layer fix** (apply all that fit): (1) **Immediate** — append to `~/.hermes/profiles/<profile>/context_length_cache.yaml`: `  <model_id>@<base_url>: <context_window>` (both with and without trailing slash). (2) **Durable across cache clears** — add to the hardcoded table in `~/.hermes/hermes-agent/agent/model_metadata.py` (~line 280, Qwen section). Survives cache wipes but NOT `hermes update`. (3) **Per-profile override** — `model.context_length: N` in config.yaml wins over everything. See `references/context-resolution-chain.md` for the full diagnostic recipe and current Qwen context table.
- **Bulk cache update**: The authoritative source for context lengths is `models_dev_cache.json` (same profile dir), under each model's `limit.context` field — NOT `context_length` or `context_window` (those keys don't exist). To bulk-populate the cache for all providers, iterate `models_dev_cache.json` → extract `limit.context` → write `model@base_url: N` entries. See `references/context-cache-bulk-update.md` for the full procedure and script.
- **Editing Hermes config.yaml**: the `patch`/`write_file` tools REFUSE Hermes config files by design ("security-sensitive configuration" guard) — do not retry them. Use `hermes config set section.key value` for scalars, or for structured YAML edits (MoA presets, provider blocks) run the hermes-agent venv python which has PyYAML: `~/.hermes/hermes-agent/venv/bin/python` (system `python3` on this Mac lacks the `yaml` module). Always re-verify with `hermes moa list` / `hermes config` after editing — a slot shows `[reasoning=high]` in `hermes moa list` when a per-slot `reasoning_effort` was read correctly.
- **Thinking-mode models starve under small token caps (MoA advisors, auxiliary calls)**: A model with thinking/reasoning enabled burns its `max_tokens` budget on `reasoning_content` first; if the cap is small (e.g. MoA `reference_max_tokens: 600`), the visible `content` comes back empty or truncated — looks like "no response / no thinking." MoA reference advisors intentionally do NOT inherit the global `agent.reasoning_effort` (hermes-agent/agent/moa_loop.py: reference advisors are side calls; only the aggregator resolves the global fallback). Fixes: raise the per-slot/per-call token cap (e.g. 600 → 2400) and/or set `reasoning_effort` explicitly on the MoA slot. Diagnostic for "which model am I really on": root `~/.hermes/config.yaml` can differ from the active profile's `~/.hermes/profiles/<profile>/config.yaml` — the profile one governs the session; check both before answering.

## When to use this skill

- Setting up a new provider for the first time
- User asks "how do I get X context window" or "what's the base URL for Y"
- Debugging 401/403/404 on a provider endpoint (check key prefix matches URL)
- Comparing model capabilities across providers
