---
name: hermes-reasoning-effort-config
description: Configure reasoning_effort for Hermes Agent to control reasoning intensity per model.
triggers:
  - "hermes reasoning mode"
  - "reasoning effort config"
  - "deepseek reasoning"
  - "model reasoning control"
  - "kimi reasoning"
  - "reasoning intensity"
version: 1.0.0
author: Hermes Agent + Senna
license: MIT
metadata:
  hermes:
    tags: [configuration, reasoning, model, providers, qwen3, deepseek, kimi]
    homepage: https://github.com/NousResearch/hermes-agent
---

# Hermes Reasoning Effort Configuration

## Overview

`reasoning_effort` controls how much reasoning tokens a model is allowed to generate before producing the final response. **Not all models support this feature** — only certain providers (Kimi/Moonshot, some LM Studio models) recognize the parameter.

---

## Valid Values

| Value | Meaning | When to Use |
|-------|---------|-------------|
| `""` (empty) | Let provider decide | Default — recommended for most models |
| `"none"` | Disable reasoning | For models that don't support it (GPT, Claude, Llama) |
| `"minimal"` | Minimal reasoning | Quick responses, simple tasks |
| `"low"` | Low reasoning | Most coding/debugging tasks |
| `"medium"` | Balanced reasoning | Default for reasoning-capable models |
| `"high"` | Heavy reasoning | Complex analysis, multi-step problems |
| `"xhigh"` | Maximum reasoning | Only for very complex tasks |

---

## Valid Providers

### Models That Support `reasoning_effort`

| Provider | Models | Notes |
|----------|--------|-------|
| **Kimi / Moonshot** | `moonshotai/kimi-k2.6`, `moonshotai/kimi-k2` | Native `reasoning_effort` parameter — use `"medium"` or `"high"` |
| **LM Studio** | Local GGUF models that support it | Use `"minimal"` or `"low"` — varies by model |

### Models That Do NOT Support `reasoning_effort`

| Provider | Models | Behavior When Set |
|----------|--------|-------------------|
| **OpenAI** | GPT-4o, GPT-4 Turbo, o1, o1-mini | Parameter ignored, no error |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus | Parameter ignored, no error |
| **DeepSeek** | deepseek-v4-flash, deepseek-chat | Parameter ignored, no error |
| **Local Llama** | llama-3.1-8b, llama-3.2-90b | Parameter ignored unless LM Studio wrapper supports it |
| **Mistral** | Mistral Large, Mistral 7B | Parameter ignored |

---

## Default Behavior

From `hermes_constants.py` and `cli.py`:

```python
# cli.py line 336
"reasoning_effort": "",  # Empty = provider default

# hermes_constants.py line 194
def parse_reasoning_effort(effort: str) -> dict | None:
    if not effort or not effort.strip():
        return None  # Let provider decide
    effort = effort.strip().lower()
    if effort == "none":
        return {"enabled": False}
    if effort in ("minimal", "low", "medium", "high", "xhigh"):
        return {"enabled": True, "effort": effort}
    return None
```

**Key point:** Empty string returns `None`, which means the provider's native behavior applies.

---

## Configuration Commands

```bash
# View current setting
hermes config get agent.reasoning_effort

# Set to none (recommended for non-reasoning models)
hermes config set agent.reasoning_effort none

# Set to medium for Kimi / Moonshot
hermes config set agent.reasoning_effort medium

# Clear (reset to empty = provider default)
hermes config set agent.reasoning_effort ""
```

---

## Delegation Support

Subagents can have their own `reasoning_effort` via `delegation.reasoning_effort` in config:

```yaml
delegation:
  reasoning_effort: low  # Inherit from parent or set independently
```

---

## When to Change It

### ✅ Change It When:
- Using **Kimi / Moonshot** models: set `"medium"` or `"high"` for complex tasks
- Using **LM Studio** with a model that supports reasoning: start with `"minimal"` or `"low"`
- You want to override a model's default reasoning behavior

### ❌ Don't Change It When:
- Using **OpenAI GPT** models (parameter ignored)
- Using **Anthropic Claude** models (parameter ignored)
- Using **DeepSeek** models (parameter ignored)
- Using **local Llama** without LM Studio wrapper (parameter ignored)

---

## Troubleshooting

### Problem: "Unknown reasoning_effort" warning

**Cause:** Invalid value in config (e.g., `"false"` instead of `"none"`)

**Fix:**
```bash
hermes config set agent.reasoning_effort none
```

### Problem: Reasoning not working on Kimi

**Cause:** `reasoning_effort` set to `"none"` or `""` (empty)

**Fix:**
```bash
hermes config set agent.reasoning_effort medium
```

### Problem: Slow responses on DeepSeek

**Cause:** Model doesn't support `reasoning_effort` — setting it does nothing

**Fix:** Set to `"none"` to make intent explicit (no performance benefit either way):
```bash
hermes config set agent.reasoning_effort none
```

---

## Provider-Specific Notes

### Kimi / Moonshot (Supported)
```yaml
model:
  provider: nous
  default: moonshotai/kimi-k2.6
  base_url: https://inference-api.nousresearch.com/v1

agent:
  reasoning_effort: medium  # Works! Use medium/high for complex tasks
```

### DeepSeek (Not Supported)
```yaml
model:
  provider: nous
  default: deepseek/deepseek-v4-flash
  base_url: https://inference-api.nousresearch.com/v1

agent:
  reasoning_effort: none  # Set to none for clarity (parameter ignored by DeepSeek)
```

### OpenAI GPT-4o (Not Supported)
```yaml
model:
  provider: openai
  default: gpt-4o

agent:
  reasoning_effort: none  # Parameter ignored, but no harm in setting it
```

---

## References

- `hermes_constants.py`: `parse_reasoning_effort()` function (lines 194-209)
- `cli.py`: Default config with `"reasoning_effort": ""` (line 336)
- `run_agent.py`: LM Studio reasoning integration (lines 10121-10203)
- `cron/scheduler.py`: Cron job reasoning config parsing (lines 1328-1330)
- `tui_gateway/server.py`: TUI reasoning effort handling (lines 3915-3958)

---

## Summary Table

| Your Model | Set `reasoning_effort` To | Why |
|------------|---------------------------|-----|
| Kimi / Moonshot | `"medium"` or `"high"` | Native support — enables reasoning tokens |
| LM Studio local | `"minimal"` or `"low"` | Model-dependent — check docs |
| DeepSeek | `"none"` | Parameter ignored — clear intent |
| OpenAI GPT | `"none"` | Parameter ignored — clear intent |
| Anthropic Claude | `"none"` | Parameter ignored — clear intent |
| Local Llama | `"none"` | Parameter ignored (unless LM Studio wrapper) |
| Any other model | `"none"` | Safe default — no harm, clear intent |