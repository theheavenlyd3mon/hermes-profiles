---
name: blender-automation
description: "Connect Blender to Hermes via MCP — 3D modeling, scene manipulation, batch operations, and asset generation through natural language."
version: 1.1.0
author: Senna
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [blender, 3d, mcp, creative, modeling, animation]
    related_skills: [native-mcp, touchdesigner-mcp]
---

# Blender Automation via MCP

Connect a running Blender instance to Hermes via the Model Context Protocol, enabling natural-language 3D modeling, scene manipulation, material editing, and asset generation.

## When to Use

Use this whenever the user wants to:
- Create, modify, or delete 3D objects by describing them in plain language
- Inspect and analyze Blender scenes (poly counts, materials, modifier stacks)
- Apply batch operations across many objects (rename, recolor, reposition)
- Generate Blender add-ons, operators, and panels without writing Python
- Set up rendering pipelines, lighting, and cameras conversationally
- Download and apply Poly Haven HDRIs / textures programmatically
- Generate AI 3D models via Hyper3D Rodin integration
- **Advise on the broader AI+Blender landscape** — texture generation tools, 3D model generation (Hyper3D, Meshy, Tripo, Hunyuan3D), AI animation (AnimateDiff, Rokoko mocap), and concept art pipelines (ControlNet). See `references/ai-blender-ecosystem.md` for a condensed reference.
- **Assess hardware viability** — proactively note Intel Mac limits (no GPU for local diffusion, cloud workarounds needed for texture gen and AI animation, Eevee preferred over Cycles for rendering speed)

## Architecture Overview

```
Hermes Agent ──stdio MCP──→ uvx blender-mcp ──TCP socket 9876──→ Blender Addon
                                                                      │
                                                                  Blender (bpy API)
```

- **MCP Server** (`uvx blender-mcp`): Bridges Hermes ↔ Blender. Hermes's native MCP client spawns this as a subprocess.
- **Blender Addon**: Runs inside Blender as a socket server on port 9876. Receives commands from the MCP server and executes them via `bpy`.
- **Tool Naming**: All tools appear as `mcp_blender_*` in Hermes (e.g., `mcp_blender_get_scene_info`, `mcp_blender_create_object`).

## Two Implementations

### 1. Community: ahujasid/blender-mcp (Recommended for now)
- **Repo**: [github.com/ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) — MIT, 22.6k stars (Jun 2026)
- **Requirements**: Blender 3.0+, Python 3.10+, `uv`
- **Features**: Scene inspection, object CRUD, materials, arbitrary bpy execution, viewport screenshots, Poly Haven assets, Hyper3D AI models, Sketchfab search
- **Install**: `uvx blender-mcp` (MCP server), addon from repo (Blender addon)
- **Ecosystem**: 107+ repos on GitHub matching "blender MCP server". MCP is the de facto standard protocol — ecosystem has converged. Multi-LLM support (Claude, ChatGPT, Gemini, Ollama) is table stakes.

### 2. Official: blender.org MCP Server
- **Source**: [blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/)
- **Requirements**: Blender **5.1+** (not yet released)
- Built by Blender dev team as part of their lab program
- Pair with any MCP client (Llama.cpp, Claude, etc.)

### 3. Notable Alternatives

| Project | Stars | Differentiator |
|---------|-------|---------------|
| **ai-forge-mcp** | 67 | 565 tools across 16 MCP servers. Full AAA pipeline: Blender + Substance + Maya + Houdini |
| **blender-mcp-pro** | 20 | 100+ tools: shader nodes, geometry nodes, animation keyframes |
| **blend-ai** | 96 | "More intuitive" alternative MCP server |
| **blender-ai-mcp** | 37 | Goal-first routing, deterministic verification, vision-assisted modeling |
| **blender-mcp-n8n** | 41 | 45+ tools integrated with n8n workflow automation |
| **Vibe3DScene** | 87 | "Create 3D scenes with words anywhere" — LangGraph + Blender MCP |

### 4. Emerging Pattern: Agent Skills for Blender
- **cc-blender-skill** — 10 chain-loadable skills (modeling, materials, lighting, rendering, animation, export, wireframe-to-3d). Validated on 6 scene classes for Blender 5.x
- **blendops** — AI-native workflow pack: Blender MCP + Claude + Three.js/React Three Fiber

