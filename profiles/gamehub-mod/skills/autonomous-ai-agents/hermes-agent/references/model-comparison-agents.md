# Model Comparison for Agentic Workloads (May 2026)

Benchmark pricing and capability comparison for models relevant to Hermes agent work. Updated 2026-05-26.

## Pricing (per 1M tokens)

| Model | Input | Output | Source | Notes |
|---|---|---|---|---|
| DeepSeek V4 Flash | $0.14 | $0.28 | DeepSeek direct | Cache: $0.0028 |
| DeepSeek V4 Pro | $0.435 | $0.87 | DeepSeek direct | Promo ends 2026-05-31, then $1.74 / $3.48 |
| MiMo V2.5 Pro | ~$0.40–0.80 | ~$0.80–1.60 | Nous API / Xiaomi | Not on OpenRouter direct; via Nous or Xiaomi |
| Owl Alpha | $0.00 | $0.00 | OpenRouter | Free. 1.34T weekly token limit. Prompts logged. |

## Agentic Benchmarks (higher = better)

| Benchmark | DS V4 Flash | DS V4 Pro | MiMo 2.5 Pro | Owl Alpha |
|---|---|---|---|---|
| SWE-Bench Verified | ~73 (est.) | 80.6 | 78.9 | not reported |
| SWE-Bench Pro | — | 55.4 | 57.2 | not reported |
| Terminal-Bench 2.0 | — | 67.9 | 68.4 | not reported |
| FrontierSWE | — | — | #3.4 | not reported |
| Claw-Eval (pass³) | — | 59.8 | 63.8 | not reported |
| τ³-bench | — | 71.8 | 72.9 | not reported |
| GDPVal-AA (Elo) | — | 1554 | 1581 | not reported |

## Architecture

| Model | Total Params | Active Params | Context |
|---|---|---|---|
| DS V4 Flash | 284B | 13B | 1M |
| DS V4 Pro | 1.6T | 49B | 1M |
| MiMo 2.5 Pro | 1.02T | 42B | 1M |
| Owl Alpha | undisclosed | undisclosed | 1M |

## Key Observations for Hermes

- **MiMo V2.5 Pro**: Token efficiency champion. 40-60% fewer tokens than Opus/Gemini/GPT-5.4 at comparable capability. Built for long-horizon agent coherence. If available via Nous API, best cost/perf for agents.
- **Owl Alpha**: Free, purpose-built for agent workloads (tool calling, automated workflows), native Claude Code/OpenClaw support. Good for cron jobs and high-volume routine tasks. Prompt logging is a trade-off.
- **DS V4 Flash**: "On par with V4 Pro on simple agent tasks" per DeepSeek. 10x cheaper output than V4 Pro. Best budget agentic model via direct API.
- **DS V4 Pro**: Open-source SOTA on agentic coding. Promo pricing expires May 31 — after that value drops 4x. Best for hard multi-step work.

## Recommended Model Assignments for Hermes Profiles

| Profile Tier | Model | Rationale |
|---|---|---|
| Primary / agentic work | MiMo 2.5 Pro (via Nous) or DS V4 Pro | Best tool calling, multi-step reasoning |
| Cron jobs, routine tasks, overflow | Owl Alpha | Free, agent-optimized, high weekly limit |
| Budget / cost-sensitive alternative | DS V4 Flash | $0.14/$0.28, strong on simple agent tasks |
| Pre-May-31 premium | DS V4 Pro (promo) | Best raw performance while promo lasts |

## Deployment Notes

- MiMo models require Nous API access (Nous Research subscriber) or Xiaomi direct API
- Owl Alpha via OpenRouter: use model ID `openrouter/owl-alpha`
- DS V4 models via DeepSeek API: model IDs `deepseek-v4-flash` and `deepseek-v4-pro`
- DS V4 also available via OpenRouter, DeepInfra, Fireworks, Novita, SiliconFlow (different pricing)
- DS V4 Pro promo: `deepseek-v4-pro` pricing bumps to 4x after 2026-05-31 15:59 UTC
