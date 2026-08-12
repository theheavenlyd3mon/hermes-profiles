---
name: provider-fallback-strategy
description: Diagnose provider auth failures (401/403/404), check credential health, configure fallback chains, and plan budget-aware model tiering across multiple providers.
tags: [hermes, configuration, providers, auth, troubleshooting, fallback]
version: 1.4.0
---

IDENTITY: Diagnostician.Planner. Diagnose provider auth failures and configure fallback chains so the agent keeps working when the primary provider goes down.
WHENUSE: UserReports{ProviderError401,ProviderError403,ProviderError404,APIKeyExpired,OutOfCredits}|Troubleshooting{ModelKeepsFailing,AuthSaysLoggedInButFails}|UserAsks{SwitchProvider,ConfigureFallback,WhatsMyProviderSetup}|Planning{ModelBudget,WhichProviderForWhat,FreeModelList,ProviderCostComparison}
REDFLAGS: FallbackModelOnSameProvider->SameCrashWillRepeat|AuthStatusIsLoggedInDoesNotMeanFunctional|hermesModelIsInteractiveOnly->CannotAutomate
QUICKREF: ConfigCheck{cat ~/.hermes/profiles/\\$HERMES_PROFILE/config.yaml}->AuthStatus{hermes auth status <provider>}->CredentialPool{hermes auth list}->ProviderSwitch{hermes config set model.default <model> && hermes config set model.provider <provider>}->ConfigureFallback{hermes fallback add (interactive CLI — only reliable way to build multi-entry chain)}

## When to Use

- User encounters a 401 / 403 / 404 from their provider mid-session
- User reports "API key is invalid, blocked or out of funds"
- User asks about switching to a different provider
- User wants to set up fallback providers so the agent auto-recovers
- User wants to audit and reconfigure provider/model setup across multiple providers
- After a credential change or billing event

## Diagnosis Flow

### 1. Check the current config

Read config.yaml to see what provider and models are configured:

```
cat ~/.hermes/profiles/<profile>/config.yaml
```

Key fields to check:
- `model.default` — the primary model
- `model.provider` — the primary provider
- `fallback_providers` — if this is empty, fallbacks will retry the same provider

### 2. Check auth status for the failing provider

```
hermes auth status <provider>
```

This returns "logged in" or an error. **"logged in" does not mean functional** — credentials can exist but be expired, out of credits, or revoked.

### 3. List the full credential pool

```
hermes auth list
```

This shows ALL providers that have credentials configured. For each, it shows the credential type (oauth, env var, api_key) and source.

Use this to discover which alternative providers are ready to use right now.

### 4. Check if fallback models use the same provider

This is the most common hidden pitfall. Config may specify:

```yaml
model:
  default: deepseek/deepseek-v4-flash:free
  provider: nous
fallback_providers: []
```

With `fallback_providers: []` and no per-model provider override in the fallback model config, every fallback retry uses the same (dead) provider. The fallback model path also resolves through the same provider — so if Nous is dead, every fallback dies the same way.

### 4b. Check gateway logs for the exact error (Discord bots)

## Verification

```bash
grep -A7 'title_generation:' ~/.hermes/profiles/<profile>/config.yaml
# Should show explicit provider, not 'auto'
```

## Multi-provider split strategy

When using multiple providers for aux tasks, explicitly assign each slot rather than relying on `auto`:

**Why split?** 
- Avoids a single provider failure taking down all aux tasks
- Lets you match model strength to task difficulty (tiny model for titles, big model for curation)
- Distributes rate limit / cost burden

**What to assign where (common pattern):**

| Aux slot | Provider | Model choice logic |
|----------|----------|--------------------|
| vision | nvidia or openrouter | Needs image input support — use a vision-capable provider |
| compression | openrouter or nvidia | Cheap fast model with good summarization |
| title_generation | nvidia or openrouter | Tiny model — fastest response |
| session_search | openrouter or nous | Query generation — cheap text model |
| curator | nvidia or nous | Needs reasoning quality — bigger model |
| web_extract | openrouter or nvidia | Fast extraction — cheap text model |
| approval | nous or openrouter | Yes/no — tiny model |

