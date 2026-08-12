# Windowshermes Fleet — Skill Distribution Map

As of 2026-06-08. Update when adding/removing skills or profiles.

## Shared Skills (skills/software-development/)

All 7 profiles reference these via `skills.paths`:

| Skill | Purpose |
|-------|---------|
| token-compression | DSL encoding for lean prompts (critical on 32K context) |
| look-before-edit | Check deps before changing files |
| karpathy-coding-discipline | Surgical edits, no overengineering |
| systematic-debugging | 4-phase root cause debugging |
| tool-call-efficiency | Fewer tool calls = less context burned |
| writing-plans | Bite-sized task decomposition |

## Profile-Specific Skills

| Profile | Category | Profile Skills | Notes |
|---------|----------|---------------|-------|
| ue5-coder | unreal-engine | 30 UE + 8 software-dev + 3 game-dev | Most loaded profile |
| threejs-coder | threejs | 5 threejs skills | Shader/camera/postprocessing |
| arch | software-development | 3 (architecture-diagram, excalidraw, technical-documentation-authoring) | Design + viz |
| designer | design | 4 (sketch, claude-design, popular-web-designs, humanizer) | Creative output |
| blender-coder | blender | 1 (blender-automation) | Shading/export pipeline |
| worldbuilder | game-dev | 1 (obsidian) | Vault is primary workspace |
| abilities | unreal-engine | 0 profile-specific | Gets UE skills via category |

## Config Pattern

Every profile uses:
```yaml
skills:
  category: <profile-category>        # auto-discovers profile-specific skills
  paths:                               # explicit shared skills
    - ../../skills/software-development/token-compression
    - ../../skills/software-development/look-before-edit
    - ../../skills/software-development/karpathy-coding-discipline
    - ../../skills/software-development/systematic-debugging
    - ../../skills/software-development/tool-call-efficiency
    - ../../skills/software-development/writing-plans
```

## Adding a New Shared Skill

1. Copy SKILL.md (and references/) to `skills/software-development/<name>/`
2. Add `- ../../skills/software-development/<name>` to ALL 7 profile configs
3. Commit and push to the repo
4. Pull on the target machine and re-run install.sh (or manually copy)

## Adding a New Profile-Specific Skill

1. Copy to `profiles/<name>/skills/<category>/<skill-name>/`
2. If the skill's category matches `skills.category`, it auto-loads — no config change needed
3. If it's in a different category, add an explicit path entry in the profile's config
