---
name: local-llm-serving
description: "Set up, launch, and verify a self-hosted local LLM serving stack (controller + web UI + llama.cpp backend) on macOS/Linux. Covers model downloads, recipe creation, CPU-only inference, OpenAI-compatible proxy verification, and usage accounting."
category: local-llm
version: 1.0.0
triggers:
  - "local llm"
  - "local studio"
  - "self-hosted llm"
  - "llama.cpp server"
  - "run model locally"
  - "download gguf"
  - "launch recipe"
  - "v1/models"
  - "usage accounting"
platforms: [macos, linux]
metadata:
  hermes:
    related_skills: [project-workspace, hermes-maintenance, docker-management]
---

# Local LLM Serving

Class-level runbook for getting a self-hosted LLM serving stack running on a workstation: controller Hono API, Next.js frontend, llama.cpp backend, model download, recipe registration, launch, and end-to-end verification through the OpenAI-compatible proxy.

## When to use this

- The user wants to run a local LLM stack (Local Studio or similar controller + frontend + inference backend).
- You need to go from "backend installed" to "chat completion works and usage is recorded."
- The machine is CPU-only or GPU-less, and you need a recipe that avoids trying to use GPU.

## Standard flow

1. **Check controller status**
   ```bash
   curl -s http://127.0.0.1:8080/health
   curl -s http://127.0.0.1:8080/api/system-status
   ```
   If the controller isn't running, start it from the controller directory first.

2. **Install the inference backend**
   - For llama.cpp on macOS, prefer Homebrew's bottled build to avoid the 45-minute managed source build:
     ```bash
     brew install --quiet cmake llama.cpp
     llama-server --version
     ```
   - Verify the controller sees it: `GET /runtime/targets` (note: NOT `/api/runtime-targets`).

3. **Download a model**
   Use the controller's download endpoint; pick a small GGUF for CPU (e.g., Qwen2.5-0.5B-Instruct Q4_K_M):
   ```bash
   curl -s -X POST http://127.0.0.1:8080/studio/downloads \
     -H 'Content-Type: application/json' \
     -d '{"model_id":"bartowski/Qwen2.5-0.5B-Instruct-GGUF","allow_patterns":["*Q4_K_M.gguf"]}'
   ```
   Then confirm with `GET /v1/studio/models`.

4. **Create a recipe**
   Recipes are the controller's unit of model launch configuration. See `templates/llamacpp-cpu-recipe.json` for a known-good CPU-only starter. Required fields:
   - `id`, `name`, `model_path` (absolute)
   - `backend`: `llamacpp`
   - `runtime`: `{ "kind": "binary", "ref": "/usr/local/bin/llama-server" }`
   - `host`, `port`, `served_model_name`
   - `extra_args`: `{ "n-gpu-layers": 0 }` for CPU-only machines

   Send it to `POST /recipes`.

5. **Launch the model**
   ```bash
   curl -s -X POST http://127.0.0.1:8080/launch/<recipe-id>
   curl -s "http://127.0.0.1:8080/wait-ready?timeout=120"
   ```

6. **Verify the OpenAI-compatible surface**
   ```bash
   curl -s http://127.0.0.1:8080/v1/models
   curl -s -X POST http://127.0.0.1:8080/v1/chat/completions \
     -H 'Content-Type: application/json' \
     -d '{"model":"<served_model_name>","messages":[{"role":"user","content":"hello"}],"max_tokens":50}'
   ```

7. **Check usage accounting**
   ```bash
   curl -s http://127.0.0.1:8080/usage?include_controller=true
   ```

## Key route map

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Controller liveness |
| `GET /api/system-status` | Controller + inference status |
| `GET /runtime/targets` | Available backends/runtimes |
| `POST /studio/downloads` | Download a model from Hugging Face |
| `GET /v1/studio/models` | Registered models |
| `POST /recipes` | Register a launch recipe |
| `POST /launch/:recipeId` | Launch a recipe |
| `GET /wait-ready` | Wait for inference backend healthy |
| `GET /v1/models` | OpenAI-compatible model list |
| `POST /v1/chat/completions` | OpenAI-compatible chat completion |
| `GET /usage` | Inference usage stats |
| `GET /usage?include_controller=true` | Include controller request telemetry |

## Windows GPU + MoE offloading

