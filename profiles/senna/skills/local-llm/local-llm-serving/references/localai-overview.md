# LocalAI (mudler/LocalAI) — overview notes

Researched 2026-07-27 from the GitHub repo. Self-hosted, open-source (MIT) AI
inference engine by Ettore Di Giacinto. Positioning: drop-in local replacement
for the OpenAI API (also Anthropic + ElevenLabs API surfaces) — point existing
apps at it by changing the base URL.

## Vitals (as of research date)
- ~47.9k stars, 4.3k forks, 234 contributors, very active (multiple commits/day)
- Latest release v4.7.1 (2026-07-14); written mostly in Go
- Docs: https://localai.io · Model gallery: https://models.localai.io

## Architecture
Small Go core + composable backends. Each backend (llama.cpp, vLLM, whisper.cpp,
stable-diffusion, MLX, ...) is a separate OCI image pulled on demand when a model
needs it — nothing installed that isn't used. 60+ backends. Auto-detects hardware
(CUDA 12/13, ROCm, Intel oneAPI, Apple Silicon/Metal, Vulkan, Jetson) and fetches
the matching backend.

## Capability surface (one API)
- Text gen: llama.cpp, transformers, vLLM, SGLang, MLX
- TTS (60 Piper voices / 42 languages, Kokoro), ASR (whisper.cpp, parakeet.cpp
  with streaming + diarization)
- Image + video gen (stablediffusion-ggml, LTX-2, Ideogram4)
- Embeddings, reranker, vision, object detection
- OpenAI Realtime API (speech-to-speech over WebRTC) with tool calling
- Constrained grammars, function calling
- Biometrics: speaker recognition, face detect/anti-spoofing (native ggml backends)

## v4.x direction (beyond inference)
Multi-user platform: OIDC, API keys, RBAC, per-user quotas + usage metrics.
Distributed cluster mode (PostgreSQL + NATS, VRAM-aware routing, autoscaling).
In-UI fine-tuning (TRL, auto-export GGUF), on-the-fly quantization. Built-in
autonomous agents with RAG + MCP + skills, community "Agent Hub".

## Quickstart
```bash
# Docker (CPU)
docker run -ti --name local-ai -p 8080:8080 localai/localai:latest
# Docker (NVIDIA CUDA 13)
docker run -ti --name local-ai -p 8080:8080 --gpus all localai/localai:latest-gpu-nvidia-cuda-13
# CLI: pull + serve a model
local-ai run llama-3.2-1b-instruct:q4_k_m
# macOS: DMG in releases (unsigned — needs: sudo xattr -d com.apple.quarantine /Applications/LocalAI.app)
```
Models load from its gallery, HuggingFace (`huggingface://...`), the Ollama
registry (`ollama://gemma:2b`), or any OCI registry.

## vs Ollama
Ollama is llama.cpp-centric and single-user. LocalAI covers every modality
(image/video/voice/biometrics), exposes more API surfaces, and adds the
multi-user/distributed/agent layer. Closer to "self-hosted OpenAI" than to Ollama.

## Relevance to this fleet
Candidate OpenAI-compatible local endpoint for agent experiments or a future
serving node. Compare against the Local Studio stack in this skill before
adopting — LocalAI is a single-binary alternative to the controller+recipe setup.
