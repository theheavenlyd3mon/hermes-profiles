# GGUF Advanced Usage Guide

## Speculative Decoding

### MTP (Multi-Token Prediction) — Preferred Method

MTP is speculative decoding baked into the model weights. The model was trained with auxiliary MTP heads that predict 2-3 tokens ahead. No extra model download, no extra VRAM. **This is the fastest speculative decoding method.**

**Requirements:**
- llama.cpp **b9180+** (merged May 16, 2026). Rebuild from latest source.
- A GGUF with MTP heads baked in (bartowski's Qwen3.6 quants, unsloth MTP builds, froggeric MTP builds)

```bash
# Enable MTP speculative decoding
./llama-server -m model-mtp.gguf \
    --spec-type draft-mtp \
    --spec-draft-n-max 2 \
    -ngl 99 -c 8192 --flash-attn
```

**Critical flags:**
- `--spec-type draft-mtp` — enables MTP (was `--spec-type mtp` before b9180)
- `--spec-draft-n-max 2` — draft 2 tokens per step. **2 is optimal for most quants.** Higher wastes compute on rejected tokens.

**Models with native MTP support (as of mid-2026):**

| Model Family | Status | Notes |
|-------------|--------|-------|
| Qwen3.5+ (including 3.6) | ✅ Full | Best documented, most GGUFs |
| DeepSeek v3/v3.2/v4 | ✅ Full | Large models |
| GLM4.5+ | ✅ Full | |
| Step3.5Flash | ✅ Full | |
| Mimo v2+ | ✅ Full | Xiaomi's model |
| Gemma 4 | ✅ Community | Pending official uncensored weights |

**MTP speedup varies by task type** (measured on Qwen3.6-27B Q4_K_M):

| Task Type | Draft Acceptance | Speedup | Enable? |
|-----------|-----------------|---------|---------|
| Code / debugging | 79-89% | +31% | ✅ Always |
| Factual Q&A / translation | 62-70% | +16% | ✅ Yes |
| Analysis / comparisons | 48-56% | marginal | 🟡 Your call |
| Creative writing / roleplay | 39-48% | -9% (slower!) | ❌ Disable |

For creative tasks at Q4_K_M or lower, use `--spec-type none` to disable MTP.

**Real-world numbers (12GB RTX 4070, Qwen3.6-35B-A3B):**
- Baseline: ~51 tok/s
- MTP n-max=2: ~65-75 tok/s (+27-47%)
- Accepted rate: ~98%

**MTP vs other speculative decoding methods:**

| Method | Extra Download? | Extra VRAM? | Speedup | Engine |
|--------|----------------|-------------|---------|--------|
| MTP | ❌ Built into model | ❌ Negligible | 1.5-2.7x | llama.cpp ✅ |
| NextN (AtomicBot) | ❌ Built into model | ❌ Negligible | 1.5-2.7x | AtomicBot fork ✅ |
| EAGLE-3 | ✅ Separate file (1.1 GB) | ✅ ~1-3 GB | 1.8-2.0x | SGLang/vLLM only ❌ |
| Draft model (legacy) | ✅ Separate model | ✅ Full draft model | 1.2-1.5x | llama.cpp ✅ |
| N-gram | ❌ | ❌ | Varies | llama.cpp ✅ |
| CPU offload draft | ❌ | ❌ | 1.2-1.5x | llama.cpp ✅ |

**For 12GB VRAM on llama.cpp:** MTP (or NextN via AtomicBot) is the only speculative decoding that matters. EAGLE-3 requires SGLang/vLLM and dense models — doesn't fit the hardware or software stack. See [constrained-vram-models.md](constrained-vram-models.md) for the full EAGLE-3 analysis.

### Draft Model Approach (Legacy)

```bash
# Use smaller model as draft for faster generation
./llama-speculative \
    -m large-model-q4_k_m.gguf \
    -md draft-model-q4_k_m.gguf \
    -p "Write a story about AI" \
    -n 500 \
    --draft 8  # Draft tokens before verification
```

### Self-Speculative Decoding

```bash
# Use same model with different context for speculation
./llama-cli -m model-q4_k_m.gguf \
    --lookup-cache-static lookup.bin \
    --lookup-cache-dynamic lookup-dynamic.bin \
    -p "Hello world"
```

## Batched Inference

### Process Multiple Prompts

```python
from llama_cpp import Llama

llm = Llama(
    model_path="model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,
    n_batch=512  # Larger batch for parallel processing
)

prompts = [
    "What is Python?",
    "Explain machine learning.",
    "Describe neural networks."
]

# Process in batch (each prompt gets separate context)
for prompt in prompts:
    output = llm(prompt, max_tokens=100)
    print(f"Q: {prompt}")
    print(f"A: {output['choices'][0]['text']}\n")
```

### Server Batching

```bash
# Start server with batching
./llama-server -m model-q4_k_m.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    -ngl 35 \
    -c 4096 \
    --parallel 4        # Concurrent requests
    --cont-batching     # Continuous batching
```

## Custom Model Conversion

### Convert with Vocabulary Modifications

```python
# custom_convert.py
import sys
sys.path.insert(0, './llama.cpp')

from convert_hf_to_gguf import main
from gguf import GGUFWriter

# Custom conversion with modified vocab
def convert_with_custom_vocab(model_path, output_path):
    # Load and modify tokenizer
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Add special tokens if needed
    special_tokens = {"additional_special_tokens": ["<|custom|>"]}
    tokenizer.add_special_tokens(special_tokens)
    tokenizer.save_pretrained(model_path)

    # Then run standard conversion
    main([model_path, "--outfile", output_path])
```

### Convert Specific Architecture

```bash
# For Mistral-style models
python convert_hf_to_gguf.py ./mistral-model \
    --outfile mistral-f16.gguf \
    --outtype f16

# For Qwen models
python convert_hf_to_gguf.py ./qwen-model \
    --outfile qwen-f16.gguf \
    --outtype f16

# For Phi models
python convert_hf_to_gguf.py ./phi-model \
    --outfile phi-f16.gguf \
    --outtype f16
```

## Advanced Quantization

### Mixed Quantization

```bash
# Quantize different layer types differently
./llama-quantize model-f16.gguf model-mixed.gguf Q4_K_M \
    --allow-requantize \
    --leave-output-tensor
```

### Quantization with Token Embeddings

```bash
# Keep embeddings at higher precision
./llama-quantize model-f16.gguf model-q4.gguf Q4_K_M \
    --token-embedding-type f16
```

### IQ Quantization (Importance-aware)

```bash
# Ultra-low bit quantization with importance
./llama-quantize --imatrix model.imatrix \
    model-f16.gguf model-iq2_xxs.gguf IQ2_XXS

# Available IQ types: IQ2_XXS, IQ2_XS, IQ2_S, IQ3_XXS, IQ3_XS, IQ3_S, IQ4_XS
```

## Memory Optimization

### Memory Mapping

```python
from llama_cpp import Llama

# Use memory mapping for large models
llm = Llama(
    model_path="model-q4_k_m.gguf",
    use_mmap=True,       # Memory map the model
    use_mlock=False,     # Don't lock in RAM
    n_gpu_layers=35
)
```

### Partial GPU Offload

```python
# Calculate layers to offload based on VRAM
import subprocess

def get_free_vram_gb():
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader'],
        capture_output=True, text=True
    )
    return int(result.stdout.strip()) / 1024

# Estimate layers based on VRAM (rough: 0.5GB per layer for 7B Q4)
free_vram = get_free_vram_gb()
layers_to_offload = int(free_vram / 0.5)

llm = Llama(
    model_path="model-q4_k_m.gguf",
    n_gpu_layers=min(layers_to_offload, 35)  # Cap at total layers
)
```

### KV Cache Optimization

```python
from llama_cpp import Llama

# Optimize KV cache for long contexts
llm = Llama(
    model_path="model-q4_k_m.gguf",
    n_ctx=8192,          # Large context
    n_gpu_layers=35,
    type_k=1,            # Q8_0 for K cache (1)
    type_v=1,            # Q8_0 for V cache (1)
    # Or use Q4_0 (2) for more compression
)
```

## Context Management

### Context Shifting

```python
from llama_cpp import Llama

llm = Llama(
    model_path="model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35
)

# Handle long conversations with context shifting
conversation = []
max_history = 10

def chat(user_message):
    conversation.append({"role": "user", "content": user_message})

    # Keep only recent history
    if len(conversation) > max_history * 2:
        conversation = conversation[-max_history * 2:]

    response = llm.create_chat_completion(
        messages=conversation,
        max_tokens=256
    )

    assistant_message = response["choices"][0]["message"]["content"]
    conversation.append({"role": "assistant", "content": assistant_message})
    return assistant_message
```

### Save and Load State

```bash
# Save state to file
./llama-cli -m model.gguf \
    -p "Once upon a time" \
    --save-session session.bin \
    -n 100

# Load and continue
./llama-cli -m model.gguf \
    --load-session session.bin \
    -p " and they lived" \
    -n 100
```

## Grammar Constrained Generation

### JSON Output

```python
from llama_cpp import Llama, LlamaGrammar

# Define JSON grammar
json_grammar = LlamaGrammar.from_string('''
root ::= object
object ::= "{" ws pair ("," ws pair)* "}" ws
pair ::= string ":" ws value
value ::= string | number | object | array | "true" | "false" | "null"
array ::= "[" ws value ("," ws value)* "]" ws
string ::= "\\"" [^"\\\\]* "\\""
number ::= [0-9]+
ws ::= [ \\t\\n]*
''')

llm = Llama(model_path="model-q4_k_m.gguf", n_gpu_layers=35)

output = llm(
    "Output a JSON object with name and age:",
    grammar=json_grammar,
    max_tokens=100
)
print(output["choices"][0]["text"])
```

### Custom Grammar

```python
# Grammar for specific format
answer_grammar = LlamaGrammar.from_string('''
root ::= "Answer: " letter "\\n" "Explanation: " explanation
letter ::= [A-D]
explanation ::= [a-zA-Z0-9 .,!?]+
''')

output = llm(
    "Q: What is 2+2? A) 3 B) 4 C) 5 D) 6",
    grammar=answer_grammar,
    max_tokens=100
)
```

## LoRA Integration

### Load LoRA Adapter

```bash
# Apply LoRA at runtime
./llama-cli -m base-model-q4_k_m.gguf \
    --lora lora-adapter.gguf \
    --lora-scale 1.0 \
    -p "Hello!"
```

### Multiple LoRA Adapters

```bash
# Stack multiple adapters
./llama-cli -m base-model.gguf \
    --lora adapter1.gguf --lora-scale 0.5 \
    --lora adapter2.gguf --lora-scale 0.5 \
    -p "Hello!"
```

### Python LoRA Usage

```python
from llama_cpp import Llama

llm = Llama(
    model_path="base-model-q4_k_m.gguf",
    lora_path="lora-adapter.gguf",
    lora_scale=1.0,
    n_gpu_layers=35
)
```

## Embedding Generation

### Extract Embeddings

```python
from llama_cpp import Llama

llm = Llama(
    model_path="model-q4_k_m.gguf",
    embedding=True,      # Enable embedding mode
    n_gpu_layers=35
)

# Get embeddings
embeddings = llm.embed("This is a test sentence.")
print(f"Embedding dimension: {len(embeddings)}")
```

### Batch Embeddings

```python
texts = [
    "Machine learning is fascinating.",
    "Deep learning uses neural networks.",
    "Python is a programming language."
]

embeddings = [llm.embed(text) for text in texts]

# Calculate similarity
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

sim = cosine_similarity(embeddings[0], embeddings[1])
print(f"Similarity: {sim:.4f}")
```

## Performance Tuning

### Benchmark Script

```python
import time
from llama_cpp import Llama

def benchmark(model_path, prompt, n_tokens=100, n_runs=5):
    llm = Llama(
        model_path=model_path,
        n_gpu_layers=35,
        n_ctx=2048,
        verbose=False
    )

    # Warmup
    llm(prompt, max_tokens=10)

    # Benchmark
    times = []
    for _ in range(n_runs):
        start = time.time()
        output = llm(prompt, max_tokens=n_tokens)
        elapsed = time.time() - start
        times.append(elapsed)

    avg_time = sum(times) / len(times)
    tokens_per_sec = n_tokens / avg_time

    print(f"Model: {model_path}")
    print(f"Avg time: {avg_time:.2f}s")
    print(f"Tokens/sec: {tokens_per_sec:.1f}")

    return tokens_per_sec

# Compare quantizations
for quant in ["q4_k_m", "q5_k_m", "q8_0"]:
    benchmark(f"model-{quant}.gguf", "Explain quantum computing:", 100)
```

### Optimal Configuration Finder

```python
def find_optimal_config(model_path, target_vram_gb=8):
    """Find optimal n_gpu_layers and n_batch for target VRAM."""
    from llama_cpp import Llama
    import gc

    best_config = None
    best_speed = 0

    for n_gpu_layers in range(0, 50, 5):
        for n_batch in [128, 256, 512, 1024]:
            try:
                gc.collect()
                llm = Llama(
                    model_path=model_path,
                    n_gpu_layers=n_gpu_layers,
                    n_batch=n_batch,
                    n_ctx=2048,
                    verbose=False
                )

                # Quick benchmark
                start = time.time()
                llm("Hello", max_tokens=50)
                speed = 50 / (time.time() - start)

                if speed > best_speed:
                    best_speed = speed
                    best_config = {
                        "n_gpu_layers": n_gpu_layers,
                        "n_batch": n_batch,
                        "speed": speed
                    }

                del llm
                gc.collect()

            except Exception as e:
                print(f"OOM at layers={n_gpu_layers}, batch={n_batch}")
                break

    return best_config
```

## Multi-GPU Setup

### Distribute Across GPUs

```bash
# Split model across multiple GPUs
./llama-cli -m large-model.gguf \
    --tensor-split 0.5,0.5 \
    -ngl 60 \
    -p "Hello!"
```

### Python Multi-GPU

```python
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

from llama_cpp import Llama

llm = Llama(
    model_path="large-model-q4_k_m.gguf",
    n_gpu_layers=60,
    tensor_split=[0.5, 0.5]  # Split evenly across 2 GPUs
)
```

## Custom Builds

### Build with All Optimizations

```bash
# Clean build with all CPU optimizations
make clean
LLAMA_OPENBLAS=1 LLAMA_BLAS_VENDOR=OpenBLAS make -j

# With CUDA and cuBLAS
make clean
GGML_CUDA=1 LLAMA_CUBLAS=1 make -j

# With specific CUDA architecture
GGML_CUDA=1 CUDA_DOCKER_ARCH=sm_86 make -j
```

### CMake Build

```bash
mkdir build && cd build
cmake .. -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release -j
```
