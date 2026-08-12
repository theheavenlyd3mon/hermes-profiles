# Model sizing for a constrained machine

Goal: pick the smallest local model that's adequate for the task, sized to the
actual hardware. Probe first — never recommend from the model name alone.

## 1. Probe the hardware (macOS)

```bash
# RAM (bytes -> GB)
sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}'
# CPU
sysctl -n machdep.cpu.brand_string
# GPU + VRAM (the number that decides Metal speed)
system_profiler SPDisplaysDataType 2>/dev/null | grep -E "Chipset|VRAM|Metal|Display Type"
# arch (Intel vs Apple Silicon)
uname -m
# disk headroom for the model file
df -h / | tail -1
```

The **VRAM total** is the key number: a GGUF that fits entirely in VRAM runs
through Metal fast; one that overflows spills to CPU cores and slows sharply.

## 2. Size the model (GGUF Q4_K_M approx)

| Model | File size | Fits 4GB VRAM? | Notes on a 16GB Intel Mac |
|-------|-----------|----------------|---------------------------|
| Qwen2.5-3B / Llama3.2-3B | ~2GB | Yes (all-Metal) | ~15-20 tok/s. Minimum that works; good for background summarization. |
| Qwen2.5-7B-Instruct | ~4.7GB | No (spills to CPU) | ~5-8 tok/s. Better quality, slower. |
| Llama-3.1-8B | ~5GB | No | Same tier as 7B, slightly slower. |
| 13B+ | 7-8GB+ | No | Avoid — eats ~half of 16GB RAM, ~2-3 tok/s. |

Rule of thumb: keep the model under VRAM for speed, and under ~half of total
RAM so macOS + the app stay healthy.

**KV cache also counts against RAM.** The KV cache grows linearly with context length: (head_dim × n_kv_heads × 2) × context_tokens × n_layers × bytes_per_element. At 256K context, a 33B MoE model's KV cache alone is ~10 GB (FP8) or ~20 GB (FP16). See `llm-provider-setup/references/kv-cache-memory-budgeting.md` for the full formula and a table of common models.

## 3. The VRAM-fit insight (the non-obvious part)

On a box with a small discrete GPU, **the smaller model that fits in VRAM is
faster than the larger model that's "better on paper."** A 3B fully in 4GB VRAM
via Metal outruns a 7B that has to page through a 6-core CPU. Recommend by
throughput-for-the-task, not parameter count.

## 4. When local isn't the answer

If the only LLM use is non-interactive (feed summarization, tagging, briefs)
and the box is RAM-capped, a free cloud tier is faster and costs zero RAM:
Groq free ~14,400 req/day, OpenRouter free ~50 req/day. Reserve local for
offline/air-gapped requirements.

## Real example

2019 Intel MacBook Pro (i7-9750H 6-core, 16GB RAM, Radeon Pro 555X 4GB):
recommended Llama3.2-3B / Qwen2.5-3B for background summarization (fits the
4GB GPU, all-Metal), with the note that a free Groq key is the lazier path
unless offline use is required.
