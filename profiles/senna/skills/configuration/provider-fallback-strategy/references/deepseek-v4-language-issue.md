# DeepSeek V4 Flash: Non-Deterministic Language Switching (Chinese)

## Symptom

The model intermittently responds in fluent Chinese even when:
- The entire conversation history is in English
- No Chinese characters or language hints were used
- The user did not request a Chinese response
- Same prompt may produce English one call and Chinese the next

## Status

**Known bug, acknowledged by community, closed as "not planned" by DeepSeek.**  
No fix is expected from the provider side.

## Sources

| Source | Link | Date |
|--------|------|------|
| GitHub Issue #1226 | https://github.com/deepseek-ai/DeepSeek-V3/issues/1226 | Apr 2026 — closed stale |
| GitHub Issue #1443 | https://github.com/deepseek-ai/DeepSeek-V3/issues/1443 | Jun 2026 (2 days before this entry) |
| Reddit (SillyTavern) | https://www.reddit.com/r/SillyTavernAI/comments/1svnjhi/ | Confirms "every message in Chinese, no matter the prompt, temp, settings" |

## Root Cause (suspected)

DeepSeek models internally reason in Chinese (their primary training language) and translate to English on output. The translation step is non-deterministic — it sometimes outputs the raw Chinese reasoning instead of the translation. This is not a config/API issue; it's baked into the model's inference behaviour.

## Attempted Fixes That Don't Reliably Work

| Attempt | Result |
|---------|--------|
| Adding "Reply in English only" to system prompt | Intermittently works — not guaranteed |
| Setting temperature to 0 | Does not fix |
| Forcing `stop` tokens | Does not fix |
| Repeating "translate to English" per-message | Tiresome and not guaranteed |
| Different provider endpoints (Nous vs direct DeepSeek) | Behaviour identical — model-level, not API-level |

## Recommended Workaround

**Switch primary model away from DeepSeek V4 Flash entirely.** Use it only as a fallback or not at all if English consistency matters.

### Known-good alternatives on Nous provider

| Model | Context | Pricing (in/out per M tok) | Notes |
|-------|---------|---------------------------|-------|
| `qwen/qwen3-coder-next` | 262K | $0.11 / $0.80 | Was the user's original primary — no language issues |
| `qwen/qwen3-coder:free` (OpenRouter) | 122K | $0 | Free tier alternative |
| `deepseek/deepseek-v4-pro` | 1M | $0.18 / $0.60 | More expensive but same language quirk exists — not recommended as primary either |

### Config change (revert to known-good setup)

```yaml
model:
  default: qwen/qwen3-coder-next
  provider: nous

fallback_providers:
  - provider: nous
    model: deepseek/deepseek-v4-flash    # fallback only — intermittent Chinese acceptable here
```

## Verification

After switching model, send 3-5 test prompts in English. If all responses are English, the switch resolved it. The bug is non-deterministic, so no single test guarantees absence — but Qwen models have no known language-switching issues.
