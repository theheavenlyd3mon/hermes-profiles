---
name: windows-isolated-dev-environment
description: "Set up Hermes Agent on a Windows PC under a restricted non-admin user account — isolated from personal data, optimized for GPU-accelerated creative/dev work (Three.js, Blender, UE5, web game dev). Covers portable installs, security boundaries, profile design, and cross-machine config transfer."
version: 1.1.0
author: Hermes Agent
license: MIT
triggers:
  - "hermes on windows"
  - "windows setup"
  - "windows pc"
  - "non-admin user"
  - "isolated account"
  - "windows dev environment"
  - "transfer hermes to windows"
  - "add hermes to windows"
  - "windows gpu dev"
metadata:
  hermes:
    tags: [windows, setup, isolation, security, gpu, cross-platform]
    related_skills: [hermes-agent, hermes-security-hardening, profile-bootstrapping, game-dev-with-hermes, blender-automation]
---

# Hermes on Windows — Isolated Dev Environment

Set up Hermes on a Windows PC under a dedicated non-admin standard user account.
Use case: GPU-accelerated creative/dev work (Three.js, Blender, UE5, web game dev)
while keeping personal data on the main account completely isolated.

## When To Use

- User wants Hermes on a Windows machine but doesn't trust it with personal files
- Dedicated dev box with a GPU (your GPU, e.g. 12-24GB VRAM, etc.) for rendering-heavy work
- Cross-machine setup: Mac for daily/personal, Windows for GPU dev
- Security-conscious: limit blast radius if Hermes is compromised

## Architecture

```
MAIN ACCOUNT (<user>):
  - Install UE5, Steam, etc. via admin (one-time)
  - Personal files stay here — Hermes cannot access them

HERMES-DEV ACCOUNT (standard user, NOT admin):
  - Python, Node, Git (user-space installs)
  - Hermes (git clone + venv)
  - Blender (portable zip)
  - VS Code (portable)
  - Runs system-wide installed programs (UE5, browsers)
  - All Hermes data in C:\Users\hermes-dev\
```

## Step-by-Step Setup

### 1. Create the account

Windows Settings → Accounts → Other users → Add account.
Name: `hermes-dev` (or whatever). Type: **Standard user** (NOT admin).

