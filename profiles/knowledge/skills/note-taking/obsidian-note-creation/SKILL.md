---
name: obsidian-note-creation
description: "Atomic Obsidian note creation: resolve vault path, pick the right container, check for duplicates, draft structured notes, patch existing pages, and update the nearest MOC/index."
version: 1.0.0
author: Senna (Hermes)
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [obsidian, notes, wiki, atomic, knowledge-base]
    category: note-taking
    related_skills: [note-taking/obsidian, productivity/obsidian-vault-audit, team-wiki/setup, memory-curator]
---

# obsidian-note-creation

IDENTITY: Librarian.AtomicNote. ResolvePath→FindHome→SearchDupes→DraftOrPatch→Backlink→Index→Verify.
Law: UseFileToolsNotShell. AtomicBeforeLongform. ExistingHomeFirst.
WHENUSE: User mentions a concept/person/decision/research item that should become a note|Capturing stable knowledge|Promoting notes/ to wiki.
ESPECIALLY:NewEntityCreation|ExistingNotePatch|MOCUpdate|Promotion|DuplicateMerge|FrontmatterMaintenance.
NoSkip:PathResolution|DuplicateCheck|WikilinkRequirement|IndexUpdate.

## Trigger

Use this when the user:
- mentions a new concept, entity, decision, or research item
- asks to capture, document, or file something in the vault
- wants atomic notes rather than sprawling documents

## Vault path

Resolve before any file-tool call:
1. Read `OBSIDIAN_VAULT_PATH` from environment, typically `~/.hermes/.env`.
2. If missing or unset, use `~/Hermes Vault/Hermes` for this user's vault.
3. Once resolved, use the concrete absolute path for `read_file`, `write_file`, `patch`, and `search_files`.
4. Use terminal only to resolve the path; all other ops should stay in file tools.
5. For full vault structure, Icarus conventions, and notes/icarus layout, see `note-taking/obsidian`.

## Preferred containers

This vault is wiki-first with a quick-capture layer. Pick the narrowest correct home:

- `llm-wiki/concepts/` — topics, frameworks, techniques
- `llm-wiki/entities/` — people, companies, products, models
- `llm-wiki/comparisons/` — side-by-side analyses
- `llm-wiki/alloys/` — narrative syntheses
- `llm-wiki/queries/` — past query results worth keeping
- `llm-wiki/operational/` — agent decisions, protocols, conventions
- `notes/` — emerging or low-stability captures; promotion target is `llm-wiki/`

## Duplicate check (do this before creating)

Do both:
- filename search: `search_files(target='files', pattern='<slug>*', path='<container>')`
- content search: `search_files(target='content', pattern='<Title or alias>', file_glob='*.md', path='<llm-wiki/>')`

If a clear match exists, prefer patching it. If two candidates exist, read both and choose one canonical page; link the other as a redirect or merge them.

## New note template

```yaml
---
title: "Human-Readable Title"
type: concept|person|company|comparison|alloy|query
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [stable, tags, here]
sources: ["<optional paths or URLs>"]
---

## Summary
One or two sentences defining the note.

## Facts
- bullet
- bullet with [[wikilink]]

## See Also
- [[related-note]]
```

Rules:
- Keep it atomic. One subject per note.
- Include at least one `[[wikilink]]`.
- Prefer short bullets over long prose.
- Keep frontmatter complete; missing `title`, `type`, `created`, `updated`, or `tags` is a defect.
- When creating entities with known aliases, include aliases in the note body rather than creating duplicate pages.

## Patch workflow when the note already exists

1. Read the file.
2. Identify the best anchor:
   - `## Timeline` → append a dated bullet
   - `## Current` → append a current-state bullet
   - no good anchor → add a new short dated section
3. Patch with minimal context to keep it surgical.
4. Update `updated:` in frontmatter.
5. Keep or add wikilinks for any newly mentioned entity.

## MOC / index update

After creating or materially updating a note:
- Identify the nearest index or category listing, typically `llm-wiki/index.md` or a subcategory index.
- Add or update the entry under the appropriate heading.
- Keep it compact: `- [[Note Title]] — one-line description`.

For promotions from `notes/`:
- Add a `promoted_to:` or source relation if applicable.
- Leave the source `notes/` file in place unless the user wants it removed.

## Verification

After write or patch:
- Re-read the target file and confirm rendered shape: frontmatter, summary, bullet facts, wikilinks.
- Confirm each `[[wikilink]]` target exists; if not, create a stub or stop and report.
- Ensure the path does not contain shell-problematic characters.
- Ensure the note remains atomic and does not absorb unrelated subjects.

## Promotion rules

Use `references/promotion-rules.md` for:
- when `notes/` content should move to `llm-wiki/`
- which tier becomes which `type`
- how to preserve source/history during promotion
- promotion gateway checklist and fast type mapping

Use `references/promotion-cheat-sheet.md` for:
- quick promotion decisions during live note creation
- source preservation defaults and archive vs delete guidance

## Common mistakes to avoid

- creating a new note when an existing note is the right home
- creating scattered session notes instead of updating an existing operational note
- longform sprawl inside a note meant to be atomic
- missing frontmatter fields
- wikilinks without an actual page target
- editing mirrored/read-only files without checking whether they are agent-generated
