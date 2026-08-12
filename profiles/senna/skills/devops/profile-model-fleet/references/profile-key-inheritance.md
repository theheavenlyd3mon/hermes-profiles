# Profile Key Inheritance — Lessons Learned

## The Rule
Each Hermes profile reads ONLY its own `.env` at `~/.hermes/profiles/<name>/.env`.
The root `~/.hermes/.env` is NOT inherited by non-default profiles.

## Evidence (2026-05-27)

**Researcher profile failure:**
- `config.yaml` had `provider: deepseek`, `default: deepseek-v4-pro`
- Root `~/.hermes/.env` had `DEEPSEEK_API_KEY` (active, not commented)
- Researcher's own `.env` had NO `DEEPSEEK_API_KEY`
- Result: `RuntimeError: Provider 'deepseek' is set in config.yaml but no API key was found.`
- Every Discord message to the researcher bot failed with this error

**Oracle profile working:**
- Same provider/model as researcher
- Oracle's own `.env` HAD `DEEPSEEK_API_KEY` (active)
- Result: worked fine

**Conclusion:** Root `.env` is irrelevant for non-default profiles.

## Config Resolution Chain

The effective config is resolved from (first match wins):
1. `~/.hermes/profiles/<name>/config.yaml` — profile's own config
2. `~/.hermes/profiles/<name>/home/.hermes/config.yaml` — profile's HERMES_HOME config
3. `~/.hermes/config.yaml` — root/default config

But `.env` (secrets) is NOT part of this chain. Each profile reads its own `.env` only.

## How to Check Key Availability

```bash
# What keys does a profile have?
grep "API_KEY" ~/.hermes/profiles/<name>/.env | sed 's/=.*/=***/'

# What provider does a profile use?
grep -A3 "^model:" ~/.hermes/profiles/<name>/config.yaml

# Does the key match the provider?
# provider: deepseek → needs DEEPSEEK_API_KEY
# provider: xiaomi → needs XIAOMI_API_KEY
# provider: openrouter → needs OPENROUTER_API_KEY
# provider: nous → may work without key (free tier)
```

## Fix Pattern

When a profile fails due to missing key:
1. Option A: Add the key to the profile's `.env` (copy from root if available)
2. Option B: Switch the profile to a provider whose key exists in its `.env`
3. Restart the gateway after either change

## Model Name Format

Always use `provider/model` format in config.yaml:
```yaml
model:
  provider: xiaomi
  default: xiaomi/mimo-v2.5-pro    # ✓ correct (with provider prefix)
  # default: mimo-v2.5-pro          # ✗ works but inconsistent
```

The bare name may work but the provider prefix is canonical and avoids ambiguity.
