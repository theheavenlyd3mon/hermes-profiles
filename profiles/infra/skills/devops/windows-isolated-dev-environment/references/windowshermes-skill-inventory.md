# Windowshermes Skill Inventory (as of 2026-06-08)

Audit of what skills each profile needs vs what the windowshermes repo ships.

## How to audit

```bash
# On Mac (source of truth): list skills per profile
for profile in ue5-coder threejs-coder blender-coder designer; do
  echo "=== $profile ==="
  ls ~/windowshermes/profiles/$profile/skills/ 2>/dev/null || echo "(empty)"
done

# Compare against senna's skills
ls ~/.hermes/profiles/senna/skills/software-development/
ls ~/.hermes/profiles/senna/skills/unreal-engine/
```

## ue5-coder — 39 skills needed

### Coding discipline (from senna's `skills/software-development/`)

| Skill | Why |
|-------|-----|
| karpathy-coding-discipline | Surgical changes, no drive-by refactors |
| test-driven-development | RED-GREEN-REFACTOR cycle |
| systematic-debugging | 4-phase root cause debugging |
| writing-plans | Bite-sized task planning |
| tool-call-efficiency | Minimize tool calls per task |
| simplify-code | Parallel 3-agent cleanup |
| look-before-edit | Check who uses a file before editing |
| requesting-code-review | Pre-commit quality gates |
| subagent-driven-development | 2-stage subagent review |
| spike | Throwaway experiments before build |

### Unreal Engine (from senna's `skills/unreal-engine/`)

All 27 UE skills:
- ue-actor-component-architecture
- ue-ai-navigation
- ue-animation-system
- ue-async-threading
- ue-audio-system
- ue-character-movement
- ue-cpp-foundations
- ue-data-assets-tables
- ue-editor-tools
- ue-game-features
- ue-gameplay-abilities
- ue-gameplay-framework
- ue-input-system
- ue-mass-entity
- ue-materials-rendering
- ue-module-build-system
- ue-networking-replication
- ue-niagara-effects
- ue-physics-collision
- ue-procedural-generation
- ue-project-context
- ue-sequencer-cinematics
- ue-serialization-savegames
- ue-state-trees
- ue-testing-debugging
- ue-ui-umg-slate
- ue-world-level-streaming

### Game dev (shared or profile-level)

| Skill | Source | Notes |
|-------|--------|-------|
| game-dev-with-hermes | senna `skills/software-development/` | Game architecture patterns |
| game-dev-memory-system | windowshermes `skills/` (shared) | Already in repo root, install.sh copies to all profiles |

## threejs-coder — 5 skills needed

From senna's `skills/software-development/`:
- threejs-cinematic-camera
- threejs-engine-trail
- threejs-postprocessing
- threejs-shader-patterns
- threejs-simulation

## blender-coder — 0 custom skills

No custom Blender skills exist in senna's profile. Blender-coder relies on:
- Bundled `blender-automation` skill (MCP integration)
- Knowledge docs in `knowledge/blender/`

## designer — 0 custom skills

No custom design skills exist in senna's profile. Designer relies on:
- Bundled creative skills (claude-design, popular-web-designs, sketch, etc.)
- Knowledge docs in `knowledge/design/`

## Sync commands (run on Mac)

```bash
# Copy coding skills to ue5-coder profile
cd ~/windowshermes
mkdir -p profiles/ue5-coder/skills/software-development
for skill in karpathy-coding-discipline test-driven-development systematic-debugging \
  writing-plans tool-call-efficiency simplify-code look-before-edit \
  requesting-code-review subagent-driven-development spike; do
  cp -r ~/.hermes/profiles/senna/skills/software-development/$skill \
    profiles/ue5-coder/skills/software-development/
done

# Copy UE5 skills
mkdir -p profiles/ue5-coder/skills/unreal-engine
cp -r ~/.hermes/profiles/senna/skills/unreal-engine/* \
  profiles/ue5-coder/skills/unreal-engine/

# Copy game-dev-with-hermes
cp -r ~/.hermes/profiles/senna/skills/software-development/game-dev-with-hermes \
  profiles/ue5-coder/skills/software-development/

# Copy threejs skills to threejs-coder
mkdir -p profiles/threejs-coder/skills/software-development
for skill in threejs-cinematic-camera threejs-engine-trail threejs-postprocessing \
  threejs-shader-patterns threejs-simulation; do
  cp -r ~/.hermes/profiles/senna/skills/software-development/$skill \
    profiles/threejs-coder/skills/software-development/
done

# Commit and push
git add -A && git commit -m "add missing skills to profiles" && git push
```
