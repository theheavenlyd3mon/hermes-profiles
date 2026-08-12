# Nous Provider — Model Availability, Pricing & Profile Assignment

Queried from `https://inference-api.nousresearch.com/v1/models` (Bearer token: `NOUS_API_KEY`).
Pricing in [ADDRESS] per 1M tokens. Updated: 2026-05-14.

## Querying Available Models

```bash
# List all models with pricing
curl [PERSON_NAME] "https://inference-api.nousresearch.com/v1/models" \
  -H "Authorization: Bearer *** | \
  python3 -c "
import json,sys
models = json.load(sys.stdin).get('data',[])
for m in sorted(models, key=lambda x: float(x['pricing']['prompt'])):
    p = m['pricing']
    print(f\"{m['id']:<50} \\${float(p['prompt'])*1e6:<8.5f} \\${float(p['completion'])*1e6:<8.5f} {m['context_length']//1000:>5.0f}k\")
"

# Filter by provider
curl [PERSON_NAME] "https://inference-api.nousresearch.com/v1/models" \
  -H "Authorization: Bearer *** | \
  python3 -c "
import json,sys
models = json.load(sys.stdin).get('data',[])
for m in models:
    if m['id'].startswith('qwen/'):
        p = m['pricing']
        print(f\"{m['id']:<50} \\${float(p['prompt'])*1e6:<8.5f} \\${float(p['completion'])*1e6:<8.5f}\")
"
```

## Profile → Model Recommendation Matrix

Based on task type, quality needs, and cost sensitivity. The user has explicitly flagged **cost as the deciding factor after capability** — prefer the lower-priced option when two models are competitive.

### Budget Tier ($0.05–$0.25 prompt /M)

Best for high-volume, low-criticality tasks where speed and cost dominate.

| Profile | Recommended Model | Prompt/M | Comp/M | Context | Rationale |
|---|---|---|---|---|---|---|
| Secretary | `qwen/qwen3.6-flash` | $0.25 | $1.50 | 1,000k | ✅ Active. Fast, cheap, 1M ctx for docs. (hermes-4-70b is free-tier gated — HTTP 426 on v0.13.0) |
| DevOps | `mistralai/mistral-small-3.2-24b-instruct` | $0.075 | $0.20 | 128k | ✅ Active. Config, infra scripts — doesn't need deep reasoning |
| Data Analyst | `mistralai/mistral-small-3.2-24b-instruct` | $0.075 | $0.20 | 128k | ✅ Active. Data queries are lightweight. (hermes-4-70b is free-tier gated) |

### Reasoning Tier — DeepSeek R1 Series ($0.50 prompt /M)

**This is the user's preferred alternative to o4-mini** — same reasoning-model class (chain-of-thought), half the price. Applied as the active assignment for Reviewer, Debugger, and Security profiles on 2026-05-14 after confirming the user wanted next-best options to o4-mini on cost grounds.

| Profile | Active Model | Prompt/M | Comp/M | Context | Rationale |
|---|---|---|---|---|---|
| **Reviewer** | `deepseek/deepseek-r1-0528` ✅ | $0.50 | $2.15 | 163k | Reasoning chain for deep code critique — catches subtle logic issues the way o4-mini would |
| **Debugger** | `deepseek/deepseek-r1-0528` ✅ | $0.50 | $2.15 | 163k | Same — systematic root cause analysis via step-by-step reasoning |
| **Security** | `deepseek/deepseek-r1-0528` ✅ | $0.50 | $2.15 | 163k | Same — audit rigor without o4-mini's $1.10/$4.40 price tag |

The o4-mini remains the *technically* sharper option ($1.10/$4.40, 200k context) but the user explicitly chose R1-0528 as the cost-efficient substitute for all three profiles.

### Sweet Spot ($0.25–$1.25 prompt /M)

Best quality-per-dollar for most profile workloads. These are the workhorses.

| Profile | Recommended Model | Prompt/M | Comp/M | Context | Rationale |
|---|---|---|---|---|---|
| **Senna (default)** | `deepseek/deepseek-v4-flash` | $0.126 | $0.252 | 1M | Already configured — excellent price/quality/completion ratio |
| **Researcher** | `deepseek/deepseek-v3.2` | $0.252 | $0.378 | 131k | ✅ Active. Latest DeepSeek flagship. (qwen3.6-plus was free-tier gated — HTTP 426 on v0.13.0) |
| **Foreman** | `qwen/qwen3.6-flash` | $0.25 | $1.50 | 1M | ✅ Currently assigned. Orchestrator only reads board + writes reports — doesn't need heavy reasoning |
| **Secretary** | `qwen/qwen3.6-flash` | $0.25 | $1.50 | 1M | Fast, cheap, ample context for docs |
| **Coder** | `qwen/[PERSON_NAME]-coder-plus` | $0.65 | $3.25 | 1M | ✅ Currently assigned. Top Qwen coding model, 1M context for large codebases |
| Coder (budget) | `qwen/[PERSON_NAME]-coder-next` | $0.11 | $0.80 | 262k | Dedicated coding, cheap, good for simple implementations |
| **Architect** | `deepseek/deepseek-v3.2` | $0.252 | $0.378 | 131k | ✅ Currently assigned. Strong reasoning, very cheap completion — architecture docs cost pennies [PERSON_NAME] (alt) | `deepseek/deepseek-v4-pro` | $0.435 | $0.87 | 1M | More capable, 1M context, but 2x the prompt cost |

