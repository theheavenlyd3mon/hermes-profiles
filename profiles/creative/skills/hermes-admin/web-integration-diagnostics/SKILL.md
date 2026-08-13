---
name: web-integration-diagnostics
description: Diagnose Hermes web/browser tools (Firecrawl, Browserbase).
---

# Web Integration Diagnostics (Firecrawl · Browserbase)

Hermes web tools (`web_search`, `web_extract`) default to Firecrawl; the browser tool defaults to Browserbase cloud. Both are wired per-profile via `config.yaml` (`web.backend`, `browser.cloud_provider`) with secrets in the profile `.env`. This is the check-and-fix path when a user asks "is Firecrawl/Browserbase working?" or when web/browser tools misbehave.

## When to use
- User asks to check/verify/configure Firecrawl, Browserbase, or "the web tools".
- `web_search` / `web_extract` fail or return empty.
- Browser tool warns about stealth/proxies or silently falls back to local.
- After rotating API keys in any profile `.env`.

## Profile layout (macOS)
- Keys live in `~/.hermes/profiles/<profile>/.env` — each profile reads ONLY its own `.env`; default-profile secrets are invisible to other profiles (and vice versa).
- Per-profile `config.yaml`: `web.backend: firecrawl`, `browser.cloud_provider: browserbase`, `browser.use_gateway: false` for direct (non-gateway) operation.
- The same key is often copied across multiple profiles — rotation must be synced everywhere the user cares about.

## Probe recipes
Run `scripts/probe_web_services.sh [env-file]` for a one-shot check of both services. Manual equivalents:

### Firecrawl — uses `Authorization: Bearer`
```bash
curl -s -o /tmp/fc.json -w "%{http_code}" -X POST https://api.firecrawl.dev/v1/scrape \
  -H "Authorization: Bearer $FC_KEY" -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","formats":["markdown"]}'
# expect HTTP 200 + {"success":true,...}
```
- `POST /v1/search` uses the same auth. `/v1/credits` no longer exists (404) — do NOT use it as a health check.

### Browserbase — uses `X-BB-API-Key` header (NOT Bearer!)
```bash
curl -s -X POST https://api.browserbase.com/v1/sessions \
  -H "X-BB-API-Key: $BB_KEY" -H "Content-Type: application/json" \
  -d "{\"projectId\":\"$BB_PROJ\"}"
# expect {"id":..., "status":"RUNNING", ...}
```
- `GET /v1/sessions` and `GET /v1/sessions/<id>` use the same header.
- A valid session includes `connectUrl: wss://connect.*.browserbase.com/...`.

## Pitfalls
1. **Auth header is the #1 trap**: Browserbase returns `401 Unauthorized` for `Authorization: Bearer` even with a VALID key. It MUST be `X-BB-API-Key`. This caused a false "dead key" diagnosis — verify the header before ever blaming the key. Hermes's own plugin (`~/.hermes/hermes-agent/plugins/browser/browserbase/provider.py`) already uses the correct header, so browser-tool failures are rarely key-auth issues.
2. **"Running WITHOUT residential proxies" is benign**: it means the Browserbase plan tier lacks the residential-proxy add-on (paid). Browser still works with `basic_stealth`; the Hermes plugin auto-falls-back when paid features are unavailable. Do not chase this as a config bug; mention the plan upgrade only if the user cares about bot-protected sites.
3. **DELETE session may 404** right after creation (session already auto-cleaned/expired). Creation + `RUNNING` status is the pass criterion; cleanup 404 is noise.
4. **Never print full keys** in tool output or chat — mask (`${KEY:0:9}****`).
5. **Back up `.env` before editing**: `cp .env .env.bak-$(date +%Y%m%d-%H%M%S)`, then replace only the target line:
   `sed -i '' -E "s|^BROWSERBASE_API_KEY=.*|BROWSERBASE_API_KEY=${NEW}|" .env`
6. **Test the new key BEFORE writing it anywhere** (curl probe with the correct header), and end-to-end AFTER (browser_navigate + web_search through Hermes tools — not just raw curl).

## Verification after a change
1. `scripts/probe_web_services.sh ~/.hermes/profiles/<profile>/.env`
2. `browser_navigate` to a normal page — expect success + `stealth_features: ["basic_stealth"]`.
3. `web_search` through the Hermes tool — expect real results (proves Firecrawl wiring, not just the API).

## Key rotation flow
1. User provides new key (they must copy from the provider dashboard — you cannot mint it).
2. Probe the new key against the API first (correct header!).
3. Back up `.env`, sed-replace the key line, verify with a masked grep.
4. Re-probe + end-to-end test. Offer to sync the identical key to other profiles that share it.
