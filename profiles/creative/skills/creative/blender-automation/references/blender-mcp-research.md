# Blender MCP Research Notes

Session date: 2026-05-16
Source: Research session investigating Blender MCP integration options for Hermes

## Ecosystem Overview

Three tiers of Blender + AI integration exist:

### Tier 1: Open-Source MCP Servers (DIY)

| Project | Repo | Stars | License | Blender Req | Notes |
|---------|------|-------|---------|-------------|-------|
| ahujasid/blender-mcp | [GitHub](https://github.com/ahujasid/blender-mcp) | 21.7k | MIT | 3.0+ | Most mature, uv-based, actively maintained |
| blender.org MCP Server | [blender.org/lab](https://www.blender.org/lab/mcp-server/) | — | — | 5.1+ | Official, part of Blender Lab, still pre-release |

### Tier 2: Commercial Wrappers

| Product | Based On | Pricing | Differentiator |
|---------|----------|---------|----------------|
| 3D-Agent | ahujasid/blender-mcp | Free tier + paid | One-click install, 24/7 support, multi-model orchestration |

### Tier 3: Anthropic "Claude for Creative Work"

Anthropic joined the Blender Development Fund and ships an official Blender MCP connector as part of their 9-tool "Claude for Creative Work" suite. The connector is built as an open MCP server maintained by the Blender team itself.

### Other Creative Tool MCP Connectors (for reference)

From the "Claude for Creative Work" announcement: Blender (flagship), Adobe Creative Cloud, Affinity by Canva, Ableton, Autodesk Fusion, SketchUp, Resolume, Splice.

## Hermes Integration Path

Hermes native MCP client connects to any MCP server via `mcp_servers` config:

```yaml
mcp_servers:
  blender:
    command: "uvx"
    args: ["blender-mcp"]
```

Tools are prefixed `mcp_blender_*` and available in all platforms automatically.

### Existing Hermes MCP Setup

Currently configured MCP servers (from `hermes mcp list`):
- `iknowkungfu` — ✓ enabled (skill registry)

## 3D-Agent Architecture (Key Learnings)

The [DevTalk post](https://devtalk.blender.org/t/3d-agent-blender-ai-assistant/44260) by Guilherme (3D-Agent developer) documented their multi-agent system:

**Three specialized models working together:**
- **Gemini** → Vision (viewport verification, scene understanding)
- **Claude** → Reasoning & planning (break into stages, decide build order)
- **GPT** → Code generation (write bpy calls)

**Orchestration stack:**
- LangGraph for the perceive → reason → act → verify loop
- Custom TCP socket (not HTTP) for responsiveness
- MCP for the tool interface layer
- DSPy to train system prompts against Blender API docs
- RAG over Blender Python API docs for code generation

**Critical finding:** The verification step (viewport screenshot → vision model → self-correction) is the single biggest quality improvement. Without it, geometry degenerates after 3-4 steps.

## Pricing Considerations

This user is cost-conscious. Options:
- **ahujasid/blender-mcp**: Free (MIT), self-hosted — no API costs beyond Hermes inference
- **3D-Agent**: Free tier available, paid plans for advanced features
- **Hyper3D Rodin AI models**: Free trial (limited daily), then paid keys from hyper3d.ai + fal.ai

## Prompt Examples That Work

From community testing:
- *"Create a low poly scene in a dungeon, with a dragon guarding a pot of gold"*
- *"Create a beach vibe using HDRIs, textures, and models like rocks and vegetation from Poly Haven"*
- *"Give a reference image and create a Blender scene out of it"*
- *"Generate a 3D model of a garden gnome through Hyper3D"*
- *"Get information about the current scene, and make a threejs sketch from it"*
- *"Make this car red and metallic"*
- *"Create a sphere and place it above the cube"*
- *"Make the lighting like a studio"*
- *"Point the camera at the scene, and make it isometric"*

## Machine Readiness

User's machine: MacBookPro15,1 (2018 Intel i7-9750H, 16GB, Radeon Pro 555X 4GB)
- `uv` is installed (v0.11.7)
- Blender is NOT installed
- Hermes venv at `~/.hermes/hermes-agent/venv/`
- Profile isolation: senna profile, config at `~/.hermes/profiles/senna/config.yaml`
