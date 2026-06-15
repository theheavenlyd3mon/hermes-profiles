---
name: nvidia-nim-expert
description: Expert guidance for using NVIDIA NIM (NVIDIA Inference Microservices) — cloud-hosted AI models via OpenAI-compatible API. Covers environment setup, model discovery, API usage, local NIM deployment, and integration patterns.
version: 1.0.0
author: Senna
license: MIT
metadata:
  hermes:
    tags: [nvidia, nim, inference, api, cloud-models, openai-compatible]
    related_skills: [ollama-cloud-expert, openrouter-expert, serving-llms-vllm]
---

IDENTITY: Guide.NVIDIANIMExpert. Discover→Verify→Configure→Integrate:NeverHardcodeModelIDs.
Law: AlwaysFetchLiveModelList.First.CheckForNativeProvider.HermesAlreadyHasNvidiaProvider.
WHENUSE: User mentions NVIDIA NIM/NIM cloud models|NVIDIA API key|Model selection on NVIDIA|NIM vs local deploy. ESPECIALLY:DeepSeek on NVIDIA|Model discovery|Endpoint config. NoSkip:LiveModelFetch|HermesNativeProviderCheck|CloudVsLocalDistinction.
REDFLAGS: HardcodedModelNames->FetchLiveList|WrongKeySource(NGC vs AI Foundation)->DifferentPortals|WrongEndpoint(cloud vs local)->Cloud=NIM_API,Local=localhost:8000|MissingV1Suffix->SDKsExpectBaseURL/v1.
RATIONALIZATIONS: DocumentationIsCurrent->ModelsRotateFrequently|OneAPIKeyWorks->NGCvsAI-FoundationKeysDiffer|SetupSameAsOpenAI->HermesHasNativeNvidiaProvider.
QUICKREF: Discovery(fetch /v1/models)➔Verify(auth+endpoint)➔Configure(env vars or Hermes native provider)➔Integrate(OpenAI SDK pattern or Hermes /model).

# NVIDIA NIM Expert

Agent resolver skill for using NVIDIA's cloud-hosted inference microservices (NIM) and local NIM deployment patterns.

NIM provides OpenAI-compatible endpoints for NVIDIA-optimized models across text, vision, embedding, and multimodal use cases.

**Skill origin:** Created by applying the provider adapter pattern from `openrouter-expert` via the `create-provider-skill` meta-skill. See that skill for the systematic approach used.

---

## A. When to load this skill

**Trigger immediately when:**
- User mentions "NVIDIA NIM", "NVIDIA cloud models", or the NIM catalog URL (build.nvidia.com/models)
- User wants to use NVIDIA-hosted AI models instead of local inference
- User asks about the NVIDIA AI Foundation endpoint or `integrate.api.nvidia.com`
- User has an NVIDIA API key and wants to integrate it with Hermes
- User asks about deploying NIM locally vs using cloud NIM
- User asks about model selection (Nemotron, Llama, Code, DeepSeek, etc.) on NVIDIA's platform
- User asks about cost, latency, or rate limits for NVIDIA NIM
- User mentions "DeepSeek on NVIDIA" or wants to run DeepSeek V3/V4 via cloud

**Implied intent (even if NVIDIA not named):**
- "run models on NVIDIA GPUs in the cloud"
- "use nvidia.com API for LLMs"
- "deploy a NIM container"
- "NGC models inference endpoint"
- "NIM microservices"
- "use DeepSeek cloud models"

**Do NOT load for:**
- Generic NVIDIA CUDA/pyTorch questions without NIM/API context
- Local GPU driver setup without NIM
- Questions about Triton Inference Server (separate from NIM)

---

## B. Pre-answer ritual — mandatory before any technical claim

1. **Verify current model catalog** — fetch `https://integrate.api.nvidia.com/v1/models` (requires API key) to see available models, context lengths, pricing, and capabilities. Never hardcode model IDs.
2. **Read live docs first** — check NVIDIA's official NIM documentation at `https://docs.nvidia.com/nim/latest/` for current API details, auth patterns, and rate limits.
3. **Confirm pricing from live source** — pricing is per-token and changes; always read from the models endpoint response or NVIDIA's pricing page.
4. **Distinguish NIM types** — Cloud NIM (hosted at `integrate.api.nvidia.com`) vs Local NIM (Docker container, `localhost:8000`). They share the same OpenAI-compatible API but different endpoints and deployment models.
5. **When environment variables matter** — always provide both `OPENAI_API_KEY`/`NVIDIA_API_KEY` and `OPENAI_BASE_URL`/`NVIDIA_BASE_URL` forms; Hermes uses `OPENAI_*` as canonical names for OpenAI-compatible backends.

