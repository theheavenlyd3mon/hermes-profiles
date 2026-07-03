# Browser-Native 3D Game Dev with AI Agents

Research compiled from hermes-world.ai analysis and 2025-2026 ecosystem survey.

## Why Browser-Native Over Unity/Godot

| Factor | Browser-Native (Three.js/R3F) | Unity/Godot |
|--------|-------------------------------|-------------|
| Install | None — runs in browser | Requires engine install |
| AI code gen | Excellent (TypeScript/JS has huge training data) | Weaker (GDScript less data, C# moderate) |
| Iteration | Instant — save and see changes | Requires compile/refresh step |
| Deployment | "wrangler deploy" to CDN | Build per platform |
| Multiplayer | WebSocket/BroadcastChannel built-in | Requires dedicated server setup |
| AI agent interaction | Agents can interact as web pages | Agents need editor plugins/MCP |
| 3D quality | Good (not AAA) | AAA capable |
| Mobile/console | Web only | Native targets |

## The Stack (hermes-world pattern)

```
@react-three/fiber    — React wrapper for Three.js (use 3D in React components)
@react-three/drei     — Helpers: Html overlays, Sparkles, OrbitControls, GLB loading
@react-three/rapier   — Physics engine (collision, gravity, rigid bodies)
@react-three/postprocessing — Visual effects (bloom, vignette, tone mapping)
three                 — The underlying 3D library
zustand               — Tiny state manager (game state, player data)
react                 — UI framework
vite                  — Build tool (fast dev server, production bundling)
tailwindcss           — Styling for UI overlays
```

## Architecture Patterns

### State Management (Zustand)
- Single store holds all game state
- Selectors for performance (only re-render when relevant state changes)
- Actions for state mutations (movePlayer, changeZone, addChat)
- Persists to localStorage for save/load

### Zone-Based World
- Each zone is a config object: id, name, groundColor, skyColor, fogDistance, decorations
- Zone change = swap entire scene contents, reset player position
- Portals are distance-triggered (check player proximity each frame)

### 3D Scene Composition
- World component assembles: lighting + environment + player + NPCs + portals
- Each game object is a React component
- useFrame() hook runs logic every frame (movement, camera, animation)
- Camera follows player with lerp smoothing

### NPC System
- GLB probing: HEAD request to check if .glb model file exists
- Falls back to simple geometry (box, capsule) if no model
- Click handlers for interaction
- Html overlay for name tags (positioned in 3D space)

### Multiplayer
- BroadcastChannel for same-origin (zero server, instant)
- WebSocket for cross-machine (Cloudflare Workers + Hibernation API)
- 5 Hz presence updates (200ms intervals)
- Position-delta gating (skip sends if player hasn't moved)
- Lerp interpolation for smooth remote movement

### UI Overlays
- Html component from drei renders HTML inside 3D scene
- HUD as absolute-positioned div on top of Canvas
- Speech bubbles as Html positioned above characters

## AI Agent Game Dev Workflow

1. **Scaffold**: Agent generates project structure + starter code
2. **Iterate**: Ask agent to add features one at a time (inventory, quests, combat)
3. **Assets**: Use image gen for concept art, textures, sprites
4. **Models**: Use Blender + agent for 3D models, export as GLB
5. **Multiplayer**: Agent generates WebSocket server + client code
6. **Deploy**: Agent runs build + deploy commands

## Limitations

- No AAA rendering quality (WebGL constraints)
- No native mobile/console (web only)
- Physics less mature than Unity/Unreal
- Complex animations harder than engine-based tools
- "Feel" (jump arcs, camera transitions) requires human hands-on testing
