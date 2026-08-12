# Hermes Lazy-Install System (tools/lazy_deps.py)

Condensed knowledge bank on how Hermes' on-demand dependency installation works, verified against source 2026-08-03. Pairs with `scripts/lazy-backends-check.py`.

## What it is

Optional Hermes backends (TTS/STT providers, messaging platforms, search providers, cloud memory providers, terminal backends, tools) install their Python SDKs **on first use** at runtime, not at setup. Implemented in `~/.hermes/hermes-agent/tools/lazy_deps.py` (module `tools.lazy_deps`). The update-time behavior is the **lazy-refresh pass** in `hermes_cli/main.py`.

Why it replaced eager `hermes-agent[all]` extras:
1. **Fragility** — one extra's broken/yanked transitive dep failed the ENTIRE `[all]` resolve; fresh installs silently fell back to a stripped tier.
2. **Bloat** — a user talking to one provider carried hundreds of never-imported packages.

## Mechanics

- A backend's first-import path calls `ensure("feature.name")` (e.g. `platform.discord`), typically inside try/except converting `FeatureUnavailable` to a runtime error. Canonical call site: `plugins/platforms/discord/adapter.py:437` (lazy-installs discord.py).
- `ensure` checks `security.allow_lazy_installs` (default **true**) then runs a **venv-scoped pip install** of exact pins from the `LAZY_DEPS` allowlist. Never touches system Python.
- Failure (offline, PyPI 404/quarantine, disabled) raises `FeatureUnavailable` with remediation hint pointing at `hermes tools` or the manual pip command — no silent retries, no caching of bad state.

## LAZY_DEPS allowlist (41 features as of 2026-08-03)

Only specs in this dict can flow into the pip command. Exact pins, many carrying CVE comments:
- `provider.anthropic` `anthropic==0.87.0` (CVE-2026-34450/34452), `provider.bedrock` boto3, `provider.vertex` google-auth+pyasn1, `provider.azure_identity`
- `platform.discord` discord.py[voice]==2.7.1 + brotlicffi + aiohttp==3.14.1 (CVE-2026-34513…34993 RCE); `platform.slack`, `platform.matrix`, `platform.teams`, `platform.dingtalk`, `platform.feishu`, `platform.wecom_callback`, `platform.telegram` python-telegram-bot[webhooks]==22.6
- `search.firecrawl` / `search.exa` / `search.parallel`; `image.fal` fal-client
- `memory.honcho` / `memory.hindsight` / `memory.supermemory` / `memory.mem0`
- `stt.*` (faster-whisper, mistral, silk), `wake.*` (openwakeword, porcupine, sherpa), `tts.edge` (installed) / `tts.elevenlabs` elevenlabs==1.59.0 / `tts.mistral`
- `terminal.modal` / `terminal.daytona` / `terminal.vercel`; `tool.acp`, `tool.dashboard` (fastapi/uvicorn/starlette — starlette==1.3.1 for CVE-2026-48710), `tool.computer_use`, `tool.vision`, `tool.trace_upload`
- `skill.google_workspace` (google-api-* + httplib2==0.32.0), `skill.youtube`; `export.otlp`

## Security model

- **Venv-scoped by default.** Installs target `sys.executable` in the active venv.
- **Durable-target mode (immutable Docker images):** `HERMES_DISABLE_LAZY_INSTALLS=1` seals the venv; `HERMES_LAZY_INSTALL_TARGET` redirects installs to a writable dir **appended to the END of sys.path** (never prepended, never via PYTHONPATH) — a lazy package can only ADD importable modules, never shadow/downgrade core. Structural guarantee a bad backend can't brick Hermes.
- **PyPI by package name only** — no `--index-url`, no `git+https://`, no file: paths. `_SAFE_SPEC` regex validates.
- **Allowlist + exact pins.** Opt-out via `security.allow_lazy_installs: false`.

## Update-time behavior

- `hermes update` runs the **lazy-refresh pass**: because `active_features()` marks a feature active from mere package presence, the refresh re-asserts exact pins for active backends against the new release's lockfile (e.g. `huggingface-hub==1.24.0` must stay inside transformers' accepted window or Hindsight breaks — policy: exact pins, must match uv.lock, test_project_metadata.py enforces).
- Marker files in repo root: `.lazy-refresh-incomplete` / `.update-incomplete`. Next launch detects them and heals via import-probe repair (`_recover_lazy_refresh_marker_locked`); `_upgrade_pip_before_lazy_refresh` runs first.
- Shared deps are NOT force-downgraded: if another package pulled newer numpy/onnxruntime than the pin, the refresh leaves it (observed 2026-08-03: numpy 2.4.6 installed vs 2.4.3 pin in wake/stt rows — expected, not breakage).

## Config knobs

- `security.allow_lazy_installs: true|false` — user-facing master switch (root config.yaml:479 = true on this fleet).
- `HERMES_LAZY_INSTALL_TARGET` — redirect lazy installs (Docker durable volume).
- `HERMES_DISABLE_LAZY_INSTALLS` — internal bridge var set by official Docker image; do NOT set manually.

## TTS provider mapping (why elevenlabs shows missing)

| Provider | Package | Key | Status on fleet (2026-08-03) |
|---|---|---|---|
| edge | edge-tts==7.2.7 | none (free, default) | ✅ installed |
| openai | (core) | Nous subscription | `tts.provider: openai` in root config |
| elevenlabs | elevenlabs==1.59.0 | `ELEVENLABS_API_KEY` | ⬜ missing — config has voice_id/model_id block but NO key; SDK pulls on first use once provider=elevenlabs + key set |
| mistral | mistralai | `MISTRAL_API_KEY` | ⬜ missing |

## Fleet snapshot 2026-08-03 (venv check)

41 features: **14 fully installed** (discord, fal, firecrawl, anthropic, vertex, dashboard, ACP, computer-use, trace-upload, vision, edge-tts, google-workspace, youtube, wecom) · **7 partial** (matrix/slack/teams = aiohttp only; faster-whisper/openwakeword/porcupine/sherpa = shared audio deps only) · **20 missing** (telegram, dingtalk, feishu, bedrock, azure-identity, exa, parallel, modal/daytona/vercel, elevenlabs, mistral, honcho/hindsight/mem0/supermemory, otlp, silk).

Notable: Telegram SDK never pulled even though gateway fleet exists — would install on first Telegram connect.
