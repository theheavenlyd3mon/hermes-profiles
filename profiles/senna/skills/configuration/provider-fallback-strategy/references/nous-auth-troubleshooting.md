# Nous Auth Troubleshooting (session capture)

## Symptoms

```
🔐 Nous 401 — Portal authentication failed.
Response: {'status': 401, 'message': 'Your API key is invalid, blocked or out of funds.'}
⚠️  API call failed (attempt 1/3): AuthenticationError [HTTP 401]
```

Fallback also fails:
```
⚠️  API call failed (attempt 1/3): NotFoundError [HTTP 404]
Response: Model 'qwen/qwen3-coder-next' requires available credits. Your account balance is too low...
```

## Diagnosis steps taken

1. Checked config.yaml — found `model.provider: nous`, `fallback_providers: []`
2. Checked auth status: `hermes auth status nous` → "logged in" (credential exists but not functional)
3. Listed credential pool: `hermes auth list` → found OPENROUTER_API_KEY env var available but not configured as fallback
4. Discovered that fallback model `qwen/qwen3-coder-next` routes through same provider (nous) → same failure

## Root cause

Nous OAuth device_code was stored and showed "logged in", but the account had insufficient credits for the request. The 401 means the API rejected the credential (expired/out of funds). The subsequent 404 on the fallback model was actually a credit issue, not a model-not-found — the error message said "requires available credits."

## Configuration fix (if user chooses to switch)

Change `model.provider` to `openrouter` and set `model.default` to a free model, OR add `fallback_providers` with a different provider so auto-retry doesn't hit the same dead provider.

## Key takeaway

"Logged in" ≠ functional for Nous. Always verify by trying an actual API call — auth status just confirms a token exists, not that it can serve requests.