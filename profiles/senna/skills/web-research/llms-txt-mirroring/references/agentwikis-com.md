# agentwikis.com — catalog snapshot (2026-08-03)

Maintained knowledge bases for humans and AI agents. Agents read them as plain
Markdown via llms.txt; humans browse HTML at /wiki/<slug>. All public wikis are
free (Pro $9.99/mo adds gated "XL" pages; Project tier $500+$100/mo lets a
product claim its wiki).

## Local mirror
Full pull (2026-08-03) lives at **~/agentwikis/** — 1,479 pages,
9.3 MB, 51 wikis:
- `catalog-llms.txt` — master llms.txt (every wiki + every page URL)
- `all-pages.txt` — extracted /raw/ paths
- `raw/<wiki>/...` — per-wiki Markdown (README.md, wiki/index.md, concepts/, syntheses/, summaries/, entities/)
- `pull.sh` — the original working fetch script

Per-wiki llms.txt also exists: `https://agentwikis.com/wiki/<slug>/llms.txt`
(use when only one wiki is needed; the raw URLs it lists download the same).

## Catalog (51 wikis, page counts)
- AI Agents: hermes 117, claude-code 34, codex 37, open-claw 21, pi-agent 20,
  grok-build 16, gbrain 21, herdr 15, buzz 14, mcp 30, agent-workflows 15,
  matt-pocock-skills 31
- Inference & serving: llama-cpp 63, vllm 19, lmstudio 23, unsloth 16, ollama 20,
  huggingface 19, dgx-spark 21
- Image & video: comfyui 31, hyperframes 242 (largest), remotion 31,
  stable-diffusion 19, blender 29
- Blockchain & DeFi: hyperliquid 18, solana 16, base 19, uniswap 20, jupiter 20, anchor 19
- Trading & markets: trading 44, stock-options 16, perpetual-futures 18, bullpen 19, polymarket 22
- Marketing & ads: google-ads 27, meta-ads 25, lead-generation 21
- Dev tools: github 21, vercel 20, vscode 21, telegram 19, godot 19, postgresql 19,
  redis 20, tailscale 21, docker 20, shopify 23, unreal 25, unity 20, threejs 23

## Key wikis — scope notes (from index.md frontmatter)
- **hermes** — v0.18.2 / v2026.7.7.2 (2026-07-17). 24 summaries (8 video
  transcripts incl. "did Hermes kill OpenClaw", 12 release notes v0.6.0→v0.18.0),
  20 concepts (CLI, config layout, skills, cron, MCP, memory, gateway, subagents,
  MoA, GEPA self-improvement loop), 63 entities (platforms, providers, backends,
  memory providers, community projects), 6 syntheses (vs-openclaw, local-stack
  playbook, memory-providers-compared, deployment-backends-compared, onchain
  stack recipe, cron troubleshooting).
- **llama-cpp** — b9859 (2026-07-01). Official docs tier (high confidence) +
  community tier (medium). llama-cli/quantize/imatrix/bench, GBNF, function
  calling, embeddings, multimodal mtmd, server API, quant tables.
- **comfyui** — v0.28.0 (2026-07-24). 177 sources: node-dev deep dive
  (LiteGraph, lazy eval, extension APIs), manager V3.38 config change, server
  internals + headless, cloud workflows/billing, update-breakage casebook.
- **hyperframes** — 242 pages (2026-07-17), all high confidence, official source.
  README.md is EMPTY — content is in wiki/. Authoring model (data-attributes,
  timeline), catalog system, deterministic rendering, frame adapters, GSAP,
  figma import, SDK, rendering pipeline, deployment/performance (4K/HDR).
- **stable-diffusion** — diffusers v0.39.0 spine (2026-07-18). SD1.5/SDXL/SD3.x
  families, txt2img/img2img/inpaint, ControlNet/T2I/IP-Adapter, schedulers,
  LoRA inference, optimization, fine-tuning methods, model/pipeline picker,
  troubleshooting (OOM, black images, seeds).
- **tailscale** — 2026-07-07. WireGuard mesh, control/data plane, STUN/DERP,
  subnet routers, exit nodes, MagicDNS, ACLs vs grants, Tailnet Lock, API.
- **unreal** — 5.8 (2026-07-17). C++ + reflection (UCLASS/UPROPERTY/UFUNCTION),
  actors/components, Blueprints + communication, gameplay framework, AI, input,
  physics, rendering (Lumen/Nanite/materials/lighting), content pipeline.
  Developer surface only — not art tutorials or full API reference.
- **threejs** — official docs snapshot 2026-08-02. Scene graph, cameras/
  OrbitControls, geometry, materials/textures, lighting/shadows, renderer,
  glTF loading, animation, raycasting, post-processing, performance. XL adds
  ~90-class API refs (gated).
- **vercel** — 2026-07-18. Deployments, builds/cache, Functions (serverless/
  edge), framework support (Next.js/ISR), git integration, preview/skew
  protection, env vars, caching/CDN, routing, vercel.json, domains, monorepos
  (Turborepo/Blob/Edge Config).

## Notes
- User's phrasing "the three dots" = Three.js; "SD" = Stable Diffusion.
- The user's stack overlap: hermes (this profile), unreal (UE5 Murim Souls +
  AgentUnreal), hyperframes/remotion (video tooling), tailscale (fleet), trading
  wikis (Oracle research), polymarket/hyperliquid (onchain trading interest).
