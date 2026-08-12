# Performance Optimization Guide

Maximize llama.cpp inference speed and efficiency.

## CPU Optimization

### Thread tuning
```bash
# Set threads (default: physical cores)
./llama-cli -m model.gguf -t 8

# For AMD Ryzen 9 7950X (16 cores, 32 threads)
-t 16  # Best: physical cores

# Avoid hyperthreading (slower for matrix ops)
```

### BLAS acceleration
```bash
# OpenBLAS (faster matrix ops)
make LLAMA_OPENBLAS=1

# BLAS gives 2-3× speedup
```

## GPU Offloading

### Layer offloading
```bash
# Offload 35 layers to GPU (hybrid mode)
./llama-cli -m model.gguf -ngl 35

# Offload all layers
./llama-cli -m model.gguf -ngl 999

# Find optimal value:
# Start with -ngl 999
# If OOM, reduce by 5 until fits
```

### MoE + CPU Offloading (`--cpu-moe`)

For Mixture-of-Experts models on limited VRAM, `--cpu-moe` is the key trick. It keeps expert FFN weights in system RAM and only moves the active experts (typically 8 of 256) to GPU per token. Attention layers stay on GPU.

This lets you run models whose file size **exceeds your VRAM** — because only ~3B params activate per token in a 35B MoE, the GPU never holds the full model.

```bash
# 22GB model on 12GB VRAM — works because only active experts move to GPU
./llama-server -m Qwen3.6-35B-A3B-Q4_K_M.gguf \
    -ngl 99 --cpu-moe \
    -c 8192 --flash-attn \
    --port 8080
```

**When to use `--cpu-moe`:**
- Model file size exceeds your VRAM but is a MoE architecture (e.g., 35B-A3B, 256 experts)
- You have enough system RAM to hold the expert weights (32GB+ recommended)
- You want better quant quality than what fits entirely on GPU

**When NOT to use:**
- Dense models (non-MoE) — `--cpu-moe` does nothing
- Model already fits on GPU — no benefit, just adds complexity
- Less than 16GB system RAM — experts need to live somewhere

**Combining with MTP:**
```bash
# MoE + CPU offload + MTP speculative decoding (fastest setup for MoE on limited VRAM)
./llama-server -m Qwen3.6-35B-A3B-Q4_K_M.gguf \
    -ngl 99 --cpu-moe \
    --spec-type draft-mtp --spec-draft-n-max 2 \
    -c 8192 --flash-attn \
    --port 8080
```

### Memory usage
```bash
# Check VRAM usage
nvidia-smi dmon

# Reduce context if needed
./llama-cli -m model.gguf -c 2048  # 2K context instead of 4K
```

## Batch Processing

```bash
# Increase batch size for throughput
./llama-cli -m model.gguf -b 512  # Default: 512

# Physical batch (GPU)
--ubatch 128  # Process 128 tokens at once
```

## Context Management

```bash
# Default context (512 tokens)
-c 512

# Longer context (slower, more memory)
-c 4096

# Very long context (if model supports)
-c 32768
```

## Benchmarks

### CPU Performance (Llama 2-7B Q4_K_M)

| Setup | Speed | Notes |
|-------|-------|-------|
| Apple M3 Max | 50 tok/s | Metal acceleration |
| AMD 7950X (16c) | 35 tok/s | OpenBLAS |
| Intel i9-13900K | 30 tok/s | AVX2 |

### GPU Offloading (RTX 4090)

| Layers GPU | Speed | VRAM |
|------------|-------|------|
| 0 (CPU only) | 30 tok/s | 0 GB |
| 20 (hybrid) | 80 tok/s | 8 GB |
| 35 (all) | 120 tok/s | 12 GB |
