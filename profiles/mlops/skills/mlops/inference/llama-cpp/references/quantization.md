# GGUF Quantization Guide

Complete guide to GGUF quantization formats and model conversion.

## Hub-first quant selection

Before using generic tables, open the model repo with:

```text
https://huggingface.co/<repo>?local-app=llama.cpp
```

Prefer the exact quant labels and sizes shown in the `Hardware compatibility` section of the fetched `?local-app=llama.cpp` page text or HTML. Then confirm the matching filenames in:

```text
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

Use the Hub page first, and only fall back to the generic heuristics below when the repo page does not expose a clear recommendation.

## Quantization Overview

**GGUF** (GPT-Generated Unified Format) - Standard format for llama.cpp models.

### Format Comparison

| Format | Perplexity | Size (7B) | Tokens/sec | Notes |
|--------|------------|-----------|------------|-------|
| FP16 | 5.9565 (baseline) | 13.0 GB | 15 tok/s | Original quality |
| Q8_0 | 5.9584 (+0.03%) | 7.0 GB | 25 tok/s | Nearly lossless |
| **Q6_K** | 5.9642 (+0.13%) | 5.5 GB | 30 tok/s | Best quality/size |
| **Q5_K_M** | 5.9796 (+0.39%) | 4.8 GB | 35 tok/s | Balanced |
| **Q4_K_M** | 6.0565 (+1.68%) | 4.1 GB | 40 tok/s | **Recommended** |
| Q4_K_S | 6.1125 (+2.62%) | 3.9 GB | 42 tok/s | Faster, lower quality |
| Q3_K_M | 6.3184 (+6.07%) | 3.3 GB | 45 tok/s | Small models only |
| Q2_K | 6.8673 (+15.3%) | 2.7 GB | 50 tok/s | Not recommended |

**Recommendation**: Use **Q4_K_M** for best balance of quality and speed.

## Converting Models

### Hugging Face to GGUF

```bash
# 1. Download Hugging Face model
hf download meta-llama/Llama-2-7b-chat-hf \
    --local-dir models/llama-2-7b-chat/

# 2. Convert to FP16 GGUF
python convert_hf_to_gguf.py \
    models/llama-2-7b-chat/ \
    --outtype f16 \
    --outfile models/llama-2-7b-chat-f16.gguf

# 3. Quantize to Q4_K_M
./llama-quantize \
    models/llama-2-7b-chat-f16.gguf \
    models/llama-2-7b-chat-Q4_K_M.gguf \
    Q4_K_M
```

### Batch quantization

```bash
# Quantize to multiple formats
for quant in Q4_K_M Q5_K_M Q6_K Q8_0; do
    ./llama-quantize \
        model-f16.gguf \
        model-${quant}.gguf \
        $quant
