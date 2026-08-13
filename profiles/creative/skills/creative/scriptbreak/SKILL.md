---
name: scriptbreak
description: "Break down screenplays: scenes, shots, prompt packs."
version: 1.0.0
author: creative profile
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [script, screenwriting, preproduction, filmmaking, mcp, prompt-pack]
---

# ScriptBreak — Screenplay Breakdown

## When to Use

- User asks to break down / analyze a screenplay, script, or draft (Fountain, FDX, PDF, TXT).
- User wants scenes, sluglines, elements, shot lists, character/location bibles, or shooting schedule / Day Out of Days from a script.
- User wants an AI prompt pack (per-generator dialects: Veo, Runway, Kling, ComfyUI/Wan, LTX, Seedance, GPT Image, Nano Banana, Krea, Seedream, Midjourney).
- Working with the ScriptBreak app or its MCP server, or setting up `SCRIPTBREAK_PROJECT`.

Part of the Wasserman Filmmaker Suite (by Sam Wasserman). Imports a script and produces a full breakdown — scenes, sluglines, elements (props/wardrobe/vehicles/VFX), character & location bibles, starter shot lists, project look — then exports **self-executing prompt packs** that turn any LLM into your assistant director. Zero accounts, zero telemetry.

## Installed State (this machine)

- App: `/Applications/ScriptBreak.app` (x86_64, v1.0.0 — Intel Mac build; quarantine cleared with `xattr -cr`)
- Source repo: `~/Projects/scriptbreak` (MCP server at `mcp/scriptbreak-mcp.mjs`)
- MCP: registered in the creative profile config as `scriptbreak` (node, 11/11 tools enabled) — profile-local only, root config untouched
- One-line reinstall: `curl -fsSL https://raw.githubusercontent.com/wassermanproductions/scriptbreak/master/install.sh | bash`

## What it does

- **Import**: `.fountain`, `.fdx` (Final Draft, uses embedded scene lengths for exact page counts), `.pdf` (offline embedded PDF engine reconstructs from page layout), plain `.txt`
- **Auto-breakdown on import**: elements tagged from word lists AND writer's CAPS in action lines; bibles seeded from intro descriptions; starter shot lists include shots the writer explicitly called (CLOSE ON, INSERT, POV…)
- **Projects & drafts**: local library, multiple drafts per project, draft comparison (scenes added/cut/rewritten, page deltas, cast changes)
- **Style guide ingestion**: drop a mood book / pitch deck PDF — framing/camera/lighting/music notes flow into the Look and ride inside every export as a binding style guide
- **Timeline**: whole film on one strip, scene widths ∝ page length, character-presence lanes
- **Shooting schedule & Day Out of Days**: draft stripboard grouped by location/day-night/int-ext under a pages-per-day budget; cast presence read from dialogue so silent/background cast need manual verification
- **Prompt-pack exports**: self-executing `.md` files with per-platform dialects — video (Veo, Runway, Kling, ComfyUI/Wan, LTX, Seedance) and stills (GPT Image, Nano Banana, Krea, Seedream, Midjourney). Scope to scene ranges, page ranges, or current filters; or zip everything.

## Workflow (GUI app)

1. Launch ScriptBreak, load a script (File → Open; formats above).
2. Review auto-tagged scenes/elements; click auto-detected suggestions or select words in the scene text to tag.
3. Check Bibles (character/location/hero-prop) — these get injected into every prompt for consistency.
4. Set the Look (13 fields of visual DNA) or ingest a mood book PDF.
5. Export a prompt pack scoped to your needs and hand it to any LLM, or to the video/still generator dialect you use.

## Hermes + ScriptBreak via MCP (headless)

The MCP server lives in the repo at `mcp/scriptbreak-mcp.mjs` (zero-dependency, Node ≥ 18). Register it pointing at a project saved with **Save project** (`.scriptbreak` file):

```bash
# generic MCP config (Hermes/Codex):
#   command: node
#   args: ["/absolute/path/to/scriptbreak/mcp/scriptbreak-mcp.mjs"]
#   env: { SCRIPTBREAK_PROJECT: "/absolute/path/to/project.scriptbreak" }
```

Eleven read-only tools:
`get_breakdown`, `list_scenes`, `get_scene`, `list_elements`, `get_character_bible`, `get_location_bible`, `get_shot_list`, `list_generators`, `export_prompt_pack`, `get_schedule`, `get_day_out_of_days`.

`export_prompt_pack` reproduces ScriptBreak's AI-video / storyboard-frame / coverage-consult / script-companion packs (same per-generator dialects) for any scene range, page range, or structured filter.

## Pitfalls

- **Gatekeeper "damaged" error**: unsigned builds aren't notarized — run `xattr -cr /Applications/ScriptBreak.app` once after installing from a DMG.
- **`.scriptbreak` files don't open on double-click**: file associations register the first time the app launches; open the app once from Finder/Applications first. macOS delivers open requests as Apple Events, not argv.
- **Schedule cast detection**: silent/background cast aren't detected (dialogue-only); verify before treating it as final for 1st-AD work.
- **No AI calls**: ScriptBreak never calls a model — the export IS the integration. Paste the pack into the LLM yourself.

## Verification

- App launches: `open /Applications/ScriptBreak.app`
- MCP responds: run the server with `SCRIPTBREAK_PROJECT` set and call `list_scenes` — expect scene count matching the script.
