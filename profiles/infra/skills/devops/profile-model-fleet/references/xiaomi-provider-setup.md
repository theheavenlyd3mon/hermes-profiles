# Xiaomi MiMo Provider — Credential & Config Reference

## Provider identity
- **Provider name in Hermes:** `xiaomi`
- **Base URL:** `https://token-plan-sgp.xiaomimimo.com/v1`
- **API key env var:** `XIAOMI_API_KEY` (set in global `~/.hermes/.env`)

## Available models (from model catalog, retrieved 2026-05-26)
| Model ID | Description |
|---|---|
| `xiaomi/mimo-v2.5-pro` | Latest flagship — used by coder, reviewer, architect, council, security, debugger |
| `xiaomi/mimo-v2.5` | Non-pro variant of v2.5 |
| `xiaomi/mimo-v2-pro` | Previous-gen pro model |
| `xiaomi/mimo-v2-omni` | Multimodal variant |
| `xiaomi/mimo-v2-flash` | Fast/cheap variant |

## Credential access

The Xiaomi credential lives in the global credential pool:

```bash
# Check credential status
python3 -c "
import json
with open('~/.hermes/auth.json') as f:
    d = json.load(f)
for cred in d.get('credential_pool', {}).get('xiaomi', []):
    print(f\"ID: {cred['id']}\")
    print(f\"Source: {cred['source']}\")
    print(f\"Status: {cred['last_status']}\")
    print(f\"Base URL: {cred['base_url']}\")
"
```

Expected output:
```
ID: 900f78
Source: env:XIAOMI_API_KEY
Status: ok
Base URL: https://token-plan-sgp.xiaomimimo.com/v1
```

## Profile config

Any profile using Xiaomi needs this in its `~/.hermes/profiles/<name>/config.yaml`:

```yaml
model:
  provider: xiaomi
  default: xiaomi/mimo-v2.5-pro
  base_url: https://token-plan-sgp.xiaomimimo.com/v1
```

No `.env` file needed per-profile — the credential pool in auth.json is shared globally.

## Pitfalls

- **Default base URL mismatch:** The `.env.example` suggests `https://api.xiaomimimo.com/v1` but this account uses `https://token-plan-sgp.xiaomimimo.com/v1`. Using the wrong base URL causes auth failures. Always verify with `hermes -p <profile> status` after configuring.
- **No per-profile auth.json:** The auth.json at `~/.hermes/auth.json` is the global one. Profile-local `auth.json` files are not needed for Xiaomi since it uses API key auth (not OAuth). The credential pool is shared.
- **Model name prefix:** Full model name is `xiaomi/mimo-v2.5-pro` (with `xiaomi/` prefix). Omitting the prefix results in "model not found" errors.