**Config shape:**
```yaml
auxiliary:
  vision:
    provider: nvidia
    model: meta/llama-3.2-11b-vision-instruct
  compression:
    provider: openrouter
    model: deepseek/deepseek-v4-flash
  title_generation:
    provider: nvidia
    model: google/gemma-3-4b-it
  session_search:
    provider: openrouter
    model: deepseek/deepseek-v4-flash
  curator:
    provider: nous
    model: deepseek/deepseek-v4-pro
  web_extract:
    provider: openrouter
    model: deepseek/deepseek-v4-flash
```

**Pitfall:** The `openrouter` provider for aux uses model IDs with `provider/model` format (e.g. `deepseek/deepseek-v4-flash`). The `nvidia` provider uses the bare model ID without `nvidia/` prefix (e.g. `meta/llama-3.2-11b-vision-instruct`). The `nous` provider uses `provider/model` format (e.g. `deepseek/deepseek-v4-pro`).

**Pitfall:** Not all providers support all aux types. For example, `nvidia` NIM has vision models (llama-3.2-vision, phi-4-multimodal). `openrouter` has cheaper text but may have rate limits. Always verify the model supports the task type before assigning.

Common error patterns:
- `RuntimeError: Provider 'X' is set in config.yaml but no API key was found` → API key missing or commented out in `.env`
- `RuntimeError: Provider 'X' returned 401` → API key exists but is invalid/expired
- `RuntimeError: Provider 'X' returned 403` → API key valid but account suspended/out of credits

**If the error says "no API key was found"**: Check if the key is commented out:
```bash
grep -i "<PROVIDER>_API_KEY" ~/.hermes/profiles/<profile>/.env
# If line starts with # → key is commented out, not active
```

### 5. Present options to the user

| # | Option | How |
|---|--------|-----|
| A | **Re-authenticate** — refresh the provider's OAuth or API key | `hermes auth logout <provider>` then run `hermes setup` or add credentials via portal |
| B | **Switch provider right now** — use a different provider immediately | Update config.yaml `model.provider` + `model.default` to a provider with working credentials |
| B2 | **Route through OpenRouter** — use OpenRouter as aggregator for the same model | Update config.yaml to `provider: openrouter` with `provider/model` format (see pitfall 3c) |
| C | **Configure fallback providers** — add `fallback_providers` so the agent tries a different provider when the primary fails | Edit config.yaml to add a fallback_providers entry with a different provider and model |
| D | **Check portal** — the account may need credits, or the key may need reissuing | Open https://portal.nousresearch.com (for Nous) or the equivalent billing page |

## Multi-Provider Model Audit & Reconfiguration

When the user wants to reconfigure their model setup across multiple providers — e.g., split aux tasks between NVIDIA NIM, OpenRouter, and Nous Portal — follow this systematic workflow:

### Step 1: Audit current provider health
```bash
hermes auth list                              # see all credentials
hermes auth status <provider>                 # per-provider status
```
Check for:
- `logged in` — credential exists (but may be expired)
- `exhausted (402)` — out of credits
- `auth failed (401)` — key is invalid/expired
- `logged out` — no credential found

**Critical:** "logged in" does NOT mean functional. The auth token may have expired or the account may be out of credits. If an aux task uses `provider: auto`, trace it back to the main `model.provider` to find the actual failing provider.

### Step 2: Read current config
```bash
cat ~/.hermes/profiles/<profile>/config.yaml | grep -A10 '^model:'       # primary
cat ~/.hermes/profiles/<profile>/config.yaml | grep -A30 '^auxiliary:'   # aux slots
cat ~/.hermes/profiles/<profile>/config.yaml | grep -A5 'fallback_providers:'  # fallbacks
```

Note which aux slots use `provider: auto` — these inherit the main provider and fail when it does.

### Step 3: Get live model catalogs from each provider being considered

| Provider | Command / endpoint | Auth needed? |
|----------|-------------------|--------------|
| OpenRouter | `curl -sL "https://openrouter.ai/api/v1/models"` | No (public) |
| NVIDIA NIM | `curl -s -H "Authorization: Bearer $NVIDIA_API_KEY" "https://integrate.api.nvidia.com/v1/models"` | Yes |
| Nous Portal | `curl -s -H "Authorization: Bearer <token>" "https://inference-api.nousresearch.com/v1/models"` | Yes (OAuth token from auth.json) |

From the live catalog, note per model: model ID (exact), context length, supported capabilities (vision? tools?), and pricing.