### 5. Moonlake AI — Computer-Use Agent (Not an Addon)
- **Approach**: Operates Blender via screen interaction (like Anthropic's computer use), NOT a Blender addon/plugin
- **Architecture**: Two-model system — multimodal reasoning model (causality, physics, persistence) + RIE neural rendering model (style transfer)
- **Philosophy**: "Structure, not scale" — language + symbolic representations are 5 orders of magnitude more data-efficient than pure pixel/video diffusion
- **Capability**: Iterative, long-horizon refinement. Builds articulated assets, physics-validated scenes, complex environments. Can learn from expert demos.
- **Status**: Beta since Feb 2026, $15/mo. Partners with $8T+ combined market cap.
- **GitHub**: github.com/MoonlakeAI — content-agents (VLM-powered USD workflows), Nova3D (Prompt-to-Code targeting Blender Python API)
- **UE5 relevance**: Explicitly mentions Unreal Engine compatibility in asset management pipeline

## Setup

### Prerequisites

```bash
# Ensure uv is installed
which uv || brew install uv   # macOS
# or: https://docs.astral.sh/uv/getting-started/installation/
```

### Step 1: Install Blender
- Download from [blender.org](https://www.blender.org/download/) or `brew install --cask blender`
- Requires 3.0+ for ahujasid/blender-mcp

### Step 2: Install the Blender Addon
1. Download `addon.py` from the [ahujasid/blender-mcp repo root](https://github.com/ahujasid/blender-mcp/blob/main/addon.py)
2. Open Blender → **Edit > Preferences > Add-ons**
3. Click **Install…** and select `addon.py`
4. Enable **"Interface: Blender MCP"**
5. In the 3D View sidebar (press `N`), switch to the **BlenderMCP** tab
6. (Optional) Enable Poly Haven checkbox for HDRI/texture assets
7. Click **"Connect to Claude"** — this starts the socket server on port 9876

### Step 3: Configure Hermes

Add to your Hermes config (`~/.hermes/profiles/senna/config.yaml` for profile-isolated setups):

```yaml
mcp_servers:
  blender:
    command: "uvx"
    args: ["blender-mcp"]
```

Then restart Hermes. Tools are auto-discovered with the `mcp_blender_*` prefix.

> ⚠️ **Only run one MCP client at a time.** If another app (Cursor, Claude Desktop) also has blender-mcp configured, stop it first — only one uvx process can connect to the Blender addon.

### Step 4: Verify

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
hermes mcp list
# → blender should appear with ✓ enabled
hermes mcp test blender
# → Should show ✓ Connected and ✓ Tools discovered: N
```

## Using Blender Tools from Hermes

Once connected, you can ask Hermes to do things like:

- *"Create a low-poly dungeon scene with a dragon guarding treasure"*
- *"Inspect the current scene and list the top 5 highest-poly objects"*
- *"Make this car red and metallic, then set up studio lighting"*
- *"Rename all objects to use consistent naming: `OBJ-material-number`"*
- *"Take a viewport screenshot and analyze the topology"*
- *"Generate a 3D model of a garden gnome via Hyper3D"*
- *"Create a sphere above the cube, rotate the cube 45°, and point the camera at the scene"*
- *"Apply subdivision surface to all selected objects with 2 levels"*

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BLENDER_HOST` | `localhost` | Host for Blender socket server |
| `BLENDER_PORT` | `9876` | Port for Blender socket server |

Set these in the `env` block of the MCP config if customizing.

## Critical Architecture Lessons (from 3D-Agent)

Research on multi-agent Blender systems revealed several hard-won lessons:

### 1. Vision Feedback Loop is Mandatory
After each operation, take a viewport screenshot and have the agent verify it before the next step. Without this, geometry degenerates into "soup" after 3-4 operations. The agent should also learn to change viewport perspective when needed.

### 2. Separate Reasoning from Code Generation
One model decides *what* to do (reasoning/planning), another generates *how* in bpy (code execution). This avoids the single-model drift problem.

### 3. DSPy for Prompt Optimization
Train system prompts against Blender API docs and expected outputs using DSPy — far more consistent than hand-tuning.

### 4. Math-Heavy Operations Are Weak
Precise geometric calculations (lattice structures, curve math, symmetry) may need a dedicated pass. Not yet reliable from raw LLM prompting.

### 5. bpy API Docs Are Insufficient Alone
RAG over docs + examples gets only ~50% coverage. Supplement with example-heavy prompts and iterative refinement.

### 6. TCP Socket > HTTP for Blender Communication
The addon uses a socket directly rather than HTTP. This matters for the 30+ back-and-forth operations per task — responsiveness is critical.

## Capabilities (ahujasid/blender-mcp v1.5.5)

| Category | Operations |
|----------|-----------|
| Scene Inspection | Get object lists, poly counts, material assignments, modifier stacks, shader node graphs |
| Object Manipulation | Create/delete/modify shapes, transform, group, parent |
| Materials | Apply/modify materials, colors, textures |
| Code Execution | Run arbitrary `bpy` Python code |
| Viewport | Take screenshots of the current view |
| Assets (Poly Haven) | Search/download HDRIs, textures, models via their API |
| Assets (Sketchfab) | Search and download Sketchfab models |
| AI Models (Hyper3D Rodin) | Generate AI 3D models from text prompts |
| AI Models (Hunyuan3D) | AI model generation (v1.5.5+) |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Connection refused | Blender addon not running or not connected | Open Blender, click "Connect to Claude" in BlenderMCP tab |
| Tools not appearing | Wrong config path (profile isolation) | `hermes mcp list` — if empty, edit the profile's config.yaml |
| Timeout errors | Request too complex | Break into smaller steps or simplify the prompt |
| First command fails | Cold-start delay | Retry — subsequent commands work faster |
| "Command not found" | uv not installed or not on PATH | `brew install uv` or check PATH |
| Multiple instances conflict | Another app also running blender-mcp | Stop Cursor/Claude Desktop instance, only run one |

## References

- `references/blender-mcp-research.md` — Detailed session notes: provider comparison, architecture diagrams, community resources.
- `references/ai-blender-ecosystem.md` — Broader AI+Blender landscape reference: texture gen tools, 3D model generators, AI animation, concept art pipelines, Intel Mac hardware reality table.
