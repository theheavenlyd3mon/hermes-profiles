---
name: markdown-corpus-digest
description: Use when reading a Markdown corpus to write one digest file.
---

# Markdown Corpus Digest

Consume a local corpus of Markdown pages and produce one standalone, topic-organized digest. Typical trigger: "read every page in <dir> (N files) and write one consolidated digest to <path>."

## Workflow

1. **Enumerate + count.** `search_files(pattern='*.md', target='files', path=<dir>)`. Note total vs. read count — some files are explicitly skipped (e.g. `log.md`). Report the accurate read count at the end.
2. **Read in parallel batches.** 6–8 `read_file` calls per turn. Pages are usually small; batch until all are read. Page through >100K-char files with `offset`.
3. **Recover binary-flagged .md files.** read_file may return "Binary file - cannot display as text" for a UTF-8 markdown file that merely contains embedded NUL bytes. Verify with `file <path>` (it will say "Unicode text, UTF-8 text" even though read_file refused), then recover:
   ```bash
   cat <file> | tr -d '\000'
   ```
4. **Scan for gated/paywall markers** before writing — grep the corpus for `PRO-ONLY|gated|XL|Pro`. The parent task often wants gated content flagged `[PRO-ONLY]` in the digest rather than silently included or omitted; the index page usually describes what the gated layer holds.
5. **Harvest frontmatter metadata.** Each page's YAML frontmatter carries `updated`, `confidence`, `sources`. Preserve: 'current as of' version (e.g. `v0.28.0`), the confidence mix (counts per level), and recency caveats ("sources fetched <date>; project ships weekly — expect drift").
6. **Write ONE digest in one `write_file` call** (parent dirs are auto-created):
   - Organize by topic — mirror the parent's requested section list exactly; each section condenses the relevant pages.
   - Keep concrete commands, file paths, and flags **verbatim** from the source pages — that is the actionable value.
   - Flag low-confidence content honestly (e.g. "reported patterns, not verified fixes").
   - Size: a few KB to ~15–30 KB — not a 1-line stub, not a 100 KB dump. Dedupe across pages; cross-link related topics instead of repeating.
7. **Return a tight summary:** absolute output path, total pages read, and a 5-bullet list of the most important actionable facts (concrete commands/paths, not prose).

## Pitfalls

- Don't web-fetch when content is already on disk — slower and explicitly discouraged in this task shape.
- read_file's binary flag ≠ corrupt file: NUL bytes make it refuse; `tr -d '\000'` is the fix. Never report a file unreadable without trying this.
- Preserve per-page confidence markers (e.g. "low confidence by design") — they are load-bearing for the consumer.
- Mark gated content with the parent's marker (e.g. `[PRO-ONLY]`) even when the gated pages are a separate set — the free-tier pages reference them.
- Trust the write result's `verified: true`; do not re-read the file to confirm.
