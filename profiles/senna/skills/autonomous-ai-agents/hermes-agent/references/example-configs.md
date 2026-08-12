# Reasoning Effort Configuration Examples

## Quick Start

**For DeepSeek models (like `deepseek-v4-flash`):**
```bash
hermes config set agent.reasoning_effort none
```
The parameter is ignored by DeepSeek, but setting it to `"none"` makes your intent clear.

**For Kimi / Moonshot models:**
```bash
hermes config set agent.reasoning_effort medium
```
This enables the reasoning tokens that Kimi supports.

---

## Verification Script

Run this to verify your current setup:
```bash
python ~/.hermes/profiles/senna/skills/configuration/hermes-reasoning-effort-config/scripts/verify_reasoning_effort.py
```

---

## Current Session Setup

### Profile: senna
- **Model:** `deepseek/deepseek-v4-flash`
- **Provider:** Nous Portal
- **Current `reasoning_effort` setting:** Not set (empty string `""`)
- **Why:** DeepSeek doesn't recognize the `reasoning_effort` parameter — setting it has no effect

### Config Location
```
~/.hermes/profiles/senna/home/.hermes/config.yaml
```

### Current Config (relevant section)
```yaml
model:
  provider: nous
  default: deepseek/deepseek-v4-flash
  base_url: https://inference-api.nousresearch.com/v1
```

### What This Means
- Empty `reasoning_effort` (default) → provider uses native behavior
- DeepSeek ignores the parameter entirely → no error, no effect
- No action needed

---

## Recommended Per-Model Settings

### Kimi / Moonshot (Supported)
```yaml
model:
  provider: nous
  default: moonshotai/kimi-k2.6
  base_url: https://inference-api.nousresearch.com/v1

agent:
  reasoning_effort: medium  # ✅ Enable reasoning for Kimi
```

### DeepSeek (Not Supported)
```yaml
model:
  provider: nous
  default: deepseek/deepseek-v4-flash

agent:
  reasoning_effort: none  # ⚠️ Set to none (parameter ignored, but intent is clear)
```

### OpenAI GPT (Not Supported)
```yaml
model:
  provider: openai
  default: gpt-4o

agent:
  reasoning_effort: none  # ⚠️ Parameter ignored, but no harm
```

### LM Studio Local (Conditional)
```yaml
model:
  provider: lm-studio
  default: qwen2.5-3b-instruct-q4_k_m.gguf

agent:
  reasoning_effort: minimal  # ✅ Only works if model supports it
```

---

## Commands to Check/Change

```bash
# View current reasoning_effort
hermes config get agent.reasoning_effort

# Set to none (for DeepSeek/OpenAI/Anthropic)
hermes config set agent.reasoning_effort none

# Set to medium (for Kimi/Moonshot)
hermes config set agent.reasoning_effort medium

# Clear (reset to empty = provider default)
hermes config set agent.reasoning_effort ""
```

---

## Key Discovery from This Session

1. **Hermes default is empty string** (`""`), not `"medium"`
2. **Empty string → `None` → provider decides** (via `parse_reasoning_effort()`)
3. **DeepSeek ignores the parameter** — setting it changes nothing
4. **Only Kimi/Moonshot and some LM Studio models actually use it**

---

## Verification

To verify your model supports reasoning effort:

```bash
# Try setting it and check if it's recognized
hermes config set agent.reasoning_effort medium
hermes status
# If model is Kimi: it will work
# If model is DeepSeek/OpenAI/Anthropic: no error, parameter just ignored
```