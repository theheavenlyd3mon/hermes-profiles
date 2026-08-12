# Promotion cheat sheet

Use this when moving knowledge from `notes/` into `llm-wiki/`.

## Promotion gateway checklist

Is the content...
1. stabilized into a fact, concept, entity, or decision?
2. referenced more than once or likely to be referenced again?
3. worth surfacing in Obsidian Graph View?
4. part of operational context or future work?

If mostly yes → promote. If mostly no → leave in `notes/`.

## Fast type mapping

- concept topic → `llm-wiki/concepts/`
- person → `llm-wiki/entities/`
- company/product/model → `llm-wiki/entities/`
- side-by-side analysis → `llm-wiki/comparisons/`
- narrative synthesis → `llm-wiki/alloys/`
- saved query outcome → `llm-wiki/queries/`
- agent decision or protocol → `llm-wiki/operational/`

## Source preservation defaults

- `sources: ["notes/<file>"]` on the promoted page
- if available: `promoted_from: notes/<file>` in frontmatter
- if relevant: `## Source` block with `[[wikilink]]` back to original note

## Archive vs delete

Never delete source notes outright. Default to leaving them in place. Only move/archive if:
- the promoted page fully subsumes all facts in the original
- the original is a transient scrapped note
- the user explicitly asks to remove it
