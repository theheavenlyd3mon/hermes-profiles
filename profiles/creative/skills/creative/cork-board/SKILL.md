---
name: cork-board
description: "Plan story structure on a cork board: cards, acts, arcs."
version: 1.0.0
author: creative profile
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [story-structure, outlining, filmmaking, preproduction, mcp, fountain]
---

# Cork Board — Story Structure Planning Wall

## When to Use

- User wants to plan/outline story structure: index cards, acts, arcs, episodes, beat sheets.
- User references Cork Board, a cork wall, story cards, or the AVA demo.
- User wants a production preset (Save the Cat, Three Acts, One-Hour Pilot, trailers, shorts) applied to a project.
- Working with the Cork Board app or its MCP server, or setting `CORK_BOARD_PROJECT`.
- User wants exports: Markdown outline, CSV scene list, Fountain scaffold, JSON, Share Wall.

Part of the Wasserman Filmmaker Suite (by Sam Wasserman). A local-first planning app that emulates a wall of index cards on cork: pin scenes, drag between acts, tag characters/locations, track arcs beat by beat, export the whole wall as outline, scene list, Fountain scaffold, or JSON. Works for short films, music videos, commercials, features, and multi-episode series.

## Installed State (this machine)

- App: `/Applications/Cork Board.app` (universal build, v1.2.0 — runs on this Intel Mac; quarantine cleared)
- Source repo: `~/Projects/cork-board` (MCP server at `mcp/cork-board-mcp.mjs`)
- MCP: registered in the creative profile config as `cork-board` (node, 25/25 tools enabled) — profile-local only, root config untouched
- One-line reinstall: `curl -fsSL https://raw.githubusercontent.com/wassermanproductions/cork-board/main/install.sh | bash`

## What it does

- **Board**: index cards on cork/paper/midnight surfaces; drag within/across columns; drag a card onto another board tab to move between episodes
- **Cards know filmmaking**: title, synopsis, INT/EXT, time of day, location, characters, colored labels, status (Idea → Outlined → Drafted → Revised → Locked → Cut), page count, due date, checklist, notes, seven card colors; pushpin color follows status
- **Three views**: Board (cork wall), Outline (numbered beat sheet with statuses/page counts), Arcs (character-by-scene grid — every cell is an arc beat written in place)
- **Cast & world drawer**: characters with color/role/want/need/arc; locations with INT/EXT + scout notes; labels for subplots/threads; live Insights (cards, pages, est. runtime, day/night split, character load, location load)
- **Presets**: 25 production structures — AVA demo feature, Three Acts, Save the Cat, Eight Sequences, One-Hour Pilot, Half-Hour Comedy, Season Arc Wall, Multi-Board Series, Short Film, Music Video, Commercial, Documentary, blank wall, plus timecoded 1–10 min shorts and :30/:60 trailer walls (every beat pinned to a runtime window)
- **Reference images on cards** (S/M/L sizes) and **AI prompts on cards** (one-click copy) — the bridge between the wall and image/video generators
- **Safety nets**: autosave, undo (60 levels), named checkpoints, full JSON export/import
- **Exports**: Markdown outline, CSV scene list (schedule-friendly), Fountain scaffold with scene headings, complete project JSON, printable Share Wall (HTML — open in browser, print, and any Cork Board user can import it)

## Workflow (GUI app)

1. Launch Cork Board — opens with the AVA demo feature (36 cards, six characters, ten locations). Start your own with **New** or **Presets**.
2. Build your wall: cards → acts → arcs. Tag characters by dragging them onto cards.
3. Attach reference images and generation prompts to cards as you go.
4. Export when ready: Fountain for a screenwriter, CSV for scheduling, Share Wall for printing, JSON for the agent (below).

## Hermes + Cork Board via MCP (headless)

The MCP server lives in the repo at `mcp/cork-board-mcp.mjs` (zero-dependency, Node ≥ 18). It reads/edits a Cork Board project JSON headlessly: walls, acts, cards, cast, places, labels, arc beats, presets, and the app's own exports — no desktop app required.

Round-trip: **Export → JSON** in the app → agent works on the file → **Export → Import** back.

```bash
# generic MCP config (Hermes/Codex):
#   command: node
#   args: ["/absolute/path/to/cork-board/mcp/cork-board-mcp.mjs"]
#   env: { CORK_BOARD_PROJECT: "/absolute/path/to/project.json" }  # optional; defaults to app-data location
```

Tools: `get_board`, `add_card` / `update_card` / `move_card` / `tag_card` / `set_arc_beat`, `add_act` / `rename_act` / `reorder_acts`, `add_entity` (cast / places / labels), `list_presets` / `apply_preset`, `export_outline` / `export_scene_list` / `export_fountain` / `export_json` / `export_share_html`.

## Pitfalls

- **Gatekeeper "damaged" error**: unsigned builds aren't notarized — run `xattr -cr "/Applications/Cork Board.app"` once after installing from a DMG (or right-click → Open → Open).
- **AVA demo persists**: the demo stays in the project menu until you delete it — don't mistake it for a user project.
- **MCP default path**: without `CORK_BOARD_PROJECT` the server points at the app-data location — pass the env or `projectPath` per call for explicit files.

## Verification

- App launches: `open "/Applications/Cork Board.app"`
- MCP responds: with `CORK_BOARD_PROJECT` set, call `get_board` — expect acts/cards matching the project.
