---
name: git-divergence-reconcile
description: "Reconcile a git branch that is ahead AND behind a remote where BOTH sides restructured in parallel (renames, re-dos, de-dup passes). Classify local-only files by CONTENT (all-vs-all Jaccard with rename-aware normalization), not by path, so merges don't silently re-create duplicates. Includes the README-after-reset pitfall and a non-destructive (no --force) commit-on-top strategy."
version: 1.0.0
author: senna
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, merge, divergence, reconciliation, renames, jaccard, obsidian-vault, no-force]
    related_skills: [github]
---

# Git Divergence Reconciliation (parallel restructure on both sides)

Use this when a branch is `ahead N, behind M` AND the local branch and the
remote both renamed / re-did / de-duplicated files independently. The naive
"keep the files that only exist locally" plan is WRONG here: the same content
lives under different names on each side, so a path-only plan re-creates
duplicates instead of resolving them.

Real example: local `BP_Class_3_Events_Functions.md` (revamped, UE 5.8) vs
remote `BP_Class_3_Events_and_Functions.md` (older). Path comparison calls both
"unique" -> you'd keep two copies. Content comparison shows they're the same
note renamed, and local is the newer version.

## Trigger
`git status` shows `ahead N, behind M` with a clean working tree AND you see
both sides touched the same folders with renames/restructures. Do NOT just
`git merge`/`rebase` blindly — parallel renames produce 50+ conflicts.

## The core technique: classify by content, not path

Run the bundled classifier `scripts/divergence_reconcile.py`. It:
1. Lists files only in local (not on remote) by path.
2. For each, computes Jaccard similarity against EVERY remote file's line set.
3. Normalizes paths by stripping leading numbers and the word "and" so rename
   pairs (`Events_Functions.md` vs `Events_and_Functions.md`) match on content.
4. Buckets each local-only file:
   - `dup`     (sim >= 0.80) — remote has an equivalent -> DROP
   - `overlap` (0.50-0.80)   — likely rename / older version -> REVIEW
   - `genuine` (< 0.50)      — truly unique -> CARRY FORWARD

```bash
python3 scripts/divergence_reconcile.py <repo> HEAD origin/main
# writes .divergence_classified.json in the repo too
```

## Verify the "genuine" bucket before trusting it
A 0.00 sim can mean a real unique file OR a near-empty stub. Always:
- Check for 0-byte stubs: `git show HEAD:<path> | wc -l` (0 = empty, drop it).
- Confirm remote doesn't have it under a different name:
  `git ls-tree --name-only origin/main | grep <basename>`.
- Peek at representative heads to confirm local is genuinely NEWER
  (`ue_version: "5.8"`, `revamped_at: <date>`) vs just a rename of an older
  remote file.

## Confirm kept files actually exist on remote (exact-path check is authoritative)
`git ls-tree --name-only origin/main <path>` — note that `git ls-tree` exits 0
EVEN WITH NO MATCH, so infer presence from the OUTPUT being non-empty, not the
exit code. (A buggy shell check like `git ls-tree ... && echo present || echo
absent` will lie — the `&&` always runs because exit code is 0.)

## Execution (non-destructive to remote — NO --force)
```bash
OLD=$(git rev-parse HEAD)          # snapshot pre-state
git reset --hard origin/main       # adopt newest base; tree now == origin
git checkout "$OLD" -- <genuine relative paths...>   # re-add ONLY unique content
git commit -m "chore: re-sync to <remote-tip> + carry forward local-unique artifacts"
git push origin main               # normal push, history stays recoverable
```
Prefer a normal commit on top of origin over `git push --force`. Force only if
the user explicitly wants local commits erased from remote history.

## Pitfall: README / docs after reset
`git reset --hard origin/main` adopts the remote's README/CHANGELOG wholesale
and DISCARDS any local doc edits. After the push, the repo can be clean but the
README still describes the remote's structure and OMIT the carried-forward
files. Always:
```bash
git diff <OLD> HEAD -- README.md   # what local docs did we lose?
```
Then add a clearly delineated section (e.g. "## Local Additions") for the
carried-forward files the remote's docs omit — without rewriting remote content.

**Real miss:** after a clean reset+re-add+push, user flagged "the readme was
never updared." The merge was correct; the docs verification step had been
skipped. Verify README against the final file list, not just "git is clean."

## Commit-strategy note
A single commit on top of origin is reversible and reviewable. Reserve
`--force` for explicit user requests to erase local history from the remote.

## Scripts
- `scripts/divergence_reconcile.py` — the content-classifier described above.
  Re-run after any strategy change; reads `.divergence_classified.json`.
