# docs/skills — web front-end of the Skills Hub

URL: https://hermes-agent.nousresearch.com/docs/skills
Docusaurus page rendering the same hub index the CLI browses. First screen =
filter-counts bar + built-in catalog; the rest is paginated behind "Show more".

## Counts bar (structure stable, numbers drift)

All | Built-in | Optional | Anthropic | OpenAI | HuggingFace | NVIDIA |
skills.sh | ClawHub | browse.sh | LobeHub | gstack

Observed 2026-08-03: All 90,683 · Built-in 71 · Optional 111 · Anthropic 17 ·
OpenAI 44 · HuggingFace 25 · NVIDIA 299 · skills.sh 19,967 · ClawHub 69,150 ·
browse.sh 440 · LobeHub 505 · gstack 53

## Built-in catalog by category (first screen, ~60 of 71 shown)

- apple (macOS): apple-notes, apple-reminders, findmy, imessage
- ai-agents: claude-code, codex, computer-use, hermes-agent, opencode
- creative: architecture-diagram, ascii-art, ascii-video, baoyu-infographic,
  claude-design, comfyui, design-md, excalidraw, humanizer, manim-video, p5js,
  popular-web-designs, pretext, sketch, songwriting-and-ai-music,
  touchdesigner-mcp
- github: codebase-inspection, github-auth, github-code-review, github-issues,
  github-pr-workflow, github-repo-management
- media: gif-search, songsee, youtube-content
- mlops: evaluating-llms-harness, huggingface-hub, llama-cpp, serving-llms-vllm,
  weights-and-biases
- productivity: airtable, docx, google-workspace, maps, nano-pdf, notion,
  ocr-and-documents, pdf, powerpoint, teams-meeting-pipeline, xlsx
- research: arxiv, blogwatcher, grounded-citations, llm-wiki, polymarket,
  research-paper-writing
- smart-home: openhue
- social-media: xurl
- software-dev: dogfood, hermes-agent-skill-authoring (+ more behind Show more)

## Creative-writing & image-gen hub searches — evaluation notes (2026-08-03)

Framework caveat applied: most community results are written for Clawdbot /
OpenClaw / Claude Code / Codex and need adaptation or skipping.

Writing track:
- `Novel` (clawhub, BytesAgain) — offline CLI for novel data: chapters,
  characters, plot timelines; JSON/CSV export. Framework-light, closest to
  Hermes-native. A data manager, not a writer.
- `novel-architect` (skills.sh, junaid18183) — Chinese webnovel (爽文) FBS
  pipeline: direction → outline → per-chapter → QC gate. zh-CN; process
  inspiration only.
- `novel-revision`, `novel-creator`, `novel-writer`, `novel-game` (skills.sh) —
  thin repo indexes, inspect before use.
- Creative Writing workshop for AI agents (Roni Bandini) — autonomous skill
  needing an external workshop server + token lifecycle; skip.
- Peer Review (clawhub, multi-model review via Ollama) — other-framework
  idioms; adapt or skip.

User's existing stack already covers fiction: book-writer profile runs
narrative v2 + narrative-revisor + book-pipeline.

Image-gen track:
- `comfyui` (clawhub) — local ComfyUI HTTP API runner (127.0.0.1:8188), ships
  default workflow JSON in assets; real value only if user runs local ComfyUI.
  Hermes also ships a built-in comfyui (creative category).
- `comfyui-pro` (clawhub) — CN, 文生图/图生图/ControlNet + auto server mgmt.
- `midjourney` (clawhub) — MJ Discord bot; needs Discord app + paid sub;
  Discord-only, no API. Skip unless user pays for MJ.
- `imagegen` (skills.sh/openai, github/openai — trusted) — OpenAI's skill but
  written for Codex tool model; adapt.
- `generate-image` (browse.sh/Perchance) — free, no key, quick-and-dirty.
- Illustration-adjacent: children-book-illustration-generator,
  illustration-style (owl-listener), long-article-illustration (CN),
  scrapbook-illustrator — cover-art style guidance.

User's existing stack covers image gen: hermes-image-studio plugin
(FLUX 2 Klein via FAL) in creative + senna profiles; FLUX 3 video tools in
session. Hub adds local-ComfyUI / Midjourney as alternative backends, and
cover-art style guides as process skills.

## Four official skills — deep-dive evaluations (2026-08-03)

From the official-optional gap list (see fleet-skill-rollout
references/hub-gap-analysis.md), user asked about four:

- `kanban-video-orchestrator` (official/creative, v1.0.0, authors SHL0MS +
  alt-glitch) — meta-pipeline, renders nothing itself. Wraps any video request
  in a Hermes Kanban pipeline: scope → design team (roles+tools) → generate
  setup script creating profiles/workspace/kanban task → hand off to a
  "director" profile → monitor stalls. Rendering inside kanban via
  ascii-video, manim-video, p5js, comfyui, touchdesigner-mcp, blender-mcp,
  songwriting-and-ai-music, heartmula, or PIL+ffmpeg. Credits
  NousResearch/kanban-video-pipeline. NOT for: single continuous procedural
  videos, one-shot conversions (ffmpeg), static images/GIFs/audio.
  Fit: strong — matches user's multi-agent kanban fleet pattern; slot on
  media/creative with FLUX 3 as render stage.
- `stable-diffusion-image-generation` (official/mlops/stable-diffusion) —
  text-to-image, inpainting, img2img via diffusers (tags: Diffusers,
  Multimodal, Computer Vision). Inspect shows header only (no body preview).
  Fit: overlaps existing FLUX/FAL stack; useful only as local SDXL/SD3
  fallback (Windows your GPU / local Mac).
- `neuroskill-bci` (official/health, author Hermes Agent + Nous Research) —
  reads real-time cognitive/emotional state from a NeuroSkill instance:
  focus, relaxation, mood, cognitive load, drowsiness, HR, HRV, sleep
  staging, 40+ EXG scores. Requires BCI wearable (Muse 2/S or OpenBCI) +
  NeuroSkill desktop app (WebSocket/HTTP API). References: metrics.md,
  protocols.md, api.md. Research-use-only, not FDA/CE cleared.
  Fit: no-op unless user owns a Muse/OpenBCI.
- `one-three-one-rule` (official/communication, author Willard Moore) —
  decision format: 1 problem statement, 3 options with pros/cons, 1
  recommendation + definition of done + impl plan. Triggers: "give me
  options", "1-3-1", architecture/tooling/migration choices. NOT for
  obvious-answer, debugging, already-decided tasks.
  Fit: cheap process win for senna — formalizes user's batched
  options/review rhythm ("1-8: yes/no/more").