This account:
- Cannot install system-wide software
- Cannot access `C:\Users\<main-user>\`
- Cannot modify system settings or registry
- CAN run programs, browse web, use GPU

### 2. Install per-user tools (as hermes-dev)

All support per-user installs (no admin needed):

**Python 3.11+:**
Download "Windows installer (64-bit)" → "Install for current user" (not system-wide).
Adds to PATH automatically for that user.

**Node.js:**
Download .zip (NOT .msi) → extract to `C:\Users\hermes-dev\nodejs\`.
Add to PATH in user environment variables.

**Git:**
Download portable Git → extract to `C:\Users\hermes-dev\git\`.
Or if Git is already installed system-wide, non-admin users can read it.

**VS Code (portable mode):**
Download .zip → extract to `C:\Users\hermes-dev\vscode\`.
Launch with `--user-data-dir` to keep settings isolated.

### 3. Install Hermes

Open PowerShell as hermes-dev:
```powershell
cd ~
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
python -m venv venv
.\venv\Scripts\activate
pip install -e .
python run_agent.py
```

### 4. Blender (portable zip)

Download .zip from blender.org → extract to `C:\Users\hermes-dev\blender\`.
Hermes can drive it via the `blender-automation` MCP skill.
Models land in `workspace\blender-models\`.

### 5. UE5 (system-wide, main account installs)

UE5 requires admin to install via Epic Games Launcher. Install from main account.
The hermes-dev standard user can **run** UE5 (read+execute), just can't install/uninstall.

If UE5 is in `C:\Program Files\Epic Games\UE_5.x`, standard users can execute it
by default. If not, grant access:
```cmd
icacls "C:\Program Files\Epic Games\UE_5.x" /grant hermes-dev:(OI)(CI)RX
```

## Workspace Structure

```
C:\Users\hermes-dev\
├── hermes-agent\          # Hermes source + venv
├── .hermes\               # Hermes config, profiles, memories
│   └── profiles\
│       └── designer\      # Profile for Three.js/Blender/UE5 work
│           ├── config.yaml
│           ├── skills\    # threejs-*, blender-automation, ue-* skills
│           └── scripts\
├── workspace\             # All dev projects go here
│   ├── threejs-scenes\
│   ├── blender-models\
│   └── ue5-projects\
└── vscode\                # Portable VS Code
```

## Security Boundaries

**HERMES CAN ACCESS:**
- `C:\Users\hermes-dev\` (its own files)
- GPU (your GPU, etc.) — browser rendering, Blender, UE5
- Network — API calls, subscriptions
- Chrome/Edge — Three.js preview

**HERMES CANNOT ACCESS:**
- `C:\Users\<main-user>\` — Windows ACL blocks this by default
- System-wide installs (read-only for standard users)
- Registry (read-only)
- Other user profiles
- Windows credentials

**WEAK POINT:** Network access is still open. For extra security,
add a Windows Firewall rule for the hermes-dev user that blocks
outbound except API endpoints (OpenRouter, Anthropic, etc.)

## Designer Profile Config

The profile on the Windows box should have:
- Skills: `threejs-*`, `blender-automation`, `ue-*`, `game-dev-with-hermes`
- Disabled toolsets: `discord`, `email`, `social-media`, `financial-markets`
- Enabled toolsets: `browser`, `terminal`, `file`, `web`, `image_gen`
- No access to Mac-only skills (`imessage`, `apple-notes`, `findmy`, etc.)

## Cross-Machine Skill Sync

**Two skill tiers in the windowshermes repo:**

1. **Shared skills** (repo root `skills/`) — installed to ALL profiles by `install.sh`. For skills every profile needs (memory system, debugging, etc.).
2. **Profile-specific skills** (each profile's `skills/`) — for domain-specific skills only that profile needs.

**Critical gap to watch for:** New profiles often ship with SOUL.md + AGENTS.md + config.yaml but NO skills directory. Always verify each profile has its required skills after initial setup. See `references/windowshermes-skill-inventory.md` for the full per-profile skill list and sync commands. See `references/magnus-skills-for-windows.md` for which Magnus Agent-Skills are recommended for Windows game dev profiles.

**Skills the ue5-coder profile needs (not exhaustive, check current senna profile):**
- `karpathy-coding-discipline` — surgical coding, no drive-by refactors
- `test-driven-development` — RED-GREEN-REFACTOR cycle
- `systematic-debugging` — 4-phase root cause debugging
- `ue-*` skills — Unreal Engine specific patterns (cpp-foundations, actor-component, gameplay-abilities, etc.)
- `game-dev-memory-system` — memory architecture (can be shared)

**Sync workflow:**
```
Mac (source of truth) → git push → Windows (pull + install.sh)
```
- Mac senna profile is the canonical source for skills
- Push to windowshermes repo → pull on Windows → run `install.sh`
- `install.sh` copies shared skills to all profiles; profile-specific skills live in `profiles/<name>/skills/`
- After pulling, verify: `ls ~/.hermes/profiles/ue5-coder/skills/` should NOT be empty

## Cross-Machine Config Transfer

When moving Hermes config from Mac to Windows:

**What to copy:**
- `~/.hermes/config.yaml` (settings)
- `~/.hermes/auth.json` (provider auth)
- `~/.hermes/.env` (API keys)
- `~/.hermes/profiles/<name>/` (config, skills, plugins, scripts)
- Mnemosyne memory export (via `mnemosyne_export`)

**What NOT to copy:**
- `~/.hermes/hermes-agent/` (reclone fresh — different OS, different venv)
- `node_modules/` (reinstall fresh)
- Platform-specific configs (launchd, macOS paths)
- Mac-only plugin state

**What to recreate:**
- Cron jobs (list with `hermes cron list --all` on Mac, recreate on Windows)
- Platform connections (Discord bot token works on both, but gateway runs one at a time)
- Any symlinks (Windows uses junctions or copies instead)

## Private Profiles Repo Pattern

Store domain-specific Hermes profiles in a private GitHub repo. Both Mac and Windows pull from it.

```
repo/
├── README.md
├── install.sh              # one-command setup (supports --setup-ollama, --setup-llamacpp)
├── .env.example            # template with placeholder API keys
├── .gitignore              # blocks .env, .DS_Store, node_modules
├── profiles/
│   ├── ue5-coder/
│   │   ├── SOUL.md         # compressed DSL persona
│   │   ├── AGENTS.md       # domain conventions
│   │   └── config.yaml     # backend toggle (ollama/llamacpp), model, inference settings
│   ├── threejs-coder/
│   ├── blender-coder/
│   └── designer/
├── knowledge/              # wiki snapshots for offline reference
│   ├── ue5/
│   ├── threejs/
│   ├── blender/
│   └── design/
└── scripts/
    ├── download-model.sh   # Pull GGUF models from HuggingFace (--list for options)
    ├── build-llamacpp.sh   # Build llama.cpp from source with CUDA
    ├── start-llamacpp.sh   # Launch server with auto-tuned GPU settings
    └── create-modelfile.sh # Convert GGUF → Ollama Modelfile
