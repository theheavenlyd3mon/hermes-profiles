# Vault-to-Repo Sync Workflow

Systematically scan an Obsidian vault for content useful to game-dev profiles, then copy organized chunks into the windowshermes repo vault.

## When to Run

When the Hermes Vault (main Obsidian vault) has accumulated new wiki concepts, research, or raw articles that could benefit the Windows game-dev team profiles.

## Workflow

### 1. Map Source Content

```bash
# Find all non-session, non-archive wiki content in the Hermes Vault
find "~/Hermes Vault/Hermes/llm-wiki/concepts" -name "*.md" | sort
find "~/Hermes Vault/Hermes/llm-wiki/raw/articles" -name "*.md" | sort
find "~/Hermes Vault/Hermes/llm-wiki/comparisons" -name "*.md" | sort
find "~/Hermes Vault/Hermes/llm-wiki/alloys" -name "*.md" | sort
```

### 2. Map Destination State

```bash
# What's already in windowshermes vault
find ~/projects/windowshermes/vault -name "*.md" -not -path "*/.obsidian/*" | sort

# What skills each profile already has
find ~/projects/windowshermes/profiles -name "SKILL.md" -exec dirname {} \; | sort
```

### 3. Identify Gaps

Read headers (first 15 lines) of source files to check tags and topics. Cross-reference against existing destination content. Focus on files whose tags match profile domains:

| Tags/Topics | Target Profile(s) | Vault Dir |
|-------------|-------------------|-----------|
| unreal-engine, rpg, cpp, gas | ue5-coder, arch | `UnrealEngine/` |
| blender, 3d-modeling, character-design | blender-coder | `Art/` |
| threejs, webgl, shaders, post-processing | threejs-coder | `Threejs/` |
| design, glassmorphism, ui | designer | `Design/` |
| anatomy, creature-design, fantasy-art | worldbuilder, blender-coder | `Art/` |

### 4. Copy and Organize

Domain-based directory structure in the vault:
```
vault/
├── UnrealEngine/concepts/    — UE5 system docs, learning paths, MCP bridges
├── UnrealEngine/references/  — Raw reference docs (GAS, etc.)
├── Art/concepts/             — Blender, anatomy, creature design
├── Design/concepts/          — Design patterns, game architecture
├── Threejs/concepts/         — Three.js techniques (lighting, particles, shaders)
└── Threejs/references/       — Library USAGE files (pre-existing)
```

### 5. Verify

```bash
# Batch diff-check all copied files
for src in <sources>; do
    diff -q "$src" "$dest_dir/$(basename $src)"
done
```

### 6. Update vault/README.md

Update the vault structure tree and agent team table to reflect new directories.

### 7. Commit and Push

Single commit per sync batch. Message format:
```
import Hermes Vault wiki content: <comma-separated domain summaries>
```

## Pitfalls

- **Don't duplicate skills as vault files.** If ue5-coder already has a `ue-gameplay-abilities` skill, don't copy the GAS concept as a vault file — the skill IS the reference. Only copy wiki content that doesn't have a corresponding skill.
- **Raw articles vs concepts.** Concepts are distilled and structured. Raw articles are ingested source material. Prefer concepts for the vault; only include raw articles for canonical references (like GAS documentation).
- **Check for overlap.** Some wiki concepts compose each other (e.g. `fantasy-creature-design` composes `face-anatomy-for-artists`). Copy both — they're independently useful.
- **Frontmatter-only files are OK.** Some wiki concepts are seedlings with just frontmatter. Still worth copying — the metadata is useful context for the profiles.

## Sources

| Source Path | Content Type |
|-------------|-------------|
| `Hermes Vault/Hermes/llm-wiki/concepts/` | Distilled wiki concepts |
| `Hermes Vault/Hermes/llm-wiki/raw/articles/` | Ingested source articles |
| `Hermes Vault/Hermes/llm-wiki/comparisons/` | Framework/tool comparisons |
| `Hermes Vault/Hermes/llm-wiki/alloys/` | Multi-concept workflow recipes |
