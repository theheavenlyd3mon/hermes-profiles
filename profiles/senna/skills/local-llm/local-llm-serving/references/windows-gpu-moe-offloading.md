# Windows GPU + MoE Offloading (llama.cpp)

For MoE models (e.g., Laguna-XS-2.1, Qwen3.6 MoE) on Windows with CUDA, use
`-ngl` (GPU layer offload) + `-cmoe` (MoE expert weights to CPU) together.

## Build (Windows, CUDA)

```powershell
winget install cmake git.git ninja-build.ninja
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
cmake -B build -DGGML_CUDA=ON -DBUILD_SHARED_LIBS=OFF
cmake --build build --config Release -j --target llama-server
```

## Run command

```powershell
.\build\bin\Release\llama-server.exe `
    -m models\Laguna-XS-2.1-Q4_K_M.gguf `
    --jinja `
    -ngl 40 `
    -cmoe `
    -c 65536 `
    -fa on `
    -cb `
    --cache-type-k q8_0 `
    --cache-type-v q8_0 `
    --host 0.0.0.0 `
    --port 8080 `
    --threads 8
```

## Flag reference

| Flag | Effect |
|---|---|
| `-ngl N` | Offload N transformer layers' shared weights to GPU VRAM |
| `-cmoe` | Keep MoE expert weights on CPU (independent of `-ngl`) |
| `-c N` | Context size (64K practical max on 12GB; 256K KV cache = ~10GB) |
| `-fa on` | Flash Attention |
| `-cb` | Continuous batching |
| `--cache-type-k/v q8_0` | Quantize KV cache to save VRAM |
| `--jinja` | Apply bundled Jinja chat template (required for some MoE models) |

## VRAM budget (Q4_K_M, 64K ctx, 12GB card)

- Non-expert weights on GPU (`-ngl 40`): ~3.6 GB
- KV cache (q8_0, 64K): ~2.5 GB
- Overhead: ~1.5 GB
- Total: ~7.6 GB — fits in 12GB

## Key insight

`-ngl` and `-cmoe` operate at different granularities:
- `-ngl` = layer-level (shared attention + FFN weights)
- `-cmoe` = tensor-level (only `.ffn_*_exps` tensors via `LLM_FFN_EXPS_REGEX`)

They combine. Without `-cmoe`, the full MoE expert set (the bulk of the model)
must fit in VRAM. With `-cmoe`, only shared weights go to GPU.

## Quant choice for 12GB

| Quant | Size | Fits 12GB? |
|---|---|---|
| IQ2_XXS | 9.4 GB | Yes with headroom |
| Q2_K | 12.2 GB | No, no room for KV |
| Q3_K_M | 16.1 GB | No, too big |
| Q4_K_M | 20.3 GB | No, needs `-cmoe` |

Recommendation: Q4_K_M + `-ngl 40 -cmoe` for best quality. Falls back to
IQ2_XXS + `-ngl 40 -cmoe` if even shared weights don't fit.

## Source reference

From llama.cpp master (common/arg.cpp, common/common.h):
- LLM_FFN_EXPS_REGEX = `\.ffn_(up|down|gate|gate_up)_(ch|)exps`
- --cpu-moe sets tensor_buft_overrides with this regex to CPU buffer
- -ngl controls n_gpu_layers (layer-level offloading)
- These are independent mechanisms