```

**Config with dual backend support** — each profile's config.yaml has a `backend` toggle:

```yaml
backend: llamacpp    # or 'ollama'

ollama:
  base_url: http://127.0.0.1:11434/v1
  model: hf.co/unsloth/Qwen3.6-35B-A3B-GGUF:UD-IQ2_XXS

llamacpp:
  base_url: http://127.0.0.1:8080/v1
  model_dir: ~/models/gguf
  model_file: Qwen3.6-35B-A3B-UD-IQ2_XXS.gguf
  server_binary: ~/llama.cpp/build/bin/llama-server
  num_gpu_layers: 999
  context_size: 16384
  flash_attention: true
  cache_type_k: bf16
  cache_type_v: bf16
  port: 8080
```

**Knowledge snapshots** — copy LLM-Wiki pages into the repo so the Windows machine has offline reference material. The agent loads skills at runtime; knowledge/ is for human reference or agent RAG.

**Sync workflow:**
- Mac is source of truth for knowledge updates
- `git push` from Mac, `git pull` on Windows, re-run `install.sh`
- Each machine has its own `.env` (never committed)

## Quick Setup Flow (8 Steps)

After creating the Windows account, run these in order:

```powershell
# 1. Python (download .exe → "Install for current user", check "Add to PATH")
# 2. Git (download portable .zip → extract to C:\Users\<account>\git\)

# 3. Clone your profiles repo
gh repo clone <owner>/<repo-name>
cd <repo-name>
copy .env.example .env
notepad .env  # fill in API keys

# 4. Install Hermes
cd ~
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
python -m venv venv
.\venv\Scripts\activate
pip install -e .

# 5. Run the profile installer
cd ~\<repo-name>

# Option A: Ollama (easy)
.\install.sh --setup-ollama

# Option B: llama.cpp (full control)
.\install.sh --setup-llamacpp

# 6. Start
# With Ollama:
ollama serve
# With llama.cpp:
.\scripts\start-llamacpp.sh ~/models/gguf/<model>/<file>.gguf

# 7. Launch Hermes
hermes --profile ue5-coder
```

## Local Inference: llama.cpp vs Ollama

Both wrap the same inference engine (llama.cpp). The difference is control vs convenience.

| | Ollama | llama.cpp |
|---|---|---|
| Setup | `winget install Ollama.Ollama` | git clone + cmake build |
| Model management | `ollama pull` handles everything | Manual GGUF download + paths |
| GPU layer control | Automatic (env vars) | Exact: `--n-gpu-layers 40` |
| KV cache control | Minimal | Full: `--cache-type-k bf16` |
| Flash attention | Hidden | `--flash-attention` flag |
| MTP speculative decoding | Not supported | `--spec-draft-n-max` |
| Context size | Approximate | Exact: `--ctx-size 16384` |

**Use Ollama when:** quick setup, don't need fine-tuning control, standard models.
**Use llama.cpp when:** aggressive quantization on constrained VRAM, need exact GPU layer offload, using Unsloth MTP models, debugging gibberish output (fix with bf16 cache).

For your GPU (12GB VRAM) with aggressive quants (UD-IQ2_XXS), llama.cpp's knobs matter — especially `--n-gpu-layers` for partial CPU offload and `--cache-type-k bf16 --cache-type-v bf16` to fix quality issues.

**llama.cpp server mode (replaces Ollama):**
```powershell
git clone https://github.com/ggml-org/llama.cpp
cmake llama.cpp -B llama.cpp/build -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j

./llama.cpp/build/bin/llama-server \
  -m path/to/model.gguf \
  --n-gpu-layers 999 \
  --ctx-size 16384 \
  --flash-attention \
  --cache-type-k bf16 \
  --cache-type-v bf16 \
  --port 8080
