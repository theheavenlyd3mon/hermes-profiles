# "Wrong Model" Discord Error — Case Study

## Symptom
User reports on Discord: "researcher couldn't respond due to wrong model" and the bot showed "deepseek" in the error message.

## Root Cause
The researcher profile's `config.yaml` was:
```yaml
model:
  provider: deepseek
  default: deepseek-v4-pro
  base_url: https://api.deepseek.com
```

But the researcher's `.env` had NO `DEEPSEEK_API_KEY`. The root `~/.hermes/.env` DID have it, but profiles don't inherit from root.

## Gateway Error
```
RuntimeError: Provider 'deepseek' is set in config.yaml but no API key was found.
Set the DEEPSEEK_API_KEY environment variable, or switch to a different provider with `hermes model`.
```

This error appears in `gateway.log` (not `gateway.error.log`) and is also sent to Discord as the bot's response.

## Fix Applied
1. Changed `config.yaml` to use xiaomi provider (key already existed in `.env`):
   ```yaml
   model:
     provider: xiaomi
     default: mimo-v2.5-pro
     base_url: https://token-plan-sgp.xiaomimimo.com/v1
   ```
2. Uncommented `XIAOMI_API_KEY` in researcher's `.env` (was commented out)
3. Restarted gateway

## Key Lesson
**Profiles do NOT inherit from root `.env`.** Always check the profile's own `.env` for the required key, not just the root.

## Quick Diagnostic Commands
```bash
# Check what provider a profile uses
grep -A3 "^model:" ~/.hermes/profiles/<name>/config.yaml

# Check what keys the profile has
grep "API_KEY" ~/.hermes/profiles/<name>/.env | sed 's/=.*/=***/'

# Check gateway.log for the specific error
grep "RuntimeError.*API key" ~/.hermes/profiles/<name>/logs/gateway.log
```
