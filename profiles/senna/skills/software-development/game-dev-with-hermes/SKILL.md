---
name: game-dev-with-hermes
description: >-
  Build games with Hermes Agent — browser-native (Three.js + React), Unity, and
  Godot workflows. Covers game architecture patterns, AI-assisted development,
  MCP bridges for game engines, and the Hermes multi-agent game studio model.
  Trigger on: game dev, game design, Three.js game, Unity AI, Godot AI, MMO,
  multiplayer browser game, RPG systems, quest system, inventory system,
  Phaser, Capacitor game, 2D game, tamagotchi, mobile game, browser game.
metadata:
  author: senna
  version: "1.0"
  related_skills:
    - threejs-simulation
    - threejs-postprocessing
    - threejs-shader-patterns
    - threejs-cinematic-camera
    - unreal-engine-solo-rpg-dev
    - blender-automation
---

# Game Dev with Hermes

Build games using Hermes Agent as your AI coding partner. Three engine paths:
browser-native (Three.js+React), Unity (C#), and Godot (GDScript/C#).

## When to Load

User says any of:
- "Build a game with Hermes"
- "Browser game with Three.js"
- "Unity game with AI assistance"
- "Godot game with AI"
- "MMO / multiplayer browser game"
- "RPG systems — quests, inventory, combat"
- "How was hermes-world.ai built?"

## Engine Decision Matrix

| Factor | Browser-native (Three.js+React) | Unity | Godot |
|--------|--------------------------------|-------|-------|
| Install needed | None (web app) | Unity Editor | Godot Editor |
| Target | Web, mobile browser | Desktop, mobile, console | Desktop, mobile, web |
| AI code gen quality | Excellent (TypeScript) | Good (C#) | Fair (GDScript less training data) |
| Hermes integration | Full (file+terminal+image gen) | Partial (CLI batchmode) | Partial (CLI --headless) |
| Multiplayer | WebSocket (simple) | Netcode for GameObjects | ENet/MultiplayerAPI |
| Best for | AI-native games, fast iteration | AAA-quality, asset store | Indie, open-source, 2D+3D |

## Path A: Browser-Native Game (Three.js + React)

This is how hermes-world.ai was built. Full game as a web app — no engine install.

### Quick Start (Starter Template)

A working starter project lives in `templates/starter-browser-game/`. To scaffold:

```bash
TARGET_DIR="$HOME/projects/my-game"
mkdir -p "$TARGET_DIR/src/components" "$TARGET_DIR/src/stores"

# Copy template files from the skill directory
SKILL_DIR="<skill-dir>/templates/starter-browser-game"
cp "$SKILL_DIR/package.json" "$SKILL_DIR/vite.config.ts" "$SKILL_DIR/tsconfig.json" "$SKILL_DIR/index.html" "$TARGET_DIR/"
cp "$SKILL_DIR/src/"*.tsx "$TARGET_DIR/src/"
cp "$SKILL_DIR/src/stores/"*.ts "$TARGET_DIR/src/stores/"
cp "$SKILL_DIR/src/components/"*.tsx "$TARGET_DIR/src/components/"

cd "$TARGET_DIR"
pnpm install --no-frozen-lockfile
pnpm dev   # → http://localhost:3000
```

The starter includes: 3 zones, 4 NPCs, portal system, WASD movement,
iso camera follow, HUD, procedural environment. ~570 lines, builds in ~8s.

### Tech Stack (proven in production)

```
Rendering:   Three.js via @react-three/fiber
Physics:     @react-three/rapier
Post-FX:     @react-three/postprocessing (Bloom, Vignette, ToneMapping)
State:       Zustand (client) + localStorage (persistence)
Routing:     TanStack Router + TanStack Start
Hosting:     Cloudflare Workers
Multiplayer: WebSocket + CF Hibernation API
Desktop:     Electron (optional shell)
Build:       Vite, pnpm, TypeScript
```

### Post-Processing Setup (pmndrs/postprocessing)

The starter template includes `postprocessing` + `@react-three/postprocessing`. Use
the R3F wrapper (not the raw Three.js EffectComposer) for proper React integration:

```tsx
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'

// Inside your World component, AFTER all scene objects:
<EffectComposer>
  <Bloom
    intensity={0.6}          // 0.2 subtle, 1.5 intense
    luminanceThreshold={0.15} // 0.05 everything glows, 0.5 only brightest
    luminanceSmoothing={0.08}
    mipmapBlur               // smoother glow spread
  />
  <Vignette offset={0.3} darkness={0.6} />
</EffectComposer>
```

**Canvas setup for post-processing:**
```tsx
<Canvas
  gl={{
    antialias: true,
    toneMapping: 3,            // ACESFilmicToneMapping
    toneMappingExposure: 1.0,
  }}
>
```

**Key constraint:** EffectComposer replaces `renderer.render()` internally. Do NOT
also call `renderer.render()` or use `<RenderPass>` — the R3F wrapper handles it.

See `references/magitech-rendering-recipe.md` for the complete zone-building approach.

### Game Architecture Pattern

```
src/
  screens/game/
    components/
      world-3d.tsx          ← Main 3D scene (Canvas + game loop)
      player-character.tsx   ← Player model + movement
      npc-character.tsx      ← NPC AI + dialog
      hud.tsx               ← Health, mana, minimap
      inventory-panel.tsx    ← Item management
      quest-dialog.tsx       ← Quest UI
      speech-bubble.tsx      ← Floating text
      environment.tsx        ← Scenery, terrain, portals
    hooks/
      use-multiplayer.ts     ← WebSocket presence + chat
      use-rpg.ts            ← RPG state (HP, XP, quests, inventory)
    lib/
      rpg-data.ts           ← Items, quests, skills, worlds data model
      avatar-config.ts       ← Character customization
      bots.ts               ← NPC profiles per zone
```

### RPG Data Model (from hermes-world)

```typescript
// Core types that drive the game
type WorldId = 'training' | 'hub' | 'dungeon' | 'forest' | 'arena'
type SkillId = 'combat' | 'crafting' | 'magic' | 'exploration'
type EquipmentSlot = 'weapon' | 'armor' | 'head' | 'accessory'

type Quest = {
  id: string
  title: string
  description: string
  objectives: QuestObjective[]  // talk_to_npc, collect_item, visit_zone, defeat_enemy
  reward: { xp: number; items?: ItemId[]; unlockWorlds?: WorldId[] }
}

type PlayerProfile = {
  displayName: string
  equipped: Record<EquipmentSlot, ItemId | null>
  inventory: ItemId[]
  questProgress: Record<string, { completed: boolean; completedObjectives: string[] }>
  level: number
  xp: number
}
```

### Multiplayer Pattern

Two transport layers (progressive enhancement):
1. **BroadcastChannel** — same-origin tabs, zero server (dev/testing)
2. **WebSocket** — cross-machine via Cloudflare Worker

```
Wire protocol:
  { kind: 'presence', id, name, world, x, y, z, yaw, avatar }
  { kind: 'chat', id, name, world, text }
  { kind: 'leave', id }
  { kind: 'count', online, byWorld }

Optimizations:
  - 5 Hz presence (not 10 Hz) — halve bandwidth, lerp interpolation
  - Position-delta gate: skip send if <0.04 units moved
  - Avatar config sent only on change (signature compare)
  - World-scoped rendering: hide players in other zones
```

### Hermes Capabilities for Browser Games

| Task | Hermes Tool |
|------|-------------|
| Generate gameplay code | terminal + file read/write/patch |
| Generate textures/sprites | image_gen (FAL) |
| Review screenshots | vision_analyze |
| Scaffold project structure | terminal (npm/pnpm/vite) |
| Run builds | terminal (vite build) |
| Export for deployment | terminal (wrangler deploy) |
| Automated testing | cron (nightly build + test) |
| Parallel work | delegate_task (code + assets + tests) |
| Create game-specific skills | skill_manage |

## Path B: Unity (C#)

### AI Tools for Unity (2026)

- **Unity AI Beta** (Unity 6) — official, integrates with CLI workflows
- **"Everything Game Dev Code" scaffold** — 42 agents, 51 commands, 86 skills
  github.com/MRCalderon3D/everything-game-dev-code
- **Claude Code** — proven for Unity C# (Dino Card Hunt shipped to Steam)
- **Cursor** — diff viewer + AI for Unity projects

### Hermes + Unity Workflow

1. Hermes generates C# scripts (MonoBehaviours, ScriptableObjects)
2. You open in Unity Editor for scene setup, visual tuning, testing
3. Hermes can run Unity CLI: `Unity -batchmode -projectPath . -buildTarget ...`
4. Use cron for automated builds and tests

### Limitations

- Scene/editor awareness: external tools only see files, not running game
- Binary assets (.unity, .prefab): AI should not edit directly
- "Feel" (jump arcs, camera): requires human hands-on iteration

## Path C: Godot (GDScript / C#)

### AI Tools for Godot (2026)

**Editor Plugins:**
- **Ziva** ($20/mo) — best in-editor agent, manipulates live scene tree
- **Godot AI Suite** ($5) — JSON execution plans
- **AI Assistant Hub** (free) — supports Ollama for local/offline

**MCP Bridges (connect Hermes to Godot):**
- **Godot AI MCP** (dlight) — ~150 operations, MIT
- **Godot MCP Pro** ($5) — 162 tools
- **GDAI MCP** (free) — popular with "vibe coders"

**AI-Native:**
- **Summer Engine** — free, Godot 4 compatible, full state awareness

### Hermes + Godot Workflow

1. Hermes generates GDScript files
2. Terminal runs Godot CLI: `godot --headless --export-release "Linux" build/`
3. MCP bridge enables live scene manipulation
4. Hermes can read/write .tscn (scene) and .tres (resource) files

### Limitations

- GDScript has less AI training data than C# — weaker code gen
- Godot community is more resistant to AI adoption (forum observations)
- Scene tree awareness requires MCP bridge setup

## Multi-Agent Game Studio Pattern

Hermes can orchestrate multiple agents for game dev:

```
Orchestrator (you)
├── Builder agent: gameplay code, systems, features
├── Artist agent: concept art, textures, sprites (image_gen)
├── QA agent: automated testing, bug reports
├── Researcher: game design references, similar games analysis
└── Documenter: lore, quest text, NPC dialog
```

Use delegate_task for parallel work:
- Agent 1: Write inventory system code
- Agent 2: Generate item icon sprites
- Agent 3: Write unit tests for inventory logic

### Multi-Profile Game Dev Team (Local)

For local game dev on a single machine, create multiple Hermes profiles — each a different game dev role — all sharing one model server. The persona comes from SOUL.md/AGENTS.md/skills/temperature, not the model.

See `references/windowshermes-example.md` for the Eldrath project's full repo structure, install script, and design decisions.
See `references/github-auth-from-sandbox.md` for pushing from Hermes sandbox to GitHub.
See `references/multi-profile-game-team.md` for the full pattern: profile roles, config templates, Obsidian vault integration, PersRubric calibration for non-coding roles, and usage workflow.

### World Building from Lore Documents

When the user provides a lore compendium, game bible, or world design document (PDF, Google Doc, markdown), extract it into a structured Obsidian vault with wikilinks and cross-references. This vault becomes the shared brain that all profiles reference.

See `references/obsidian-vault-from-lore.md` for the extraction workflow, vault structure, page templates, cross-reference patterns, and pitfalls.

## Game Design Principles

Before building, review `references/game-design-principles.md` — it covers:
- Core loops at 4 time scales (moment → minute → hour → day)
- The convenience-community tradeoff (every QoL removes a social touchpoint)
- Dunbar's layers for social system design (5/15/50/150 player groups)
- Horizontal > vertical progression for social games
- Building system patterns (grid, editing, permissions, persistence)
- Prosocial design (commendations > punishment, fashion as social currency)
- Roblox platform model (building = content engine)

These principles should inform zone layout, system design, and feature
prioritization for any social/multiplayer game project.

## Skills Loading Strategy

Load companion skills based on the task at hand.

### For Code/Build Sessions
```
skill_view(name='game-dev-with-hermes')         ← this skill (architecture, pitfalls)
skill_view(name='game-dev-memory-system')       ← Mnemosyne/Fabric/Obsidian memory architecture
skill_view(name='threejs-postprocessing')       ← Bloom, Vignette, ToneMapping
skill_view(name='threejs-shader-patterns')      ← custom GLSL shaders
skill_view(name='karpathy-coding-discipline')   ← clean surgical code
skill_view(name='threejs-cinematic-camera')     ← camera moves (optional)
skill_view(name='threejs-simulation')           ← scene setup patterns (optional)
skill_view(name='writing-plans')                ← task breakdown (optional)
```

### For Design/Content Sessions
```
skill_view(name='game-dev-with-hermes')   ← this skill (RPG data model, quest patterns)
skill_view(name='humanizer')              ← NPC dialogue that sounds real (CRITICAL for NPCs)
skill_view(name='excalidraw')            ← zone layout diagrams (optional)
skill_view(name='architecture-diagram')  ← world map visualization (optional)
```

**World content authoring:** See `references/world-content-authoring.md` for the
full pipeline — lore → zones → NPCs → quests → items → cosmetics — with document
structures, cross-reference rules, and pitfalls. Load `humanizer` alongside for
NPC dialogue — it has the anti-AI-slop patterns and "add soul" section directly
applicable to game character writing.

Note: `ideation` skill does not exist (was expected but not found in skill registry).

## Parallel Track Development

When a game needs both code AND content, split into parallel tracks.
See `references/parallel-track-workflow.md` for the full pattern.

Summary: Track A builds the engine, Track B creates the world content.
Both read the same design doc. Merge when both are complete.

## Deployment Infrastructure (Supabase + Cloudflare)

For browser-native games that need auth, database, and hosting:

```
Stack:
  Hosting:     Cloudflare Pages (free, global CDN, auto-HTTPS)
  Database:    Supabase (Postgres, free tier: 500MB, 50K users)
  Auth:        Supabase Auth (email, Google, GitHub login)
  Realtime:    Supabase Realtime (multiplayer presence, later)
  Domain:      Cloudflare Registrar (~$10/year for .com)

Cost: ~$10/year to start, ~$35/year at 10K players.
```

### Environment Variable Setup

```
# .env (git-ignored, NEVER committed)
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJxxxxxx...

# .env.example (committed — shows format without real values)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

The `VITE_` prefix is required — Vite only exposes env vars starting with `VITE_`
to frontend code. Anything without the prefix stays server-side only.

Supabase has TWO keys:
- **Anon Key** → safe for frontend (public, rate-limited, RLS-protected)
- **Service Key** → NEVER in frontend (full admin access, bypasses RLS)

### Database Schema Pattern

```sql
-- Players (linked to auth.users)
create table players (
  id uuid primary key references auth.users(id),
  display_name text not null default 'Wanderer',
  avatar_config jsonb default '{}',
  level int default 1, xp int default 0,
  created_at timestamptz default now(),
  last_seen timestamptz default now()
);

-- Inventory, quest_progress, zone_state follow same pattern
-- with player_id foreign key and ON DELETE CASCADE
```

### Row Level Security (CRITICAL)

Every table must have RLS enabled. Without it, any logged-in user can
read ALL data in the table. Pattern:

```sql
alter table players enable row level security;
create policy "Players can view own profile"
  on players for select using (auth.uid() = id);
create policy "Players can update own profile"
  on players for update using (auth.uid() = id);
create policy "Players can insert own profile"
  on players for insert with check (auth.uid() = id);
```

### Game ↔ Database Sync

Zustand (client state) ↔ Supabase (server state) sync layer:
- Save position to `zone_state` on zone change (not every frame)
- Load inventory on login, sync on change
- Quest progress syncs on completion
- Level/XP syncs on gain

See `references/supabase-cloudflare-deployment.md` for the full deployment plan
with SQL schemas, RLS policies, security checklist, and cost breakdown.

### User Workflow: Save Plans as Files

When planning deployment or infrastructure, save the plan as a file
(e.g., `docs/DEPLOYMENT-PLAN.md`) so the user can review it later.
Don't just explain in chat — the user may want to set up accounts
on their own time and return to the plan later.

## See Also

- `game-dev-memory-system` — Mnemosyne/Fabric/Obsidian memory architecture for game dev. Setup script, initial seeds, memory hygiene.
- `ue-*` skills — Unreal Engine specific patterns
- `references/ue5-open-source-references.md` — ActionRoguelike (C++ code reference), ALIS (plugin architecture template), BAR (data-driven patterns). Clone these as primary learning sources.
- `references/ue-llm-ecosystem-deep-dive.md` — MCP servers, skills, model recommendations, AND UE5 fine-tuning landscape (AdamCodd dataset, Claude Opus distillation, Pragma, cost comparison, VRAM guide).
- `references/hermes-world-architecture.md` — full architecture analysis of
  hermes-world.ai from source code, including file structure, data models,
  multiplayer protocol, and development timeline.
- `references/ai-game-dev-workflows.md` — AI tool landscape for Unity/Godot/browser,
  cost-effective model routing, success stories, and recommended workflows.
- `references/game-design-principles.md` — game design research: core loops,
  social systems, building patterns, progression, world building theory.
- `references/parallel-track-workflow.md` — parallel Build + Design track pattern
  for splitting code and content work across sessions.
- `references/social-hub-design.md` — walkable hub layout pattern with layered
  capacity (Bench in the Park principle applied).
- `references/persistence-legacy-system.md` — never-delete persistence promise,
  dormant/archive/rebuild system for inactive players.
- `references/world-content-authoring.md` — full pipeline for creating game world
  content (lore, zones, NPCs, quests, items, cosmetics) from a design doc.
- `references/magitech-rendering-recipe.md` — complete zone-building approach:
  color palette, custom GLSL shaders (circuitry, crystal glow), ambient particles,
  crystalline character models, day/night cycle, CSS fade transitions, performance
  budget. Proven in Hermes Nexus Phase 0.

## Convenience-Community Decision Framework

For every feature, ask: "What social moment does this remove?"

| Feature | Keep Organic (Good Friction) | Automate (Bad Friction) |
|---------|------------------------------|-------------------------|
| Travel | Walk to portals, walk through zones | Teleport menus |
| Grouping | Walk up and ask nearby players | Auto-matchmaking queues |
| Shopping | Physical vendors in hub | Global auction house |
| Chat | Proximity + zone chat | Global cross-zone chat |
| Building | Templates + customization | Full auto-build |

**Principle:** Don't remove friction. Remove UNNECESSARY friction.
Walking past other players = good friction (creates encounters).
Scrolling through menus = bad friction (just annoying).

## Path E: Phaser 3 + Capacitor (2D Mobile/Browser)

For 2D games targeting mobile via Capacitor. Phaser is a standalone 2D/2.5D engine
(not React-based) with arcade physics, tilemaps, tweens, and a scene system.

### When to Choose Phaser over Three.js+React

| Factor | Phaser 3 | Three.js + React |
|--------|----------|-----------------|
| Dimension | 2D / 2.5D | 3D |
| React integration | None (standalone) | Native (R3F) |
| Mobile packaging | Capacitor (web→native) | Capacitor (web→native) |
| Bundle size | ~1MB gzipped | ~1MB gzipped |
| Physics | Arcade (built-in), Matter.js | Rapier (WASM) |
| Best for | Tamagotchi, platformers, puzzle games | MMO, 3D worlds, simulations |

### Quick Start

```bash
npm create vite my-game -- --template react-ts
cd my-game
npm install phaser react react-dom @capacitor/core
npm install -D @capacitor/cli @vitejs/plugin-react typescript
```

### Architecture Pattern

```
src/
  App.tsx           # React UI (status bars, buttons, overlays)
  Game.tsx          # Phaser wrapper (creates game, bridges events)
  game/
    main.ts         # Phaser config factory
    scenes/
      Boot.ts       # Asset loading, texture generation
      Game.ts       # Main gameplay scene
    systems/
      PoopManager.ts # Game-specific logic (ECS-lite)
```

### Key Patterns

See `references/phaser3-capacitor-patterns.md` for:
- Texture generation API (changed in 3.80+)
- TypeScript config (`esModuleInterop`)
- React ↔ Phaser bridge (window globals + scene events)
- Capacitor integration (notifications, status bar, splash)
- Emoji sprite prototyping

## Path D: Unreal Engine (C++ / Blueprint Hybrid)

For solo RPG development in UE with LLM assistance. Covers GAS (Gameplay Ability System), C++/Blueprint hybrid patterns, knowledge base architecture, and the LLM tool ecosystem.

### Engine Decision: When to Choose UE

| Factor | UE vs Browser-native/Unity/Godot |
|--------|----------------------------------|
| Best for | AAA-quality RPGs, action combat, large worlds |
| AI code gen quality | Good (C++) but LLMs hallucinate UE API signatures — always validate |
| Hermes integration | Partial (CLI batchmode, MCP bridges) |
| Install needed | Unreal Engine 5.x (40GB+) |
| Solo dev sweet spot | C++ base classes + Blueprint child classes + Data Assets |

### C++ vs Blueprint Decision

| Put in **C++** | Put in **Blueprints** |
|---|---|
| Persistent, background-running features | Temporary/fleeting mechanics |
| Heavy computation (pathfinding, physics) | Game-specific tuning values |
| Core architecture (inventory, GAS) | Iterative level logic |
| Systems that must survive refactors | Visual sequences, cutscenes |
| Networked/replicated logic | Designer-facing content |

**The sweet spot:** Write C++ base classes with `BlueprintCallable`/`BlueprintNativeEvent` hooks → Create Blueprint child classes for every concrete asset → Use `UPrimaryDataAsset` for item/quest/enemy definitions.

### GAS — The RPG Backbone

GAS is *the* framework for RPGs in UE (used by Fortnite, Genshin Impact):

| RPG System | GAS Maps To |
|---|---|
| Spellcasting | `UGameplayAbility` with cost, cooldown, animation |
| Damage formulas | `UGameplayEffect` + `ModifierMagnitudeCalculation` |
| Stats (STR, INT, AGI) | `UAttributeSet` with gameplay tags |
| Buffs/Debuffs | `UGameplayEffect` (duration-based) |
| Status effects | `FGameplayTag` blocking other abilities |
| Passive skills | Always-active `UGameplayAbility` |
| Item effects | Granted abilities via item's GameplayEffect |

**Definitive reference:** `tranek/GASDocumentation` on GitHub (800+★, community bible).

### Knowledge Base Architecture

All content at `~/UnrealEngine5/`:
- `KNOWLEDGE_BASE/` — 8 modules (CPP foundations, gameplay framework, GAS reference, RPG systems, blueprint workflow, LLM tooling, learning path)
- `GASDocumentation/` — cloned tranek/GASDocumentation
- `reference/` — MCP server setup, UE LLM toolkit
- `AGENTS.md` — LLM context instructions

### LLM Tooling for UE

| Tool | Stars | Purpose |
|---|---|---|
| `quodsoler/unreal-engine-skills` | 157★ | 27 pre-audited markdown skills for AI agents |
| `flopperam/unreal-engine-mcp` | 946★ | MCP server, 50+ tools: Blueprint, GAS, materials |
| `ColtonWilley/ue-llm-toolkit` | — | C++ plugin, 37 tools/200+ operations over HTTP |
| `kevinpbuckley/VibeUE` | — | In-Editor Chat Client + MCP |

### Open-Source UE5 Reference Repos

Two repos serve as primary references for AI-assisted UE5 C++ coding:

- **ActionRoguelike** (Tom Looman, 4.5k★) — THE C++ code style reference. LLMs know this codebase. Use it to verify generated code. `git clone https://github.com/tomlooman/ActionRoguelike.git`
- **ALIS** (fallintodusk) — THE architecture template. Plugin-based, contract-first, JSON→DataAsset pipeline. `git clone https://github.com/fallintodusk/alis.git`

Workflow: when LLM generates UE5 C++, compare output against ActionRoguelike patterns. When setting up a new project, use ALIS plugin structure as template. See `references/open-source-ue5-references.md` for full analysis.

### Critical C++ Rules for LLMs

- ❌ `delete MyActor` → use `->Destroy()`
- ❌ `new UObject()` → use `NewObject<>()`
- ❌ Raw pointers without `UPROPERTY()` for GC-tracked objects
- ❌ Loading all assets at game start → use `TSoftObjectPtr` + async loading
- ❌ LLMs default to C++-only — always add Blueprint hooks

### Recommended Learning Path

1. GAS in practice (`tranek/GASDocumentation` + Epic's free course)
2. Composition with `UActorComponent`
3. C++/Blueprint hybrid workflow
4. Data Assets + Data Tables
5. Save/Load + Subsystems

### Open-Source UE5 Reference Projects

Clone these as primary learning references:
- **ActionRoguelike** (tomlooman) — THE canonical UE5 C++ reference. LLMs know this code. Compare generated code against Tom's patterns. `git clone https://github.com/tomlooman/ActionRoguelike.git`
- **ALIS** (fallintodusk) — Plugin architecture template. Contract-first, JSON data pipeline, modular plugin structure. `git clone https://github.com/fallintodusk/alis.git`

See `references/ue5-open-source-references.md` for full analysis.

### UE5 Fine-Tuning & Local Models

For long-term cost reduction, fine-tuning a local model on UE5 code is viable:
- **AdamCodd/unreal-engine-5-code** — 364K rows of UE5 C++, ready for fine-tuning
- **Claude Opus distillation** — Jackrong's approach (Qwen3.5-27B + Opus reasoning traces), 177K downloads, full guide published
- **Pragma** — Community-built UE5-specific model (track for public release)
- **Hybrid approach** — Local Qwen for 70% of tasks (free), Claude API for 30% that needs frontier quality ($30-80/month)

See `references/ue-llm-ecosystem-deep-dive.md` for full landscape, cost comparison, and VRAM guide.

For the full knowledge base modules, LLM model selection benchmarks, and detailed GAS patterns, see `references/ue-rpg-dev-guide.md`.

## Pitfalls

- **Browser-native is NOT Unity/Godot** — hermes-world.ai looks like a game
  engine product but it's actually a React web app with Three.js. Don't assume
  Unity/Godot when someone says "browser game."
- **GDScript < C# for AI code gen** — models have less training data for Godot.
  Consider C# mode in Godot for better AI assistance.
- **Binary scene files** — Unity .unity and Godot .tscn are semi-textual but
  complex. AI should modify scripts, not scene files, unless using MCP bridges.
- **"Feel" cannot be AI-optimized** — jump arcs, analog deadzones, camera
  transitions require human hands-on testing. AI generates the code, human
  tunes the numbers.
- **Agent over-engineering** — AI agents may author 200-file refactors for a
  harmless warning. Cap patch size to <10 minute reviews.
- **MCP bridges are the unlock** — without them, AI tools only see files.
  With them, AI can manipulate the live scene tree, read game state, and
  test changes in real-time.
- **`pnpm add -D` may hang** in Hermes terminal (detected as long-lived process).
  Workaround: write package.json manually with deps, then `pnpm install`.
- **Terminal `~/` resolves to Hermes profile home** (`~/.hermes/profiles/senna/home/`),
  not the actual user home. Use absolute paths (e.g., `~/projects/...`)
  for project scaffolding to avoid path confusion between write_file and terminal.
- **`execute_code` write_file paths are relative to session CWD** — when using
  `write_file()` inside `execute_code` Python scripts, the path is relative to
  the terminal's working directory (usually `~`), NOT relative to
  the project directory you're building. If you write `"my-project/package.json"`,
  it lands at `~/my-project/package.json`. If the project directory
  is already `~/my-project/`, you get a nested
  `~/my-project/my-project/package.json`. Fix: use absolute paths
  in `execute_code` write_file calls, or use the top-level `write_file` tool
  directly which takes absolute paths.
- **Three.js bundle size** — a minimal R3F app is ~1MB gzipped. The `vite build`
  chunk-size warning is expected; use `build.rollupOptions.output.manualChunks`
  to split three.js into its own chunk if needed.
- **Postprocessing deps must both be installed** — `@react-three/postprocessing`
  is the R3F wrapper, but it depends on `postprocessing` (the pmndrs lib) as a
  peer dependency. Install BOTH: `pnpm add @react-three/postprocessing postprocessing`.
  Missing `postprocessing` causes cryptic import failures at runtime.
- **Three.js r184 deprecation warnings are harmless** — `THREE.Clock: deprecated`
  (from @react-three/fiber internals) and `PCFSoftShadowMap deprecated` appear in
  every r184 project. They do not affect rendering. Ignore them.
- **`vite build` may be flagged as long-lived** — Hermes terminal sometimes refuses
  `npx vite build` thinking it's a server. Workaround: use
  `./node_modules/.bin/vite build` directly, or run via `execute_code` with Python
  subprocess: `subprocess.run(['./node_modules/.bin/vite', 'build'], ...)`.
- **Shader materials: separate .tsx file** — export GLSL vertex/fragment strings
  and factory functions (e.g., `createCircuitMaterial()`) from a dedicated
  `components/shaders.tsx`. Keeps environment components readable. Use
  `new THREE.ShaderMaterial()` in factories, then `<primitive object={mat} attach="material" />`
  in JSX for layered overlays (base MeshStandard + shader overlay 1-2% larger).
- **Velocity-based movement > instant snap** — for smooth WASD, store `vx`/`vz`
  on the player and lerp toward target velocity (accel) or decay toward zero
  (decel). Direct position += input * speed feels robotic. Pattern:
  `newVx = input ? vx + (target - vx) * accel * dt : vx * (1 - decel * dt)`.
- **Zone transition: CSS fade overlay** — use a fixed `<div>` with
  `transition: opacity 0.35s ease` and `pointer-events: none`. Toggle via state
  when portal proximity triggers. Set zone change inside `setTimeout(600ms)` so
  the fade-out completes before the scene swap. Don't use Three.js fade shaders
  for this — DOM overlay is simpler and doesn't interfere with post-processing.
