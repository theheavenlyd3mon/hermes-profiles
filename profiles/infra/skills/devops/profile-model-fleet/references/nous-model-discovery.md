# Nous Provider — Model Discovery & Pricing

## Listing available models

All models available through the Nous provider:

```bash
curl -s "https://inference-api.nousresearch.com/v1/models" \
  -H "Authorization: Bearer $(python3 -c "import json; d=json.load(open('~/.hermes/auth.json')); cp=d.get('credential_pool',{}).get('nous',[]); print(cp[0]['agent_key'] if cp else '')")" \
  | python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin).get('data',[])]"
```

## Checking pricing for specific models

Authenticated requests return real pass-through pricing. Unauthenticated requests return all $0.0000.

```bash
# Get auth key from Hermes credential pool
NOUS_KEY=$(python3 -c "
import json
try:
    d = json.load(open('~/.hermes/auth.json'))
    cp = d.get('credential_pool', {}).get('nous', [])
    print(cp[0]['agent_key'] if cp else '')
except: pass
")

# Check specific models by name
targets='deepseek/deepseek-v4-flash qwen/qwen3-coder-next qwen/qwen3-coder-flash'
curl -s "https://inference-api.nousresearch.com/v1/models" \
  -H "Authorization: Bearer $NOUS_KEY" \
  | python3 -c "
import json,sys
data = json.load(sys.stdin)
targets = ['${targets// /,}')
for m in data.get('data',[]):
    pkey=m['id']
    if pkey in targets:
        p = float(m.get('pricing',{}).get('prompt',0))*1_000_000
        c = float(m.get('pricing',{}).get('completion',0))*1_000_000
        ctx = m.get('context_length',0)
        print(f'{pkey:50s}  \${p:<8.4f}/M in  \${c:<8.4f}/M out  ctx={ctx}')
\"
```

## Filtering for text-capable models

The models list includes image gen, TTS, and embedding models. Filter to text chat models:

```bash
curl -s "https://inference-api.nousresearch.com/v1/models" \
  -H "Authorization: Bearer $NOUS_KEY" \
  | python3 -c "
import json,sys
data = json.load(sys.stdin)
keywords = ['gpt','claude','deepseek','qwen','mistral','llama','gemini','hermes',
            'minimax','phi','command','step','snowflake','o3','o4','r1']
text_models = [
    m for m in data.get('data',[])
    if any(k in m['id'].lower() for k in keywords)
    and 'image' not in m.get('architecture',{}).get('modality','')
    and 'audio' not in m.get('architecture',{}).get('modality','')
    and 'video' not in m.get('architecture',{}).get('modality','')
]
text_models.sort(key=lambda m: m['id'])
for m in text_models:
    p = float(m.get('pricing',{}).get('prompt',0))*1_000_000
    c = float(m.get('pricing',{}).get('completion',0))*1_000_000
    ctx = m.get('context_length',0)
    print(f\"{m['id']:55s}  P: \${p:.4f}/M  C: \${c:.4f}/M  CTX: {ctx}\")
\"
```

## Evaluating models for agentic use

When assessing a model for tool-calling/agentic profiles on the Nous provider:

1. **Tool-call discipline** — Qwen coder variants train specifically on structured outputs. General chat models (Llama, Mistral base) may hallucinate tool schemas or add extra fields.
2. **Input cost dominates** — agentic loops are read-heavy. A model with $0.11/M input (coder-next) beats $0.126/M (v4-flash) despite costing 3x on output, because input is typically 80%+ of total tokens.
3. **Output verbosity matters** — minimax models produce longer responses per turn. In tool loops, every extra output token increases cost without improving call quality.
4. **Flash tier for latency** — coder-flash, v4-flash, step-3.5-flash return first tokens faster. Worth optimizing for interactive profiles.
5. **Free-model gating** — if a test returns HTTP 426, the model is classified as "free" on Nous and needs a newer Hermes client. Swap to a paid-tier equivalent.

Also reference SKILL.md's "Evaluating models for agentic fitness" section for the full criteria matrix.

## Testing a model works before assigning

```bash
hermes chat --model "<model-id>" --provider nous -q "ping" --ignore-user-config -Q
```

Expected success: returns a response like "Pong!" or "Hello!"
Expected failure: HTTP 426 = free-tier gated (need newer Hermes client); timeout = model too slow or unresponsive

## Free-tier model gating (Hermes v0.13.0)

Models classified as "free" by the Nous provider return HTTP 426:
- `qwen/qwen3.6-plus`
- `nousresearch/hermes-4-70b`
- `nousresearch/hermes-4-405b`

These require the `alice/nous-portal-recommended-models` branch (not merged to main as of May 14). Use paid alternatives instead.

## Verifying a profile's model config

After changing a profile's model, verify the profile can use it:

```bash
hermes chat --model "<model-id>" --provider nous --profile <profile> -q "ping" --ignore-user-config -Q
```

Note: `--profile <profile>` loads the profile's config.yaml. If this fails while `--profile senna` succeeds, the profile's config may be pointing at the wrong model, or the profile has a session infrastructure issue.

## Profile config structure

```yaml
# ~/.hermes/profiles/<profile>/config.yaml
model:
  provider: nous
  default: <model-id>
  base_url: https://inference-api.nousresearch.com/v1
```

Apply changes via:
```bash
hermes config set --profile <profile> model.default <model-id>
```
Or by editing the file directly and running `hermes config check --profile <profile>` to validate.