### Step 4: Compare free tiers, rate limits, and pricing

For each viable provider, check:
- **Rate limits** — see the provider skill (e.g., `nvidia-nim-expert`, `openrouter-expert`) for current limits
- **Free tier** — which models are $0, what's the request cap?
- **Credit-based vs dollar-based** — does the user have a token grant or cash balance?

Key thresholds for aux tasks (typical daily aux usage is ~25-70 requests across all slots):
| Provider | Free tier cap | Rate limit | Per-model? |
|----------|--------------|------------|------------|
| OpenRouter `:free` | 50 or 1,000 requests/day per model | 20 RPM per model | Yes — each aux slot with a different model ID has its own limit |
| NVIDIA NIM | 1,000 inference credits (up to 5,000) | 40 RPM (shared) | No — shared across all slots |

### Step 5: Propose a config plan

**User preference (learned from correction):** Do NOT present model options without having already gathered and included rate limits, free tier caps, and pricing. The user needs ALL constraints simultaneously to make a decision. Presenting models first and asking "which one?" before you've checked limits will get you corrected.

Before writing any config proposal, confirm you have all three for every provider in scope:
- [ ] Rate limit (requests per minute/second — shared pool or per-model?)
- [ ] Free tier cap (daily requests, free credits, or pay-per-token?)
- [ ] Per-token pricing beyond free tier

If you haven't loaded the provider's skill (e.g. `nvidia-nim-expert`, `openrouter-expert`) to get this data, load it now. The multi-provider comparison table at Step 4 above is a summary — the per-skill reference files have the full verified data.

Present the user with concrete slot assignments. For decisions involving free models:

- **OpenRouter `:free` is permanently $0** but rate-limited per model. Using different `:free` model IDs for different aux slots gives each its own rate limit budget.
- **NVIDIA NIM** has good vision models and text models but the free credits are finite (1,000). Beyond that, billing applies.
- **Free models from NVIDIA on OpenRouter** (e.g. `nvidia/nemotron-3-ultra-550b-a55b:free` through OpenRouter) get OpenRouter `:free` rate limits rather than NVIDIA's shared 40 RPM.

The recommended split (all $0):
```yaml
auxiliary:
  vision:              # OpenRouter :free — nvidia vl model
    provider: openrouter
    model: nvidia/nemotron-nano-12b-v2-vl:free
  compression:         # OpenRouter :free — 1M ctx, excellent summarizer
    provider: openrouter
    model: qwen/qwen3-coder:free
  title_generation:    # OpenRouter :free — reuses same model, minimal calls
    provider: openrouter
    model: qwen/qwen3-coder:free
  session_search:      # OpenRouter :free — strong recall at 1M ctx
    provider: openrouter
    model: nvidia/nemotron-3-super-120b-a12b:free
  web_extract:         # OpenRouter :free — handles long pages
    provider: openrouter
    model: qwen/qwen3-coder:free
  curator:             # OpenRouter :free — 550B MoE for decisions
    provider: openrouter
    model: nvidia/nemotron-3-ultra-550b-a55b:free
```

### Step 6: Apply and verify

1. Edit `config.yaml` with the new aux slot assignments
2. Restart gateway or start new CLI session
3. Verify: `hermes config show | grep -A5 'auxiliary:'` confirms the config is loaded
4. Test each aux slot by exercising the relevant feature (send an image for vision, trigger a compression event, etc.)

## Configuring Fallback Providers

### Three-Layer Fallback System

Hermes has THREE fallback keys. Understanding which is active matters:

| Key | Format | Priority | Notes |
|-----|--------|----------|-------|
| `fallback_providers` | YAML list of `{provider, model, ...}` entries | **Highest** — takes priority when non-empty | Preferred. Supports multiple entries tried in order. |
| `fallback_model` | Single `{provider, model}` dict | Medium — used when `fallback_providers` is empty | Legacy. One entry only. |
| `model.fallback` | Single `{provider, default}` dict | Lowest | Legacy. Often ignored when other keys are set. |

`hermes fallback ls` shows the active chain. `hermes fallback clear` empties the chain.

### Correct Config Format

Each entry in `fallback_providers` needs `provider` and `model` (singular, not `models`):

