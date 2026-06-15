---
name: local-model-agent-evaluation
description: Evaluate local LLMs for agent/coding tasks — BenchLoop harnesses, coding agent selection, tool-calling format matching, and community-tested setups.
triggers:
  - "benchmark local model"
  - "benchloop"
  - "which harness"
  - "tool calling format"
  - "local coding agent"
  - "swival"
  - "opencode local"
  - "evaluate model agent"
version: 1.0.0
---

# Local Model Agent Evaluation

How to benchmark, evaluate, and tool up local models for agent/coding tasks. Covers BenchLoop harnesses, coding agent selection, and the "harness mismatch" problem.

## The Harness Mismatch Problem

Many "this model can't tool-call" claims are actually **harness mismatches** — wrong tool format for the model family. BenchLoop has observed **+15 point overall score swings** just from switching harnesses.

## BenchLoop Harnesses

BenchLoop (`pipx install benchloop-cli`) is the standard local-First benchmark suite. Seven fixed task suites (speed, toolcall, coding, dataextract, instructfollow, reasonmath, agent). Four harnesses control how tools are presented and parsed:

| Harness | Format | Best For |
|---------|--------|----------|
| `raw` | OpenAI `tools=[...]` param | Frontier models, generic endpoints |
| `hermes` | `<tools>` in system prompt, `<tool_call>{...}</tool_call>` output | Nous models, Hermes fleet |
| `qwen` | `<function_call>{...}</function_call>` XML tags | Qwen3-Coder, Qwen-Agent |
| `pi` | `<think>...</think>` + Hermes tags (reasoning stripped before scoring) | Reasoning models (R1-style) |

### Quick A/B Test

```bash
benchloop run --model qwen3:8b --harness raw --suites toolcall
benchloop run --model qwen3:8b --harness qwen --suites toolcall
benchloop run --model qwen3:8b --harness hermes --suites toolcall
```

Run all four on a new model to find its best format. Results at `~/.bench-loop/runs/`.

### Web Dashboard

```bash
benchloop dashboard  # → http://127.0.0.1:8877
```

Auto-discovers models on localhost:11434 (Ollama), :1234 (LM Studio), :8000 (MLX/vLLM). Also supports cloud models via `--remote`.

## Coding Agent Selection

### Swival (swival.dev)

Frank Denis (jedisct1 / libsodium). Purpose-built for local/small models. MIT, no telemetry.

**Why it's different:** Assumes the model WILL fail tool calls. Engineers around it:
- **3-pass forgiving JSON parser** — exact → line-trimmed → unicode-normalized
- **Graduated 4-level context compaction** — shrink → drop low-value → nuclear → shed tools
- **Durable state** — `think`/`todo`/`snapshot` survive context resets
- **Loop protection** — warns after 2 repeats, stops after 3
- **Bounded output** — 50KB reads, 100 grep matches, 10KB commands

Install: `brew install swival/tap/swival` (macOS) or `uv tool install swival`.

### OpenCode

The dominant open-source option (~185K stars). More "plug and play," larger community, more integrations. Better default choice if the model handles tool calling well natively.

### Qwen-Code

Qwen-specific CLI. Best if exclusively using Qwen models. Less general.

### Claude Code / Codex

Frontier-model agents. Not designed for local models. Users report Claude Code is "heavily subsidized" but quality-regressed at times. Codex stronger for large codebases and following plans.

## Harness-to-Model Mapping (Community-Tested)

| Model | Best Harness | Notes |
|-------|-------------|-------|
| Qwen3-Coder / Qwen3.6 | `qwen` or `pi` | Native `<function_call>` format; pi for reasoning variants |
| Hermes models | `hermes` | Native format |
| Generic OpenAI endpoints | `raw` | Safe default, may underperform |
| Reasoning models (R1-style) | `pi` | Strips think blocks from scoring |

## Pitfalls

- **Don't assume `raw` is best** — it's the default but rarely optimal for local models
- **BenchLoop requires model already pulled** — it doesn't pull models, just tests endpoints
- **Swival: very new (208 stars, 1 primary dev)** — active development but bus factor of 1. OpenCode is the safer community choice.
- **Provider edge cases** — Swival had issues with Gemini/DeepSeek (now resolved in latest releases). Test with your specific provider.
- **12GB VRAM constraint** — Qwen3-Coder-Next GGUF (Q4) runs on 12GB. Qwen3.6-35B-A3B at Q4 also fits.

## References

- `references/swival-community-sentiment.md` — Community reviews, HN discussions, user experiences
- BenchLoop docs: https://bench-loop.com/docs
- Swival docs: https://swival.dev/pages/
