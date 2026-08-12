# Provider Error Patterns & Fixes

Common RuntimeError messages from `run_agent.py` and their root causes.

## "no API key was found"

```
RuntimeError: Provider 'deepseek' is set in config.yaml but no API key was found.
Set the DEEPSEEK_API_KEY environment variable, or switch to a different provider with `hermes model`.
```

**Root causes** (in order of likelihood):
1. Key is **commented out** in `.env` (line starts with `# `)
2. Key is **missing entirely** from `.env`
3. Key env var name **doesn't match** what the provider expects (e.g., `DEEPSEEK_KEY` vs `DEEPSEEK_API_KEY`)
4. `.env` file is **empty or missing** for that profile

**Diagnostic**:
```bash
# Check if key exists (active or commented)
grep -i "<PROVIDER>" ~/.hermes/profiles/<profile>/.env

# Check if it's commented out
grep "^#.*API_KEY" ~/.hermes/profiles/<profile>/.env

# Compare with a working profile
diff <(grep "API_KEY" ~/.hermes/profiles/senna/.env | sed 's/=.*/=***/') \
     <(grep "API_KEY" ~/.hermes/profiles/<profile>/.env | sed 's/=.*/=***/')
```

**Fix**: Uncomment the key or add it. Use Python for safe editing (sed corrupts keys with special characters):
```python
with open('.env', 'r') as f:
    content = f.read()
content = content.replace('# XIAOMI_API_KEY=***XIAOMI_API_KEY=***with open('.env', 'w') as f:
    f.write(content)
```

**After fix**: Restart the gateway for the change to take effect.

## "returned 401"

```
RuntimeError: Provider 'X' returned 401: Unauthorized
```

**Root cause**: API key exists but is **invalid, expired, or revoked**.

**Fix**: Re-authenticate or get a new key from the provider's portal.

## "returned 403"

```
RuntimeError: Provider 'X' returned 403: Forbidden
```

**Root cause**: API key is valid but **account is suspended, out of credits, or lacks permission**.

**Fix**: Check billing/credits on the provider's portal.

## "returned 404"

```
RuntimeError: Provider 'X' returned 404: Not Found
```

**Root cause**: Model name doesn't exist on this provider, or the endpoint URL is wrong.

**Fix**: Verify model name with `hermes models` or check the provider's model list.

## Model name mismatch

```
RuntimeError: Model 'deepseek-v4-pro' not found for provider 'openrouter'
```

**Root cause**: OpenRouter uses `provider/model` format (e.g., `deepseek/deepseek-v4-pro`), not bare model names.

**Fix**: Use the correct format for the provider:
- OpenRouter: `deepseek/deepseek-v4-pro`
- DeepSeek direct: `deepseek-v4-pro`
- Xiaomi: `mimo-v2.5-pro`
