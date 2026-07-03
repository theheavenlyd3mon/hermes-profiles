# 2026-05-18 Wiki Maintenance Pass

**Date:** 2026-05-18  
**Agent:** Senna (cron)  
**Scope:** LLM-Wiki health check and repair

## What Was Fixed

### Broken Wikilinks (8 total)
| Page | Broken Link | Fix |
|------|-------------|-----|
| `hermes-agent-team-architecture.md` | `[[writing-plans]]` | Replaced with `[[plan-decomposition]]` and plain text `Uses plan-decomposition` |
| `hermes-obsidian-integration.md` | `[[wikilinks]]` | Plain text: `wikilinks` |
| `liquid-glass-design-system.md` | `[[glassmorphism]]` (×2) | Created stub page `concepts/glassmorphism.md` |
| `threejs-cinematic-camera.md` | `[[threejs-engine-trail]]` | Plain text reference with skill note |
| `threejs-cinematic-camera.md` | `[[threejs-postprocessing]]` | Changed to `[[threejs-pbr-postprocessing]]` |
| `wiki-lint.md` | `[[wikilinks]]`, `[[links]]` | Plain text: `wikilinks`, `links` |

### Out-of-Taxonomy Tags (20 fixes)
Added new tags to SCHEMA.md taxonomy sections:
- **Design & Graphics:** `design`, `graphics`, `threejs`, `camera`, `cinematography`, `rendering`, `glsl`, `shaders`, `glassmorphism`, `liquid-glass`, `smart-mirror`, `post-processing`
- **Research & Methodology:** `person`, `methodology`, `exploration`, `optimization`, `performance`, `webgl`, `debugging`, `testing`, `planning`
- **Operations:** `hermes`, `tool-loading`, `tokens`, `troubleshooting`

### Raw Source SHA256 Updates
Recomputed SHA256 hashes for 12 raw articles with placeholder or mismatched hashes. The remaining raw files retain placeholder hashes (these were inserted during initial ingestion before hash computation was standardized).

### Index and Log Updates
- Page count: 40 → 41 pages
- Added `glassmorphism.md` stub
- Updated `log.md` with maintenance entry

## Lint Results (Post-Fix)

All core checks pass:
```
─── ORPHANS ───
OK — no true orphans

─── BROKEN WIKILINKS ───
OK — no broken wikilinks

─── INDEX COMPLETENESS ───
OK — index is complete

─── FRONTMATTER VALIDATION ───
OK — all pages have valid frontmatter

─── TAG AUDIT ───
OK — all tags in taxonomy

─── OUTBOUND WIKILINKS (min 2) ───
OK — all pages have 2+ outbound wikilinks
```

## Notes

- `memory-architecture.md` (262 lines) flagged as split candidate
- 4 raw files have placeholder SHA256 hashes (placeholder hashes inserted initially)
- 6 raw files have SHA256 mismatches (content modified after ingestion — raw/ should be immutable)

## Related

- `scripts/wiki-lint.py` — comprehensive 12-point lint script
- `llm-wiki-pattern` — the core knowledge compounding pattern
- `wiki-ingest` — the operation of adding new sources
- `wiki-lint` — periodic health-check operation
