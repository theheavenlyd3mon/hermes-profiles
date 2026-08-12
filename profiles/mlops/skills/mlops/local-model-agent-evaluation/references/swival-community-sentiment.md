# Swival Community Sentiment (June 2026)

## Author

**Frank Denis (jedisct1)** — author of libsodium. Active on HN, transparent about development. Dogfoods Swival as daily driver (GPT-5.4 + Swival). Responds quickly to GitHub issues.

## Direct Quotes

### Frank Denis on HN

> "GPT-5.4 + Swival are now my daily drivers. I've moved away from Claude and toward open-source models + ChatGPT subscription."

> "There are plenty of evals showing Claude Code isn't actually that great. Even with Anthropic models, other harnesses are more efficient both in terms of number of problems solved and token usage. Better: Opencode or Swival.dev."

> "I systematically use reviewer agents in Swival. Even with the same model (--self-review), it makes a huge difference and immediately highlights how bad the first iterations of an LLM output can be."

### Real Users

**virushuo (X/Twitter):**
> "2×3090 / vLLM / Qwen3.6-27B-AWQ-BF16-INT4, 200k context. Swival as my coding agent."

**iMilnb (X/Twitter):**
> "It tries to work well with local models, even with small context windows, flaky tool calling, etc."

**HN commenter:**
> "I systematically use reviewer agents in Swival... makes a huge difference."

## Reddit LocalLLaMA

Thread: "Best CLI coding agent for local dev like Claude Code?" (176 upvotes, 167 comments)

- soulhacker recommended "Swival" — 2 upvotes, no elaboration
- OP (exaknight21) ended up choosing **OpenCode** — "most plug and play"
- OP was running Qwen3.6-35B-A3B on llama.cpp (Mi50 32GB, 32 TPS at Q4 XL)

## GitHub Activity

- **208 stars**, 16 forks, 3 contributors
- **79 releases** — very active development
- **1 open issue** (#23: looping halts until another command entered, May 2026)
- **23 closed** — responsive maintainer
- Common closed issues: Gemini 3 compatibility, DeepSeek failures, truncated provider responses, A2A protocol support

## Competitive Positioning

| Tool | Stars | Position |
|------|-------|----------|
| OpenCode | ~185K | Dominant open-source option, "plug and play" |
| Claude Code | n/a (closed) | Best UX, most subsidized, frontier-only |
| Codex | n/a (closed) | Best for large codebases and plan-following |
| **Swival** | **208** | Principled local-first, small but growing |
| Qwen-Code | smaller | Qwen-specific, less general |

## Key Takeaways

- Swival is respected but tiny — community trust comes from Frank Denis's reputation
- Core pitch (forgiving parsers, context compaction, local-first) resonates with the local model crowd
- OpenCode is the safer default; Swival is the principled choice for local models specifically
- Active development pace (79 releases) suggests it'll close the feature gap quickly
- `--self-review` feature praised as genuinely useful for catching LLM mistakes
