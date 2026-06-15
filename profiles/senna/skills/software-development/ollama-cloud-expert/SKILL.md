---
name: ollama-cloud-expert
category: software-development
description: |
  Use this skill when configuring Hermes to use Ollama Cloud (ollama.com) as a hosted LLM provider. Covers provider naming, environment setup, dynamic model discovery, profile configuration, verification, and common gotchas. Tells agents where to look in Hermes code and Ollama API to answer accurately. Do not rely on memory for model IDs or capabilities — always fetch live from the API.
triggers:
  - "ollama cloud"
  - "ollama.com"
  - "OLLAMA_API_KEY"
  - "ollama cloud provider"
  - "set up ollama cloud"
  - "use ollama from cloud"
  - "ollama cloud api"
---

IDENTITY: ProviderResolver{OllamaCloud,LiveOnly,OpenAICompatible}. CoreRole: Configure Hermes to use Ollama Cloud as hosted LLM provider. BehavioralContract: Never hardcode model IDs. Always verify env/comments, fetch live model list, confirm provider ID is ollama-cloud (not ollama). Check .env for uncommented key.
Law: ollama-cloud (with hyphen) is canonical. ollama maps to localhost:11434 — wrong target.
WHENUSE: Configuring Ollama Cloud as LLM provider, mentioning OLLAMA_API_KEY, switching from local Ollama. ESPECIALLY:{ProviderSetup,ModelDiscovery,ConnectivityVerification}.
REDFLAGS: CommentedKey->UncommentInEnv|WrongProviderID->UseOllamaCloud|GuessedModelID->FetchLive|OpenRouterConfusion->SeparateServices|StaleEnv->RestartGateway|HardcodedClaims->AlwaysVerify.
RATIONALIZATIONS: "ollama works"->MapsToLocalhost|"I know the models"->FetchLiveAnyway|"Just use ollama_cloud"->CanonicalIsHyphenated.
QUICKREF: VerifyEnv{uncommented OLLAMA_API_KEY}->CheckProvider{registry: ollama-cloud, transport: openai_chat}->FetchModels{GET /v1/models}->Configure{provider: ollama-cloud in config.yaml}->Restart{gateway restart}->Verify{hermes models --provider ollama-cloud}.

## A. Quick trigger/usage guidance

**Load this skill when:** the user wants to use Ollama's hosted cloud API (ollama.com) instead of a local Ollama instance, or mentions `OLLAMA_API_KEY`, or asks about running Ollama models from the cloud with Hermes.

**What this skill covers:**
- Provider naming: `ollama-cloud` (canonical), `ollama_cloud` (alias), NOT `ollama`
- Required and optional environment variables
- Dynamic model discovery via live API
- Switching Hermes profiles/config to use the provider
- Verifying connectivity and model availability
- Common failure modes and how to avoid them

**What the agent must verify before answering:**
- Read Hermes provider registry to confirm `ollama-cloud` is registered and its transport type
- Check that the user's `.env` has `OLLAMA_API_KEY` uncommented
- Fetch live model list from Ollama Cloud when model IDs matter
- Confirm the user's active provider in `config.yaml` if they're having issues

---

## B. Pre-answer ritual

Before answering any Ollama Cloud question, follow this checklist:

1. **Read Hermes provider registry** to confirm:
   - Provider ID (`ollama-cloud`)
   - Transport (`openai_chat`)
   - Required auth (`OLLAMA_API_KEY`)
   - Optional base URL env var (`OLLAMA_BASE_URL`, default `https://ollama.com/v1`)

2. **Inspect the user's `.env`** to confirm `OLLAMA_API_KEY` is present and **uncommented**. If it is commented (`# OLLAMA_API_KEY=...`), tell the user to uncomment it.

3. **Fetch live model list** if the question involves model IDs, capabilities, or availability:
   ```bash
   curl -H "Authorization: Bearer $OLLAMA_API_KEY" https://ollama.com/v1/models
   ```
   Cache is short-lived (<1 hour) in Hermes (`fetch_ollama_cloud_models`). Prefer live.

4. **Verify the user's active provider** in `config.yaml` under `model.provider`. If it's not `ollama-cloud`, they need to switch profiles or change the config.

5. **Never hardcode** model IDs or assume pricing/rate limits — tell the agent to check the live API or Ollama account page.

---

## C. Core API surface (Ollama Cloud)

Ollama Cloud exposes an **OpenAI-compatible REST API** at `https://ollama.com/v1`. Hermes uses the `openai_chat` transport.

**Base URL:**
- Default: `https://ollama.com/v1`
- Override with `OLLAMA_BASE_URL` environment variable

**Authentication:**
```http
Authorization: Bearer $OLLAMA_API_KEY
```
Required for all requests. Key from https://ollama.com/settings

**Key endpoints (verify in live API or Hermes code):**
- `POST /v1/chat/completions` — chat inference
- `POST /v1/completions` — text completion (legacy)
- `GET /v1/models` — list available models
- `GET /v1/health` — health check

**Response format:** OpenAI-compatible JSON with `choices`, `usage`, etc.

**Important:** Unlike OpenRouter, Ollama Cloud does not use special suffixes like `:free`, `:nitro`, etc. Model IDs are raw strings returned by `/v1/models` (e.g., `qwen3:397b`, `glm-5`).

---

## D. Provider configuration in Hermes

### Required environment variables (in `~/.hermes/profiles/<profile>/.env`)
```
OLLAMA_API_KEY=ollama_xxxxxxxxxxxxxxxxxxxxxxxx  # REQUIRED, uncommented
OLLAMA_BASE_URL=https://ollama.com/v1            # OPTIONAL, default shown
```

