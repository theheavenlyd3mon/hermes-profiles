# DeepSeek V4 — API reference

Source: https://api-docs.deepseek.com/updates/ and https://api-docs.deepseek.com/guides/thinking_mode (verified 2026-07-31).

## Model names (V4 era)

- `deepseek-v4-flash` — official release 2026-07-31 (build V4-Flash-0731), public beta. Same model name as the preview; no API change needed. Re-post-trained only (same architecture/size). Enhanced agent benchmarks (Terminal Bench 2.1: 82.7, Toolathlon verified: 70.3, etc.).
- `deepseek-v4-pro` — flagship, preview since 2026-04-24; official release "follows soon."
- Legacy `deepseek-chat` / `deepseek-reasoner` retired 2026-07-24 15:59 UTC. They previously mapped to non-thinking / thinking modes of v4-flash.
- DeepSeek native API is OpenAI-compatible: base_url `https://api.deepseek.com`, key `DEEPSEEK_API_KEY` in `~/.hermes/.env` (provider: `deepseek`).

## Thinking mode (critical for tool/agent workloads)

- Enabled BY DEFAULT, effort defaults to `high`. To control: `reasoning_effort` ("low"/"high"/"max") as a top-level OpenAI param, plus `extra_body={"thinking": {"type": "enabled"}}` when using the OpenAI SDK.
- Effort mapping (v4-flash): low→low, high→high, xhigh→high, max→max.
- CoT is returned in a SEPARATE `reasoning_content` field alongside `content`. Multi-turn with tool calls: `reasoning_content` MUST be passed back in subsequent requests or the API returns 400. Between two user turns with no tool call, it can be omitted.
- Thinking mode ignores `temperature`, `top_p`, `presence_penalty`, `frequency_penalty` (no error, no effect).
- 1M context window on both v4 models.

## Hermes integration notes

- Direct `api.deepseek.com` requests do NOT get reasoning/thinking params emitted by Hermes' chat_completions transport (the `supports_reasoning` gate only covers Nous Portal, GitHub, LM Studio, Ollama, OpenRouter, Kimi, TokenHub). Thinking still happens server-side by default — the transport DOES parse `reasoning_content` back out of responses.
- MoA advisors using deepseek: add `reasoning_effort: high` to the slot AND raise `reference_max_tokens` (default 600 is too small; reasoning consumes it and the visible advisor content comes back empty). See the Universal Gotchas bullet in SKILL.md.
