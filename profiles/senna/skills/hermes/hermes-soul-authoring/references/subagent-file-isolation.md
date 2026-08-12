# Subagent File Write Isolation

> Subagents write to their own sandboxed filesystem. Files created by subagents are NOT visible in the parent terminal's sandbox.

## The Problem

When you use `delegate_task` with subagents that call `write_file`, the files are written to the subagent's isolated sandbox — not the parent's working directory. After the subagent completes, the parent terminal cannot find those files.

## What Happened (2026-06-12)

1. Parent delegated 3 subagents to write SOUL.md files to `~/Downloads/soul-drafts/`
2. All 3 subagents reported success
3. Parent tried `cp ~/Downloads/soul-drafts/*.md ~/.hermes/profiles/*/SOUL.md` — files didn't exist
4. Had to rewrite all 21 files directly in the parent context

## Workaround

**Option A: Write directly in parent context** (preferred for files that need to persist)
- Use `write_file` or `terminal` in the parent agent's own context
- Files are immediately available for subsequent operations

**Option B: Use terminal copy in subagent** (if delegation is needed)
- Have subagent write to a temp path, then `cat` the content to stdout
- Parent reads the output and writes files directly

**Option C: Use `skill_manage(action='write_file')`** (for skill files only)
- `skill_manage` writes to the skill directory, which is NOT sandboxed
- Works for skill support files, not arbitrary output files

## Rule of Thumb

If the parent needs to USE the files after the subagent finishes (copy, deploy, verify), write them in the parent context directly. Use subagents for analysis, research, and tasks whose deliverable is a summary — not file artifacts.
