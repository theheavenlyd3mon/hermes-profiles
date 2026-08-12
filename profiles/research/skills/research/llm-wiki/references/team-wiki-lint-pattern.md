# Team-Wiki Lint Pattern

Diagnosing an empty/skeleton Team-Wiki is a common cron audit finding.

## Signals

1. **Only README.md placeholders** in entities/, concepts/, comparisons/, queries/
   — 3-line stubs with no frontmatter, just "# CategoryName" and "# Primary home for..." text.
2. **index.md has commented-out wikilinks** with `<!-- List: [[slug]], ... -->` syntax
   that's inside the comment marker but the `[[` `]]` may render as broken links if
   the comment isn't properly formed.
3. **Index header placeholder** — literal `$(date +%Y-%m-%d placeholder)` in the
   "Last updated" field.
4. **Log has only the init entry** — single `create | Wiki initialized` entry from
   creation date.
5. **No content pages** — zero files in subdirectories that aren't README.md.

## How to Report

- **Don't flag README.md as orphans** — they're structural. Note them as placeholders.
- **Do flag index entries that reference nonexistent pages** — even commented-out
  `[[agent:foreman]]`-style links should be cleaned up or created.
- **Do flag the $(date) placeholder** — it indicates the index was never finalized.
- **Do note how long the skeleton has existed** — if >14 days, it's likely abandoned
  setup rather than an in-progress workstream.

## Remediation Options (for reference, not to execute without approval)

- **Populate:** Create entity/concept pages matching the index placeholders.
- **Archive:** Move the entire Team-Wiki to `_archive/` and remove from index.
- **Merge:** If content is better placed in LLM-Wiki, cross-link or absorb.
- **Remove:** If Team-Wiki is wholly replaced by another system, delete the directory.
