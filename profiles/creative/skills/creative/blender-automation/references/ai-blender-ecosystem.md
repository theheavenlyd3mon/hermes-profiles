# AI / Blender Ecosystem Reference

> Condensed reference for the broader AI tools landscape around Blender.
> Use when the user asks about AI texture generation, 3D model generation, AI animation,
> or concept art pipelining — anything outside the MCP automation scope.
> Full detail: wiki page [[ai-blender-workflows]] in the LLM Wiki.

---

## AI Texture Generation

| Tool | Type | Works on Intel Mac? |
|------|------|-------------------|
| **Dream Textures** (carson-katri) | Blender addon, local SD | ❌ No (needs GPU) |
| **StableGen** (sakalond) | Blender addon + ComfyUI bridge | ⚠️ Cloud ComfyUI only |
| **ComfyUI-BlenderAI-node** | Bidirectional Blender↔ComfyUI | ⚠️ Cloud ComfyUI only |
| **PBRgen** | Cloud PBR map generation | ✅ Browser |
| **AI Material Factory** | Cloud text→PBR material | ✅ Browser |
| **AITextured** | Cloud image→PBR tile | ✅ Browser |

**Intel Mac path:** Use cloud PBR generators or generate textures in Midjourney/Flux, import to Blender's shader editor via image texture nodes.

## AI 3D Model Generation

**Hierarchy (2026):**
1. **Hyper3D.ai (Rodin Gen-2)** — Free to generate, pay on download. Clean quad topology, auto PBR textures, T/A-pose, 18K/50K quads. Integrated into ahujasid/blender-mcp.
2. **Meshy AI** — Fastest iteration (8 previews/60s). Blender plugin. $14.50/mo.
3. **Tripo AI** — Game-ready output, auto-rigging. $11.94/mo.
4. **Hunyuan3D 2.5** — Best open-source. Free but needs GPU.
5. **TRELLIS 2** — Gaussian Splatting for previz. Free web app.
6. **SF3D** — Sub-second prototypes via fal.ai. GLB only.

**Pattern:** AI generators produce starting points only. Always: generate → import to Blender → retopo → UV fix → texture polish → refine.

## AI Retopology / Sculpting

No mature AI sculpting tool exists in Blender. Available:
- **Quad Remesher** ($100) — gold standard for automatic retopo
- **QRemeshify** — free Blender addon
- **Instant Meshes** — free, open-source
- **Blender Self-Quadratify** — native filter, basic but improving

## AI Animation

**AnimateDiff:** Transform Blender renders into stylized AI video via ComfyUI. GPU-heavy — cloud only on Intel Mac.

**AI Motion Capture (all browser-based, work on Intel Mac):**
- **Rokoko Vision** — free tier, FBV export to Blender
- **DeepMotion** — free tier, FBX to Blender
- **Plask** — freemium, FBX/GLB export

**Workflow:** Record yourself acting → upload → download FBX → import to Blender → retarget to character rig.

## Concept Art Pipeline (Blender → ControlNet → SD)

The most powerful AI concept art workflow:
1. Blockout in Blender
2. Render depth map, normal pass, or edge map
3. Use as ControlNet inputs in Stable Diffusion / Midjourney / Flux
4. Generate 2D concept art with perfect perspective
5. Iterate: adjust Blender scene → re-render passes → regenerate

## Blender MCP Server Landscape (Jun 2026)

**107+ repos** on GitHub matching "blender MCP server". MCP is the de facto standard protocol.

### Dominant: ahujasid/blender-mcp (22.6k ★)
- Socket-based bridge: Blender addon → MCP server → any LLM
- ~20 core tools: object CRUD, materials, lighting, arbitrary Python execution, Poly Haven, Sketchfab, Hyper3D Rodin, Hunyuan3D
- Client support: Claude Desktop, Claude Code, Cursor, VSCode (Cline/Roo), ChatGPT, Gemini CLI, Ollama, OpenCode
- Install: `uvx blender-mcp`

### Notable Alternatives