```yaml
fallback_providers:
  - provider: custom              # for direct API endpoints
    model: deepseek-v4-pro
    base_url: https://api.deepseek.com
    key_env: DEEPSEEK_API_KEY     # env var name, not the key itself
  - provider: openrouter          # for OpenRouter aggregated models
    model: deepseek/deepseek-v4-flash:free
  - provider: nous                # for Nous Portal models
    model: qwen3-coder-next
```

For built-in providers (openrouter, nous, xiaomi, etc.), only `provider` + `model` needed.
For custom/direct API endpoints, also set `base_url` and `key_env`.

### Setting Up Fallback Chains — CLI Workflow

**Use `hermes fallback add` — it's the only reliable way.** The interactive picker handles proper YAML list creation.

```bash
# 1. Clear any stale state
hermes fallback clear       # type 'y'

# 2. Add entries one at a time (each opens an interactive picker)
hermes fallback add         # pick provider → pick model → confirm
hermes fallback add         # repeat for each fallback tier
hermes fallback add

# 3. Verify
hermes fallback ls
```

The picker shows numbered choices. Type the number, press Enter, follow prompts.
For `custom` provider: you'll be prompted for base_url, model name, and key_env.

## Diagnosing Custom Provider Connectivity

Custom providers often fail before the auth layer — the host is unreachable, DNS doesn't resolve, or the model name doesn't match. **Diagnose in this order:**

### 1. DNS / Network reachability

```bash
# Quick check — does the host resolve and respond?
curl -s -w '\n%{http_code}' --connect-timeout 5 <base_url>/models
```

| Exit code | Meaning | Likely cause |
|-----------|---------|-------------|
| `curl: (6)` | DNS resolution failure | Tailscale hostname from a machine not on the same tailnet; wrong hostname entirely |
| `curl: (7)` | Connection refused | Server not running (Ollama/llama.cpp not started, wrong port) |
| `curl: (28)` | Timeout | Firewall, wrong network (host exists but blocks the port) |
| HTTP 200 | Reachable | Move to model name check |

### Step 3b: Check for cross-tailnet shared nodes (invisible in `tailscale status`)

`tailscale status` only shows devices that are **direct members** of your tailnet. If someone shared a device from another tailnet to you, it does NOT appear in `tailscale status` until you accept the share via the admin console. A shared-but-not-accepted node times out on `curl` with `(28)` — looks identical to an offline machine.

**Check:** Open https://login.tailscale.com/admin/machines → look for "External Devices" or "Shared to my tailnet" sections. If the share is pending, accept it there. Once accepted, the node appears in `tailscale status`.

**Pitfall:** `tailscale up --reset` nukes ALL accepted cross-tailnet shares. After a reset, you must re-accept shares through the admin console — `tailscale up --accept-dns` alone does NOT restore them. The shares remain active server-side; only the local acceptance is dropped.

### 2. Tailscale-specific: `*.ts.net` hostnames

```bash
# Check tailnet membership
tailscale status

# If it shows your machine: great, DNS should work with --accept-dns=true
# If "not connected" or empty: you're not on the same tailnet

# Fix: connect
tailscale up --accept-dns=true

# Alternative: use the Tailscale IP directly (100.x.x.x)
# Replace https://host.tailnet.ts.net/v1 with https://100.x.x.x/v1
```

**Pitfall:** The Mac App Store version of Tailscale runs as an IPNExtension and may not expose the unix socket the CLI needs. In that case, `tailscale status` returns `failed to connect to local tailscaled` even though the tunnel is active. Check the Tailscale menubar icon instead, or use the official CLI from Homebrew (`brew install tailscale`).

**Pitfall: `tailscale up --reset` nukes accepted cross-tailnet shares.** If the target machine was shared from another tailnet, `--reset` drops the acceptance — the hostname stops resolving. `tailscale up --accept-dns` (without `--reset`) does NOT re-accept it either; you must re-accept the share via the admin console or run `tailscale logout && tailscale up --accept-dns` to re-pull fresh server state. See `references/tailscale-connectivity-pitfalls.md` for the full set of Tailscale-specific failure modes relevant to custom provider diagnosis.

### 3. Model name doesn't match

The model name in your custom provider config must match **exactly** what the server advertises.

```bash
# Check which models the server exposes
curl -s <base_url>/models | python3 -m json.tool
```

For a plain llama.cpp server, the model name defaults to the filename of the loaded GGUF. For Ollama, it's the tag you used when pulling. For vLLM/TGI, it's whatever was passed as `--model`.

