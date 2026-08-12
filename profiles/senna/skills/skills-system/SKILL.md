---
name: skills-system
description: Skills system architecture — progressive disclosure, frontmatter, platform filtering, self-editing
version: 1.0.0
---
# Skills System

Skills are procedural memory — reusable recipes stored as markdown. The system uses progressive disclosure to stay token-efficient.

## Layout

```
skills/
├── simple-skill.md              # flat
└── domain/                      # domain-grouped
    └── skill-name/
        ├── SKILL.md             # main instructions (required)
        └── references/          # linked files (loaded on demand)
```

## Three disclosure tiers

- `skills_list` → name + one-line summary only (~100 tokens each)
- `skill_view(name)` → full SKILL.md body
- `skill_view(name, file_path)` → linked reference file

## Self-growing

- `skill_manage(create, name, content=...)` → write a new skill
- `skill_manage(patch, name, old_string, new_string)` → fix a gap
- `skill_manage(edit, name, content=...)` → full rewrite
- `skill_manage(delete, name)` → remove

## PITFALL: Platform filtering

`sys.platform` on macOS returns `"darwin"`, NOT `"macos"`. When filtering skills by platform, map `darwin` → `macos` before checking membership. See `references/platform-mapping.md` for the exact code pattern.

## PITFALL: Linked files require directory-based skills

`skill_view(name, file_path)` resolves the file relative to the skill's directory. Flat-file skills (`skills/name.md`) don't have a directory, so linked files won't work. Use `skills/domain/name/SKILL.md` if you need references/templates/scripts.

## PITFALL: Support file filtering

When scanning for skills, skip files in `references/`, `templates/`, `assets/` directories. Check ALL path parts, not just `parts[1]` — a path like `domain/skill/references/api.md` has `parts[1] == "skill"`, not `"references"`.