| Project | Stars | Differentiator |
|---------|-------|---------------|
| **ai-forge-mcp** | 67 | 565 tools across 16 MCP servers. Full AAA pipeline: Blender + Substance + Maya + Houdini |
| **blend-ai** | 96 | "More intuitive" alternative MCP server |
| **Vibe3DScene** | 87 | "Create 3D scenes with words anywhere" — LangGraph + Blender MCP |
| **blender-mcp-n8n** | 41 | 45+ tools integrated with n8n workflow automation |
| **blender-ai-mcp** | 37 | Goal-first routing, deterministic verification, vision-assisted modeling |
| **blender-mcp-pro** | 20 | 100+ tools: shader nodes, geometry nodes, animation keyframes |

### Emerging: Agent Skills (Not Just API Wrappers)
- **cc-blender-skill** — 10 chain-loadable skills (modeling, materials, lighting, rendering, animation, export, wireframe-to-3d). Validated on 6 scene classes for Blender 5.x
- **blendops** — AI-native workflow pack: Blender MCP + Claude + Three.js/React Three Fiber
- **GenesisCore** — One-click BlenderMCP install supporting DeepSeek, Claude, etc.

### Niche Integrations
- **Bambu Lab 3D Printer MCP** — Blender → STL → BambuStudio slicing → direct printer control
- **PLATEAU City Data MCP** — 3D city data (CityGML) as Blender scene-editing tools
- **Flint** — macOS Blender MCP API server with visionOS connectivity

### Key Patterns
1. **MCP is the standard** — ecosystem has converged on this as the bridge layer
2. **Multi-LLM support is table stakes** — nobody locks to one provider
3. **Tool count is the differentiator** — blender-mcp ~20, blender-mcp-pro 100+, ai-forge-mcp 565
4. **Python execution is the escape hatch** — every MCP server exposes `bpy` execution, making the full Blender API available to the LLM
5. **Vision feedback loop is critical** — take a viewport screenshot after each operation and verify. Without this, geometry degenerates after 3-4 operations
6. **No major commercial addon** — almost entirely open-source community work

## Moonlake AI — Computer-Use Agent for Blender

**What:** A computer-use agent that drives Blender via screen interaction (like Anthropic's computer use). NOT a Blender addon/plugin.

**Architecture:** Two-model system:
1. **Multimodal Reasoning Model** — handles causality, physics, persistence, symbolic logic. Uses game engines as "cognitive tools."
2. **RIE (Neural Rendering Model)** — takes persistent world representations and skins them into any visual style.

**Philosophy:** "Structure, not scale." Language + symbolic representations are 5 orders of magnitude more data-efficient than pure pixel/video diffusion. Chris Manning argues language is humanity's unique cognitive tool.

**Capabilities:**
- Iterative, long-horizon refinement (not one-shot)
- Multi-layer reward: scene quality → reference consistency → structural correctness via code verification
- Can learn from expert demos and generalize into reusable procedures
- Builds articulated assets, physics-validated scenes, complex environments
- Builds complete playable games autonomously in 10 phases (assets → physics → layout → game logic → edge cases → audio → IK → polish)

**GitHub (github.com/MoonlakeAI):**
- **content-agents** — VLM-powered agents for USD-based 3D workflows (material assignment, physics classification, texture generation). Supports NIM, OpenAI, Anthropic, Gemini backends.
- **Nova3D** — Prompt-to-Code targeting Blender's Python API. Model-agnostic (Claude, GPT-4o, Gemini).

**Status:** Beta since Feb 2026, $15/mo. 10K+ waitlist. Partners with $8T+ combined market cap. Founded by Fan-Yun Sun (Stanford AI Lab, ex-NVIDIA) and Sharon Lee. $28M seed from NVentures, AIX Ventures, Threshold.

**UE5 relevance:** Explicitly mentions Unreal Engine compatibility in asset management pipeline. Worth watching for Blender→UE5 asset pipeline.

## Hardware Reality (Mac MBP 2018 Intel)

| Task | Viable? | Best Approach |
|------|---------|--------------|
| Blender MCP | ✅ Yes | MCP server + addon |
| AI texture gen | ⚠️ Cloud only | Cloud PBR / Midjourney |
| AI 3D model gen | ✅ Cloud | Hyper3D/Meshy web UIs |
| AI retopo | ✅ Yes | Quad Remesher, no GPU needed |
| AI animation local | ❌ No | Cloud ComfyUI |
| AI motion capture | ✅ Yes | Rokoko/DeepMotion (browser) |
| Cycles rendering | ⚠️ Slow | CPU 64-256 samples + denoising |
| Eevee real-time | ✅ Yes | Best option, rapid feedback |
