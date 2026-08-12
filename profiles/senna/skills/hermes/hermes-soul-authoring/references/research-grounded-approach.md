# Research-Grounded Approach — Workflow Checklist

> Use this before drafting any domain-specific SOUL.md or skill.
> Prevents guessing on API conventions, deprecations, and workflow patterns.

## Pre-Draft Research Pass

- [ ] **Release notes searched** — `web_search` `<technology> <version> release notes` from authoritative source
- [ ] **Authoritative docs extracted** — `web_extract` on release notes page. Note specific API changes and new features.
- [ ] **Deprecations checked** — `web_search` `<technology> <version> deprecated API changes migration guide`
- [ ] **Ecosystem tooling checked** — `web_search` `<technology> <version> MCP` or `<technology> <version> agent`
- [ ] **Community migration sources checked** — blogs and third-party summaries often have the most concise API change lists (e.g., slowburn.dev for UE, migration guides)
- [ ] **Research brief compiled** — saved to `research/<topic>-research-brief.md`
- [ ] **Draft sources cited** — every claim about API, convention, or deprecation in the final draft must trace back to a source in the brief

## What Not To Do

❌ Draft from memory of an older version
❌ Guess API names or signatures
❌ Omit version number in DEFAULTS or STYLE sections
❌ Skip researching MCP/tooling integration (this is what enables smooth agent workflow)

## Source Priority

1. **Official docs** (dev.epicgames.com, docs.python.org, etc.) — release notes, API reference, migration guide
2. **Official announcement** (unrealengine.com/news, blog posts) — feature overview, production-ready status
3. **Curated community sources** (slowburn.dev, strayspark.studio) — concise API change lists
4. **Forums/github** — for ecosystem tools (MCP bridges, plugins)
5. **Everything else** — lowest confidence, verify against official source before using

## Real Example: UE 5.8 Research (2026-06-26)

| Step | Source | Key Finding |
|------|--------|-------------|
| Release notes | dev.epicgames.com | MegaLights Production Ready, Iris Prod Ready, Mesh Terrain Experimental |
| Deprecations | slowburn.dev | 21 API changes: `FProperty::ElementSize`→`GetElementSize()`, `UClass::ClassDefaultObject`→`GetDefault<>()`, `RunUBT` replaces `UnrealBuildTool` |
| MCP ecosystem | forums/epic + github | 3 bridges: native Unreal MCP (5.8 built-in), AgenticLink (paid), ue5-mcp-bridge (OSS) |