done
```

## K-Quantization Methods

**K-quants** use mixed precision for better quality:
- Attention weights: Higher precision
- Feed-forward weights: Lower precision

**Variants**:
- `_S` (Small): Faster, lower quality
- `_M` (Medium): Balanced (recommended)
- `_L` (Large): Better quality, larger size

**Example**: `Q4_K_M`
- `Q4`: 4-bit quantization
- `K`: Mixed precision method
- `M`: Medium quality

## Unsloth UD (Ultra-Dense) Variants

Unsloth's Dynamic 2.0 quantization uses per-layer optimal bit-widths. These show up as `UD-` prefixed quants:

| Variant | Typical Size (27B) | Quality | Notes |
|:--------|:-------------------|:--------|:------|
| UD-Q8_K_XL | ~35 GB | Highest UD | Near-lossless |
| UD-Q6_K_XL | ~26 GB | Excellent | Best practical UD |
| UD-Q5_K_XL | ~20 GB | Very good | Balanced |
| UD-Q4_K_XL | ~18 GB | Good | Recommended general-use UD |
| UD-Q3_K_XL | ~15 GB | Acceptable | Tight budgets |
| UD-Q2_K_XL | ~12 GB | Degraded | Fits 12GB GPUs |
| UD-IQ2_XXS | ~10 GB | Compressed | Extreme squeeze |
| UD-IQ2_M | ~11 GB | Better | Best for ≤12GB GPUs |

**UD vs standard at same nominal bit-width**: UD is usually smaller AND better quality. Prefer UD when available.

## IQ (Importance-Quantized) Variants

Standard llama.cpp also has IQ variants (not Unsloth-specific):

| Variant | Bits | Best For |
|:--------|:-----|:---------|
| IQ1_M | ~1.5 bit | Extreme compression, quality loss acceptable |
| IQ2_M | ~2 bit | Very tight VRAM (8-12GB GPUs) |
| IQ2_XXS | ~2 bit | Smallest possible |
| IQ3_S / IQ3_XXS | ~3 bit | Better than Q2, still compact |
| IQ4_NL / IQ4_XS | ~4 bit | Optimized for ARM/Apple Silicon |

IQ variants use importance matrices to allocate bits to critical weights. Better than standard Q at ≤3 bit.

## Quality Testing

```bash
# Calculate perplexity (quality metric)
./llama-perplexity \
    -m model.gguf \
    -f wikitext-2-raw/wiki.test.raw \
    -c 512

# Lower perplexity = better quality
# Baseline (FP16): ~5.96
# Q4_K_M: ~6.06 (+1.7%)
# Q2_K: ~6.87 (+15.3% - too much degradation)
```

## Use Case Guide

### General purpose (chatbots, assistants)
```
Q4_K_M - Best balance
Q5_K_M - If you have extra RAM
```

### Code generation
```
Q5_K_M or Q6_K - Higher precision helps with code
```

### Creative writing
```
Q4_K_M - Sufficient quality
Q3_K_M - Acceptable for draft generation
```

### Technical/medical
```
Q6_K or Q8_0 - Maximum accuracy
```

### Edge devices (Raspberry Pi)
```
Q2_K or Q3_K_S - Fit in limited RAM
```

## Model Size Scaling

### 7B parameter models

| Format | Size | RAM needed |
|--------|------|------------|
| Q2_K | 2.7 GB | 5 GB |
| Q3_K_M | 3.3 GB | 6 GB |
| Q4_K_M | 4.1 GB | 7 GB |
| Q5_K_M | 4.8 GB | 8 GB |
| Q6_K | 5.5 GB | 9 GB |
| Q8_0 | 7.0 GB | 11 GB |

### 13B parameter models

| Format | Size | RAM needed |
|--------|------|------------|
| Q2_K | 5.1 GB | 8 GB |
| Q3_K_M | 6.2 GB | 10 GB |
| Q4_K_M | 7.9 GB | 12 GB |
| Q5_K_M | 9.2 GB | 14 GB |
| Q6_K | 10.7 GB | 16 GB |

### 70B parameter models

| Format | Size | RAM needed |
|--------|------|------------|
| Q2_K | 26 GB | 32 GB |
| Q3_K_M | 32 GB | 40 GB |
| Q4_K_M | 41 GB | 48 GB |
| Q4_K_S | 39 GB | 46 GB |
| Q5_K_M | 48 GB | 56 GB |

**Recommendation for 70B**: Use Q3_K_M or Q4_K_S to fit in consumer hardware.

## Finding Pre-Quantized Models

Use the Hub search with the llama.cpp app filter:

```text
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending
```

For a specific repo, open:

```text
https://huggingface.co/<repo>?local-app=llama.cpp
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

Then launch directly from the Hub without extra Hub tooling:

```bash
llama-cli -hf <repo>:Q4_K_M
llama-server -hf <repo>:Q4_K_M
```

If you need the exact file name from the tree API:

```bash
llama-server --hf-repo <repo> --hf-file <filename.gguf>
```

