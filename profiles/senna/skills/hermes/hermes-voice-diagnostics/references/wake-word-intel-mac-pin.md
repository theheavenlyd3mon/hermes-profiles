# Wake word pin failure on Intel macOS (session 2026-08-04)

## Symptom

Every `hermes` launch on senna profile (Intel MacBook Pro, macOS 15.7.7):

```
Installing wake word engine (first use — this may take a minute)...
Failed to start wake word: Feature 'wake.openwakeword' unavailable: pip install failed:
ERROR: Could not find a version that satisfies the requirement onnxruntime==1.27.0
(from versions: 1.15.0 ... 1.23.2)
```

## Root cause

- `tools/lazy_deps.py` `LAZY_DEPS["wake.openwakeword"]` = `openwakeword==0.6.0`, `onnxruntime==1.27.0`, `sounddevice==0.5.5`, `numpy==2.4.3`.
- onnxruntime 1.27.0 exists on PyPI (latest was 1.28.0 at the time), but **all macOS wheels for 1.24.0+ are `macosx_14_0_arm64` only**. Intel (x86_64) wheels stop at 1.23.2.
- This Mac is x86_64 → pip's "from versions" list correctly tops out at 1.23.2.
- numpy 2.4.3 still ships `macosx_10_9_x86_64` / `macosx_14_0_x86_64` cp311 wheels — only onnxruntime is the blocker.

## Verified facts

- Upstream `main` had no fix as of 2026-08-04 (`git fetch` + `git log HEAD..origin/main -- tools/lazy_deps.py tools/wake_word.py` → empty).
- `lazy_deps._is_satisfied()` checks presence AND version against the `==` pin. Installing onnxruntime 1.23.2 manually does not help — version mismatch re-triggers the install loop every launch.
- Install path: `uv pip install` targeting the venv of `sys.executable` (`.hermes-runtime` cpython-3.11.15). The shell's `python3` was 3.14.5 — irrelevant to the failure; always check wheel tags for the runtime interpreter (cp311).
- `wake_word.enabled: true` was set in `~/.hermes/profiles/senna/config.yaml` — that's why it fires every startup.
- tflite fallback path exists (`wake.openwakeword.tflite` → `ai-edge-litert==2.1.6`, platform-gated by the caller because dep specs can't carry PEP 508 markers) but on non-ARM Macs it warns and falls back to onnx, which is the failing backend.

## Fix options (presented to user, pending their pick)

1. Patch the pin in `tools/lazy_deps.py` to be platform-conditional, e.g. `"onnxruntime==1.23.2" if (sys.platform == "darwin" and platform.machine() == "x86_64") else "onnxruntime==1.27.0"`, then run the install once. Wake word works. Local patch is overwritten by `hermes update` until upstream lands a fix — file an issue/PR.
2. `wake_word.enabled: false` in the profile config.yaml if the user doesn't use "hey Hermes" activation. Zero code changes.

## Reusable diagnosis recipe (any lazy-dep pip failure)

```bash
# 1. Find the pin
grep -n -A5 "<feature-name>" ~/.hermes/hermes-agent/tools/lazy_deps.py
# 2. List wheels for the pinned version on your platform
curl -s https://pypi.org/pypi/<pkg>/<pinned-ver>/json | python3 -c "
import json,sys
print([f['filename'] for f in json.load(sys.stdin)['urls']])"
# 3. Check upstream for a fix
cd ~/.hermes/hermes-agent && git fetch origin main -q && git log HEAD..origin/main --oneline -- tools/lazy_deps.py
```
