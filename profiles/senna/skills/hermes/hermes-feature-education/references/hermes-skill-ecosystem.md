# Hermes Skill Ecosystem

How skills are sourced, where they live, and how to replicate them across machines.

## Three Skill Sources

| Source | Origin | Protected? | Updates | Available To |
|--------|--------|------------|---------|-------------|
| **Builtin** | Ships with Hermes Agent installation (`<hermes-root>/skills/`) | ✅ Yes — DO NOT edit | Via `hermes update` | All profiles automatically |
| **Created** | Made via `skill_manage(action='create')` | ❌ No — fully editable | Manual via `skill_manage(action='patch')` | Only the profile that created them |
| **Installed** | Pulled from catalogs (Hub, IKnowKungFu, git repos) via `hermes skills install` or `mcp_iknowkungfu_install_skill` | ✅ Yes — DO NOT edit | Re-install from source | Only the profile that installed them |

### Builtin Skills (most common)

Shipped with every Hermes install. ~220 builtins across categories:
- `hermes/*` — agent management, gateway, profiles, SOUL, cron
- `software-development/*` — debugging, planning, code review, TDD
- `unreal-engine/*` — 25 UE skills (actor-component, GAS, animation, CMC, input, etc.)
- `devops/*`, `creative/*`, `research/*`, `github/*`, `note-taking/*`, etc.

**Key property:** Builtins follow the Hermes installation, not individual profiles. Every profile on a given Hermes install can see them. No file copying needed.

### Created Skills

Made by the agent mid-session using `skill_manage`. Stored in `~/.hermes/profiles/<profile>/skills/`. These are specific to one profile — other profiles cannot see them unless explicitly seeded.

### Installed Skills

Installed from external registries will be stored in the profile's `skills/` directory. Protected from edits by design.

## How Skills Load

When a session starts, Hermes loads skills into the system prompt:
1. **Builtins** from `<hermes-root>/skills/` — category-matched to the profile's config
2. **Profile-specific** from `~/.hermes/profiles/<profile>/skills/` — agent-created and installed skills

This means a skill file physically located at `~/.hermes/profiles/senna/skills/unreal-engine/ue-actor-component-architecture/SKILL.md` is loaded ONLY when running under the `senna` profile — not when `ue5` or `code` profiles are active. Each profile's skill config determines what loads for that session.

**Builtins are different:** they're served from a central location (the Hermes install dir) and referenced by category mapping, not by file. So `unreal-engine/*` skills load for any profile whose config says `category: unreal-engine`.

## Cross-Machine Profile Setup

When setting up a second Hermes instance (e.g., Windows PC):

### Builtin skills
These come with Hermes. Steps:
1. Update Hermes on the target machine (`hermes update`)
2. Ensure the profile's config includes the right categories
   ```yaml
   # ~/.hermes/profiles/ue5-coder/config.yaml
   skills:
     categories: [unreal-engine, software-development, github]
   ```
3. Builtins auto-load. No file transfer needed.

### Created skills
These are profile-specific and must be copied:
```powershell
# From source machine (Mac) to target machine (Windows)
# Copy the skill files
xcopy /E /I "\\macshare\.hermes\profiles\senna\skills\custom-skill" "%USERPROFILE%\.hermes\profiles\ue5-coder\skills\custom-skill"
```

### Installed skills
Re-install on the target machine from the original source:
```powershell
hermes skills install <source>
```

## FAQ

**Q: "Are these builtin or did we create them?"**
A: The 25 `ue-*` skills are **Hermes builtins**. They ship with every Hermes installation. Neither of us wrote them — Epic/Unreal Engine experts at the Hermes project maintain them.

**Q: "I updated the UE skills — will my Windows PC get the update?"**
A: Yes — builtins update with `hermes update`. Run that on Windows and the updated versions are available. No manual copy needed.

**Q: "How do I make my ue5-coder profile on Windows have the same skills as the Mac ue5 profile?"**
A: Ensure the profile's config includes the `unreal-engine` category. Builtins auto-load. No file sync required.

**Q: "What if I created a custom skill on Mac that I want on Windows?"**
A: Those need manual transfer. Use the `hermes-profile-publishing` skill to package them, or copy the skill directory directly.