**Common mismatch:** config says `qwen3.6-27b-gptq` but the server exposes `qwen3.6-27B-gptq` (different capitalization) or a hash-based name.

### 4. Auth / API key

```bash
# Test with the actual auth header
curl -s -H "Authorization: Bearer <api_key>" <base_url>/models
```

If this returns models but Hermes still fails: the key is correct but the env var name may not match `key_env` in config, or the key exists in root `.env` but not the **profile's** `.env`.

### 5. Full chat completion smoke test

```bash
curl <base_url>/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"<model-name>","messages":[{"role":"user","content":"say hi"}],"max_tokens":10}'
```

Expected: a JSON response with `choices[0].message.content`. Any other response (HTML error page, empty body, timeout) means the server isn't fully operational.

### Common Failure Patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| `curl: (6)` — DNS fail | Not on same tailnet | `tailscale up` or use Tailscale IP |
| `curl: (7)` — conn refused | Server not running | Start llama.cpp/Ollama/vLLM |
| HTTP 404 on `/v1/models` | Wrong base_url | Should end with `/v1` (e.g. `http://host:8080/v1`) |
| Empty model list | Server has no model loaded | Load a model first (Ollama: `ollama pull <model>`) |
| HTTP 401/403 on completions | Wrong/expired API key | Check the key in profile `.env` |
| HTTP 200 but empty response | Missing/wrong Content-Type header | Ensure server returns `application/json` |
| `model "<x>" not found` | Model name mismatch | Check server's `/v1/models` for exact name |

### Concrete Scenario: Remote Self-Hosted Model (Another Machine)

When the user reports "the model we set up didn't connect correctly" and the endpoint lives on another machine (e.g., llama.cpp on a Windows PC, Ollama on a home server), follow the flow in `references/remote-model-endpoint-diagnosis.md`:

1. **Check what's actually configured** — the provider entry may have been lost in a config revision. The API key env var may still be in `.env` but nothing references it.
2. **Test raw endpoint reachability** with `curl` — separates DNS, network, and server-problems
3. **Check tailnet membership** with `tailscale status` — if the host machine isn't listed, it's never been connected
4. **Verify host machine** is online and the server process is running
5. **Re-establish the provider config** with the correct URL, API key, and model name

**Common trap: config from an old session, not in current config.yaml.** The user remembers "setting it up" but a subsequent config change overwrote the entry. Always check the actual current `fallback_providers` or `providers:` block in the profile's config.yaml before re-adding.

## Adding Custom Providers (Switchable, Not Just Fallback)

When you receive a base URL + API key for someone's endpoint (self-hosted, Tailscale, private API), add it as a named provider in config.yaml so it appears in `hermes model` and `/model` as a switchable option — not just a fallback entry.

### Config Format

Use the `providers:` keyed dict (v12+ format, preferred over legacy `custom_providers` list):

```yaml
providers:
  stewart:                          # provider key (used with --provider flag)
    name: stewart                   # display name
    base_url: https://host.tailnet.ts.net/v1  # OpenAI-compatible endpoint
    key_env: STEWART_API_KEY        # env var name in profile .env (NOT the key itself)
    model: qwen3.6-27b-gptq        # default model to offer
    discover_models: true           # auto-detect available models via /v1/models
```

### Required Fields

| Field | Purpose |
|-------|---------|
| `name` | Display name in model picker. Falls back to the provider key if omitted. |
| `base_url` OR `url` OR `api` | The OpenAI-compatible endpoint URL. Must have scheme + host. |
| `key_env` | Name of the env var in the profile's `.env` that holds the API key. |

### Optional Fields

| Field | Default | Purpose |
|-------|---------|---------|
| `model` | — | Default model name to suggest |
| `models` | — | Dict or list of available model IDs |
| `context_length` | — | Override context window size |
| `discover_models` | `false` | Auto-query `/v1/models` at startup |
| `rate_limit_delay` | `0` | Seconds to wait between requests |
| `api_mode` / `transport` | — | `chat_completions` or other transport mode |
| `extra_body` | — | Dict merged into every API request body |

### Setup Steps

