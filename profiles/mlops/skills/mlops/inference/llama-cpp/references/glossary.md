# Local LLM Glossary

Beginner-friendly explanations of terms used across the local LLM ecosystem.

## Core Formats

**GGUF** — **G**GML **U**nified **F**ormat. A single-file container that holds everything needed to run a model: weights, tokenizer, config. Created by the llama.cpp project. Drop it into LM Studio, Ollama, or llama.cpp and it runs. Think of it as a "ready to execute" model package.

**BF16 / FP16** — The original unquantized model weights using 16-bit floating-point numbers. Highest quality, massive file sizes (50+ GB for a 27B model). Not practical for consumer hardware.

**Safetensors** — HuggingFace's format for model weights. Requires the full model directory (config.json, tokenizer files, etc.) to run. Used by transformers, vLLM, etc. Not the same as GGUF.

## Quantization

**Quantization** — Compressing a model by reducing the precision of its numbers. Original uses 16-bit; quantizing to Q4 means each number uses ~4 bits. Smaller file = less VRAM = faster inference, but slightly lower quality.

**Q4_K_M / Q5_K_M / Q8_0** — Specific quantization recipes. The number (4, 5, 8) = bits per weight. **K** = k-quant method (mixed precision — attention weights get higher precision, FFN weights get lower). **M** = medium, **S** = small (more compressed), **L** = large. Higher number = better quality but bigger file.

**IQ variants** (IQ1_M, IQ2_M, IQ2_XXS, IQ3_S, IQ4_NL, IQ4_XS) — **I**mportance-quantized variants. Use importance matrices to allocate bits more intelligently — critical weights get more precision. Better than standard Q at very low bit-widths (1-3 bit).

**UD** (Ultra-Dense) — Unsloth's proprietary quantization prefix. Per-layer optimal bit-width using their Dynamic 2.0 method. Usually smaller AND better quality than standard quants at the same nominal bit-width.

**MXFP4** — Mixed-precision 4-bit format optimized for MoE architectures. Available from Unsloth for MoE models.

**imatrix** (Importance Matrix) — Calibration data that tells the quantizer which weights matter most. 10-20% perplexity improvement at Q4. Essential for Q3 and below.

## Architecture

**Dense model** — Every parameter activates for every token. A 27B dense model uses all 27B every time. Simpler, more predictable quality, but slower.

**MoE** (Mixture of Experts) — The model has many total parameters but only activates a fraction per token. A "35B-A3B" MoE has 35B total but only 3B active per token — runs at 3B speed with 3B knowledge breadth but needs all 35B in memory.

**`--cpu-moe`** — A llama.cpp flag for MoE models that keeps expert FFN weights in system RAM instead of GPU VRAM. Only the ~8 active experts per token shuttle to GPU. Lets you run a 22GB MoE model on 12GB VRAM because the GPU never holds the full model. Only works on MoE architectures.

**A3B / A12B / A22B** — The number of active parameters in a MoE model. "35B-A3B" = 35B total, 3B active.

**Context window** — How many tokens the model can see at once (input + output). 262K = ~200K words. Longer context = more VRAM for KV cache.

**KV Cache** — Memory the model uses to remember previous tokens in the conversation. Longer conversations = more KV cache = more VRAM beyond just the model file. Can add 20-40 GB for 1M-token context. Compressible with `--cache-type-k q4_0 --cache-type-v q4_0` (TurboQuant or standard q4_0).

**MTP** (Multi-Token Prediction) — Speculative decoding baked into model weights. The model was pre-trained with auxiliary heads that predict 2-3 tokens ahead, then verifies them in one pass. No extra model or VRAM needed. Enabled with `--spec-type draft-mtp --spec-draft-n-max 2`. 1.5-2.7x faster for code/factual tasks. Can be slower for creative writing at low quants. Requires llama.cpp b9180+ and a GGUF with MTP heads (bartowski, unsloth MTP, froggeric MTP builds).

## Hardware

**VRAM** — Your GPU's dedicated memory. This is the hard ceiling — model weights + KV cache must fit. Common sizes: 8GB (4060), 12GB (4070 Ti), 16GB (4060 Ti 16GB), 24GB (4090).

**CPU Offload** — When the model doesn't fit in VRAM, some layers get sent to system RAM. Works but 5-10x slower. Configured via `-ngl` (number of GPU layers) in llama.cpp.

**tok/s** (tokens per second) — Inference speed. 30+ tok/s feels interactive. 5-15 tok/s is usable but slow. Below 5 tok/s is painful.

**Unified memory** — Mac M-series chips share RAM between CPU and GPU. A 36GB Mac can fit a 36GB model entirely in "VRAM" — no offloading needed.

## Abliteration

**Abliterated** — Refusal guardrails surgically removed from model weights. The model will answer things it normally refuses. Trade-off: ~20% capability loss on average, but uncensored.

**Heretic** — A specific community tool/method for abliteration. Uses MPOA (Magnitude-Preserving Orthogonal Abliteration) — two-stage weight surgery targeting specific refusal layers. Generally better quality preservation than crude abliteration.

**OBLITERATUS** — A comprehensive abliteration toolkit with 9 methods, 28 analysis modules, 116 model presets. Supports diff-in-means, SVD, LEACE, SAE, and more.

## Tools & Platforms

**llama.cpp** — The inference engine. Runs GGUF models on CPU, CUDA, Metal, ROCm. The standard for local LLM inference.

**Ollama** — Simplified wrapper around llama.cpp. `ollama run model-name` — handles downloading and running. Good for beginners, less control.

**LM Studio** — Desktop GUI for local models. Search, download, and chat with models. Uses llama.cpp under the hood.

**Unsloth Studio** — Web UI for downloading, running, and training models. Features self-healing tool calling, automatic parameter tuning, and no-code fine-tuning.

**vLLM** — High-throughput serving engine for production. OpenAI-compatible API. Uses safetensors, not GGUF.

**HuggingFace Hub** — The main repository for open-weight models. Search, download, and host models. Most GGUFs are hosted here.
