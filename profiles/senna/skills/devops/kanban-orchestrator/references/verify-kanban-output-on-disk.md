# Verify Kanban output is real (board "done" ≠ disk real)

A kanban task showing `status: done` only means the *worker process* exited cleanly.
It does NOT prove files were created/edited — especially if the task ran against a
wrong/missing `--workspace` path (the worker completes with phantom/empty output).

This is the most dangerous failure mode because it looks legitimate: the board is
green, the summary says "done", but nothing on disk changed.

## The trust-the-disk recipe (run after any bulk wave)

From the REAL workspace root (the one you intended, not the one the task claimed):

```bash
cd /real/vault/path
# 1. What actually changed vs git HEAD?
git status --short
git diff --stat
# 2. Did the expected annotation/frontmatter actually land?
grep -rl "ue_version:" . --include=*.md | grep -v Research/_incoming | wc -l
# 3. Did a file the worker claimed to create actually exist?
ls -la path/the/worker/claimed.md
```

If `git status --short` is empty (or shows only the few edits you expected from a
*prior correct* run) but the board shows 20+ "done" tasks, those tasks are phantoms.

## Two extra verification lenses (beyond "did files change")

### 1. Frontmatter was MERGED, not REPLACED
A non-empty `git diff` is necessary but NOT sufficient — a worker that overwrote the
whole `---` block still produces diffs, while silently wiping original `source:` URLs,
`title:`, `tags:`, `video_id:`. After any bulk frontmatter/schema wave, check:
```bash
cd /real/vault/path
# (a) content notes should NOT have empty source (URL destroyed)
grep -rl 'source: ""' . --include='*.md' | grep -vE '/(.git|.obsidian|Research/_incoming|MOC)/' | wc -l   # expect ~0
# (b) title: must still sit INSIDE the first --- block, not pushed to body
# (c) count notes missing ue_version: only among intended targets (governance/MOC files legitimately lack it)
```
Recovery: `scripts/frontmatter-merge-recover.py <vault-path>` rebuilds frontmatter by
merging canonical fields ON TOP of `git HEAD` originals (which still hold the source
URLs/title), keeping the current body. Re-audit after.

### 2. Worker "findings" are self-reports — verify factual claims against disk
Review/analysis tasks may post confident claims that are simply wrong. Verify before
relaying to the user or spawning follow-up work:
- "duplicate of X" → diff the two files; a pointer/stub is not a duplicate of applied notes.
- "zero notes on topic" → `find . -iname '*topic*' -name '*.md'` — the worker's scan may
  have missed files, or recalled a stale empty state.
- "doesn't exist / is deprecated" → confirm against the actual file, not the summary.
If the worker was wrong, `hermes kanban comment` the correction onto the task so the
board record doesn't carry the error forward.

## Scrub phantom cards

```bash
# Archive the whole stale wave in one call (space-separated IDs)
hermes kanban archive t_aaa t_bbb t_ccc ...
# Then re-create against the CORRECT workspace path
```

Do NOT trust `hermes kanban list` counts from a wave that ran on a wrong workspace —
the count is inflated. Recount after scrub.

## Spot-check a "done" category before believing it

Pick one task the board marked done and read the actual file:

```bash
head -10 path/to/category/_MOC_Something.md   # does it have the new frontmatter?
```

If the frontmatter/annotation is absent, the "done" label is phantom. Never report a
task complete until you've verified its artifact on disk.