---

## C. Core API surface — stable basics

### Cloud NIM endpoints

**Base endpoint** (OpenAI-compatible):
```
https://integrate.api.nvidia.com/v1
```

**Environment variables:**
```bash
export OPENAI_API_KEY="$NVIDIA_API_KEY"      # or NVIDIA_API_KEY directly
export OPENAI_BASE_URL="https://integrate.api.nvidia.com/v1"
```

**Authentication:**
- Header: `Authorization: Bearer $NVIDIA_API_KEY`
- Key obtained from NVIDIA Developer portal (build.nvidia.com)

**Key endpoints:**
- `POST /chat/completions` — chat completions (OpenAI format)
- `POST /embeddings` — create vector embeddings
- `GET /models` — list available models (requires auth)

### Local NIM endpoints

**Base endpoint** (for NIM containers):
```
http://localhost:8000/v1
```

**NVIDIA API Catalog:**
- Web UI: `https://build.nvidia.com/models`
- CLI: `ngc` (NVIDIA GPU Cloud CLI) for model pulls and container management

---

## D. Model types and naming conventions

NIM organizes models by provider-prefixed family names. Model IDs follow the pattern `provider/model-name-version`:

Current verified working examples (April 2026):
- `google/gemma-3-12b-it` — Gemma 3 12B instruction-tuned
- `meta/llama-3.3-70b-instruct` — Llama 3.3 70B instruction-tuned
- `mistralai/mistral-large-3-675b-instruct-2512` — Mistral Large 3 675B (2501 context)
- `deepseek-ai/deepseek-v3.2` — DeepSeek V3.2 full reasoning model (~235B params, 128K context)
- `deepseek-ai/deepseek-v4-flash` — DeepSeek V4 lightweight model, fast responses (~0.9s)
- `deepseek-ai/deepseek-v3.1-terminus` — DeepSeek V3.1 chat variant

Additional families you'll commonly see:
- `nvidia/nemotron-4-340b-instruct` — Nemotron 4 340B
- `microsoft/phi-3-mini-4k-instruct` — Phi-3 Mini (4K context)
- `meta/llama-3.1-70b-instruct` — Llama 3.1 70B (may be retired; verify)
- `01-ai/yi-large` — Yi 34B (retired April 2026, returns 410 Gone)

**DeepSeek access note:** `deepseek-ai/deepseek-v4-pro` returns HTTP 400 ("Function id") — this indicates a tiered-access model requiring a higher subscription level on NVIDIA's platform. Stick to V3.2 and V4-flash for general use.

**Critical:** Always fetch the live model list (`GET /v1/models`) to get exact IDs. NVIDIA rotates models frequently — names change, old models are deactivated (410), and new models may appear in the catalog but not yet be deployed (404). Never hardcode model IDs without a live lookup.

---

## E. Integration patterns

### 0. Hermes native provider (recommended)

Hermes already includes a built-in `nvidia` provider. No custom skill or config.yaml needed. Just ensure `NVIDIA_API_KEY` is in your shell environment:

```bash
# One-time: add to ~/.zshrc
echo 'source ~/.config/nim/env.sh' >> ~/.zshrc
source ~/.zshrc

# Then use Hermes directly
hermes chat --provider nvidia --model nvidia/deepseek-ai/deepseek-v3.2 -q "Hello"
```

Or interactively inside Hermes:
```
> /model nvidia/deepseek-ai/deepseek-v3.2
> Your question here...
```

**Why this works:** Hermes `providers.py` defines `nvidia` with:
- `base_url_override = "https://integrate.api.nvidia.com/v1"`
- `base_url_env_var = "NVIDIA_BASE_URL"` (optional)
- API key read from `NVIDIA_API_KEY` env var (from models.dev catalog)

**Security:** Keys stay in your shell environment, never written to files.

### 1. Direct OpenAI SDK usage

The simplest integration — point OpenAI-compatible clients at NVIDIA's endpoint:

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY")  # or OPENAI_API_KEY
)

