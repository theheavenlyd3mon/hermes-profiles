# Promotion Rules

Use these rules when moving content from `notes/` into `llm-wiki/`.

## When to promote

Promote when the content:
- has stabilized into a stable fact, concept, entity, or decision
- is referenced more than once or likely to be referenced again
- would benefit from being queryable in Obsidian Graph View
- becomes part of operational context or future work

Do not promote when the content is:
- transient, experimental, or superseded
- already represented elsewhere in wiki form
- a short scrap better left in `notes/`

## Type mapping

- concept topic → `llm-wiki/concepts/`
- person → `llm-wiki/entities/`
- company/product/model → `llm-wiki/entities/`
- side-by-side analysis → `llm-wiki/comparisons/`
- narrative synthesis → `llm-wiki/alloys/`
- saved query outcome → `llm-wiki/queries/`
- agent decision or protocol → `llm-wiki/operational/`

## Source preservation best practice

When promoting, prefer one of these:
- Add `sources: ["notes/<file>"]` to the promoted page.
- Update frontmatter with a relation, e.g., `promoted_from: notes/<file>`.
- Add a ## Source block in the promoted page with a `[[wikilink]]` back to the original note.

If the promoted page fully subsumes the source note, the user may choose to archive the original rather than delete it.
