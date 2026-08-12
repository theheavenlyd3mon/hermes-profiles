# Curated Models for Constrained VRAM (12GB)

Models tested and recommended for RTX 4070 Ti (12GB VRAM) + 32GB RAM setups.

## Primary Recommendation (June 2026)

**AtomicChat Qwen3.6-35B-A3B UDT-Q4_K_XL** on **AtomicBot TurboQuant fork**.

| Spec | Value |
|------|-------|
| Repo | `AtomicChat/Qwen3.6-35B-A3B-UDT-MTP-GGUF:Q4_K_XL` |
| Size | 20.7 GB |
| PPL | 6.789 (best of all GGUF sources) |
| MTP | NextN (combined file) |
| KV Cache | TurboQuant3 (4.3× compression) |
| Fork | AtomicBot TurboQuant |
| Speed | +11% over Unsloth reference |
| Context | 128K on 12 GB VRAM |

Run: `./llama-server -hf AtomicChat/Qwen3.6-35B-A3B-UDT-MTP-GGUF:Q4_K_XL -hfd AtomicChat/Qwen3.6-35B-A3B-UDT-MTP-GGUF:Q4_K_XL --spec-type nextn --draft-max 2 --draft-min 1 -c 32768 -ngl 99 -ngld 99 -fa on -ctk turbo3 -ctv turbo3 --host 0.0.0.0 --port 8080`

See [atomicbot-turboquant.md](atomicbot-turboquant.md) for full fork setup.

## GGUF Source Comparison (Qwen3.6-35B-A3B)

| GGUF | Size | PPL | MTP | TurboQuant | Notes |
|------|------|-----|-----|------------|-------|
| **AtomicChat UDT-Q4_K_XL** | **20.7 GB** | **6.789** | **✅ NextN** | **✅ turbo3** | **Primary — best on every axis** |
| Unsloth UD-Q4_K_XL | 22.9 GB | 6.971 | ✅ draft-mtp | ❌ | Fallback if AtomicBot issues |
| bartowski Q4_K_M | 22 GB | — | ❌ | ❌ | No MTP heads, basic |

**Unsloth → AtomicChat relationship:** Unsloth provides MTP-aware imatrix (calibration data for quantization) → AtomicChat applies UDT mask (NextN-preserve + TurboQuant3-friendly) → result is smaller (20.7 vs 22.9 GB), faster (+11%), better PPL (6.789 vs 6.971). You don't need the Unsloth GGUF separately — AtomicChat is the refined product. Only grab Unsloth directly if AtomicChat's version isn't available for a model you want.

## Secondary: local-36B-Opus (Reasoning / General Agent)

| Spec | Value |
|------|-------|
| Repo | `mudler/local-36B-Opus-APEX-GGUF` |
| Architecture | MoE 36B, 3B active (same as Qwen3.6) |
| GPQA Diamond | 88.4% |
| Best for | Scientific reasoning, general agent use, architecture discussions |

| APEX Variant | Size | Fits 12GB? | Quality | Notes |
|---|---|---|---|---|
| I-Nano | 11 GB | ✅ Entirely | ⚠️ Experimental | IQ2_XXS mid-layer experts — risky for agent use |
| **I-Mini** | **13 GB** | **⚠️ ~3 layers on CPU** | **⭐⭐⭐ Safe** | **Smallest "safe" tier — recommended for agent use** |
| **I-Compact** | **16 GB** | **⚠️ ~10 layers on CPU** | **⭐⭐⭐⭐ Great** | **Best quality for consumer GPUs** |
| **I-Balanced** | **24 GB** | **✅ With --cpu-moe** | **⭐⭐⭐⭐⭐ Best** | **Best quality/size ratio** |

**For agent use (tool calling, reasoning, instruction following): use I-Mini.** I-Nano's IQ2_XXS quantization degrades precision in ways that hurt agent tasks more than coding — unreliable tool calls, hallucinated parameters, lost multi-step context. I-Mini is the smallest tier APEX considers "safe" (no IQ2 degradation). Only 1 GB over VRAM, ~3 layers offloaded to RAM.

Run I-Mini: `./llama-server -m ./local-36B-Opus-APEX-I-Mini.gguf -ngl 99 -c 32768 -fa on -ctk q8_0 -ctv turbo3 --host 0.0.0.0 --port 8080`

Run I-Compact: `./llama-server -m ./local-36B-Opus-APEX-I-Compact.gguf -ngl 99 -c 32768 -fa on -ctk q8_0 -ctv turbo3 --host 0.0.0.0 --port 8080`

Run I-Balanced: `./llama-server -m ./local-36B-Opus-APEX-I-Balanced.gguf -ngl 99 --cpu-moe -c 32768 -fa on -ctk turbo3 -ctv turbo3 --host 0.0.0.0 --port 8080`

