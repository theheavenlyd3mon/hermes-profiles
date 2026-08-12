# AtomicBot TurboQuant — Fork for MoE Models on Constrained VRAM

The recommended llama.cpp fork for running MoE models (Qwen3.6-35B-A3B, local-36B) on 12GB VRAM with TurboQuant KV cache and NextN speculative decoding.

## What It Adds Over Mainline llama.cpp

| Feature | Mainline | AtomicBot |
|---------|----------|-----------|
| KV cache types | q4_0, q8_0, f16 | + turbo2, turbo3, turbo4 (WHT-rotated) |
| KV compression | ~4× (q4_0) | ~4.3× (turbo3), ~6.4× (turbo2) |
| MTP speculative | draft-mtp | + nextn (shared-model, no separate draft file) |
| Context on 12GB VRAM | 32K (q4_0) | **128K** (turbo3) |
| Windows CUDA | ✅ | ✅ |

## When To Use

- Running MoE models (Qwen3.6-35B-A3B, local-36B) on 12GB VRAM
- Need >32K context (turbo3/4 cache enables 64-128K)
- Want NextN speculative decoding (shared-model path, no separate draft GGUF)
- Using AtomicChat UDT GGUFs (optimized for this fork)

## Build (Windows)

```powershell
git clone https://github.com/AtomicBot-ai/atomic-llama-cpp-turboquant.git
cd atomic-llama-cpp-turboquant
cmake -B build -DGGML_NATIVE=ON -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j
```

Prerequisites: CUDA Toolkit + Visual Studio 2022 (Desktop C++ workload) + CMake.

## Build (macOS/Linux)

```bash
git clone https://github.com/AtomicBot-ai/atomic-llama-cpp-turboquant.git
cd atomic-llama-cpp-turboquant
cmake -B build -DGGML_NATIVE=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j
```

## AtomicChat UDT GGUFs

AtomicChat publishes UDT (UD-Turbo) GGUFs optimized for this fork:

| GGUF | Size | PPL | Features |
|------|------|-----|----------|
| `Qwen3.6-35B-A3B-UDT-Q4_K_XL_MTP.gguf` | 20.7 GB | 6.789 | NextN head combined, attn_q/k at Q6_K |
| `Qwen3.6-35B-A3B-UDT-Q3_K_XL_MTP.gguf` | 16.5 GB | 7.005 | Smaller, for tighter RAM |

**UDT advantages over Unsloth/bartowski:**
- Smaller file (20.7 vs 22/22.9 GB)
- Better PPL (6.789 vs 6.971)
- Faster inference (+11% over Unsloth reference)
- Combined MTP GGUF (no separate draft model file)
- NextN-preserve mask: MTP tensors pinned to Q8_0
- TurboQuant3-friendly mask: attn_q/k bumped to Q6_K

Repo: `AtomicChat/Qwen3.6-35B-A3B-UDT-MTP-GGUF`

## Run Commands

### AtomicChat UDT (recommended, auto-download)

```bash
./llama-server \
  -hf AtomicChat/Qwen3.6-35B-A3B-UDT-MTP-GGUF:Q4_K_XL \
  -hfd AtomicChat/Qwen3.6-35B-A3B-UDT-MTP-GGUF:Q4_K_XL \
  --spec-type nextn --draft-max 2 --draft-min 1 \
  -c 32768 -ngl 99 -ngld 99 -fa on \
  -ctk turbo3 -ctv turbo3 \
  --jinja --temp 0.6 --top-p 0.95 --top-k 20 \
  --host 0.0.0.0 --port 8080
```

### AtomicChat UDT (local file)

```bash
./llama-server \
  -m ./Qwen3.6-35B-A3B-UDT-Q4_K_XL_MTP.gguf \
  -md ./Qwen3.6-35B-A3B-UDT-Q4_K_XL_MTP.gguf \
  --spec-type nextn --draft-max 2 --draft-min 1 \
  -c 32768 -ngl 99 -ngld 99 -fa on \
  -ctk turbo3 -ctv turbo3 \
  --host 0.0.0.0 --port 8080
```

Note: `-md` points to same file — UDT combined GGUFs have NextN head inside.

### local-36B-Opus APEX (reasoning, no MTP)

```bash
./llama-server \
  -m ./local-36B-Opus-APEX-I-Balanced.gguf \
  -ngl 99 --cpu-moe \
  -c 32768 -fa on \
  -ctk turbo3 -ctv turbo3 \
  --host 0.0.0.0 --port 8080
```

## Key Flags

