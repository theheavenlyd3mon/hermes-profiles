---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `${HERMES_HOME:-~/.hermes}/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Vault Maintenance

For duplicate detection, vault migration, and cleanup workflows, see `references/vault-maintenance.md`.

## Vault Structure Audit

When asked to review or assess an Obsidian vault's structure, evaluate these dimensions:

1. **Root MOC** — does the vault have a single entry point linking all folder MOCs? If not, orphan clusters form in graph view.
2. **Naming consistency** — are folders source-based (tied to a creator/series) or topic-based (system reference)? Mixed is fine but should be documented.
3. **Frontmatter uniform** — check YAML keys (title, type, tags, episode) are consistent across files.
4. **Cross-linking density** — do topic folders link to architecture/reference docs? Do episode files have prev/next chains?
5. **Orphan files** — files at root or in folders with no MOC linking to them.
6. **Stale metadata** — queue files, review artifacts, or tracking docs that no longer reflect reality.
7. **Git hygiene** — `.obsidian/workspace.json` in `.gitignore`? One-shot review artifacts archived or deleted?

Present findings as concrete, numbered tasks for user approval before executing. See `references/vault-renumbering.md` for the specific technique of renumbering files while maintaining wikilink integrity.

## Workflow Preferences

When proposing vault changes (cleanup, restructure, migration):
1. **Break into discrete, numbered tasks** — each task should be independently approvable. The user wants to approve/reject individual items, not a monolithic plan.
2. **Describe each task before executing** — state what will change and why. Don't start writing until the user approves.
3. **One canonical approach per task** — don't present a menu of alternatives. Pick the best option. (Exception: when a task genuinely has two valid paths the user must choose, like "delete vs archive".)
4. **List files explicitly before deleting** — show the exact paths so the user can review.
5. **Execute all approved tasks, report results** — file count before/after, broken links fixed, MOCs updated. One summary table at the end.