For MoE models (Laguna-XS-2.1, Qwen3.6 MoE) on Windows with CUDA, combine
`-ngl` (layer-level GPU offload) with `-cmoe` (MoE expert weights to CPU).
These are independent mechanisms — `-ngl` controls shared weights, `-cmoe`
controls expert tensors via regex. See `references/windows-gpu-moe-offloading.md`
for the full runbook, build commands, and VRAM budget.

## Choosing a model size for the machine

Before recommending a model, **probe the actual hardware** — don't guess from the model name. Run the probe commands in `references/model-sizing-constrained-mac.md`, then size by this rule:

- **A model that fits entirely in GPU VRAM beats a larger "better" model that spills to CPU.** On a Mac with a small discrete GPU (e.g. 4GB Radeon Pro), a 3B Q4 (~2GB) runs fully in VRAM via Metal at ~15-20 tok/s, while a 7B Q4 (~4.7GB) spills past VRAM onto the CPU cores and drops to ~5-8 tok/s. Bigger ≠ faster when it overflows VRAM.
- **Match the workload, not the leaderboard.** Background/feed summarization tolerates a smaller, faster model; interactive chat wants the quality bump. Pick the smallest model that's adequate for the task.
- **On a RAM-capped box (16GB), a free cloud API often beats local.** If the only LLM use is non-interactive summarization, a free-tier API (Groq ~14k req/day, OpenRouter) is faster and costs zero RAM. Local is the right call only for offline/air-gapped needs.

Rough GGUF Q4_K_M sizing: 3B≈2GB, 7-8B≈4.7-5GB, 13B≈7-8GB. Keep the model under VRAM for Metal speed; keep it under ~half of total RAM so the OS + app stay healthy.

## Pitfalls

- **Wrong runtime-targets route.** The controller exposes `GET /runtime/targets`, not `/api/runtime-targets`. Cache TTL is 300s for targets.
- **Managed llama.cpp build timeout.** The controller can build llama.cpp from source, but on macOS the Homebrew bottle is much faster and avoids needing `cmake`/`git` from scratch. Use `brew install llama.cpp` unless the user explicitly wants a source build.
- **CPU-only machines must disable GPU layers.** Always add `"n-gpu-layers": 0` in `extra_args` for CPU-only recipes. Otherwise llama.cpp may try to initialize Metal and crash or hang on Intel Macs.
- **Recipe `served_model_name` is what callers use.** The chat completion request must match `served_model_name` (or the recipe `id` if no alias is set). The controller will map it to the canonical name.
- **Shell quoting breaks JSON.** When testing with `curl -d`, use double quotes for the JSON and escape inner double quotes, or write the JSON to a file. Single-quoted JSON with embedded single quotes (e.g., `'Say 'hello''`) will fail with `Invalid JSON body`.
- **Frontend needs separate startup.** The frontend is usually a Next.js dev server on port 3000. Start it with `npm run dev` in the frontend directory, not via the controller. Verify `/setup` returns 200.
- **Usage cache is 15s.** `/usage` is analytics, not real-time. Use `include_controller=true` to see controller request telemetry in the same payload.
- **No model auto-launch.** The chat proxy never launches a model. If the requested model isn't running, it returns a 503 OpenAI-shaped error.

## Recipe template

See `templates/llamacpp-cpu-recipe.json` for a copy-paste starter. Adjust `model_path`, `id`, `name`, and `served_model_name` for the model you downloaded.

## Verification script

See `scripts/verify-local-studio.sh` — a quick curl-based smoke test that checks health, runtime targets, models, launches a recipe, waits for readiness, and tests a chat completion. Copy and modify the recipe/model variables before running.

## References

- `references/local-studio-route-map.md` — full route summary with example responses from a working session.
- `references/llamacpp-cpu-recipe-notes.md` — field-by-field recipe notes and common `extra_args` for llama.cpp.
- `references/model-sizing-constrained-mac.md` — hardware probe commands + how to size a model to VRAM/RAM (the "fits-in-VRAM beats bigger" rule).
- `references/windows-gpu-moe-offloading.md` — Windows CUDA build, MoE offloading with `-ngl` + `-cmoe`, VRAM budgets for 12GB cards.
- `references/localai-overview.md` — LocalAI (mudler/LocalAI) condensed overview: composable-backend architecture, API surface, quickstart, vs Ollama. Alternative single-binary serving stack.
- `llm-provider-setup/references/kv-cache-memory-budgeting.md` — KV cache memory formula and table of common models. Essential when sizing context length against RAM.
