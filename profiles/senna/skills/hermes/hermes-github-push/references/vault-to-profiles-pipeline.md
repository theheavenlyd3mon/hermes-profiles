# Vault-to-Profiles Content Pipeline

When updating windowshermes game-dev profiles, check the Hermes Vault llm-wiki for content that should be copied over.

## Content Sources

**Hermes Vault (Obsidian):** `~/Hermes Vault/Hermes/llm-wiki/`
- `concepts/` — distilled knowledge (concept pages with frontmatter)
- `comparisons/` — side-by-side tech comparisons
- `raw/articles/` — ingested source articles (longer, less distilled)
- `alloys/` — cross-domain synthesized pages

**windowshermes vault:** `~/projects/windowshermes/vault/`
- `World/Lore/` + `World/Characters/` — Eldrath game world
- `Design/` — game design docs
- `Threejs/` — Three.js reference library

## Profile-to-Content Mapping

| Profile | Relevant llm-wiki topics |
|---------|-------------------------|
| ue5-coder | unreal-engine-rpg-systems, unreal-engine-solo-rpg-learning-path, unreal-engine-mcp-bridge-comparison, open-source-ue5-game-references, unreal-engine-llm-tooling |
| arch | unreal-engine-mcp-bridge-comparison, open-source-ue5-game-references, system-design concepts |
| blender-coder | ai-blender-workflows, blender-shading-compositing, face-anatomy-for-artists, fantasy-creature-design |
| designer | glassmorphism, liquid-glass-design-system, html-as-communication-medium |
| worldbuilder | face-anatomy-for-artists, fantasy-creature-design, Eldrath lore |
| threejs-coder | threejs-cinematic-lighting, threejs-glow-and-effects, threejs-hologram-particle-techniques, threejs-video-export, threejs-particle-effects, threejs-model-optimization, threejs-performance-optimization, threejs-shader-techniques |

## Workflow

1. List concept files: `find "~/Hermes Vault/Hermes/llm-wiki/concepts" -name "*.md"`
2. List existing profile skills: `find ~/projects/windowshermes/profiles -name "SKILL.md"`
3. Diff — find vault concepts not yet in profiles
4. Copy relevant .md files into profile `vault/` or as skill references
5. Commit + push via `hermes-github-push` workflow

## Pitfall: Don't Duplicate Skills

If a profile already has a skill covering the same topic (e.g. ue5-coder has `ue-gameplay-abilities` which covers GAS), don't copy the wiki concept as a competing skill. Instead:
- Copy it as a reference file under the existing skill, OR
- Skip it if the skill already covers the same ground

## Pitfall: Raw Articles Are Too Long

`raw/articles/` files are often 500+ lines of ingested web content. Don't copy these directly into profiles. Use the distilled `concepts/` versions instead — they're shorter, have frontmatter, and cross-reference each other.