1. Add the provider block to the **profile** `config.yaml` at `~/.hermes/profiles/<profile>/config.yaml` under `providers:` — NOT the root `~/.hermes/config.yaml` (see pitfall below)
2. Add the API key to the **profile's** `.env` at `~/.hermes/profiles/<profile>/.env`: `<KEY_ENV_VAR>=sk-...`
3. Restart gateway or start new CLI session
4. Verify: `hermes config show` should list the provider; test with `curl -s -H "Authorization: Bearer $KEY" <base_url>/models` to confirm endpoint reachability + auth before relying on Hermes routing

### Pitfall: `providers` vs `custom_providers`

Both work. `providers` (keyed dict) is the v12+ format. `custom_providers` (list) is legacy. The runtime normalizes both internally. Use `providers` for new configs — it's cleaner and the provider key doubles as the `--provider` flag value.

### Pitfall: `key_env` vs `api_key`

Use `key_env` (references an env var name) rather than putting the raw key in config.yaml. Config files get shared, logged, and committed — API keys belong in `.env` only.

Full schema reference: `references/custom-provider-config-schema.md`

## Budget-Aware Model Tiering

When the user has multiple providers with different budget types (token grants, dollar credits, free tiers), configure the fallback chain to maximize budget longevity:

**Tier priority (cheapest-first for fallback chain):**
1. Token grant providers (e.g., Xiaomi MiMo with 82B token grant) — use as default until exhausted
2. Free rate-limited models (e.g., OpenRouter free tier) — first fallback, never runs out of money
3. Direct API with dollar credits (e.g., DeepSeek API with $10) — reserve for tasks requiring specific strengths

**Important:** "Burn the expiring resource first" is not always optimal. Compare models on quality AND token efficiency before deciding. A smarter, more token-efficient model may cost less per task even if another option is "free." See `references/model-comparison-mimo-vs-deepseek.md` for a worked example.

**How to present options:**
- List all providers with their budget type and approximate remaining balance
- Calculate how many tokens each dollar-credit provider buys at current pricing
- Note time-limited promotions (e.g., DeepSeek V4 Pro at 75% off until May 31)
- Recommend a tier order and explain the tradeoff (quality vs cost vs reliability)

**Config pattern for multi-tier (use `hermes fallback add` — see CLI Workflow section):**
```yaml
model:
  default: mimo-v2.5-pro          # Tier 1: token grant, smartest, most efficient
  provider: xiaomi
fallback_providers:
  - provider: openrouter           # Tier 2: free rate-limited
    model: deepseek/deepseek-v4-flash:free
  - provider: custom               # Tier 3: paid credits, brute-force coding
    model: deepseek-v4-pro
    base_url: https://api.deepseek.com
    key_env: DEEPSEEK_API_KEY
  - provider: nous                 # Tier 4: subscription credits
    model: qwen3-coder-next
```

**References**: `references/provider-pricing-and-free-models.md` (current pricing and free model lists), `references/model-comparison-mimo-vs-deepseek.md` (head-to-head model comparisons), `references/error-patterns.md` (RuntimeError messages and their root causes), `references/auxiliary-model-provider-resolution.md` (how `provider: auto` in auxiliary config inherits the main provider and fails when that key dies), `references/remote-model-endpoint-diagnosis.md` (step-by-step diagnosis for self-hosted endpoints on another machine).

## Common Provider + Available Model Reference

| Provider | Credential check | Budget type | Notes |
|----------|-----------------|-------------|-------|
| xiaomi | env:XIAOMI_API_KEY + XIAOMI_BASE_URL | Token grant | MiMo models (mimo-v2.5-pro, mimo-v2-flash). Singapore endpoint. |
| deepseek | env:DEEPSEEK_API_KEY + DEEPSEEK_BASE_URL | Dollar credits | V4 Flash ($0.14/M in, $0.28/M out), V4 Pro (promo pricing varies). Direct API. |
| openrouter | env:OPENROUTER_API_KEY | Free models + credits | Aggregates 350+ models. Free tier includes DeepSeek V4 Flash, Qwen3 Coder, Nemotron 3 Super, etc. |
| nous | hermes auth (OAuth) | Subscription credits | Portal-managed. Free DeepSeek V4 Flash may come and go. |
| nvidia | env:NVIDIA_API_KEY | Free tier | Nemotron models. |
| z.ai | env:ZAI_API_KEY | Free tier | GLM models. |
| minimax | env:MINIMAX_API_KEY | Credits | MiniMax models. |

## Pitfalls

