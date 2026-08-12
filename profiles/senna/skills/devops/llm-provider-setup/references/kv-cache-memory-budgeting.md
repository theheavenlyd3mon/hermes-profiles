# KV Cache Memory Budgeting

## When to use this

When a user asks "why can't I run the full context?" or "is 64K really the max?" — the answer is usually memory, not architecture.

## The formula (from llama.cpp source)

From `src/llama-kv-cache.cpp`:

```cpp
ggml_tensor * k = ggml_new_tensor_3d(ctx, type_k, n_embd_k_gqa, kv_size, n_stream);
ggml_tensor * v = ggml_new_tensor_3d(ctx, type_v, n_embd_v_gqa, kv_size, n_stream);
```

**KV cache per layer** = `(n_embd_k_gqa + n_embd_v_gqa) × kv_size × bytes_per_element`

Where:
- `n_embd_k_gqa` = `head_dim × num_key_value_heads`
- `n_embd_v_gqa` = `head_dim × num_key_value_heads`
- `kv_size` = context length (n_ctx)
- `bytes_per_element` = FP8 = 1 byte, FP16/BF16 = 2 bytes, FP32 = 4 bytes

**Total KV cache** = per_layer × num_hidden_layers

## Worked example: Laguna XS 2.1

From config.json:
- `hidden_size`: 2048
- `num_attention_heads`: 48
- `num_key_value_heads`: 8
- `head_dim`: 128
- `num_hidden_layers`: 40
- `max_position_embeddings`: 262144
- KV cache type: FP8

Calculation:
- `n_embd_k_gqa` = 128 × 8 = 1024
- `n_embd_v_gqa` = 128 × 8 = 1024
- Per layer: (1024 + 1024) × 262,144 × 1 = 536,870,912 bytes
- 40 layers: 536,870,912 × 40 = 21,474,836,480 ≈ 20 GB (FP16)
- With FP8: 20 GB ÷ 2 = **10 GB** at 256K context

## Memory budget on 64 GB RAM

| Config | Weights | KV Cache | Total | Fits? |
|--------|---------|----------|-------|-------|
| BF16 + 64K | 66 GB | 2.5 GB | 68.5 GB | ❌ |
| BF16 + 256K | 66 GB | 10 GB | 76 GB | ❌ |
| INT8 + 64K | 33 GB | 2.5 GB | 35.5 GB | ✅ |
| INT8 + 256K | 33 GB | 10 GB | 43 GB | ✅ |

**Key insight**: The "64K is the highest context" claim is a practical recommendation for BF16 inference on 64 GB systems. With 8-bit quantization, 256K context fits. The model's architecture supports 256K — the limit is memory, not capability.

## SWA doesn't reduce KV cache allocation

Sliding Window Attention (SWA) with a 512-token window does NOT reduce the allocated KV cache size. From `src/llama-kv-cache.cpp`, the cache is allocated at full `kv_size` regardless of `n_swa`. The SWA window only affects which cells are *used* during attention computation, not the *allocated* cache. The full context is still cached.

## Quick reference for common models

| Model | head_dim | n_head | n_kv | layers | 256K KV (FP16) | 256K KV (FP8) |
|-------|----------|--------|------|--------|----------------|---------------|
| Qwen3-32B | 128 | 51 | 8 | 64 | ~42 GB | ~21 GB |
| Qwen3-235B | 128 | 80 | 8 | 80 | ~134 GB | ~67 GB |
| Llama 3.1-70B | 128 | 64 | 8 | 80 | ~52 GB | ~26 GB |
| Llama 3.1-405B | 128 | 80 | 8 | 126 | ~103 GB | ~51 GB |

## Verification checklist

1. Check `config.json` for `max_position_embeddings` — this is the architectural max
2. Check `hidden_size`, `num_attention_heads`, `num_key_value_heads`, `head_dim`
3. Calculate KV cache size using the formula above
4. Check model card for KV cache dtype (FP8, FP16, etc.)
5. Compare against available RAM (weights + KV cache + 20% overhead)
6. If it fits, the limit is likely a default config, not a hard constraint