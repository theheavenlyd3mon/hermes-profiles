# hermes-world.ai Architecture

Source: github.com/outsourc-e/hermes-workspace (MIT, 4.8k stars)
Built by: Eric (@outsource_) with AI agent swarm assistance

## What It Is

A browser-native 3D MMO where humans and AI agents coexist. NOT built with Unity or Godot — it's a web app with 3D graphics.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| 3D Rendering | Three.js via @react-three/fiber | 3D scene in React |
| Helpers | @react-three/drei | Html overlays, Sparkles effects |
| Post-processing | @react-three/postprocessing | Bloom, Vignette, ToneMapping |
| Physics | @react-three/rapier | Collision and physics |
| State | Zustand | Client-side game state |
| Routing | TanStack Router/Start | Page routing |
| Styling | Tailwind CSS v4 | UI styling |
| Hosting | Cloudflare Workers | Web app + WebSocket server |
| Desktop | Electron (optional) | Desktop app wrapper |
| Build | Vite 7 | Development and bundling |
| Language | TypeScript (100%) | Type-safe code |

## Architecture Layers

### 1. Router (src/router.tsx)
Table of contents. Maps URLs to pages:
- /hermes-world → landing page
- /playground → game (loads via iframe from hermes-world.ai/play/)

### 2. Screens (src/screens/playground/)
- hermes-world-landing.tsx — Marketing/landing page with zone descriptions
- hermes-world-embed.tsx — Iframe wrapper that loads the actual game
- components/playground-world-3d.tsx (3,349 lines) — THE CORE: entire 3D scene
- components/playground-hud.tsx — UI overlay (stats, quest arrow, chat)
- components/playground-npc-glb.tsx — NPC 3D models
- components/playground-player-glb.tsx — Player 3D model
- components/playground-environment.tsx — Trees, rocks, decorations
- components/playground-chat.tsx — Chat panel
- components/inventory-panel.tsx — Inventory UI
- components/quest-dialog-panel.tsx — Quest popup
- components/map-panel.tsx / minimap.tsx — Map UI

### 3. Game Data (lib/playground-rpg.ts, 625 lines)
The "rulebook" defining:
- 6 zones (Training, Agora, Forge, Grove, Oracle, Arena)
- 16 items with rarity tiers (common/rare/epic/legendary)
- 6 skills (Promptcraft, Worldsmithing, Summoning, Engineering, Oracle, Diplomacy)
- Quests with objectives, lessons, and rewards
- Equipment slots (weapon, cloak, head, artifact)

### 4. Player State (hooks/use-playground-rpg.ts, 569 lines)
Tracks everything about the player:
- Name, appearance, avatar config
- Inventory and equipped items
- Level, XP, HP/MP/SP
- Quest progress
- Unlocked zones
- Persists to localStorage

### 5. Multiplayer (hooks/use-playground-multiplayer.ts, 556 lines)
Two transports:
- BroadcastChannel: same-origin tabs, zero server needed
- WebSocket: cross-machine, 5 Hz presence updates, Cloudflare Workers
- Position-delta gating (skip sends if player hasn't moved)
- Lerp interpolation for smooth remote player movement
- World-scoped rendering (only see players in your zone)

### 6. HUD (components/playground-hud.tsx, 281 lines)
HTML overlay showing:
- Zone name and description
- Level, HP, XP bar
- Current quest and objective arrow
- Toast notifications (item/level-up rewards)
- Chat messages

### 7. NPC System (components/playground-npc-glb.tsx)
- Each NPC has: name, position, zone, greeting, 3D model
- GLB model probing: checks if .glb file exists, falls back to voxel shape
- Click-to-interact triggers quest dialogs

## How Zone Transitions Work

1. Player walks near a portal (glowing ring, distance < 1.5 units)
2. changeZone() is called: swaps zone ID, resets player position to center
3. 3D scene re-renders with: new ground color, sky, fog, NPCs, decorations, portals

## How Quests Work

1. Approach NPC → click → quest dialog appears
2. HUD shows arrow pointing toward current objective
3. Complete objectives (talk, collect, equip, visit, chat)
4. Get rewards: XP, items, skill points, zone unlocks

## How Multiplayer Works

1. Player position sent 5x/sec to other players
2. Chat messages appear as speech bubbles above characters
3. Server tracks online players per zone
4. Different-zone players are hidden from each other
5. 30-second timeout before removing disconnected players

## Key Patterns for Reuse

- **Zustand for game state**: Single store, selectors for performance
- **Zone-based scene swapping**: Change zone = swap entire scene contents
- **GLB probing**: Check if 3D model exists, fall back to simple geometry
- **Position-delta gating**: Skip network sends when player hasn't moved
- **Iso camera follow**: Lerp camera toward player position each frame
- **HTML overlays via drei**: UI elements rendered on top of 3D canvas

## Development Process

- Started as a "playground" feature in hermes-workspace
- v2.1.x: Multi-agent swarm orchestration added
- v2.2.0 (May 4, 2026): HermesWorld shipped — 6 zones, NPCs, quests
- v2.3.0 (May 8, 2026): Polish — iframe embed, wave chat panels, name reservation
- Built with Claude Opus + GPT orchestrated through OpenClaw/Hermes Agent
- Creator's key lesson: agents needed persistent memory, handoff docs, runbooks, strict constraints