1. **Fallback model on same provider = same failure.** If the primary provider's auth is dead, every model routed through that provider will fail. Always configure `fallback_providers` with a different provider.
2. **"Logged in" ≠ functional.** `hermes auth status nous` returns "logged in" even when the OAuth token has expired or credits are exhausted. The credential exists but the API rejects it.
3. **API key present but COMMENTED OUT in .env.** A grep for `XIAOMI_API_KEY` may show the key exists in the profile's `.env`, but if the line starts with `#`, it's a comment and the provider has no credentials. The gateway will fail with:
   ```
   RuntimeError: Provider 'X' is set in config.yaml but no API key was found.
   Set the X_API_KEY environment variable, or switch to a different provider.
   ```
   **Fix**: Uncomment the key line (remove the leading `# `). Be careful with sed on API keys — special characters can corrupt the value. Use Python for safe editing:
   ```python
   with open('.env', 'r') as f:
       content = f.read()
   content = content.replace('# XIAOMI_API_KEY=sk-', 'XIAOMI_API_KEY=sk-')
   with open('.env', 'w') as f:
       f.write(content)
   ```
   **Verify**: `grep '^XIAOMI_API_KEY' .env` (no leading `#`) and compare line length with a known-working profile's key.
3b. **Profile `.env` is isolated — root `.env` is NOT inherited.** Each profile reads ONLY its own `~/.hermes/profiles/<name>/.env`. The root `~/.hermes/.env` is only read by the default profile (senna). If a key exists in root but not in the profile's `.env`, the profile will fail with "no API key was found" even though the key clearly exists on the system. Always check the profile's own `.env`, not just root.
3c. **Use OpenRouter as aggregator when direct provider key is missing.** If a profile is configured for a direct provider (e.g. `provider: deepseek`) but the API key is missing and you don't have one to add, switch to OpenRouter instead — it aggregates the same models and the user likely already has an OpenRouter key. Edit `config.yaml`:
   ```yaml
   # Before (broken — no DEEPSEEK_API_KEY)
   model:
     provider: deepseek
     default: deepseek-v4-pro
   
   # After (works — routes through OpenRouter)
   model:
     provider: openrouter
     default: deepseek/deepseek-chat-v3-0324
   ```
   OpenRouter model names use `provider/model` format. Common mappings:
   - `deepseek-v4-pro` → `deepseek/deepseek-chat-v3-0324` (verify current ID at openrouter.ai/models)
   - `deepseek-v4-flash` → `deepseek/deepseek-v4-flash:free`
   After editing, restart the gateway: `hermes gateway restart --profile <name>`