### Premium Tier ($1.10–$5.00 prompt /M)

Best reasoning but costs add up. These are *not* currently assigned — kept as upgrade candidates.

| Model | Prompt/M | Comp/M | Context | Best suited for |
|---|---|---|---|---|
| `openai/o4-mini` | $1.10 | $4.40 | 200k | Debugger, Reviewer, Security (if budget allows) |
| `openai/gpt-5-codex` | $1.25 | $10.00 | 400k | Coder (premium) — [ADDRESS]'s dedicated coding line |
| `anthropic/[PERSON_NAME]` | $3.00 | $15.00 | 1M | Architect (premium) — best-in-class reasoning |

### Luxury Tier ($5.00+ prompt /M)

Use sparingly — only for one-off critical tasks, not daily profile work.

| Model | Prompt/M | Comp/M | Notes |
|---|---|---|---|
| `anthropic/[PERSON_NAME]-opus-4.7` | $5.00 | $25.00 | Best general reasoning on Nous |
| `anthropic/claude-opus-4.6-fast` | $30.00 | $150.00 | 6x markup for speed — rarely worth it |
| `openai/gpt-5.4-pro` | $30.00 | $180.00 | Price reflects peak capability |
| `openai/o3` | $2.00 | $8.00 | Strong reasoning alternative |

## Provider Coverage on Nous

Nous proxies through OpenRouter infrastructure. Key providers available:

| Provider | Model Count | Notable Families |
|---|---|---|
| qwen | 47 | [PERSON_NAME], [PERSON_NAME], [PERSON_NAME], [PERSON_NAME] |
| openai | 73 | GPT-5.x (codex, pro, mini), o-series (o3, o4), GPT-4.1 |
| google | 32 | Gemini 2.5/3.0/3.1, Gemma 3/4 |
| anthropic | 13 | [PERSON_NAME], Haiku 3.5/4.5 |
| mistralai | 27 | Mistral Large/Small, [ADDRESS], [PERSON_NAME], Pixtral |
| deepseek | 13 | V4 (flash/pro), V3.2, R1 series |
| meta-llama | 12 | Llama 4 Maverick/Scout, Llama 3.x |
| x-ai | 11 | Grok 3/4, Grok Code |
| minimax | 8 | M2.5, M2.7 |
| nousresearch | 5 | Hermes 4 (70b, 405b) |

## Diagnostics: Checking Profile Model Health

When a profile's worker fails to spawn:

```bash
# 1. Check what model the profile is configured with
grep "default:" ~/.hermes/profiles/<profile>/config.yaml

# 2. Check what provider it uses
grep "provider:" ~/.hermes/profiles/<profile>/config.yaml
grep "base_url:" ~/.hermes/profiles/<profile>/config.yaml

# 3. Verify the model still exists on that provider
curl [PERSON_NAME] "$BASE_URL/v1/models" \
  -H "Authorization: Bearer *** | \
  python3 -c "import json,sys; ms=[PERSON_NAME]']; print([m['id'] for m in ms if '$MODEL' in m['id']])"
```

If the model is missing, the profile's model name is stale/deprecated. Pick a replacement from the available list at the same provider, prioritizing price and context length.

## Free-Tier Model Gating

**Important:** Some models on the Nous provider are classified as "free" models and return **HTTP 426 `you must update Hermes Agent to access this free model`** on current Hermes v0.13.0. The fix branch (`[PERSON_NAME]/nous-portal-recommended-models`) has not been merged to `main` yet.

**Gated (doesn't work):**
- `qwen/qwen3.6-plus` — $0.325/$1.95, 1M ctx
- `nousresearch/hermes-4-70b` — $0.05/$0.20, [PERSON_NAME] ctx
- `nousresearch/hermes-4-405b` — $0.09/$0.37, 131k ctx (likely also gated)

**Working paid alternatives:**
- `deepseek/deepseek-v3.2` ($0.252/$0.378) — good replacement for qwen3.6-plus
- `qwen/qwen3.6-flash` ($0.25/$1.50) — good replacement for hermes-4-70b
- `mistralai/mistral-small-3.2-24b-instruct` ($0.075/$0.20) — cheap alternative

**Diagnostic signal:** When a kanban worker crashes with `pid N not alive` and the run history shows sub-10s failures, check the worker log (`hermes kanban log <task_id>`) for HTTP 426. This error is non-retryable — re-dispatching won't help. The model must be changed to a non-free alternative.

## Cost Estimation

For a typical profile dispatch (1 task, ~50 turns, ~2K input + ~500 output per turn):
- **Budget model** ($0.05/$0.20): ~$0.01 per task
- **Sweet spot** ($0.33/$1.95): ~$0.05 per task
- **Premium** ($1.10/$4.40): ~$0.15 per task
- **Luxury** ($5/$25): ~$0.65 per task

The user has 11 profiles but they don't all run simultaneously. At most 1-2 specialist tasks per foreman tick. Daily cost even with premium picks is under $5.