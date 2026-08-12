---
name: hermes-profile-config
description: Manage Hermes Agent profile configurations — audit, update, and fix model/provider settings across profiles. Use when the user asks to review, fix, or bulk-update profile configs, model names, provider URLs, or Discord/platform settings across multiple profiles.
---

# Hermes Profile Config Management

Audit, update, and fix Hermes Agent profile configurations across the `~/.hermes/profiles/` directory.

## Key Paths

```
~/.hermes/profiles/<name>/config.yaml    # Per-profile config
~/.hermes/config.yaml                     # Global config
~/.hermes/.env                            # API keys (XIAOMI_API_KEY, etc.)
```

## Model Naming Convention

**Correct format** — model name and provider are separate fields:

```yaml
model:
  default: mimo-v2.5-pro
  provider: xiaomi
providers:
  xiaomi:
    base_url: https://token-plan-sgp.xiaomimimo.com/v1
```

**Incorrect format** — provider prefix baked into model string:

```yaml
model: xiaomi/mimo-v2.5-pro   # ← Wrong: no explicit provider, relies on implicit resolution
```

Always split into `model.default` + `model.provider` + `providers.<name>.base_url`.

## Audit Pattern

Quick audit of all profiles' model and provider status:

```bash
for dir in ~/.hermes/profiles/*/; do
  name=$(basename "$dir")
  model=$(grep "^model:" "$dir/config.yaml" 2>/dev/null | head -1 | awk '{print $2}')
  echo "$name: $model"
done
```

Check which profiles have `providers:` set:

```bash
for dir in ~/.hermes/profiles/*/; do
  name=$(basename "$dir")
  echo "=== $name ==="
  grep -A8 "^providers:" "$dir/config.yaml" 2>/dev/null | head -9
done
```

## Bulk Update Pattern

When updating many profiles at once, use `execute_code` with Python to batch-patch all `config.yaml` files. This is more reliable than individual `patch` calls for multi-file changes.

```python
import os

profiles_dir = os.path.expanduser("~/.hermes/profiles")

for name in sorted(os.listdir(profiles_dir)):
    config_path = os.path.join(profiles_dir, name, "config.yaml")
    if not os.path.isfile(config_path):
        continue
    with open(config_path, "r") as f:
        content = f.read()
    # ... apply transformations ...
    with open(config_path, "w") as f:
        f.write(content)
```

## Common Fixes

### Add provider block to profiles missing it

Replace flat model string with structured model + providers:

```yaml
# Before
model: xiaomi/mimo-v2.5-pro

# After
model:
  default: mimo-v2.5-pro
  provider: xiaomi
providers:
  xiaomi:
    base_url: https://token-plan-sgp.xiaomimimo.com/v1
```

### Fix Discord bot not responding

Check these settings in the profile's `config.yaml` under the `discord:` section:

| Setting | Symptom if wrong | Fix |
|---|---|---|
| `require_mention: true` | Bot ignores all messages without `@` | Set to `false` if bot should respond freely |
| `free_response_channels` | Bot only responds in one specific channel | Add the channel ID or set `require_mention: false` |
| `allowed_channels: ''` (empty) | May block all channels if non-empty elsewhere | Ensure target channel is allowed |

**Most common cause of silent Discord bot:** `require_mention: true` — the bot is working fine but ignoring messages that don't @mention it.

### Switch a profile to OpenRouter / owl-alpha

```yaml
model:
  default: owl-alpha
  provider: openrouter
providers:
  openrouter:
    base_url: https://openrouter.ai/api/v1
```

Ensure `OPENROUTER_API_KEY` is set in `~/.hermes/.env`.

## Provider Base URLs

| Provider | Base URL |
|---|---|
| xiaomi | `https://token-plan-sgp.xiaomimimo.com/v1` |
| openrouter | `https://openrouter.ai/api/v1` |
| deepseek | `https://api.deepseek.com` |

## After Making Changes

Always restart the gateway for config changes to take effect:

```bash
hermes gateway restart
```

Or in-session: `/restart` (gateway session) or `/new` (CLI session).
