# Auxiliary Model Provider Resolution

## How `provider: auto` works

Every auxiliary subsystem in `config.yaml` has this structure:

```yaml
auxiliary:
  title_generation:
    api_key: ''
    base_url: ''
    extra_body: {}
    model: ''
    provider: auto
    timeout: 30
```

When `provider: auto`:
1. If `api_key` is set → use it with the configured `base_url`
2. If `api_key` is empty → inherit from `model.provider` + `model.default`
3. The aux call uses the **main model's provider credentials**

## Failure mode

If the main provider's API key is invalid/expired:
- Main model may still work (cached auth, OAuth refresh, etc.)
- Auxiliary calls fail with `HTTP 401: Invalid API Key`
- Error is generic — doesn't name the provider it tried

## Which aux types are affected

All of them. The default for every aux type is `provider: auto`. If your main provider is xiaomi/deepseek/etc. with an API key, all aux calls route through that key.

Exception: `vision` is often explicitly set to `provider: nous` (OAuth-based, no API key needed).

## Fix pattern

Only fix the broken aux type. Don't reconfigure everything.

```yaml
# Before (broken — inherits dead xiaomi key)
auxiliary:
  title_generation:
    model: ''
    provider: auto

# After (explicit — uses Nous Portal OAuth)
auxiliary:
  title_generation:
    model: openai/gpt-4.1-nano
    provider: nous
```

## Cheapest models per aux type (Nous Portal)

| Aux type | Recommended model | Reason |
|----------|------------------|--------|
| title_generation | openai/gpt-4.1-nano | Short text, trivial task |
| approval | openai/gpt-4.1-nano | Yes/no decisions |
| session_search | openai/gpt-4.1-nano | Query generation |
| vision | openai/gpt-4.1-nano | Already default |
| compression | openai/gpt-5.4-mini | Needs summarization quality |
| curator | openai/gpt-5.4-mini | Skill/memory curation |
| kanban_decomposer | openai/gpt-5.4-mini | Task breakdown |
| web_extract | openai/gpt-5.4-mini | Content extraction |

## Verification

```bash
grep -A7 'title_generation:' ~/.hermes/profiles/<profile>/config.yaml
# Should show explicit provider, not 'auto'
```