response = client.chat.completions.create(
    model="meta/llama3-70b-instruct",
    messages=[{"role": "user", "content": "Hello from NIM!"}],
    temperature=0.7,
    max_tokens=1024
)
print(response.choices[0].message.content)
```

### 2. Hermes profile configuration

Add to your Hermes agent profile (e.g., `~/.hermes/profiles/senna/profile.js` or environment):

```bash
# In your shell profile (~/.zshrc, ~/.bashrc, or Hermes env)
export NVIDIA_API_KEY="nv-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export OPENAI_BASE_URL="https://integrate.api.nvidia.com/v1"
# Optional: NVIDIA_BASE_URL for clarity
export NVIDIA_BASE_URL="https://integrate.api.nvidia.com/v1"
```

Then Hermes tools that rely on an OpenAI-compatible backend will use NVIDIA's models by default.

### 3. PydanticAI / LlamaIndex / LangChain integration

All frameworks that support OpenAI-compatible bases work identically:

```python
# PydanticAI example
from pydantic_ai import Agent
import os

agent = Agent(
    'openai:meta/llama3-70b-instruct',
    model_kwargs={
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'api_key': os.environ['NVIDIA_API_KEY']
    }
)
```

---

## F. Task-to-docs routing table

| Task | Primary Docs | Notes |
|------|---------------|-------|
| Getting started with Cloud NIM | https://docs.nvidia.com/nim/latest/cloud/overview.html | Quickstart, auth, API usage |
| Model catalog & available models | https://build.nvidia.com/models | Always prefer live `/v1/models` API for exact IDs |
| Local NIM deployment (Docker) | https://docs.nvidia.com/nim/latest/deploy.html | Pull containers, run locally |
| Rate limits & quotas | https://docs.nvidia.com/nim/latest/cloud/usage.html | Per-model and per-key limits |
| Pricing information | https://build.nvidia.com/pricing | Per-token costs, cached vs uncached |
| API reference (chat, embeddings) | https://docs.nvidia.com/nim/latest/cloud/api.html | Request/response schemas |
| Error codes & troubleshooting | https://docs.nvidia.com/nim/latest/cloud/errors.html | Common failure modes |
| Tool calling with function calls | https://docs.nvidia.com/nim/latest/cloud/tool-calling.html | Supported models only |
| Vision / multimodal models | https://docs.nvidia.com/nim/latest/cloud/multimodal.html | Image inputs, vision tasks |

---

## G. Common gotchas — failure modes to prevent

**Authentication errors:**
- ❌ Using `NVIDIA_API_KEY` directly without also setting `OPENAI_API_KEY` — some SDKs expect the OpenAI-named variable. Set both.
- ❌ Forgetting to prefix the base URL with `/v1` — SDKs assume `https://api.openai.com/v1`; NVIDIA uses `https://integrate.api.nvidia.com/v1`.
- ❌ Using a key from the NGC portal (for container pulls) instead of the NVIDIA AI Foundation portal (for API access). They are different keys.

**Model ID mistakes:**
- ❌ Hardcoding model names without checking availability — models rotate frequently. Always call `GET /models` first to discover what's live.
- ❌ Using shorthand names like `llama3-70b` — full provider-prefixed names are required (`meta/llama3-70b-instruct`).
- ❌ Assuming free tier or free variants exist — NIM is largely pay-per-use; verify pricing per model.

**Endpoint confusion:**
- ❌ Using localhost:8000 for cloud NIM — cloud NIM talks to `integrate.api.nvidia.com`.
- ❌ Using `integrate.api.nvidia.com` for locally deployed NIM containers — those run at `localhost:8000`.
- ❌ Mixing up Triton Inference Server endpoints with NIM endpoints — Triton uses different REST API.

**Integration gotchas:**
- ❌ Setting `base_url` at the client level but also in `model_kwargs` — pass it once (client or model, not both, to avoid clashes).
- ❌ Relying on provider-specific OpenAI features that aren't implemented identically in NIM — streaming works; structured outputs vary by model.
- ❌ Expecting all NVIDIA models to support vision, function calling, or extended context — check the capabilities in the models response.

**Rate limits & costs:**
- ❌ Undercounting tokens — NIM uses the same tokenizers as the base models, but NVIDIA-specific variants may have slight differences.
- ❌ Running long conversations without cost awareness — NIM billing is per-token; monitor usage in the NVIDIA developer dashboard.