```

Then Hermes config uses `base_url: http://127.0.0.1:8080/v1` instead of Ollama's `11434`.

## Secrets in Private Repos

When storing profiles in a private GitHub repo, use `.env.example` + `.gitignore`:

```
repo/
├── .env.example    ← committed, has placeholder values
├── .gitignore      ← blocks .env from commit
└── .env            ← local only, has real keys
```

`.gitignore` must contain: `.env`, `.env.local`, `.env.*.local`

Each machine creates its own `.env` from the template. Safe to include API keys in a private repo's `.env` if you create dedicated keys for that machine.

## CPU Offloading

When the model doesn't fit fully in VRAM, layers spill to system RAM. This is handled transparently by Ollama/llama.cpp — Hermes doesn't know or care.

| Model | Quant | Size | Fits in 12GB? | With offload |
|-------|-------|------|---------------|--------------|
| Qwen3.6-35B-A3B | UD-IQ2_XXS | 10.8GB | ✅ Yes | Not needed |
| Qwen3.6-27B | Q3_K_M | 13.6GB | ❌ ~1.6GB over | ~1.6GB in RAM, barely slower |
| Qwen3.6-27B | Q4_K_M | 16.8GB | ❌ ~4.8GB over | ~5GB in RAM, noticeably slower |

With 32GB system RAM, CPU offload is viable. Rule of thumb: each 1GB offloaded costs ~2-3 tok/s.

## MCP Server Configuration

Windows profiles need MCP servers configured in each profile's `config.yaml` (profile isolation — the global config is NOT read). The most common MCP server for Windows is **Mnemosyne** (memory), but the pattern applies to any MCP server.

### Mnemosyne MCP Server

Mnemosyne has a built-in MCP server (`mnemosyne mcp`, stdio transport). This is the way to use Mnemosyne on Windows where it's not natively integrated like on Mac.

**Install on Windows:**
```powershell
pip install "mnemosyne-memory[mcp]"
```

The `[mcp]` extra pulls the MCP SDK dependencies. Without it, `mnemosyne mcp` fails with "MCP not installed".

**Add to each profile's config.yaml:**
```yaml
mcp_servers:
  mnemosyne:
    command: mnemosyne
    args: ["mcp"]
    enabled: true
    env:
      MNEMOSYNE_DB_PATH: "C:\\Users\\hermes-dev\\.hermes\\mnemosyne.db"
```

**Key details:**
- Uses stdio transport (default) — no port, no network exposure
- Each profile can share one DB or have its own (set different `MNEMOSYNE_DB_PATH` per profile)
- The `command` is `mnemosyne` (the CLI entry point), NOT a full path — it resolves via PATH in the venv
- Tools register as `mcp_mnemosyne_*` after Hermes restart

**Verify:**
```powershell
hermes mcp list                    # should show mnemosyne with ✓
hermes mcp test mnemosyne          # should show tools discovered
```

### Other MCP Servers

Same pattern — add to `mcp_servers` in profile config. Examples:

```yaml
mcp_servers:
  codegraph:
    command: codegraph
    args: ["serve", "--mcp"]
    enabled: true

  blender:
    command: uvx
    args: ["blender-mcp"]
    enabled: true
```

See `native-mcp` skill for full MCP client configuration reference.

## Plugin Configuration

Hermes plugins (pip packages with `hermes_agent.plugins` entry points) are enabled per-profile via the `plugins` section in `config.yaml`. This is separate from MCP servers.

### rtk-rewrite Plugin

Rewrites terminal commands through RTK for lower-context tool output. Requires two things:

1. **Pip package:** `pip install rtk-hermes`
2. **RTK binary in PATH:** The `rtk` CLI must be available. On Windows, check with `where rtk`.

**Add to each profile's config.yaml:**
```yaml
plugins:
  disabled: []
  enabled:
    - rtk-rewrite
```

**Config via env vars (optional):**
- `RTK_HERMES_MODE`: `rewrite` (default), `suggest`, or `off`
- `RTK_HERMES_TIMEOUT_MS`: per-rewrite timeout (default 2000)
- `RTK_HERMES_BACKENDS`: `local` (default), or comma-separated list

### Other Plugins

Same pattern. Common plugins for Windows profiles:
```yaml
plugins:
  disabled: []
  enabled:
    - rtk-rewrite
    - disk-cleanup
```

