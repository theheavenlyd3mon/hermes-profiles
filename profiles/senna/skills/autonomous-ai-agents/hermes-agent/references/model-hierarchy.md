# Hermes Multi-Model Hierarchy

Hermes has a layered model architecture — different model slots serve different purposes, with independent fallback chains. This file consolidates information from the docs at https://hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers and https://hermes-agent.nousresearch.com/docs/user-guide/configuration.

## Layer 1: Primary Model

The main conversation model. Set at the top level of `config.yaml`:

```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek
  base_url: https://api.deepseek.com
  api_key: <routed to .env automatically>
  context_length: 65536
```

Override per session: `hermes chat -m <model> --provider <provider>`

## Layer 2: Fallback Providers

When the primary model fails (rate limit 429, auth 401/403, server error 500-503, malformed response), Hermes iterates through fallback chain. **Turn-scoped** — each new user message tries the primary model again.

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
  - provider: openai
    model: gpt-4o
```

Set interactively with `hermes fallback` (a=add, arrows=reorder, d=remove, q=save).

Legacy single-fallback (overridden if `fallback_providers` exists):
```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

Subagent delegation and cron jobs do NOT inherit fallback settings.

## Layer 3: Auxiliary Models (Background Tasks)

Each auxiliary task has its own model slot, independently configurable:

| Task | Config key | Purpose |
|------|-----------|---------|
| Vision | `auxiliary.vision` | Image analysis (web_extract, vision tool) |
| Compression | `auxiliary.compression` | Context summarization |
| Session search | `auxiliary.session_search` | Searching past conversations |
| Web extract | `auxiliary.web_extract` | Content extraction |

Each supports the same sub-keys:

```yaml
auxiliary:
  vision:
    provider: auto           # "auto", "main", or specific provider name
    model: openai/gpt-4o     # specific model override
  compression:
    provider: auto
  session_search:
    provider: main           # reuses the primary model
    max_concurrency: 2
    extra_body:
      enable_thinking: false
```

**Auto-detection chains** (when provider is `"auto"`):
- **Text tasks** (compression, web extract): OpenRouter → Nous Portal → Custom → Codex → API-key providers (Anthropic, DeepSeek, etc.)
- **Vision tasks**: Main provider (if capable) → OpenRouter → Nous Portal → Codex → Anthropic → Custom

**Provider names in config.yaml** — use these exact strings as `provider:` values:

| Config provider name | Actual service | Auth |
|---|---|---|
| `deepseek` | DeepSeek API | `DEEPSEEK_API_KEY` |
| `nous` | Nous Portal | OAuth (`hermes login --provider nous`) |
| `openrouter` | OpenRouter | `OPENROUTER_API_KEY` |
| `anthropic` | Anthropic API | `ANTHROPIC_API_KEY` |
| `openai` | OpenAI API | `OPENAI_API_KEY` |
| `zai` | Z.AI / GLM | `ZAI_API_KEY` |
| `minimax` | MiniMax | `MINIMAX_API_KEY` |
| `minimax-cn` | MiniMax (China) | `MINIMAX_CN_API_KEY` |
| `kimi` / `kimi-coding` | Kimi / Moonshot | `KIMI_API_KEY` |

**Pitfall**: `nous` (capitalized as Nous Portal in docs) is written as `nous` in config.yaml — lowercase.

**Pitfall**: if a model is set but no key is available for its provider, auxiliary tasks silently fail. Set `auto` or ensure the provider's key is present.

**Pitfall**: the compression model must have a context window at least as large as the main model, otherwise summarization truncates silently.

## Layer 4: Delegation Model (Subagents)

Subagents spawned via `delegate_task` use a separate model — good for routing expensive reasoning to the primary and cheap batch work to a budget model:

```yaml
delegation:
  provider: openrouter
  model: google/gemini-3-flash-preview
  max_iterations: 50
  max_concurrent_children: 3
  base_url: <optional custom endpoint>
```

Subagents also support per-call override via the `delegate_task` tool's `provider` and `model` parameters.

## Layer 5: Per-Session Override

Temporary override without changing config:

```bash
hermes -m anthropic/claude-opus-4                     # shorthand
hermes chat -m anthropic/claude-opus-4 --provider anthropic
```

In interactive session: `/model anthropic/claude-opus-4` slash command.

## Layer 6: Credential Pools (Same Provider Rotation)

Not a model slot, but related — rotates API keys for the same provider:

```bash
hermes auth add             # interactive wizard
hermes auth list [PROVIDER] # list pooled credentials
```

Fallback across keys within a provider happens before falling back to the next provider.

## Quick Ref: Which Model Does What

| Context | Model source | Config path |
|---------|-------------|-------------|
| Main conversation | `model.default` | model section |
| Rate limit recovery | `fallback_providers[]` | fallback_providers list |
| Image analysis | `auxiliary.vision.*` | auxiliary.vision |
| Context summarization | `auxiliary.compression.*` | auxiliary.compression |
| Session search | `auxiliary.session_search.*` | auxiliary.session_search |
| Subagent (delegate_task) | `delegation.model` | delegation |
| Cron job | Per-job config | cron job definition |
| CLI one-off | CLI flag | `hermes chat -m ...` |
| Interactive switch | `/model` slash command | session-local |
