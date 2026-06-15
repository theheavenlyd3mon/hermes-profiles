---
name: provider-fallback-strategy
description: Diagnose provider auth failures (401/403/404), check credential health, configure fallback chains, and plan budget-aware model tiering across multiple providers.
tags: [hermes, configuration, providers, auth, troubleshooting, fallback]
version: 1.2.0
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

When a Discord bot fails to respond, check its gateway log for the specific error:

```bash
tail -30 ~/.hermes/profiles/<profile>/logs/gateway.log | grep -A5 "RuntimeError\|Agent error"
tail -10 ~/.hermes/profiles/<profile>/logs/gateway.error.log
```

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

**References**: `references/provider-pricing-and-free-models.md` (current pricing and free model lists), `references/model-comparison-mimo-vs-deepseek.md` (head-to-head model comparisons), `references/error-patterns.md` (RuntimeError messages and their root causes), `references/auxiliary-model-provider-resolution.md` (how `provider: auto` in auxiliary config inherits the main provider and fails when that key dies).

## Common Provider + Available Model Reference

| Provider | Credential check | Budget type | Notes |
|----------|-----------------|-------------|-------|
| xiaomi | env:XIAOMI_API_KEY + XIAOMI_BASE_URL | Token grant | MiMo models (mimo-v2.5-pro, mimo-v2-flash). Singapore endpoint. |
| deepseek | env:DEEPSEEK_API_KEY + DEEPSEEK_BASE_URL | Dollar credits | V4 Flash ($0.14/M in, $0.28/M out), V4 Pro (promo pricing varies). Direct API. |
| openrouter | env:OPENROUTER_API_KEY | Free models + credits | Aggregates 350+ models. Free tier includes DeepSeek V4 Flash, Qwen3 Coder, Nemotron 3 Super, etc. |
| nous | hermes auth (OAuth) | Subscription credits | Portal-managed. Free DeepSeek V4 Flash may come and go. |
| nvidia | env:NVIDIA_API_KEY | Free tier | Nemotron models. |
| z.ai | env:ZAI_API_KEY | Free tier | GLM models. |
| kimi | env:KIMI_API_KEY | Credits | Moonshot AI models. |
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
7. **`hermes config set` CANNOT create YAML arrays.** `hermes config set fallback_providers '[{...}]'` stores the array as a quoted string, not a proper YAML list. The `[0]`, `[1]` indexing syntax creates literal keys like `fallback_providers[0]` in the file. Always use `hermes fallback add` for multi-entry chains.
8. **`hermes fallback add` is interactive-only.** Cannot be automated via expect, PTY mode, piped input, or any non-interactive method. The picker requires a real terminal. For automation, you must ask the user to run it manually.
9. **"Burn the expiring resource first" is not always optimal.** When comparing providers, quality and token efficiency matter more than expiration dates. A model that's both smarter AND more token-efficient (like MiMo v2.5 Pro vs DeepSeek V4 Pro) should stay as default even if another resource expires sooner. Save the expiring resource for tasks that specifically need its strengths.
10. **`auxiliary.*.provider: auto` silently inherits the main model provider.** Every auxiliary subsystem (title_generation, compression, vision, curator, etc.) defaults to `provider: auto` with empty `model` and `api_key`. This means they route through the main `model.provider` (e.g., xiaomi). If that provider's API key expires or becomes invalid, the main model may still work (if re-authenticated or cached) but auxiliary calls fail with HTTP 401. The error message is generic ("Auxiliary X failed: HTTP 401: Invalid API Key") and doesn't tell you which provider it tried. **Diagnosis**: check `config.yaml` for the failing aux type's `provider: auto` → trace to `model.provider` → check that provider's key. **Fix**: explicitly set the aux type's `provider` and `model` to a known-working provider (e.g., `nous` with OAuth auth, which doesn't depend on API keys in `.env`). Minimal fix — only change the broken aux type, not all of them. **Verification**: `grep -A7 'title_generation:' ~/.hermes/profiles/<profile>/config.yaml` should show the explicit provider, not `auto`.
