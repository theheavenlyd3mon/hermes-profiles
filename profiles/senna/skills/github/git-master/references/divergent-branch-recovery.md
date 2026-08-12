# Divergent Branch Recovery

When `git pull` fails with "divergent branches," the local and remote have
commits the other doesn't have. This happens when:
- A PR was merged on GitHub but local has old commits from a different branch
- Local commits were made on a branch that was never pushed
- Force-push or reset changed remote history

## Diagnosis

```bash
# What does remote have that local doesn't?
git log --oneline main..origin/main

# What does local have that remote doesn't?
git log --oneline origin/main..main

# What branch is local actually on?
git branch --show-current
```

## Decision Tree

```
Local has unique commits (origin/main..main is non-empty)?
├── NO  (local is just behind) → git reset --hard origin/main
└── YES (local has commits to preserve)
    ├── Are the local commits valuable?
    │   ├── YES → Cherry-pick them onto origin/main
    │   └── NO  → git reset --hard origin/main
    └── Is the local branch even the right one?
        └── Check with: git branch --show-current
            (may be on an old branch like v1.3.1-housekeeping)
```

## Cherry-pick onto updated main

```bash
# Save the commit SHA(s) from the local log
git log --oneline origin/main..main
# e.g., abc1234 v1.3.1: Housekeeping

# Reset to remote
git reset --hard origin/main

# Cherry-pick the saved commit(s)
git cherry-pick abc1234 --no-commit

# Check for conflicts
git diff --name-only --diff-filter=U

# Resolve conflicts, then stage and commit
git add -A
git commit -m "cherry-pick: <original commit message>"
git push
```

## Conflict Resolution for CHANGELOG.md / README.md

These files change frequently and almost always conflict on cherry-pick.

Strategy:
1. Keep the HEAD (current main) version as the base structure
2. Insert cherry-picked content as a new section (e.g., a new version entry)
3. Remove conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
4. Ensure version numbers are sequential and dates are correct
5. Stage and commit

Don't try to auto-merge version histories — manually compose the final state.

## Case C: Parallel restructures (both sides renamed/deduped the same files)

A special divergence where local and remote didn't just add different files —
they both ran an independent cleanup/renumber/version-bump pass over the SAME
file set. `git diff --name-status` then shows a near-mirror image of adds and
deletes (e.g. local added 48 / deleted 81 while remote added 81 / deleted 48),
and a `git merge` produces 50–80 conflicts that are mostly modify/delete and
rename collisions, NOT genuine contradictory edits.

Path-based diffs LIE here. "Local-unique by path" (present in `HEAD`, absent
from `origin/main`) is NOT the same as "genuinely new content" — many of those
files are renames of files the other side already has under a different name
(e.g. `BP_Class_3_Events_Functions.md` vs their `BP_Class_3_Events_and_Functions.md`;
a 1263-line RPG tutorial vs their 217-line `Step_by_Step_Guides/...` copy of the
same YouTube video). A naive "re-add everything local-unique" plan would
RE-CREATE the duplicates you're trying to strip.

**Decision rule for this case:**
1. Reset local to the newer side (`git reset --hard origin/main` when remote is
   the newer canonical), OR rebase — do NOT try to hand-resolve 78 conflicts.
2. Before discarding local-unique files, run a **content-similarity probe**
   (see `scripts/reconcile_probe.py`): all-vs-all Jaccard similarity of local
   files against the target's files, bucketed as:
   - `dup` (sim ≥ 0.80) — target already has equivalent content → drop.
   - `overlap` (0.50–0.80) — likely older/renamed version → inspect, usually drop.
   - `genuine` (sim < 0.50) — truly new content → **carry forward** with
     `git checkout <old_head> -- <path>` AFTER the reset.
3. Watch the normalizer: strip leading digits AND collapse ` and ` → space
   before matching, or rename pairs slip through as false "genuine."
4. Verify post-reset: working tree must equal target + exactly the carried
   files; no duplicate/rename paths remain. Then commit + normal push (no force
   needed — you're adding one commit on top of origin, history stays intact).

## Reversible conflict probe (always run before a real merge)

Never guess the conflict surface. Do a throwaway merge, tally, then abort:

```bash
git merge --no-ff --no-commit origin/main   # does NOT commit
git status --porcelain | awk '$1 ~ /^(UU|UD|DU|DD|AA|AU|UA)$/{print $1}' | sort | uniq -c
git merge --abort                            # restores clean tree
```

Conflict codes: `UU`=both modified, `UD`=modified-ours/deleted-theirs,
`DU`=deleted-ours/modified-theirs, `DD`=deleted-both, `AA`=added-both
(`AU`/`UA` are the opposite-order variants).

Cleaner: run `scripts/reconcile_probe.py` — it does the dry-run merge, counts
the codes, aborts, then prints the keep/drop/dup classification. Safe on a
clean tree; never commits.

## Pitfalls

- **Check the branch name first.** `git branch --show-current` — if you're on
  an old branch like `v1.3.1-housekeeping`, the divergent history is because
  that branch was never merged, not because main diverged.
- **Don't cherry-pick if local has no unique commits.** If
  `git log --oneline origin/main..main` is empty, just reset.
- **Force-push after reset if needed.** If local was pushed to a different
  branch, the old branch still exists on remote. Clean it up with
  `git push origin --delete <branch-name>`.
- **Buggy shell check on git ls-tree lies.** `git ls-tree <path>` exits 0 and
  prints nothing when the path is absent — so `if git ls-tree ... <f>; then
  present; fi` always reports "present." Use an exact-path membership test
  instead: `git ls-tree -r --name-only origin/main | grep -qxF "$f"`.