**Hermes-specific gotchas:**
- ❌ Assuming NVIDIA models are "just another provider" — Hermes has a native `nvidia` provider already defined in `providers.py` with `base_url_override` to `integrate.api.nvidia.com/v1`. You do NOT need a custom skill or config.yaml entry to use NVIDIA models; just set `NVIDIA_API_KEY` in your shell environment (never store keys in plaintext config files).
- ❌ **Empty `OPENAI_BASE_URL=` in `~/.hermes/.env` overrides the nvidia provider's hardcoded base URL.** If `OPENAI_BASE_URL=` (set to empty string) exists in the root Hermes env, it silently breaks the nvidia provider — Hermes reads it and uses the empty URL instead of the provider's built-in base URL. **Fix:** comment out any empty `OPENAI_BASE_URL=` line in the env file so it's not sourced. The nvidia provider has its own base URL baked in and doesn't need it.
- ❌ Relying on `~` expansion in scripts — Hermes sandboxes `$HOME` to the profile directory (`~/.hermes/profiles/senna/home`), breaking config discovery. Always use absolute paths (`~/.config/nim/.env`) when accessing files outside the Hermes profile.
- ❌ Forgetting to use the Hermes venv Python — call `~/.hermes/hermes-agent/venv/bin/python3` explicitly to ensure the `openai` SDK (2.32.0) and other deps are available.
- ❌ Setting `OPENAI_API_KEY` alone expecting Hermes to route to NVIDIA — you must also set `OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1`, or configure the `nvidia` provider explicitly in `~/.config/hermes/config.yaml`.
- ❌ **Treating the `/v1/models` endpoint pricing as real** — NVIDIA's models list endpoint returns `$0.0000` for all models. Real pricing is on a per-endpoint basis. Do not assume a model is free just because the list says $0.0000. For accurate pricing, check NVIDIA's pricing page at `https://build.nvidia.com/pricing` or make a completion call and check the actual spend.

---

## H. Verification checklist (pre-delivery)

Before answering an NVIDIA NIM question:
- [ ] **Live model list checked:** Called `GET https://integrate.api.nvidia.com/v1/models` if model IDs were cited
- [ ] **Docs verified:** Located relevant section in `https://docs.nvidia.com/nim/latest/` for any claimed feature/behavior
- [ ] **Endpoint clarity:** Distinguishes Cloud NIM vs Local NIM endpoint in the response
- [ ] **Environment variables correct:** Provides `OPENAI_BASE_URL` and `NVIDIA_API_KEY` or the cross-mapped pair
- [ ] **No stale model IDs:** If citing specific models, notes they should be verified from live sources
- [ ] **SDK pattern matches OpenAI Compatible:** Code examples follow the OpenAI Python/JS SDK patterns (since NIM is compatible)

---

## I. Helper scripts

### `scripts/list-nim-models.sh`

Fetch available NIM models (requires API key).

```bash
#!/bin/bash
# Usage: ./scripts/list-nim-models.sh
# Requires NVIDIA_API_KEY environment variable

API_KEY="${NVIDIA_API_KEY:-${OPENAI_API_KEY:-}}"
if [ -z "$API_KEY" ]; then
  echo "Error: NVIDIA API key not set. Export NVIDIA_API_KEY or OPENAI_API_KEY"
  exit 1
fi

curl -sL -H "Authorization: Bearer $API_KEY" \
  "https://integrate.api.nvidia.com/v1/models" | python3 -m json.tool
```

### `scripts/test-nim-connection.sh`

Quick verification that your NVIDIA API key can connect.

```bash
#!/bin/bash
# Usage: ./scripts/test-nim-connection.sh

API_KEY="${NVIDIA_API_KEY:-${OPENAI_API_KEY:-}}"
if [ -z "$API_KEY" ]; then
  echo "Error: NVIDIA API key not set"
  exit 1
fi

response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -H "Authorization: Bearer $API_KEY" \
  "https://integrate.api.nvidia.com/v1/models")

body=$(echo "$response" | grep -v "HTTP_CODE")
code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)

if [ "$code" = "200" ]; then
  echo "✓ Connection successful. Models received:"
  echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f"{len(d['data'])} models available")" 2>/dev/null || echo "$body"
else
  echo "✗ Connection failed (HTTP $code):"
  echo "$body"
  exit 1
fi
```

---

## J. Quick reference — one-liners

**Use Hermes native provider (first check):**
```bash
# Ensure env is loaded, then
hermes chat --provider nvidia --model nvidia/deepseek-ai/deepseek-v3.2 -q "Hello"
```

