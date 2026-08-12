# Unsloth Dynamic 2.0 GGUFs

## What It Is

Unsloth Dynamic v2.0 is a per-layer intelligent quantization method that assigns different bit-widths to different layers based on their importance. Unlike standard quantization (which applies the same bit-width everywhere), Dynamic 2.0 uses a calibration dataset and model-specific analysis to optimize each layer independently.

## Key Differences from Standard GGUFs

| Aspect | Standard llama.cpp GGUF | Unsloth Dynamic 2.0 |
|:-------|:------------------------|:---------------------|
| Layer quantization | Same bit-width all layers | Per-layer optimal bit-width |
| Calibration | imatrix (optional) | Proprietary 1.5M+ token dataset |
| Naming | Q4_K_M, Q5_K_S, etc. | UD-Q4_K_M, UD-Q3_K_XL, etc. |
| Quality at same size | Baseline | Better (less KL divergence) |
| Size at same quality | Baseline | Smaller (~8GB less for equivalent quality) |

## UD (Ultra-Dense) Naming Convention

Unsloth GGUFs use the `UD-` prefix to distinguish Dynamic 2.0 quants:
- `UD-Q4_K_M` — Dynamic 2.0 version of Q4_K_M
- `UD-Q3_K_XL` — Dynamic 2.0 extra-large 3-bit (Unsloth-specific)
- `UD-IQ2_XXS` — Dynamic 2.0 importance-quantized 2-bit extra-extra-small
- `UD-IQ1_M` — Dynamic 2.0 importance-quantized 1-bit medium

The `XL` suffix is Unsloth-specific (not in standard llama.cpp) — means "extra-large" variant with more aggressive optimization.

## IQ (Importance-Quantized) Variants

Lower-bit quants that use importance matrices for smarter weight allocation:
- `IQ1_M` — 1-bit, extreme compression, significant quality loss
- `IQ2_M` — 2-bit, very compressed
- `IQ2_XXS` — 2-bit extra-extra-small
- `IQ3_S` / `IQ3_XXS` — 3-bit variants
- `IQ4_NL` / `IQ4_XS` — 4-bit variants optimized for specific architectures

## MXFP4 (MoE-Specific)

For Mixture-of-Experts models, Unsloth provides `MXFP4_MOE` variants that use mixed-precision specifically optimized for MoE architectures. Example: `Qwen3.6-35B-A3B-MXFP4_MOE.gguf` (21.7 GB).

## Benchmarks (Apr 2026)

### Qwen3.6 Performance
Unsloth Dynamic 2.0 GGUFs outperform standard imatrix GGUFs on:
- Aider Polyglot (code editing benchmark)
- 5-shot MMLU (knowledge benchmark)
- KL Divergence (output distribution fidelity)

### Key Result
Unsloth's Dynamic 3-bit DeepSeek V3.1 GGUF scores **75.6%** on Aider Polyglot, surpassing many full-precision SOTA LLMs.

### Gemma 3 (27B) Comparison
| Quant | Unsloth MMLU | Disk Size | Efficiency |
|:------|:-------------|:----------|:-----------|
| IQ1_M | 48.10 | 6.51 GB | 3.42 |
| IQ2_M | 66.47 | 8.96 GB | 4.40 |
| Q4_K_XL | 71.47 | 15.64 GB | 2.94 |
| Google QAT | 70.64 | 17.2 GB | 2.65 |

Dynamic 4-bit: 2GB smaller with +1% accuracy over Google's QAT.

## Calibration Methodology

- Uses `Calibration_v3` and `Calibration_v5` datasets (1.5M+ tokens)
- Hand-curated, high-quality data optimized for chat/instruct models
- Avoids overfitting to Wikipedia (common pitfall with standard calibration)
- KL Divergence used as primary metric (better than perplexity for measuring output fidelity)

## How to Use

### Via Unsloth Studio
```bash
curl -fsSL https://unsloth.ai/install.sh | sh
unsloth studio -H 0.0.0.0 -p 8888
# Search for model, download UD variant, run
```

### Via llama.cpp
```bash
# Shorthand (auto-downloads)
llama-cli -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL

# Exact file
llama-server --model unsloth/Qwen3.6-27B-GGUF/Qwen3.6-27B-UD-Q4_K_XL.gguf
```

### Via Python (huggingface_hub)
```python
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="unsloth/Qwen3.6-27B-GGUF",
    local_dir="Qwen3.6-27B-GGUF",
    allow_patterns=["*UD-Q4_K_XL*"],
)
```

## Sources

- Blog: https://unsloth.ai/blog/dynamic-v2
- Docs: https://unsloth.ai/docs/basics/unsloth-dynamic-2.0-ggufs
- Reddit discussion: https://www.reddit.com/r/LocalLLaMA/comments/1rh0xwk/
