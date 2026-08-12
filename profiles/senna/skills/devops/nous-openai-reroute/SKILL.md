---
name: nous-openai-reroute
description: Reroute any external tool or library that assumes the OpenAI SDK (litellm, dspy, langchain, openai Python client, etc.) to run against the Nous inference endpoint instead — with no Claude/OpenAI key. Covers the auth-store key location, the base URL, and the litellm double-prefix model-name trick. Use whenever an external OpenAI-SDK-based tool must run on this user's Nous subscription.
---

# Reroute OpenAI-SDK Tools to Nous

This user runs on the **Nous** provider (no OpenAI or Anthropic API key). Many external tools (DSPy, litellm, LangChain, raw `openai` client) call `api.openai.com` by default. Reroute them to Nous's OpenAI-compatible endpoint so they work without extra keys.

## When to use
- An external Python tool/library needs an `OPENAI_API_KEY` / `base_url` and you want it to hit Nous.
- You see `Missing credentials` or `Model not found` errors when pointing such a tool at Nous.

## Prereqs — the Nous key is NOT in config.yaml or .env
Hermes stores the Nous credential in `~/.hermes/auth.json` (OAuth), under:
```
providers.nous.agent_key             # the JWT to use as the OpenAI key
providers.nous.inference_base_url    # usually https://inference-api.nousresearch.com/v1
```
Load it at runtime — never commit it:
```python
import json, os
from pathlib import Path
auth = json.loads(Path(os.path.expanduser("~/.hermes/auth.json")).read_text())
nous = auth.get("providers", {}).get("nous", {})
key = nous.get("agent_key") or nous.get("access_token") or ""
os.environ["OPENAI_API_KEY"] = key
os.environ["OPENAI_BASE_URL"] = "https://inference-api.nousresearch.com/v1"
```
Note: terminal subprocesses do NOT inherit the key — Hermes resolves it via the auth store internally. You must read `auth.json` yourself in any external script.

## The critical trick — double model prefix
litellm (used by dspy, langchain, etc.) **strips ONE `openai/` prefix** before sending the model name. Nous expects the full `openai/gpt-4.1*` slug. So:
- ❌ `gpt-4.1-mini` → Nous receives `gpt-4.1-mini` → 404 "Model not found".
- ❌ `openai/gpt-4.1-mini` → litellm strips to `gpt-4.1-mini` → 404.
- ✅ `openai/openai/gpt-4.1-mini` → litellm strips one → Nous receives `openai/gpt-4.1-mini` → works.

Pass the **double prefix** as the model name: `openai/openai/gpt-4.1` (optimizer) and `openai/openai/gpt-4.1-mini` (eval/judge). For the raw `openai` Python client (NOT via litellm), use the single `openai/gpt-4.1-mini` — it does not strip.

## Verify
```python
from openai import OpenAI
c = OpenAI(api_key=key, base_url="https://inference-api.nousresearch.com/v1")
r = c.chat.completions.create(model="openai/gpt-4.1-mini", messages=[{"role":"user","content":"say OK"}])
print(r.choices[0].message.content)
```
For dspy: `dspy.LM("openai/openai/gpt-4.1-mini")` then confirm a trivial predict returns text.

## Gotchas
- **dspy 3.x** changed `GEPA.__init__` (no `max_steps`; now `max_full_evals` / `max_metric_calls`). Code calling the old signature raises and falls back to MIPROv2 — install `dspy[optuna]`, not just `dspy`, or the fallback fails on `ModuleNotFoundError: optuna`.
- Some tools cache the key at import time; set env BEFORE importing the tool, or pass `api_key=` / `api_base=` explicitly to the client constructor.
- The Nous endpoint proxies 270+ models (Claude, GPT, DeepSeek, Qwen, Llama) — prefer non-Claude/non-OpenAI slugs to honor this user's key situation; `openai/gpt-4.1*` is proxied and safe.

## References
- `references/repro-recipe.md` — exact error transcripts we hit (Missing credentials, Model not found, GEPA max_steps, optuna missing) and the minimal working snippet.
