# llama.cpp Recipe Notes — CPU-Only

Field-by-field notes for writing a controller recipe that runs a GGUF model with the system llama-server binary on a CPU-only machine.

## Required fields

| Field | Example | Notes |
|-------|---------|-------|
| `id` | `"qwen2-5-0.5b-cpu"` | Non-empty string; used in `/recipes/:id` and `/launch/:id`. |
| `name` | `"Qwen2.5 0.5B Instruct Q4_K_M (CPU)"` | Human-readable display name. |
| `model_path` | `/.../Qwen2.5-0.5B-Instruct-Q4_K_M.gguf` | Absolute path. The controller does not expand `~`. |
| `backend` | `"llamacpp"` | One of `vllm`, `sglang`, `llamacpp`, `mlx`. |
| `runtime` | `{ "kind": "binary", "ref": "/usr/local/bin/llama-server" }` | `kind` is `binary` for a system llama-server. `ref` must be the absolute binary path. |
| `host` | `"127.0.0.1"` | Address llama-server binds to. |
| `port` | `8000` | Must match the controller's `inference_port` (default 8000). |
| `served_model_name` | `"qwen2.5-0.5b-instruct"` | What callers use in the `model` field for chat completions. If omitted, callers use `id`. |

## Common `extra_args` for CPU-only runs

```json
{
  "extra_args": {
    "n-gpu-layers": 0,
    "threads": 4
  }
}
```

- `n-gpu-layers` (or `n_gpu_layers`): `0` forces CPU. Do not omit on CPU-only machines — llama.cpp may try to load Metal/GPU and fail.
- `threads`: number of threads. Default is usually fine; set explicitly for reproducibility on shared machines.
- `ctx-size`: optional override. The controller already maps `max_model_len` to `--ctx-size` if no override is given.
- `chat-template`: usually not needed; the GGUF carries the template. Use only if the model misbehaves.

## Runtime normalization rules

From the recipe serializer:
- If `runtime` is omitted, `llamacpp` defaults to `{ "kind": "binary", "ref": "llama-server" }`, which relies on `$PATH` resolution.
- If you installed via Homebrew, prefer the absolute path in `ref` to avoid ambiguity.
- `kind` values are normalized: `venv` becomes `managed_venv`, and legacy `docker_image`/`docker-image` keys are folded into `runtime.kind=docker`.

## Backend command construction

The controller builds the launch command roughly as:

```text
llama-server --model <model_path> --host <host> --port <port> --alias <served_model_name> --ctx-size <max_model_len> --n-gpu-layers 0 --threads 4
```

You can inspect the exact process after launch with:

```bash
ps -o pid,args -p $(lsof -ti :8000)
```

## Troubleshooting

- **Model not running error from `/v1/chat/completions`:** The chat proxy never auto-starts a model. Verify the recipe is running via `GET /status` or `/v1/models` first.
- **Invalid JSON body:** Usually shell quoting in the curl command. Write JSON to a file and use `-d @file.json`.
- **llama-server exits immediately:** Check logs; common causes are bad `model_path`, missing model file, or GPU flags on a CPU-only machine.
