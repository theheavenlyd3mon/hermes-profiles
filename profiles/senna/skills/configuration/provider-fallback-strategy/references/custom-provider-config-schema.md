# Custom Provider Config Schema

Source: `hermes_cli/config.py` — `_normalize_custom_provider_entry()` (line 3774+)

## `providers:` Keyed Dict (v12+ format, recommended)

```yaml
providers:
  <provider_key>:        # doubles as --provider flag value
    name: string         # display name (falls back to provider_key)
    base_url: string     # OpenAI-compatible endpoint URL (required)
    key_env: string      # env var name in profile .env (recommended)
    api_key: string      # raw key (NOT recommended — use key_env)
    model: string        # default model to offer
    models:              # explicit model list (dict or list)
      model-id-1: {}
      model-id-2: {}
    context_length: int  # override context window
    discover_models: bool  # auto-query /v1/models
    rate_limit_delay: float  # seconds between requests
    api_mode: string     # transport mode (e.g. chat_completions)
    transport: string    # alias for api_mode
    extra_body: {}       # merged into every API request
    request_timeout_seconds: int
    stale_timeout_seconds: int
```

## `custom_providers:` List (legacy format)

```yaml
custom_providers:
  - name: stewart
    base_url: https://host.tailnet.ts.net/v1
    key_env: STEWART_API_KEY
    model: qwen3.6-27b-gptq
```

Same fields, just as a list entry instead of a keyed dict.

## URL Resolution Order

The normalizer checks these fields in order, using the first valid URL found:
1. `base_url`
2. `url`
3. `api`

Must be a valid URL with scheme (`https://`) and host. Relative paths or bare hostnames are rejected with a warning.

## CamelCase Aliases (auto-mapped with warning)

| CamelCase | Snake_case |
|-----------|------------|
| `apiKey` | `api_key` |
| `baseUrl` | `base_url` |
| `apiMode` | `api_mode` |
| `keyEnv` | `key_env` |
| `apiKeyEnv` | `key_env` |
| `defaultModel` | `default_model` |
| `contextLength` | `context_length` |
| `rateLimitDelay` | `rate_limit_delay` |

## How It Appears in the Model Picker

After adding a provider, `hermes model` and `/model` show it as a selectable option. The provider key (e.g. `stewart`) is what you pass to `--provider`. If `discover_models: true`, available models are auto-detected from the endpoint's `/v1/models` response.

## Environment Variable Loading

The profile's `.env` is loaded in order:
1. Root `~/.hermes/.env` (global defaults)
2. Profile `~/.hermes/profiles/<name>/.env` (overrides matching keys)

The `key_env` value (e.g. `STEWART_API_KEY`) must be set in the profile's `.env` — not just root.
