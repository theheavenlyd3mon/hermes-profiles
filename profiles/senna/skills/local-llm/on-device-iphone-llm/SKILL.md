---
name: on-device-iphone-llm
description: Run quantized LLMs natively on iPhone/iPad — MLX vs GGUF sizing, mlx-swift kernel forks, phone RAM budgets, and the Xcode sideload flow.
trigger: User wants to run a local/quantized model on an iPhone or iPad (e.g. Bonsai 1-bit, MLX packs, mlx-swift), or asks whether a model fits / will run on their phone.
domain: local-llm
version: 1.0.0
---

# On-Device iPhone LLM Inference

Class-level guidance for getting a quantized LLM running natively on iOS. The headline trap: numbers quoted for the *GGUF/CUDA* build do NOT apply to the *MLX/iOS* build.

## Pitfall #1 — MLX pack is larger than the advertised GGUF number
Model cards advertise a tiny "GGUF footprint" (e.g. Bonsai 1-bit = 3.9 GB). That is the llama.cpp/CUDA pack. The iOS path uses **MLX**, whose grouped low-bit format stores a scale AND a bias per group — it inflates the same 1-bit weights to ~5.13 GB on disk / ~4.2 GB resident. Always size against the MLX pack, not the GGUF marketing number. (See worked Bonsai example below.)

## Pitfall #2 — custom kernels usually mean no turnkey app
If a model ships a *fork* of mlx-swift (custom 1-bit/2-bit Metal kernels), the repo typically ships only macOS/Linux examples — NOT a ready iPhone chat app. You write the SwiftUI shell (load the model container from the bundled weights dir + a generation loop). The kernels are the hard part; the app glue is ~150 lines. Confirm whether the repo has an iOS example target before assuming one-click.

## Phone RAM budgets (per-app memory cap ≈ device RAM minus OS overhead)
| Device | RAM | Runs 1-bit MLX? | Notes |
|--------|-----|-----------------|-------|
| iPhone 15 Pro / 15 Pro Max | 8 GB | Yes, short/medium ctx | keep context ≤ ~8K tokens or OOM |
| iPhone 16 Pro (8 GB) | 8 GB | Yes, short/medium ctx | same as 15 Pro |
| iPhone 17 Pro / 17 Pro Max | 12 GB | Yes, full | headroom for long ctx |
| iPhone base (6 GB) | 6 GB | No | at the budget, no room for KV cache |
| Android | varies | Not via MLX | MLX Swift is Apple-Silicon-only; GGUF/llama.cpp CPU is the fallback but unbenchmarked |

## Xcode sideload flow (no App Store, no jailbreak)
1. Xcode 16 on macOS (runs on macOS 15; newer Xcode may require newer macOS — pin if needed).
2. Clone the model's mlx-swift fork + get MLX weights (e.g. `hf download <org>/<model>-mlx-1bit`).
3. Build a SwiftUI app depending on the local mlx-swift package; bundle the weights dir into the app.
4. Signing & Capabilities → Team = Apple ID. Free tier: re-sign every 7 days. $99 dev account: permanent.
5. Cable device → Trust Developer (Settings → General → VPN & Device Management) → Product → Run.

## Verify before claiming feasibility
- Pull the actual MLX repo, not just the model card. Check for an iOS example target.
- Confirm the phone's RAM vs the MLX *resident* size at your intended context length (enable 4-bit KV cache to shrink the context-dependent term ~4x).
- Thermals: phone decode is thermally limited — sustained tok/s sits ~10–15% below cold peak.

## Worked example — Bonsai 27B 1-bit (prism-ml)
- Repos: `Bonsai-27B-gguf` (1-bit, llama.cpp/CUDA/Metal, 3.9 GB) and `Ternary-Bonsai-27B-gguf` (2-bit, 7.2 GB) for laptop/GPU. For phone: **`Bonsai-27B-mlx-1bit`** (MLX, 5.13 GB disk / 4.2 GB resident). Base: Qwen3.6-27B, 262K ctx, 1.125 bpw, ~14x smaller than 54 GB FP16.
- Kernels: `github.com/PrismML-Eng/mlx-swift` fork has 1-bit Metal kernels (no iOS app target — build the SwiftUI shell yourself).
- Throughput: iPhone 17 Pro Max (A19 Pro) ~11 tok/s cold, ~10.8 sustained (672 tokens per 1% battery); iPhone 15 Pro Max (A17 Pro) ~7–9 tok/s estimated (no official number).
- Generation: temp 0.7, top_p 0.95, top_k 20. DSpark spec-dec drafter NOT enabled on Apple Silicon (batch-1 verify doesn't amortize).
- MLX limitation: scale-only group format unsupported, so effective 1.25 bpw vs native 1.125; 4-bit KV cache brings 100K-ctx peak to ~6.8 GB, 262K window to ~9.4 GB.
