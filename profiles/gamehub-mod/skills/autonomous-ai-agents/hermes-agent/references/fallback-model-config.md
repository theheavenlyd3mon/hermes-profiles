# Fallback Model Configuration

When your primary model/provider returns errors (HTTP 503 capacity limits, rate limiting, provider downtime), Hermes falls back to an alternative model. This keeps the session running when the primary upstream is degraded.

## How It Works

From the error log when fallback activates:

```
⚠️  API call failed (attempt 1/3): InternalServerError [HTTP 503]
⚠️  API call failed (attempt 2/3): InternalServerError [HTTP 503]
⚠️  API call failed (attempt 3/3): InternalServerError [HTTP 503]
❌ API failed after 3 retries — trying fallback...
```

After exhausting retries on the primary model, Hermes retries with the fallback. If the fallback also fails, the error is terminal.

## Configuration

Add a `fallback` section under `model` in the profile's `config.yaml`:

```yaml
model:
  provider: nous
  default: deepseek/deepseek-v4-flash
  base_url: https://inference-api.nousresearch.com/v1
  fallback:
    provider: openrouter          # Different provider for resilience
    default: qwen/qwen3.6-plus    # Fallback model
```

### Via CLI

```bash
hermes config set model.fallback.provider openrouter
hermes config set model.fallback.default qwen/qwen3.6-plus
```

### Check current config

```bash
grep -A10 'model:' ~/.hermes/profiles/senna/config.yaml

# Verify credentials for fallback provider
grep -l OPENROUTER_API_KEY ~/.hermes/.env 2>/dev/null || echo "No OpenRouter key found"
```

## Key Principles

| Factor | Recommendation |
|--------|---------------|
| **Provider diversity** | Fallback to a different provider than primary. If DeepSeek upstream is down, routing fallback through Nous Portal (same endpoint) may still hit the same capacity issue |
| **Verify credentials** | The fallback provider's API key must be set in `~/.hermes/.env` |
| **Model capability match** | Fallback should match task type — don't fall back to a non-coding model for code work |
| **Profile vs root** | Each profile has its own model config. Apply per-profile or at root config. Specialist profiles (architect, coder, researcher) that use DeepSeek models need their own fallbacks too |
| **Cost awareness** | Fallback to an expensive model may increase cost — plan for the delta |

## Real-World Example (this session)

**Symptom:** `deepseek/deepseek-v4-flash` via Nous Portal returned HTTP 503 — upstream capacity limits. All 3 retries + fallback (unconfigured) failed.

**Root cause:** DeepSeek's upstream was overloaded. The specific model `deepseek-v4-flash` was temporarily unavailable.

**Fix applied:** No fallback was configured. After the outage resolved, the model worked again.

**Long-term fix:** Add a fallback to OpenRouter with `qwen/qwen3.6-plus` or `mistralai/mistral-small-3.1` so future outages don't block the session.

## Specialist Profile Considerations

Many specialist profiles also use DeepSeek models. A DeepSeek outage impacts the entire kanban team:

| Profile | Model | Same Upstream? |
|---------|-------|----------------|
| senna | deepseek/deepseek-v4-flash | Yes |
| architect | deepseek/deepseek-v3.2 | Yes |
| researcher | deepseek/deepseek-v3.2 | Yes |
| reviewer | deepseek/deepseek-r1-0528 | Yes |
| debugger | deepseek/deepseek-r1-0528 | Yes |
| security | deepseek/deepseek-r1-0528 | Yes |

To protect the full team, add fallback models to each profile that uses DeepSeek.

## Pitfalls

- **No fallback = single point of failure.** Without one, a 503 from the upstream terminates the session.
- **Same-provider fallback doesn't help for provider-wide outages.** If DeepSeek's upstream is down, falling back to another DeepSeek model on the same provider still hits the same capacity issue.
- **Test your fallback explicitly.** Don't assume it works until you've seen it successfully respond after a simulated primary failure.
- **Don't set fallback to the same model.** If `deepseek-v4-flash` is the one 503ing, falling back to the same model on the same provider doesn't help.