The key must be present and visible (no `#` prefix).

### Profile config (`config.yaml`)
```yaml
model:
  provider: ollama-cloud   # exact string with hyphen
  # optional default model if you don't want auto-select
  # default: qwen3.5:397b
```

**Do NOT use:**
- `ollama` → maps to local Ollama (`localhost:11434`)
- `ollama_cloud` → works as an alias, but `ollama-cloud` is canonical

### Switching profiles
```bash
# Option 1: Switch in-place (edit config.yaml of current profile)
# Option 2: Create separate profile and select it
hermes chat -p ollama-cloud-profile-name
```

---

## E. Model discovery and selection

### No static model list
Ollama Cloud's model catalog changes. Hermes does not ship a hardcoded list.

### How to fetch models
**Method 1 — Direct API (fastest):**
```bash
curl -H "Authorization: Bearer $OLLAMA_API_KEY" \
     https://ollama.com/v1/models | jq .
```

**Method 2 — Hermes helper:**
```bash
hermes models --provider ollama-cloud
```
(Uses `fetch_ollama_cloud_models()` under the hood, cached <1 hour.)

### Model ID format
Model IDs are exactly as returned by the API, e.g.:
- `qwen3:397b`
- `glm-5`
- `nemotron-3-nano:30b`

Do NOT append `:free`, `:exacto`, `:nitro`, etc. Those are OpenRouter concepts.

### Picking a model
1. Fetch the list
2. Choose by name, size, or capability
3. Use the exact string in your config or prompt

---

## F. Task-to-docs routing (Hermes-specific)

When answering, point the agent to these canonical locations in the Hermes codebase:

| Task | Where to look |
|------|---------------|
| Provider registry definition | `~/.hermes/hermes-agent/hermes_cli/providers.py` (look for `ollama-cloud`) |
| Model fetching logic | `~/.hermes/hermes-agent/hermes_cli/models.py` → `fetch_ollama_cloud_models()` |
| Transport type confirmation | `providers.py` → `transport: "openai_chat"` |
| Test coverage | `~/.hermes/hermes-agent/tests/hermes_cli/test_ollama_cloud_provider.py` |
| Env var handling | `providers.py` → `api_key_env_vars`, `base_url_env_var` |
| Provider auto-detection rules | `models.py` → auto-detection logic based on env vars |
| Alias mapping | `models_dev.py` or alias registry |

---

## G. Common gotchas and how to prevent them

| Gotcha | How to avoid |
|--------|-------------|
| `# OLLAMA_API_KEY=xxx` in `.env` (commented) | Inspect `.env` and tell user to uncomment the line |
| Using `provider: ollama` (local) instead of `ollama-cloud` | Explicitly state the exact string: `ollama-cloud` |
| Guessing model IDs (e.g., `llama3:70b`) | Tell the agent to fetch `/v1/models` first or use `hermes models` |
| Assuming base and variant models have identical capabilities | Remind: variants may differ in context length, tool support, pricing |
| Stale `.env` after editing | Restart Hermes gateway: `hermes gateway restart` |
| Wrong base URL set | Verify `OLLAMA_BASE_URL` matches API; default is `https://ollama.com/v1` |
| Rate limits or quota exceeded | Check Ollama Cloud account page; fallback to another provider |
| Model not found after switching | Model may have been removed from catalog; refetch the list |
| Confusing OpenRouter with Ollama Cloud | These are separate services; do not mix their concepts |

---

## H. Verification checklist for agents

Before giving a final answer or code snippet about Ollama Cloud, verify:

- [ ] **Docs/code checked**: Read `providers.py` and `models.py` in the local Hermes installation to confirm behavior
- [ ] **Env vars verified**: User's `.env` actually contains uncommented `OLLAMA_API_KEY`
- [ ] **Models fetched**: Called `/v1/models` or `hermes models` to get current model IDs if relevant
- [ ] **Provider ID correct**: Using `ollama-cloud`, not `ollama` or `ollama_cloud` in final recommendations
- [ ] **Base URL correct**: Default is `https://ollama.com/v1`, or user's custom `OLLAMA_BASE_URL`
- [ ] **No hardcoded claims**: No invented model IDs, pricing, or capabilities referenced without a live check
- [ ] **Command examples match Hermes**: Hermes CLI syntax verified against installed version

---

## I. Example interactions (for agent reference only)

**User:** "I added my Ollama API key. How do I use it with Hermes?"
**Agent response structure:**
- Confirm the key is uncommented in `.env`
- Explain `ollama-cloud` provider and how it differs from local `ollama`
- Show how to change `model.provider` in `config.yaml`
- Suggest fetching models: `curl -H "Authorization: Bearer $OLLAMA_API_KEY" https://ollama.com/v1/models`
- Recommend a model from the returned list
- Remind to restart gateway

**User:** "What models are available on Ollama Cloud?"
**Agent response structure:**
- Fetch live from `/v1/models` (don't guess)
- Print the list or key entries
- Note that model availability is dynamic

**User:** "How do I use server-side web search with Ollama?"
**Agent response structure:**
- Check Ollama Cloud docs for server tools support (permissions, available tools)
- If not supported, fall back to client-side tool use (Hermes tools)
- Link to relevant Hermes code for server tools implementation

---

## J. References and further reading (internal)

This skill is derived from investigation of:
- `~/.hermes/hermes-agent/hermes_cli/providers.py`
- `~/.hermes/hermes-agent/hermes_cli/models.py`
- `~/.hermes/hermes-agent/tests/hermes_cli/test_ollama_cloud_provider.py`
- `~/.hermes/profiles/senna/.env` (template)
- Live Ollama Cloud API: `https://ollama.com/v1/models`