## Importance Matrices (imatrix)

**What**: Calibration data to improve quantization quality.

**Benefits**:
- 10-20% perplexity improvement with Q4
- Essential for Q3 and below

**Usage**:
```bash
# 1. Generate importance matrix
./llama-imatrix \
    -m model-f16.gguf \
    -f calibration-data.txt \
    -o model.imatrix

# 2. Quantize with imatrix
./llama-quantize \
    --imatrix model.imatrix \
    model-f16.gguf \
    model-Q4_K_M.gguf \
    Q4_K_M
```

**Calibration data**:
- Use domain-specific text (e.g., code for code models)
- ~100MB of representative text
- Higher quality data = better quantization

## APEX (Adaptive Precision for EXpert Models)

**What**: MoE-aware mixed-precision quantization by LocalAI (mudler). Exploits the structural sparsity of MoE models — only ~8/256 experts activate per token, so most expert weights can be compressed aggressively.

**How it works**:
1. Classifies tensors by role: routed experts (97% sparse), shared experts (always active), attention/SSM weights
2. Applies layer-wise precision gradient: edge layers (first/last 5) get higher precision, middle layers compressed more
3. I-variants use diverse imatrix calibration (chat, code, reasoning, tool-calling, agentic traces)

**Key insight**: In MoE models, expert FFN tensors make up ~97% of weights but only ~3% activate per token. APEX compresses middle-layer experts to Q5_K-Q6_K while keeping shared experts at Q8_0 and attention at Q6_K. Beats Q8_0 perplexity at half the size.

**APEX tiers (tested on Qwen3.5-35B-A3B):**

| Tier | Size (35B MoE) | PPL | HellaSwag | Notes |
|------|---------------|-----|-----------|-------|
| F16 | 64.6 GB | 6.537 | 82.5% | Reference |
| Q8_0 | 34.4 GB | 6.533 | 83.0% | Standard baseline |
| **APEX Quality** | **21.3 GB** | **6.527** | **83.0%** | **Beats Q8_0 at 60% size** |
| **APEX I-Quality** | **21.3 GB** | 6.552 | **83.5%** | **Best benchmark scores** |
| **APEX Balanced** | **23.6 GB** | **6.533** | 83.0% | Best quality/size ratio |
| **APEX Compact** | **16.1 GB** | 6.783 | 82.5% | Consumer GPUs |
| **APEX Mini** | **12.2 GB** | 7.088 | 81.0% | **Smallest "safe" tier** |
| APEX Nano | ~11 GB | — | — | Experimental (IQ2_XXS mid-layer) |

**When to use APEX vs standard quants:**
- APEX is only for MoE models (Qwen3.5-35B, local-36B, Gemma-4-26B, etc.)
- For dense models, use standard Q4_K_M / UD variants
- APEX I-Quality at 21.3 GB matches Unsloth UD-Q8_K_XL at 45.3 GB — nearly half the size for same quality

**Agent vs coding model selection with APEX:**
- For agent use (tool calling, multi-step reasoning): use I-Mini or higher. IQ2_XXS (Nano tier) degrades precision in ways that hurt agent reliability — hallucinated tool parameters, lost context
- For coding: I-Nano may be acceptable since code has more pattern-matching tolerance

**Repo**: `https://github.com/mudler/apex-quant`
**GGUF collection**: `https://huggingface.co/collections/mudler/apex-quants-gguf`

## Troubleshooting

**Model outputs gibberish**:
- Quantization too aggressive (Q2_K)
- Try Q4_K_M or Q5_K_M
- Verify model converted correctly

**Out of memory**:
- Use lower quantization (Q4_K_S instead of Q5_K_M)
- Offload fewer layers to GPU (`-ngl`)
- Use smaller context (`-c 2048`)

**Slow inference**:
- Higher quantization uses more compute
- Q8_0 much slower than Q4_K_M
- Consider speed vs quality trade-off