| Flag | Value | Purpose |
|------|-------|---------|
| `-ctk turbo3` | TurboQuant3 KV (keys) | 4.3× compression vs f16 |
| `-ctv turbo3` | TurboQuant3 KV (values) | Same |
| `--spec-type nextn` | NextN speculative | Shared-model MTP, no separate draft |
| `--draft-max 2` | Max draft tokens | 2 optimal for code |
| `--draft-min 1` | Min draft tokens | Always draft at least 1 |
| `-ngld 99` | Draft layers on GPU | NextN head on GPU (negligible VRAM) |

## Context Budget (12GB VRAM, --cpu-moe)

| Cache | 32K | 64K | 128K |
|-------|-----|-----|------|
| q4_0 (mainline) | ~2 GB ✅ | ~4 GB ✅ | ~8 GB ⚠️ |
| **turbo3** | **~1.5 GB ✅** | **~3 GB ✅** | **~6 GB ✅** |
| turbo4 | ~1 GB ✅ | ~2 GB ✅ | ~4 GB ✅ |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Gibberish output | Try `-cuda graphs=0` |
| OOM on VRAM | Use `-ctk turbo2 -ctv turbo2` (more compression) |
| NextN not working | Ensure `-hfd` points to same UDT-MTP file |
| Build fails on Windows | Verify CUDA Toolkit + VS 2022 C++ workload installed |
| `--cpu-moe` not needed for UDT | UDT handles expert offloading via quantization mask |

## Fork Comparison (June 2026)

| Fork | Windows CUDA | TurboQuant | NextN MTP | Unique Feature | Maturity |
|------|-------------|------------|-----------|----------------|----------|
| **AtomicBot TurboQuant** | ✅ | ✅ turbo3/4 | ✅ | WHT-rotated KV cache, AtomicChat UDT GGUFs | 255 stars, active |
| **ik_llama.cpp** | ✅ | ❌ (Hadamard instead) | ✅ | Better CPU perf, novel quants (IQK/Trellis), Hadamard KV transforms, fused MoE ops | Active, well-maintained |
| **Southpaw Turbohaul** | ⚠️ Docker only | ✅ (wraps AtomicBot) | ✅ | Auto model swapping, multi-agent GPU sharing, tool-call recovery | 5 commits, early |
| **Mainline llama.cpp** | ✅ | ❌ | ✅ (draft-mtp) | Production stable, 80k+ stars | Battle-tested |

**Decision:** Use AtomicBot for primary setup (TurboQuant + UDT GGUFs). ik_llama.cpp as fallback if AtomicBot has issues. Southpaw only if you need model swapping (Docker/WSL2 on Windows). Mainline as last resort (no TurboQuant, smaller context budget).

### ik_llama.cpp (ikawrakow/ik_llama.cpp)

llama.cpp fork focused on better CPU and hybrid GPU/CPU performance.

**Key features:**
- Novel quantization types: Trellis (IQ1_KT–IQ4_KT), IQK quants, MXFP4
- Hadamard transforms for K-cache and V-cache (better quality at low-bit cache)
- DeepSeek optimizations: FlashMLA, fused MoE, Smart Expert Reduction (SER)
- Auto-fit offloaded tensors to VRAM for MoE models
- Function call parsers: Kimi-K2, Qwen3, DeepSeek R1
- MTP decoding, self-speculative decoding (ngram, suffix)
- Multi-modal vision support

**Build (Windows):**
```powershell
git clone https://github.com/ikawrakow/ik_llama.cpp
cd ik_llama.cpp
cmake -B build -DGGML_NATIVE=ON -DGGML_CUDA=ON
cmake --build build --config Release -j
```

**⚠️ Warnings:**
- Don't use `-rtr` with hybrid CPU/GPU MoE (forces CPU computation for some tensors)
- Avoid Unsloth `_XL` models with `f16` tensors (may not work)
- If gibberish with `--cpu-moe`, try `-cuda graphs=0`

### Southpaw Turbohaul

Python model management server wrapping AtomicBot's llama.cpp. Auto model swapping, FIFO queue, 5-min warm-hold, tool-call recovery for Qwen3 family.

**Windows:** Docker only (`docker build -f Dockerfile.cuda`). Bare metal requires Linux (`install.sh` is bash-only). Use WSL2 + NVIDIA Container Toolkit.

**When to consider:** Multiple models to swap between, multi-agent GPU sharing.

## Source

- Fork: https://github.com/AtomicBot-ai/atomic-llama-cpp-turboquant
- GGUFs: https://huggingface.co/AtomicChat/Qwen3.6-35B-A3B-UDT-MTP-GGUF
- Upstream TurboQuant: https://github.com/TheTom/llama-cpp-turboquant
