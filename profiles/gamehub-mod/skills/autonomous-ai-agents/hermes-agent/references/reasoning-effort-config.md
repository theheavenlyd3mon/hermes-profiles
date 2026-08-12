# Reasoning Effort Configuration (merged from `hermes-reasoning-effort-config`)

`reasoning_effort` controls how much reasoning tokens a model generates before the final response. Only certain providers recognize it.

## Valid Values

| Value | Meaning | When to Use |
|-------|---------|-------------|
| `""` (empty) | Let provider decide | Default — recommended |
| `"none"` | Disable reasoning | For unsupported models |
| `"minimal"` | Minimal reasoning | Quick responses |
| `"low"` | Low reasoning | Most coding tasks |
| `"medium"` | Balanced | Default for reasoning models |
| `"high"` | Heavy reasoning | Complex analysis |
| `"xhigh"` | Maximum | Very complex tasks |

## Supported Providers

| Provider | Models | Notes |
|----------|--------|-------|
| **Kimi / Moonshot** | `moonshotai/kimi-k2.6`, `kimi-k2` | Native support — use `"medium"` or `"high"` |
| **LM Studio** | Local GGUF models | Model-dependent — start with `"minimal"` |

## Unsupported Providers (parameter ignored)

OpenAI GPT, Anthropic Claude, DeepSeek, local Llama (without LM Studio wrapper), Mistral.

## Configuration

```bash
hermes config get agent.reasoning_effort    # View current
hermes config set agent.reasoning_effort medium    # Set
hermes config set agent.reasoning_effort ""        # Reset to default
hermes config set agent.reasoning_effort none      # Disable
```

Subagents can have their own via `delegation.reasoning_effort` in config.

## Source References

- `hermes_constants.py`: `parse_reasoning_effort()` (lines 194-209)
- `cli.py`: Default config with `"reasoning_effort": ""` (line 336)
- `run_agent.py`: LM Studio reasoning integration (lines 10121-10203)
- `scripts/verify_reasoning_effort.py`: Verification script
- `references/example-configs.md`: Provider-specific config examples
- `references/support-files.md`: Supporting code references