4. **`hermes model` is interactive-only.** You can't run it from automation or pipe input to it. For non-interactive provider switches, edit `config.yaml` directly.
5. **Free models may need logged-in-but-not-zero-balance accounts.** Some providers allow free-tier model access but still require a valid (non-zero) account. A 404 with "requires available credits" means the account exists but has $0 balance — not the same as an invalid key.
6. **Auth check is per-provider, not per-model.** If the provider has one OAuth credential (like Nous's device_code), all models under that provider use the same credential. A single failed model = all models under that provider likely also fail.
7. **`hermes config set` CANNOT create YAML arrays.** `hermes config set fallback_providers '[{...}]'` stores the array as a quoted string, not a proper YAML list. Same trap with `custom_providers` — `hermes config set custom_providers '{"name": "my-box", "base_url": "http://..."}'` silently fails; the entry never lands in config.yaml. The `[0]`, `[1]` indexing syntax creates literal keys like `fallback_providers[0]` in the file. For `fallback_providers`, use `hermes fallback add`. For `providers:` (keyed dict), manually edit config.yaml.
8. **`hermes fallback add` is interactive-only.** Cannot be automated via expect, PTY mode, piped input, or any non-interactive method. The picker requires a real terminal. For automation, you must ask the user to run it manually.
9. **"Burn the expiring resource first" is not always optimal.** When comparing providers, quality and token efficiency matter more than expiration dates. A model that's both smarter AND more token-efficient (like MiMo v2.5 Pro vs DeepSeek V4 Pro) should stay as default even if another resource expires sooner. Save the expiring resource for tasks that specifically need its strengths.
10. **`auxiliary.*.provider: auto` silently inherits the main model provider.** Every auxiliary subsystem (title_generation, compression, vision, curator, etc.) defaults to `provider: auto` with empty `model` and `api_key`. This means they route through the main `model.provider` (e.g., xiaomi). If that provider's API key expires or becomes invalid, the main model may still work (if re-authenticated or cached) but auxiliary calls fail with HTTP 401. The error message is generic ("Auxiliary X failed: HTTP 401: Invalid API Key") and doesn't tell you which provider it tried. **Diagnosis**: check `config.yaml` for the failing aux type's `provider: auto` → trace to `model.provider` → check that provider's key. **Fix**: explicitly set the aux type's `provider` and `model` to a known-working provider (e.g., `nous` with OAuth auth, which doesn't depend on API keys in `.env`). Minimal fix — only change the broken aux type, not all of them. **Verification**: `grep -A7 'title_generation:' ~/.hermes/profiles/<profile>/config.yaml` should show the explicit provider, not `auto`.
11. **Profile `config.yaml` is isolated — root config does NOT apply.** Each Hermes profile reads ONLY its own `~/.hermes/profiles/<name>/config.yaml`. The root `~/.hermes/config.yaml` is the default profile's config. Adding `providers:`, `fallback_providers:`, or any model config to the root file has NO effect on named profiles. Same isolation pattern as `.env` (pitfall 3b), but applies to the entire config. **Symptom**: you add a custom provider block, restart, and `hermes config show` doesn't show it. **Diagnosis**: `hermes config show` prints the Config path at the top — verify it says `~/.hermes/profiles/<name>/config.yaml`, not the root. **Fix**: move the config to the correct profile's config.yaml. For the senna profile, the active config is at `~/.hermes/profiles/senna/config.yaml`.
12. **DeepSeek V4 Flash has a known non-deterministic language switching bug.** The model intermittently responds in Chinese despite English prompts, regardless of temperature, system prompt, or API provider. This is a model-level issue — not configurable away. **Do not set DeepSeek V4 Flash as the primary model for English-only use.** See `references/deepseek-v4-language-issue.md` for full details, reproduction sources (GitHub #1226, #1443), attempted fixes, and recommended workaround (switch to Qwen3-Coder-Next as primary, keep DeepSeek as fallback only).
13. **`openrouter/free` meta-model in auxiliary slots → HTTP 403 content-filter size errors.** The `openrouter/free` router rotates across backing providers, and some sit behind content filters with a max request size. A session with large early content fails with `HTTP 403: Request blocked by content filter: Request content exceeds maximum size for content filtering` — surfaced as `WARNING agent.title_generator: Title generation failed: Error code: 403` in agent.log. This is NOT an auth 403 (contrast pitfall 10's 401); the key is fine, the routed provider rejected the payload size. Title generation is harmless (falls back to a default title) but noisy; the same failure on `compression` is consequential. **Fix:** pin the aux slot to a specific free model instead of the meta-router — `google/gemma-4-31b-it:free` is proven in this fleet's vision slot. **Fleet audit:** `grep -l "openrouter/free" ~/.hermes/profiles/*/config.yaml` — any hit inside an `auxiliary:` block is latent debt. Applied fleet-wide (23 profiles, title_generation) 2026-07-27; requires gateway/profile restart to take effect.
14. **MOA (virtual `moa` provider) crashes with `TypeError: 'types.SimpleNamespace' object is not iterable` and falls back — the configured references NEVER ran.** When the session model is a MOA preset (banner `council via provider moa`), a crash in the MOA streaming facade triggers the fallback chain (typically `openrouter/free`), and THAT model produces the visible answer. So "what the user saw" ≠ "what was configured": reference models (e.g. DeepSeek V4 Flash) may be selected (`Auxiliary moa_reference: using ...` in the per-profile agent log) but never deliver output. This is NOT an auth failure — direct DeepSeek calls succeed in the same session. **Diagnosis**: per-profile log at `~/.hermes/profiles/<profile>/logs/agent.log` (NOT `~/.hermes/logs/agent.log`) + per-session model attribution in `state.db`; exact queries and signatures in `references/moa-fallback-diagnosis.md`. **First workaround**: `display.streaming: false` in the profile config — MOA then uses the complete-response path and skips the broken stream iterator. Also verify whether `hermes update` touches the MOA files before promising an update fixes it (the 2026-07-31 gap of 72 commits touched zero MOA files).
