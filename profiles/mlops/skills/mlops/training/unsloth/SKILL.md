---
name: unsloth
description: "Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [unsloth, torch, transformers, trl, datasets, peft]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Fine-Tuning, Unsloth, Fast Training, LoRA, QLoRA, Memory-Efficient, Optimization, Llama, Mistral, Gemma, Qwen]

---

# Unsloth Skill

Comprehensive assistance with unsloth development, generated from official documentation.

## When to Use This Skill

This skill should be triggered when:
- Working with unsloth
- Asking about unsloth features or APIs
- Implementing unsloth solutions
- Debugging unsloth code
- Learning unsloth best practices

## When NOT to Use

- For running GGUF models locally → use `llama-cpp`
- For abliteration/refusal removal → use `obliteratus`
- For serving models at scale → use `serving-llms-vllm`

## Unsloth Studio (Web UI)

Unsloth Studio is a no-code local AI web UI for downloading, running, and training models.

```bash
# macOS / Linux / WSL
curl -fsSL https://unsloth.ai/install.sh | sh

# Windows PowerShell
irm https://unsloth.ai/install.ps1 | iex

# Launch
unsloth studio -H 0.0.0.0 -p 8888
# Open http://127.0.0.1:8888
```

Features: search/download GGUFs, self-healing tool calling, web search, code execution, automatic parameter tuning, fast CPU/GPU inference, no-code training (2x faster, 70% less VRAM).

## Unsloth Dynamic 2.0 GGUFs

Unsloth's proprietary quantization method. Key differences from standard llama.cpp quants:

- **Per-layer quantization**: each layer gets its own optimal bit-width (attention layers get higher precision, less important layers get compressed more)
- **UD (Ultra-Dense) variants**: Unsloth-specific labels like `UD-Q4_K_M`, `UD-Q3_K_XL` — these are Dynamic 2.0 quants
- **Result**: smaller files with less quality loss. Unsloth's 3-bit can outperform standard 4-bit
- **New formats**: Q4_NL, Q5.1, Q5.0, Q4.1, Q4.0 optimized for Apple Silicon/ARM

Benchmarks: Unsloth Dynamic 2.0 outperforms standard imatrix GGUFs and even Google's QAT (Quantization-Aware Training) on MMLU while being ~8GB smaller.

### MTP (Multi Token Prediction)

Enables **1.4-2.2x faster inference** without accuracy loss. Available for Qwen3.6 models as `MTP-GGUF` variants. Uses ~1GB extra VRAM. Test `--spec-draft-n-max` values 1-6 for your hardware.

## Model Catalog

Unsloth provides GGUFs for major model families. Key repos:

| Model Family | Repo Pattern | Notes |
|:-------------|:-------------|:------|
| Qwen3.6 | `unsloth/Qwen3.6-27B-GGUF` | Dense, vision, 262K context |
| Qwen3.6 MoE | `unsloth/Qwen3.6-35B-A3B-GGUF` | MoE, text-only, 1M context |
| Qwen3.6 MTP | `unsloth/Qwen3.6-35B-A3B-MTP-GGUF` | 1.4-2.2x faster via speculative decoding |
| Qwen3-Coder-Next | `unsloth/Qwen3-Coder-Next-GGUF` | 80B-A3B, coding-specific |
| Qwen3.5 | `unsloth/Qwen3.5-35B-A3B-GGUF` | Previous gen MoE |
| Gemma 4 | `unsloth/Gemma-4-*-GGUF` | Google's models |
| Llama 4 | `unsloth/Llama-4-*-GGUF` | Meta's models |
| DeepSeek V3/V4 | `unsloth/DeepSeek-*-GGUF` | MoE models |

Full catalog: https://unsloth.ai/docs/get-started/unsloth-model-catalog

## Hardware Requirements (Qwen3.6)

| Model | 3-bit | 4-bit | 6-bit | 8-bit | BF16 |
|:------|:------|:------|:------|:------|:-----|
| Qwen3.6-27B | 15 GB | 18 GB | 24 GB | 30 GB | 55 GB |
| Qwen3.6-35B-A3B | 17 GB | 23 GB | 30 GB | 38 GB | 70 GB |

**Units = total memory (RAM + VRAM, or unified memory).** CPU offload kicks in automatically if model exceeds VRAM, but inference drops to ~5-15 tok/s.

### Tight VRAM Guidance (≤12GB)

For RTX 4070 Ti (12GB), RTX 4060 Ti (8-16GB), etc:
- Qwen3.6-27B UD-IQ2_XXS (9.4 GB) — fits, some quality loss
- Qwen3.6-27B UD-IQ2_M (10.8 GB) — tight fit, better quality
- Qwen3.6-35B-A3B UD-IQ1_M (10.0 GB) — MoE benefits help at extreme quant
- Qwen3.6-35B-A3B UD-IQ2_XXS (10.8 GB) — best MoE option for 12GB

**MoE advantage**: only 3B params activate per token, so even aggressive quantization keeps decent quality because most weights aren't used per inference step.

## Running via llama.cpp

```bash
# Quant shorthand (downloads from Hub automatically)
llama-cli -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL

# Exact file
llama-server \
    --model unsloth/Qwen3.6-35B-A3B-GGUF/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf \
    --mmproj unsloth/Qwen3.6-35B-A3B-GGUF/mmproj-F16.gguf \
    --alias "unsloth/Qwen3.6-35B-A3B" \
    --temp 0.6 --top-p 0.95 --ctx-size 16384 --port 8001
```

## Fine-Tuning

Unsloth's core feature: 2x faster fine-tuning with 70% less VRAM via LoRA/QLoRA.

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen3.6-27B",
    max_seq_length=2048,
    load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(
    model, r=16, target_modules=["q_proj","k_proj","v_proj","o_proj"],
    lora_alpha=16, lora_dropout=0,
)
```

## Common Pitfalls

1. **Do NOT use CUDA 13.2** — may produce gibberish outputs with Qwen3.6
2. **UD variants are Unsloth-specific** — don't assume they exist for every model; check the repo
3. **MTP needs extra VRAM** — plan ~1GB headroom beyond the model file size
4. **MoE models load ALL params into memory** — 35B-A3B needs space for 35B even though only 3B activates
5. **BF16 shards may need merging** — some repos ship split BF16; use the GGUF instead
6. **mmproj files are separate** — multimodal models need both the main GGUF and a mmproj-*.gguf projector file

## Reference Files

- **[dynamic-gguf.md](references/dynamic-gguf.md)** — Unsloth Dynamic 2.0 detailed technical reference, benchmarks, calibration methodology

## Resources

### references/
Organized documentation extracted from official sources. These files contain:
- Detailed explanations
- Code examples with language annotations
- Links to original documentation
- Table of contents for quick navigation

### scripts/
Add helper scripts here for common automation tasks.

### assets/
Add templates, boilerplate, or example projects here.

## Notes

- This skill was automatically generated from official documentation
- Reference files preserve the structure and examples from source docs
- Code examples include language detection for better syntax highlighting
- Quick reference patterns are extracted from common usage examples in the docs

## Updating

To refresh this skill with updated documentation:
1. Re-run the scraper with the same configuration
2. The skill will be rebuilt with the latest information

<!-- Trigger re-upload 1763621536 -->



