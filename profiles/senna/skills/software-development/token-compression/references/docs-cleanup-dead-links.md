# Docs Cleanup Pass: Dead Links and Schema Drift

Use when reviewing markdown docs for correctness after making bulk changes to a repo.

## Trigger signals
- Added new profiles, guides, or sections
- Moved/renamed files
- External contributors report "linked file missing"

## Checks
- Tone/voice: consistent second-person, no "more coming soon" filler.
- Completeness: every profile listed in README actually exists in `profiles/`.
- Links: relative links from `guides/*.md` must use `../`, not `./`, for repo-root targets.
- Skills sections: if a profile README claims to follow a pattern, ensure `## Skills` exists.
- Tables: orchestrator/worker role lists must match actual roles in each SOUL.md.

## Fix pattern
1. Reproduce the broken state.
2. Apply smallest possible patch to each file.
3. Re-run `git add -A` and verify status before committing.

## Example
- Bad: `[Obsidian Setup Guide](./hermes-obsidian-setup-guide.md)` from inside `guides/`
- Good: `[Obsidian Setup Guide](../hermes-obsidian-setup-guide.md)`