**Test your NVIDIA API key:**
```bash
curl -s -H "Authorization: Bearer $NVIDIA_API_KEY" \
  "https://integrate.api.nvidia.com/v1/models" | python3 -m json.tool | head -30
```

**Simple Python chat completion:**
```python
from openai import OpenAI
c = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key="YOUR_KEY")
print(c.chat.completions.create(model="meta/llama3-70b-instruct",
  messages=[{"role":"user","content":"Test"}]).choices[0].message.content)
```

**List models via CLI:**
```bash
export NVIDIA_API_KEY="xxx"
curl -s -H "Authorization: Bearer $NVIDIA_API_KEY" \
  "https://integrate.api.nvidia.com/v1/models" | jq '.data[].id'
```

**Pull a model locally (Local NIM):**
```bash
docker pull nvcr.io/nim/meta/llama3-70b-instruct:1.0.0
docker run --gpus all -p 8000:8000 nvcr.io/nim/meta/llama3-70b-instruct:1.0.0
```

---

## K. Model discovery flow (mandatory for model selection tasks)

When the user asks "Which NVIDIA model should I use for X?" or "Is model Y available?":

1. Fetch `GET https://integrate.api.nvidia.com/v1/models` using their API key
2. Filter by task match (context length, modality, model family)
3. Return the top 2-3 candidates with: model ID, max context length, pricing (prompt/completion), and known capabilities
4. Remind the user to verify model availability themselves via the catalog or models API before commitment

---

## L. Decision framework — Cloud NIM vs Local NIM vs other providers

| Factor | Cloud NIM | Local NIM (Docker) | OpenRouter (Alternative) |
|--------|-----------|-------------------|-------------------------|
| **Cost model** | Pay-per-token (per-request) | Upfront GPU, then free inference | Pay-per-token (route to many providers) |
| **Latency** | Network round-trip + queueing | In-process, lowest latency | Network, varies by provider |
| **Privacy** | Data leaves your environment | Fully on-premises | Varies by provider selected |
| **Scale** | Automatic, NVIDIA manages | Manual GPU scaling | Managed by OpenRouter |
| **Model freshness** | NVIDIA's hosted versions only | Pull any NGC model version | Catalog across many providers |
| **Rate limits** | Per-key limits enforced | Your own hardware limits | Per-provider limits via fallbacks |
| **Maintenance** | None (API only) | Container/GPU maintenance | None (managed gateway) |

**Choose Cloud NIM when:** You want NVIDIA-optimized hosted inference, predictable pricing per token, and no infrastructure maintenance.

**Choose Local NIM when:** You need maximum privacy, lowest latency, or want to run large batch jobs without per-token costs.

**Choose another provider/OpenRouter when:** You need multiple providers, automatic failovers, or want to compare model quality across vendors.


### Hermes sandbox PATH issues

When running inside Hermes, `$HOME` typically points to the sandboxed profile directory (e.g., `~/.hermes/profiles/senna/home`), not your real home. This breaks config loading if you use `~` expansion in scripts.

**Fix:** Always use absolute paths `~` when reading config files outside the Hermes profile. The `run_nim.py` script checks both the sandbox HOME and the real `~` to find `~/.config/nim/.env`.

Also, the Hermes venv is at a fixed location. When calling Python scripts from Hermes tools, use the explicit path:
```bash
~/.hermes/hermes-agent/venv/bin/python3
```
to ensure you're using the correct interpreter and dependencies (OpenAI SDK, etc.).

---

### Model availability volatility on NIM Cloud

NVIDIA's hosted catalog rotates frequently:
- **410 Gone** — Model retired/deactivated. Example: `01-ai/yi-large` (retired April 2026), older Llama 3 instruct variants.
- **404 Function not found** — Model ID valid catalog-wise but not yet deployed on the cloud endpoint. Some new model IDs appear in the catalog but aren't live yet.

**Workflow:** Always call `GET https://integrate.api.nvidia.com/v1/models` to get the live list. Do not rely on model IDs from documentation or third-party posts older than a few days.

**Recommended practice:** Maintain a small list of known-working model IDs (validated within the last week) and prefer them first. The `run_nim.py` test script hardcodes `google/gemma-3-12b-it` and `meta/llama-3.3-70b-instruct` as fallbacks because they have been stable in the April 2026 catalog.

---

---

## End of skill