## Profile Config Completeness Checklist

Windows profiles often ship with SOUL.md + AGENTS.md + config.yaml but are missing critical sections. After cloning/pulling the windowshermes repo, verify each profile's config.yaml has:

- [ ] `backend` — `llamacpp` or `ollama`
- [ ] `llamacpp` or `ollama` section — model, base_url, server settings
- [ ] `skills` — category + paths to shared skills
- [ ] `inference` — temperature, top_p, max_tokens, etc.
- [ ] `mcp_servers` — at minimum Mnemosyne for memory
- [ ] `plugins` — at minimum `rtk-rewrite` if rtk is installed
- [ ] `description` — one-line profile purpose

**Common gap:** Profiles in the windowshermes repo (as of 2026-06-09) have NONE of the last two sections. Always add them when setting up a new Windows machine.

## Memory System

For game dev, set up a three-layer memory system (Mnemosyne + Fabric + Obsidian).
See `game-dev-memory-system` skill for full setup and conventions.

**Quick setup on Windows PC:**
```powershell
# Run the setup script from the skill
.\skills\game-dev\game-dev-memory-system\scripts\setup-game-dev-memory.ps1
```

**Memory layers:**
1. **Mnemosyne** — Hot facts (auto-injected every turn). On Windows, use MCP server mode (see MCP Server Configuration above).
2. **Fabric** — Decision history (ranked recall)
3. **Obsidian** — Knowledge wiki (file tools)

## Pitfalls

- **UE5 admin requirement:** Epic Games Launcher needs admin. Install once from main account, run from hermes-dev.
- **Node.js .msi vs .zip:** The .msi installer requires admin. Always use .zip for per-user installs.
- **Python PATH:** "Install for current user" option is easy to miss — it's a small checkbox during setup.
- **Windows Defender:** First run of Hermes may be slow as Defender scans Python/Node. Add exclusion for `C:\Users\hermes-dev\` to speed things up.
- **Long paths:** Windows has a 260-char path limit by default. Enable long paths in registry (requires admin once) or keep project directories short.
- **GPU in browser:** Three.js WebGL/WebGPU uses whatever GPU the browser has access to. Chrome/Edge on Windows will use the discrete GPU by default. No special config needed.
- **Port conflicts:** If running Hermes on both Mac and Windows simultaneously, they're different machines so no conflict. But if gateway is exposed, only one should be the public endpoint.
- **Empty profile skills dir:** Profiles often ship with SOUL.md + AGENTS.md + config.yaml but forget the skills directory. After cloning/pulling the windowshermes repo, always verify `ls profiles/ue5-coder/skills/` is non-empty. If empty, copy required skills from senna's profile on the Mac and push.
- **Missing mcp_servers/plugins in profiles:** The windowshermes repo profiles (as of 2026-06-09) have NO `mcp_servers` or `plugins` sections. Every profile needs both. Without `mcp_servers`, Mnemosyne memory doesn't work. Without `plugins`, rtk-rewrite and other plugins are silent no-ops. Always add these sections when setting up a new Windows machine or creating new profiles.
- **Mnemosyne MCP vs native:** On Mac, Mnemosyne is a native Hermes plugin (tools injected directly). On Windows, use the MCP server mode (`mnemosyne mcp`) instead. The tools register as `mcp_mnemosyne_*` (prefixed) rather than bare `mnemosyne_*`. Same functionality, different integration path.
- **rtk binary separate from rtk-hermes:** `pip install rtk-hermes` installs the Hermes plugin. The `rtk` CLI binary is a separate install. If `where rtk` fails, the plugin silently passes commands through unrewritten (fail-open). Always verify both are installed.
- **MCP `[mcp]` extra:** `pip install mnemosyne-memory` alone does NOT install MCP deps. Use `pip install "mnemosyne-memory[mcp]"` or `mnemosyne mcp` will fail with "MCP not installed".
- **Ollama auto-start:** Ollama installs as a Windows service and starts on boot. Verify with `ollama list`. If not running: `ollama serve`.
- **CUDA 13.2:** Do NOT use CUDA 13.2 with Unsloth GGUFs — produces gibberish output. Use CUDA 12.x.
- **Model file naming:** Unsloth GGUF filenames include quantization suffix (e.g., `UD-IQ2_XXS`). When pulling via Ollama, use the full `hf.co/unsloth/<model>-GGUF:<tag>` format.
