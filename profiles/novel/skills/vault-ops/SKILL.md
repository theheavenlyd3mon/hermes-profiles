---
name: vault-ops
description: Systematic Obsidian vault audit and normalization — structure, frontmatter, wikilinks, broken links, Git hygiene.
platforms: [linux, macos, windows]
---

# Vault Operations — Obsidian Normalization & Audit

Systematic procedures for auditing and normalizing Obsidian vaults when they arrive unstructured, headerless, or flat. Target: make a vault queryable and graph-friendly without manual editing.

## When to invoke

- User reports an Obsidian vault feels messy, disconnected, or hard to navigate
- Manuscript/fiction pipeline lands in an Obsidian directory with no frontmatter on planning docs
- Any time a project directory doubles as an Obsidian vault root (common with novel pipelines)

## Prerequisites

Resolve vault path first: check `$OBSIDIAN_VAULT_PATH`, fallback to `~/Documents/Obsidian Vault`. Never pass shell variables to file tools.

Use execute_code (Python) for all scanning — never ls/grep/find/shell loops. File tools handle reads/writes.

## Audit Procedure (9 dimensions)

Run a single Python scan covering all dimensions below. Present results as a table before proposing fixes.

### 1. Depth distribution
Walk vault recursively. Count files at each directory depth level. Flat = most at depth 0–1. Report counts per level. Flag if >50% at depth 0 (no hierarchy) or any file at depth >3 (too nested).

### 2. Root MOC
Check if any file at depth 0 looks like a master index (names containing "MOC", "index", "overview", "directory"). If none exists, note that the graph will have no entry point.

### 3. Naming consistency
Extract basenames. Count how many use snake_case, kebab-case, camelCase, spaces, or mixed. Mixed separators within a single filename is the worst case — flag it explicitly.

### 4. Frontmatter presence
Read top 200 chars of every .md. Check if line starts with `---`. Count with-frontmatter vs without. Files without ANY frontmatter break all Obsidian community plugins' metadata features. This is usually the #1 finding in manuscript-project-as-vault setups.

### 5. Cross-linking density
Regex-scan all .md for `[[...]]` patterns. List files that contain wikilinks and their counts. Zero across the board = disconnected graph nodes. This is common with fresh manuscript projects that haven't started cross-referencing yet.

### 6. Broken wikilinks
Extract every `[[name]]` from all files. Match against actual filenames in the vault. Report dangling links. Do NOT auto-fix broken links — present them to user first (could be intentional aliases or planned future notes).

### 7. Orphan analysis
Files with zero outgoing wikilinks AND zero incoming wikilinks are structural orphans. They exist in the vault but aren't connected to anything. Report count and list names. (Note: some orphans are fine — standalone reference notes.)

### 8. Git hygiene
Check `.git` directory presence. Check `.obsidian/workspace.json` contents for recently-opened files (confirms vault state). Verify `.gitignore` excludes workspace files if git exists.

### 9. Vault-path anomaly
If vault root equals a manuscript/project repo root, warn: conflation of tool config with content complicates migration. Note what files serve dual purpose.

## Frontmatter Auto-Normalize

When audit finds >5 headerless files and user has approved frontmatter addition:

1. Classify each file into a type: `canon`, `character`, `plot`, `worldbuilding`, `voice`, `concept`, `foreshadow`, `outline`, `reference`, `meeting`, etc.
2. For each file, prepend minimal YAML: `title`, `type`, `status`, `tags`.
3. Tags should always include: `[project-name, context-label]` (e.g., `[eldrath, book-1, world-rules]`).
4. Run via execute_code: read each file, check if already has `---`, prepend only if missing, write back.
5. Report updated vs skipped files.

File-type metadata mapping (author-preferred):

| Type | Typical files | Standard keys |
|------|--------------|---------------|
| canon | canon.md | title, type, status, tags: [project, rules] |
| character | character-sheet.md, characters/*.md | title, type, status, tags, protagonist, race |
| concept | concept.md, pitch.md | title, type, status, tags, series_title, book_number |
| plot | plot-ledger.md, beat-sheet.md | title, type, status, tags, framework, chapters_target |
| worldbuilding | worldbuilding.md, lore.md | title, type, status, tags, power_system, pillars |
| voice | voice-profile.md, style-guide.md | title, type, status, tags, tone_anchor, register |
| foreshadow | foreshadow-bank.md | title, type, status, tags, tracking: plants-payoffs |
| outline | outlines/synopsis.md, chapter-outline.md | title, type, status, tags, word_count_target |

Frontmatter template format (always triple-dash delimiters, blank line before body):

```yaml
---
title: <basename without .md>
type: <classified_type>
status: draft
tags: [project-name, label-1, label-2]
<additional_keys>: <values>
---
```

Execute via bulk Python script — never edit files individually with patch unless there are exactly 1–2 to fix.

## Pitfalls

- **Don't auto-create MOC files** — only after user confirms they want them. Some vaults intentionally live flat.
- **Don't merge directories** — a flat layout may be user preference. Only report; don't restructure without explicit approval.
- **Broken wikilinks might be intentional** — `[[Future Character]]` could be a planned note. Always present first, fix later.
- **Don't touch .obsidian/ directory** — app.json, workspace.json, core-plugins.json are Obsidian internals. Auditing them for diagnostics is fine; modifying them is not.
- **Vault = project root** is a real pattern (manuscript notebooks). Warn once, don't try to separate them unless user asks.

## Verify

After changes: re-run audit dimensions 4 (frontmatter presence) and 5 (cross-linking) to confirm improvement. All previously-headerless files now have headers. All previously-flagged items resolved.

See `references/vault-maintenance.md` for duplicate detection and bulk-deletion workflows (from obsidian skill umbrella).
