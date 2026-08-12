# Rerouting OpenAI-SDK tools to Nous — reproduction recipe & error transcripts

Minimal working runner (no Claude, no OpenAI key):

```python
import os, json
from pathlib import Path

auth = json.loads(Path(os.path.expanduser("~/.hermes/auth.json")).read_text())
nous = auth.get("providers", {}).get("nous", {})
key = nous.get("agent_key") or nous.get("access_token") or ""
assert key, "no Nous agent_key in ~/.hermes/auth.json"

os.environ["OPENAI_API_KEY"] = key
os.environ["OPENAI_BASE_URL"] = "https://inference-api.nousresearch.com/v1"

# raw openai client: single prefix is correct
from openai import OpenAI
c = OpenAI(api_key=key, base_url="https://inference-api.nousresearch.com/v1")
print(c.chat.completions.create(model="openai/gpt-4.1-mini",
      messages=[{"role":"user","content":"say OK"}]).choices[0].message.content)

# dspy / litellm: DOUBLE prefix
import dspy
lm = dspy.LM("openai/openai/gpt-4.1-mini")   # litellm strips one -> Nous sees openai/gpt-4.1-mini
dspy.configure(lm=lm)
class T(dspy.Signature):
    q: str = dspy.InputField(); a: str = dspy.OutputField()
print(dspy.Predict(T)(q="say OK").a.strip())
```

## Error transcripts (with root cause + fix)

### 1. Missing credentials
```
litellm.exceptions.InternalServerError: OpenAIException - Missing credentials.
Please pass an `api_key`, ... or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable.
```
- **Cause**: `OPENAI_API_KEY` was empty. The key was read from `config.yaml` / `.env`
  (both have empty `api_key:` for nous) instead of `~/.hermes/auth.json` -> `providers.nous.agent_key`.
- **Fix**: load `agent_key` from `auth.json` at runtime (see runner above).

### 2. Model not found (404)
```
openai.NotFoundError: Error code: 404 - {'status': 404,
'message': "Model 'gpt-4.1-mini' not found. The requested model does not exist
in our configuration or OpenRouter catalog."}
```
- **Cause**: litellm stripped the `openai/` prefix, so Nous received `gpt-4.1-mini` (no provider namespace).
- **Fix**: pass the double prefix `openai/openai/gpt-4.1-mini` so Nous receives `openai/gpt-4.1-mini`.

### 3. GEPA signature drift (dspy 3.x)
```
optimizer = dspy.GEPA(
TypeError: GEPA.__init__() got an unexpected keyword argument 'max_steps'
```
- **Cause**: repo written against older dspy; 3.x uses `max_full_evals` / `max_metric_calls`.
- **Fix**: nothing required — the repo's try/except catches this and falls back to MIPROv2.
  Just ensure the fallback works (next error).

### 4. MIPROv2 missing optuna
```
ImportError: MIPROv2 requires optional dependency 'optuna'.
Install it with `pip install dspy[optuna]`.
```
- **Cause**: only `dspy` (not `dspy[optuna]`) installed.
- **Fix**: `pip install "dspy[optuna]"` (or `uv pip install "dspy[optuna]"`).