No MTP/NextN heads available for Darwin.

## New Contender: Gemma 4 26B-A4B (June 2026)

**Best fit for 12GB VRAM** — only 4B active params, fits fully on GPU without offloading.

| Spec | Value |
|------|-------|
| Repo | `unsloth/Gemma-4-26B-A4B-GGUF` (or Google's official) |
| Architecture | MoE 26B, 4B active |
| Size (UD-Q5_K_XL) | ~14 GB — fits with light CPU offload |
| Size (Q4_K_M) | ~13 GB — fits with `--cpu-moe` |
| Speed | 44 tps text, 42 tps vision |
| Context | 128K |
| Vision | ✅ Built-in |
| Fork | Mainline llama.cpp (no fork needed) |
| MTP | ✅ via AtomicChat Gemma 4 MTP assistant drafters (E2B, E4B) |

**Why it's notable:** Smaller total params than Qwen3.6 (26B vs 35B) but 4B active (vs 3B) — slightly more compute per token. Vision support built in. Works on mainline llama.cpp without any fork. AtomicChat provides MTP assistant drafters for speculative decoding.

Run: `llama-server -hf unsloth/Gemma-4-26B-A4B-GGUF:UD-Q5_K_XL -ngl 99 -c 32768 --flash-attn --host 0.0.0.0 --port 8080`

With MTP assistant: `llama-server -hf unsloth/Gemma-4-26B-A4B-GGUF:UD-Q5_K_XL -ngl 99 --spec-type mtp -c 32768 --flash-attn`

### Running Multiple Models (Different Ports)

Can't load two models simultaneously on 12 GB VRAM. Use different ports and swap:

```bash
# Terminal 1 — Primary coder (port 8080)
./llama-server -hf AtomicChat/Qwen3.6-35B-A3B-UDT-MTP-GGUF:Q4_K_XL ... --port 8080

# Terminal 2 — Reasoning model (port 8081), start when needed
./llama-server -m ./local-36B-Opus-APEX-I-Balanced.gguf ... --port 8081
```

Hermes config per profile points to different ports. Only one server should be running at a time (unless you have 24+ GB VRAM).

## Other Models

All Qwen3.6-35B-A3B family (MoE: 35B total, 3B active, 256 experts, 8 routed per token).

### Tier 1 — Fits Entirely on GPU (no offloading)

| Model | Repo | Quant | Size | Notes |
|-------|------|-------|------|-------|
| local-36B-Opus APEX I-Nano | mudler/local-36B-Opus-APEX-GGUF | I-Nano | 11 GB | Experimental, MoE with APEX quantization |
| **local-36B-Opus APEX I-Mini** | **mudler/local-36B-Opus-APEX-GGUF** | **I-Mini** | **13 GB** | **Smallest safe APEX tier, ~3 layers offload** |
| Qwen3.6-35B-A3B-Uncensored | HauhauCS/...-Aggressive | IQ2_M | 11 GB | Abliterated, 0/465 refusals |

Run with: `-ngl 99 -c 8192 --flash-attn`

### Tier 2 — Needs --cpu-moe or -ot (better quality, experts on CPU)

There are two approaches for MoE CPU offloading:

**Approach A: `--cpu-moe`** (simple, all experts to CPU)
```bash
llama-server -m ./model.gguf -ngl 99 --cpu-moe -c 8192 --flash-attn
```

**Approach B: `-ot ".ffn_.*_exps.=CPU"`** (regex-based, fine-grained)
```bash
# Targets only expert FFN layers by name pattern, keeps attention on GPU
# More control — can target specific layer patterns
# Reported: 60-80 tok/s on Qwen3.6-35B-A3B Q4_K_M on 12GB VRAM
llama-server -hf bartowski/Qwen3.6-35B-A3B-Instruct-GGUF:Q4_K_M \
    -ngl 99 -ot ".ffn_.*_exps.=CPU" -c 32768 \
    --jinja --temp 0.3 --host 127.0.0.1 --port 8080
```

| Model | Repo | Quant | Size | Flags |
|-------|------|-------|------|-------|
| Qwen3.6-35B-A3B-Uncensored | HauhauCS/...-Aggressive | Q2_K_P | 15 GB | `--cpu-moe` |
| Qwen3.6-35B-A3B-Uncensored | HauhauCS/...-Aggressive | Q3_K_P | 19 GB | `--cpu-moe -ngl 30` |

Run with: `-ngl 99 --cpu-moe -c 8192 --flash-attn`

## Key Download URLs

```
# PRIMARY: AtomicChat UDT-Q4_K_XL (recommended)
https://huggingface.co/AtomicChat/Qwen3.6-35B-A3B-UDT-MTP-GGUF

# REASONING: local-36B-Opus APEX I-Balanced
https://huggingface.co/mudler/local-36B-Opus-APEX-GGUF

# AGENT: local-36B-Opus APEX I-Mini (smallest safe tier, 13GB)
# Download: .\scripts\download-model.sh darwin-36b-mini

# FALLBACK: Unsloth MTP
https://huggingface.co/unsloth/Qwen3.6-35B-A3B-MTP-GGUF

# UNCENSORED: Qwen3.6-35B-A3B-Uncensored IQ2_M
https://huggingface.co/HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive
```

## Nemotron 3 Nano 30B A3B (NVIDIA, June 2026)

NVIDIA's hybrid Mamba-Transformer MoE. Strong coding + reasoning, 1M context. Community favorite on r/LocalLLaMA.

| Spec | Value |
|------|-------|
| Repo | `unsloth/Nemotron-3-Nano-30B-A3B-GGUF` |
| Architecture | MoE 31.6B total, 3.6B active (128 experts, 6 per token), Mamba-2 + Transformer hybrid |
| Context | 1M tokens |
| Size (Q4_K_M) | ~10 GB — fits entirely on 12GB VRAM |
| License | Nvidia Nemotron Open Model License (commercial OK) |

**Benchmarks vs peers:**

| Benchmark | Nemotron 3 Nano | Qwen3-30B-A3B | DeepSeek-Coder-V2-Lite | Phi-4-mini |
|-----------|-----------------|---------------|------------------------|------------|
| LiveCodeBench v6 | **68.3%** | 66.0% | ~50% | ~40-45% |
| AIME 2025 | **89.1%** | 85.0% | N/A | ~50% |
| SciCode | **30%** | N/A | 14% | N/A |
| GPQA Diamond | **76%** | N/A | 32% | ~45% |
| MMLU-Pro | 78.3% | **80.9%** | N/A | N/A |
| Arena-Hard-v2 (agentic) | **67.7%** | 57.8% | N/A | N/A |
| Artificial Analysis Index | **24.3** | N/A | 8.5 | N/A |

**Key advantages:**
- 3.3x higher throughput than Qwen3-30B-A3B on same hardware (sparse activation)
- 1M context (vs 128K on most peers) — great for large codebases
- Mamba layers reduce attention cost at long context
- Strongest open-weight model for agentic tasks (Arena-Hard-v2)

**Weaknesses:**
- Slightly trails Qwen3 on broad general knowledge (MMLU-Pro 78.3 vs 80.9)
- Reasoning mode adds latency (~15s thinking time before output)
- Mamba hybrid may need llama.cpp b9180+ for full support

**Run:**
```bash
llama-server -hf unsloth/Nemotron-3-Nano-30B-A3B-GGUF:Q4_K_M \
    -ngl 99 -c 32768 --flash-attn --host 0.0.0.0 --port 8080
```

## Smaller Alternatives (for quick tasks or very tight VRAM)

### Phi-4-mini (3.8B dense)

Microsoft's tiny model. Fast, fits anywhere, but limited for serious coding.

| Spec | Value |
|------|-------|
| Repo | `microsoft/Phi-4-mini-instruct` (or GGUF from bartowski/unsloth) |
| Size (Q4_K_M) | ~3 GB |
| Best for | Quick Q&A, scaffolding, simple edits |
| NOT for | UE5 C++, complex refactors, multi-file projects |

**Verdict:** Keep as a "fast answers" fallback at 3GB. Not a primary coding model.

### DeepSeek-Coder-V2-Lite (16B MoE)

Dedicated coding model from June 2024. Was good for its time, now outclassed.

| Spec | Value |
|------|-------|
| Repo | `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct` |
| Size | ~10 GB |
| Context | 128K |
| Best for | Code completion, fill-in-middle |

**Verdict:** Nemotron 3 Nano beats it on every benchmark (SciCode 30% vs 14%, GPQA 76% vs 32%) with 8x the context. No compelling reason to use over Nano.

### Model Selection Quick Reference (12GB VRAM)

| Need | Model | Why |
|------|-------|-----|
| Primary coding | AtomicChat Qwen3.6-35B-A3B UDT | Best quality/speed/size, TurboQuant3 + NextN |
| Coding + reasoning + 1M context | Nemotron 3 Nano 30B | Strongest benchmarks, Mamba hybrid, huge context |
| Deep reasoning | local-36B-Opus APEX | 88.4% GPQA, scientific/architecture discussions |
| **General agent (tool calling, multi-step)** | **local-36B-Opus APEX I-Mini** | **Smallest "safe" APEX tier, reliable tool calling** |
| Quick answers (3GB) | Phi-4-mini | Fast, tiny, basic tasks only |

## Models That DON'T Fit 12 GB VRAM

| Model | Type | Issue |
|-------|------|-------|
| Darwin-28B-REASON | Dense 27.6B | Needs ~55 GB (BF16), ~16 GB at Q4. No MoE offloading. |
| Qwen3.6-27B | Dense 27B | ~16 GB at Q4. No offloading trick for dense models. |
| Qwen3.6-27B-PRISM-EAGLE3 | Dense 27B + drafter | Same dense issue + requires SGLang/vLLM, not llama.cpp. See below. |

Dense models load ALL parameters every token. MoE models only activate ~3B of 35B — that's why MoE with `--cpu-moe` works on 12 GB but dense 27B doesn't.

### EAGLE-3 Speculative Decoding (Why It Doesn't Help Here)

[EAGLE-3](https://huggingface.co/Ex0bit/Qwen3.6-27B-PRISM-EAGLE3) is a trained drafter head (~0.6B params, 1.1 GB compressed) that speeds up dense Qwen3.6-27B via speculative decoding. It's lossless — output is token-identical to non-speculative greedy decode.

**The numbers (SGLang, BF16, high-end GPU):**
| Config | Base tok/s | EAGLE-3 tok/s | Speedup |
|--------|-----------|---------------|---------|
| PRISM-PRO + compressed drafter | 93 | 183 | 1.97× |
| Stock Qwen3.6-27B + compressed | 93 | 171 | 1.84× |
| PRISM-PRO + vLLM | 90 | 130 | 1.44× |

**Why it doesn't work for 12GB VRAM:**
1. **Wrong serving stack.** Requires SGLang or vLLM (Linux-native, Python/PyTorch). Not compatible with llama.cpp or AtomicBot. On Windows you'd need WSL2.
2. **Dense 27B is too heavy.** Even with EAGLE-3's ~2× speedup, a dense 27B model computes 27B params per token. Your MoE 35B-A3B activates only 3B — MoE is inherently ~9× cheaper per token. The MoE baseline (~60-80 tok/s on AtomicBot) already beats what EAGLE-3 + dense 27B could deliver with CPU offload.
3. **CPU offload kills the gain.** Q4 dense 27B needs ~16 GB. With 12 GB VRAM, ~4-5 layers on CPU. EAGLE-3's 2× claim assumes full GPU — with offload penalty, real gain drops to ~1.4-1.6×, and base throughput is already lower than MoE.

**When EAGLE-3 IS interesting:** Linux server with 24+ GB VRAM running dense Qwen3.6-27B via SGLang. If someone trains an EAGLE-3 drafter for the 35B-A3B MoE variant, that would be worth revisiting — but no such drafter exists yet.

**Key terminology:**
- EAGLE-3: Trained external drafter head (separate file, needs SGLang/vLLM patch)
- MTP: Built-in multi-token prediction heads (baked into model, works with llama.cpp)
- NextN: AtomicBot's MTP implementation (turbo3 + NextN combo)
- Draft model: Generic smaller model used for speculation (legacy approach, lower acceptance rate)

For your hardware: **MTP (NextN via AtomicBot) is the speculative decoding method that works.** EAGLE-3 is for a different hardware/software tier entirely.

## Fork Comparison for 12GB VRAM

| Fork | Best For | TurboQuant KV | MTP | CPU MoE |
|------|----------|---------------|-----|---------|
| **Mainline** | General use, Gemma 4 | ❌ (PR #21089 open) | ✅ Merged (May 2026) | ✅ `--cpu-moe` and `-ot` |
| **AtomicBot TQ** | Max throughput, turbo3+NextN combo | ✅ turbo3/4 | ✅ + optimized async | ✅ |
| **ik_llama.cpp** | CPU-heavy, DeepSeek | ❌ (own Hadamard) | ⚠️ Basic | ✅ Fused MoE ops |
| **turbohaul-manager** | Multi-model GPU sharing | Via AtomicBot backend | Via AtomicBot | Via AtomicBot |

**For 12GB VRAM specifically:** AtomicBot TurboQuant gives the best throughput (turbo3 KV + NextN = 128K context on 12GB). Mainline is fine if you just want MTP without a fork. ik_llama.cpp is best if you're CPU-heavy (e.g., DeepSeek-V3 671B with heavy offloading).

**Southpaw-Turbohaul** does not exist as a llama.cpp fork. `turbohaul-manager` (MrTrenchTrucker) is a model management wrapper that uses AtomicBot's fork as its backend. Not a fork itself.

## Model Architecture Reference

- Architecture: `qwen35moe` (Qwen3.5 MoE family)
- Layers: 40
- Experts: 256 routed, 8 active per token
- Active params: ~3B per token
- Context: 262K native (1M with YaRN)
- Attention: Hybrid (full softmax every 4th layer, linear/Mamba otherwise)
- Thinking mode: Toggleable (enable_thinking true/false)
- Multimodal: Text, images, documents, video
