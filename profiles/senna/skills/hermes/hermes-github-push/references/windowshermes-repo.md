# Windowshermes Repo Structure

**Repo:** `https://github.com/<your-github-username>/windowshermes`
**Local path:** `~/projects/windowshermes`
**Purpose:** Hermes profiles for Windows PC game dev (Eldrath project)

## Profile Names (EXACT — do not rename)

| Profile | Role | Model |
|---------|------|-------|
| `worldbuilder` | Narrative, lore, characters | AtomicBot local |
| `abilities` | Combat, GAS, balance | AtomicBot local |
| `ue5-coder` | UE5 C++ implementation | AtomicBot local |
| `designer` | UI/UX, visual design | MiMo v2.5 Pro (cloud) |
| `arch` | System architecture | local-36B |
| `threejs-coder` | Three.js 3D | — |
| `blender-coder` | Blender automation | — |

**Pitfall:** Profile directory names use no hyphens for `worldbuilder` (not `world-builder`). Check `install.sh` ALL_PROFILES array for exact names.

## Directory Structure

```
windowshermes/
├── profiles/
│   ├── worldbuilder/     SOUL.md + AGENTS.md + config.yaml
│   ├── abilities/        SOUL.md + AGENTS.md + config.yaml
│   ├── ue5-coder/        SOUL.md + AGENTS.md + config.yaml + ue-* skills
│   ├── designer/         SOUL.md + AGENTS.md + config.yaml
│   ├── arch/             SOUL.md + AGENTS.md + config.yaml
│   ├── threejs-coder/
│   └── blender-coder/
├── vault/                Obsidian vault (Eldrath world)
│   ├── .obsidian/        Obsidian config
│   ├── Design/           Game design docs
│   │   └── concepts/     Design patterns (glassmorphism, liquid glass)
│   ├── World/            Lore, characters, factions
│   ├── Systems/          Abilities, combat, progression
│   ├── UnrealEngine/     UE5 reference material
│   │   ├── concepts/     RPG systems, learning path, MCP bridges, LLM tooling
│   │   └── references/   GAS documentation (tranek)
│   ├── Art/              3D art pipeline
│   │   └── concepts/     Blender workflows, shading, anatomy, creature design
│   ├── Threejs/          Three.js ecosystem
│   │   ├── references/   Library refs (17 USAGE files, 12 wiki articles)
│   │   └── concepts/     Lighting, glow/fx, particles, shaders, video export
│   └── References/       Inspirations
├── skills/               Shared skills (installed to all profiles)
│   ├── game-dev-memory-system/
│   └── game-design-team/
├── scripts/              Build/start scripts for llama.cpp
├── docs/                 Setup guides
├── knowledge/            Wiki snapshots
└── install.sh            Profile installer
```

## Before Adding Content

1. **Check existing profiles:** `search_files(path='~/projects/windowshermes/profiles', target='files')`
2. **Read existing SOUL.md:** `read_file(path='~/projects/windowshermes/profiles/<name>/SOUL.md')`
3. **Check install.sh:** `read_file(path='~/projects/windowshermes/install.sh')` for ALL_PROFILES array
4. **Check README:** `read_file(path='~/projects/windowshermes/README.md')` for current state

## Adding New Profiles

1. Create directory: `profiles/<name>/`
2. Create SOUL.md, AGENTS.md, config.yaml
3. Add to ALL_PROFILES in `install.sh`
4. Update README.md directory tree

## Adding Shared Skills

1. Create in `skills/<skill-name>/SKILL.md`
2. `install.sh` auto-installs shared skills to all profiles

## Obsidian Vault

The vault at `vault/` is a proper Obsidian vault with `.obsidian/` config. Open in Obsidian:
1. Open Obsidian → "Open folder as vault"
2. Select `vault/` directory
3. Obsidian detects `.obsidian/` config automatically

## Git Push

See `hermes-github-push` skill for auth workflow. Key points:
- `gh auth login` must be run in real Mac terminal
- Copy config to sandboxed home: `cp ~/.config/gh/hosts.yml ~/.config/gh/hosts.yml`
- Then `git push` works
