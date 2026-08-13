---
name: master-canvas
description: "Plan AI video pre-production with Master Canvas packages."
version: 1.0.0
author: creative profile
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [media, video, comfyui, ltx, veo, kling, preproduction, handoff]
---

# Master Canvas — AI Video Pre-Production Board

## When to Use

- User wants to concept an AI video project from a brief: scenes → shots → prompts → handoff package.
- User provides a Master Canvas ZIP / `project_manifest.json` and wants it inspected, extracted, planned for ComfyUI/LTX, or handed to Kling/Veo.
- Working with the Master Canvas desktop app, the Hermes plugin tools, or the MCP server.
- User wants scene/shot order preserved, prompts written per shot (lens, lighting, camera, action), or deliverables binned by scene.

Part of the Wasserman Filmmaker Suite (by Sam Wasserman). An infinite visual canvas for planning AI video projects: scene/shot cards, prompts, negative prompts, lenses, lighting, camera movement, references, and handoff exports that downstream generators (ComfyUI/LTX, Kling, Veo) can actually execute. Local-first, no account, no cloud.

## Installed State (this machine)

- App: `/Applications/Master Canvas.app` (x86_64 — built from source for this Intel Mac, `npm run desktop:dir`; quarantine cleared)
- Hermes plugin: `master-canvas` v1.1.0 installed + enabled at `~/.hermes/profiles/creative/plugins/master-canvas/` — provides 8 tools + the bundled `master-canvas:handoff` skill
- Source: `~/Projects/master-canvas` (clone of wassermanproductions/master-canvas)
- MCP server: `~/Projects/master-canvas/mcp/master-canvas-mcp.mjs` — registered in the creative profile config as `master-canvas` (node, 14/14 tools enabled), profile-local only, root config untouched

## Two ways to work

### 1. Hermes plugin (primary — autonomous)

The plugin's tools build/read the handoff package format directly, no GUI needed:

| Tool | Use |
|---|---|
| `mastercanvas_capabilities` | List what the plugin can do |
| `mastercanvas_create_package` | Create package from brief + scenes + shots + prompts + asset paths |
| `mastercanvas_upsert_scene` | Add/update a scene (structure, description, style prompt, music prompt) |
| `mastercanvas_upsert_shot` | Add/update a shot (prompt, negative prompt, camera, lens, lighting, duration, source image, notes) |
| `mastercanvas_inspect_package` | Confirm scene/shot counts, missing assets, readiness |
| `mastercanvas_package_zip` | Zip a package for sharing/archiving/downstream |
| `mastercanvas_extract_package` | Extract a ZIP for local generation work |
| `mastercanvas_comfy_plan` | Build the ComfyUI/LTX execution plan from the package |

Load the bundled **`master-canvas:handoff`** skill for the full package-contract workflow (inspect → extract → plan → treat `project_manifest.json` as source of truth for scene/shot order, prompts, refs, and output bins).

### 2. Desktop app (visual editing)

Open `/Applications/Master Canvas.app`. Infinite canvas with zoom/pan, lasso selection, grouping, node connections; local asset library (images, video, audio, links, style refs, music refs); per-shot inspectors; exports: Markdown, JSON, visual storyboard HTML, storyboard PDF, and the ZIP handoff package. Projects live in local browser/Electron storage.

## Package contract (handoff ZIP)

```
project_manifest.json      # source of truth: scenes, shots, prompts, order, bins
comfyui/                   # ComfyUI/LTX job JSON
kling-veo/                 # prompt sheets per generator
hermes-agent/              # context for agents
timeline/                  # shot order CSV, scene bin plan
deliverables/              # output bins, bin_plan.json
README.md
```

## Workflow (autonomous)

1. `mastercanvas_create_package` from the brief (title, brief, scenes, shots, prompts, asset paths).
2. Iterate with `mastercanvas_upsert_scene` / `mastercanvas_upsert_shot` as the user changes structure or shots.
3. `mastercanvas_inspect_package` to verify counts + missing assets.
4. `mastercanvas_comfy_plan` to build the ComfyUI/LTX plan, keep outputs organized by scene via `outputBin` / `deliverables/bin_plan.json`.
5. `mastercanvas_package_zip` when ready to share/archive/send downstream.
6. Keep the package compatible with the app's handoff contract — don't invent a separate schema.

## Pitfalls

- **Plugin tools only appear in fresh sessions**: after install/enable, open a new chat (or ⌘Q + reopen the desktop app) — the tools register per-session.
- **App is a source build**: don't overwrite `/Applications/Master Canvas.app` with an arm64 DMG — this Mac is Intel; rebuild from `~/Projects/master-canvas` with `npm run desktop:dir` if you need to refresh it.
- **Assets must exist**: `mastercanvas_inspect_package` reports missing assets — copy referenced images into the package before zipping.
- **Plugin ≠ MCP**: the 8 plugin tools operate on packages directly; the MCP server (`master-canvas-mcp.mjs`) is for external MCP clients. Don't register both unless you need external clients.

## Verification

- `mastercanvas_capabilities` returns the tool list.
- `mastercanvas_create_package` on a one-line brief produces a complete package (manifest + comfyui/ + kling-veo/ + hermes-agent/ + timeline/ + deliverables/ + README.md).
- App launches: `open "/Applications/Master Canvas.app"`
