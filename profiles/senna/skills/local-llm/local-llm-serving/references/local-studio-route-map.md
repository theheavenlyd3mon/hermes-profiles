# Local Studio Route Map — Reference Session

Captured from a working CPU-only Local Studio setup on macOS 15.7.7 (Intel). Ports and paths are illustrative; update them to the actual controller config.

## Status / health

```bash
curl -s http://127.0.0.1:8080/health
# {"status":"ok"}

curl -s http://127.0.0.1:8080/api/system-status
# {"status":"ok","controller":{"uptime":...,"pid":...},"inference":{"running":false,"model":null}}

curl -s http://127.0.0.1:8080/api/system-info
```

## Runtimes

```bash
curl -s http://127.0.0.1:8080/runtime/targets
```

Note: route is `/runtime/targets`, NOT `/api/runtime-targets`. After installing llama.cpp via Homebrew, expect a `llamacpp:system` target with `binaryPath=/usr/local/bin/llama-server`.

## Models

### Download a model

```bash
curl -s -X POST http://127.0.0.1:8080/studio/downloads \
  -H 'Content-Type: application/json' \
  -d '{
    "model_id": "bartowski/Qwen2.5-0.5B-Instruct-GGUF",
    "allow_patterns": ["*Q4_K_M.gguf"]
  }'
```

Returns a download ID. The file lands under `data/models/<model_id>/`.

### List registered models

```bash
curl -s http://127.0.0.1:8080/v1/studio/models
```

## Recipes

### Create / update

```bash
curl -s -X POST http://127.0.0.1:8080/recipes \
  -H 'Content-Type: application/json' \
  -d @llamacpp-cpu-recipe.json

curl -s -X PUT http://127.0.0.1:8080/recipes/<recipe-id> \
  -H 'Content-Type: application/json' \
  -d @llamacpp-cpu-recipe.json
```

### List / inspect

```bash
curl -s http://127.0.0.1:8080/recipes
curl -s http://127.0.0.1:8080/recipes/<recipe-id>
```

## Lifecycle

### Launch

```bash
curl -s -X POST http://127.0.0.1:8080/launch/<recipe-id>
# {"success":true,"message":"Launch started"}

curl -s "http://127.0.0.1:8080/wait-ready?timeout=120"
# {"ready":true,"elapsed":0}
```

### Evict

```bash
curl -s -X POST http://127.0.0.1:8080/evict
```

## OpenAI-compatible surface

### Models

```bash
curl -s http://127.0.0.1:8080/v1/models
```

Expected response shape:
```json
{
  "object": "list",
  "data": [
    {
      "id": "qwen2.5-0.5b-instruct",
      "object": "model",
      "created": ...,
      "owned_by": "local-studio",
      "active": true,
      "max_model_len": 32768,
      "metadata": { "vision": false }
    }
  ]
}
```

### Chat completion

```bash
curl -s -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen2.5-0.5b-instruct",
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 50
  }'
```

## Usage

```bash
# Inference usage only
curl -s http://127.0.0.1:8080/usage

# Include controller request telemetry
curl -s http://127.0.0.1:8080/usage?include_controller=true
```

The analytics endpoint caches for 15s. `totals` includes `total_tokens`, `prompt_tokens`, `completion_tokens`, `total_requests`, `successful_requests`, and `by_model`.
