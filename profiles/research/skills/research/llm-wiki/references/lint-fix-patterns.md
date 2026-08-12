# Lint Fix Patterns

Quick reference for fixing common wiki lint findings. Use after running `scripts/wiki-lint.py`.

## Broken Wikilinks

Three categories, each with a different fix:

| Link type | Example | Fix |
|-----------|---------|-----|
| Skill/tool reference | `[[blender-automation-skill]]` | Replace with plain text (no wiki page needed) |
| Technical term | `[[principled BSDF]]` | Replace with backtick-quoted: `` `Principled BSDF` `` |
| Project/codename | `[[Neon Approach]]` | Replace with italic: `*Neon Approach*` |
| Genuine wiki page (typo) | `[[agentic-practices]]` (missing word) | Fix the slug to match existing page |
| Genuine wiki page (missing) | `[[new-concept]]` (3+ backlinks) | Create the page (ghost note threshold met) |

**Rule:** Only create a page for a broken link if it has 3+ backlinks (ghost note threshold). Otherwise, convert to appropriate inline format.

## Index Mismatches

| Finding | Fix |
|---------|-----|
| Page on disk, not in index | Add entry alphabetically under correct section |
| Entry in index, no page file | Remove from index (or create the page if it should exist) |

When adding to index.md, find the correct alphabetical position within the section. Use `execute_code` with Python for batch index edits — `patch` creates duplicates when adding multiple entries sequentially.

## Low Outbound Wikilinks (<2)

Find the page's `## Related` section and add cross-references to conceptually related pages. If no Related section exists, add one before the end of the file. Prefer links to pages that already link TO this page (bidirectional linking).

## Source Drift (SHA256 Mismatch)

Informational — don't auto-fix. The raw file was modified after ingestion. Report to user. If the stored hash is a placeholder pattern (e.g., `placeholder`, repeating hex), flag it as "needs real computation" rather than "drift."

## Tags Outside Taxonomy

Two cases, different fixes:

**Few tags (1-5):** Suggest remapping to taxonomy-equivalent (e.g., `methodology` → `workflow`). Only add to SCHEMA.md if the tag genuinely represents a new domain.

**Batch drift (10+ tags):** The wiki domain expanded without updating the taxonomy. Group the missing tags by category, add them to SCHEMA.md in bulk under the appropriate sections, then re-run lint to confirm. This is faster and less error-prone than remapping dozens of pages. Example: a wiki that grew to cover Unreal Engine needs `unreal-engine`, `cpp`, `blueprints`, `gas`, `rpg`, `dialogue`, `inventory`, `quests`, `save-system` added as a batch under a new "Unreal Engine & Game Development" section.

**Regex edge case:** The lint script's tag-extraction regex (`[a-z][a-z0-9-]+`) misses tags starting with digits (e.g., `3d-modeling`). If a known-valid tag keeps appearing as "not in taxonomy" despite being in SCHEMA.md, check whether the regex matches it. Fix: change to `[a-z0-9][a-z0-9-]+` in `scripts/wiki-lint.py` line with `re.findall`.

## Pages >200 Lines

Informational — flag for user review. Don't auto-split. The page may be fine at 220 lines if it's cohesive.

## Verification

After fixing, re-run the lint script to confirm:
```bash
python3 scripts/wiki-lint.py <wiki_path> 2>&1 | grep -E "^\[ERR\]|^OK"
```
