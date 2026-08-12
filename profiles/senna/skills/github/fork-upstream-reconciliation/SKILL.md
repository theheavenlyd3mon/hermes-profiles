---
name: fork-upstream-reconciliation
description: "Reconcile a GitHub fork against its TRUE upstream parent: verify a fork is actually in sync, repoint a local clone's origin to the fork, track upstream, and compare a running pip install against its git fork. Use whenever the user says 'make sure our fork is up to date', 'sync the fork', 'check the fork against upstream', or wants to compare a running plugin/package with its GitHub fork."
version: 1.0.0
author: Senna
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Fork, Upstream, Sync, Reconciliation, gh, git]
    related_skills: [github]
---

# Fork ↔ Upstream Reconciliation

The naive "pull the fork" flow misses the entire point of a fork: a fork is always
"in sync with itself." What matters is whether the fork has drifted from the repo it
was **forked from** (its parent). This skill covers verifying that, repointing a local
clone, and comparing a *running install* against the fork.

## When to use
- "Make sure our fork is up to date" / "sync the fork with upstream"
- "Check the fork against the original"
- "Compare our current version with the fork" (running plugin/package vs git fork)
- A local clone's `origin` still points at the upstream org, not our fork
- A user says "both are upstream so we should have the most up to date version"

## 1. Find the fork's TRUE parent and compare

```bash
FORK=<owner>/<fork>                     # e.g. <your-github-username>/hermes-lcm
gh api repos/$FORK --jq '{fork, parent: (.parent.full_name // "none"), default_branch}'
PARENT=$(gh api repos/$FORK --jq '.parent.full_name')        # e.g. stephenschoettler/hermes-lcm
PARENT_DEFAULT=$(gh api repos/$PARENT --jq '.default_branch') # resolve on the PARENT
FORK_DEFAULT=$(gh api repos/$FORK --jq '.default_branch')

# The reconciliation call — compare PARENT's default branch against OUR fork:
gh api repos/$PARENT/compare/${PARENT_DEFAULT}...${FORK%/*}:$FORK_DEFAULT \
  --jq '{status, ahead_by, behind_by, total_commits}'
```
- `status: "identical"` with `ahead_by:0 behind_by:0` → fork is fully synced to upstream. ✓
- `behind_by > 0` → upstream has commits we don't; pull them (see §3).
- `ahead_by > 0` → we have fork-only commits (local work); expected if we develop on the fork.

**PITFALL — fork and parent default branches differ.** A fork's `default_branch` is NOT
always the parent's. Real example: `liftaris/herm` uses `dev`, not `main`. If you compare
on the fork's default branch against the wrong parent base, the compare silently reports
a false "identical". Always resolve `PARENT_DEFAULT` from the parent and compare on that.
`gh api repos/$PARENT --jq .default_branch` is the source of truth.

## 2. Inspect local clone state BEFORE touching it

```bash
D=~/.hermes/plugins/<name>
git -C "$D" rev-parse 2>/dev/null && echo "IS GIT REPO" || echo "NOT A GIT REPO (pip pkg / symlink?)"
git -C "$D" remote -v
git -C "$D" branch -vv
git -C "$D" describe --tags 2>/dev/null || echo "(no tags)"
git -C "$D" log --oneline HEAD..origin/main | head   # commits behind origin
git -C "$D" rev-list --count HEAD..origin/main         # numeric: behind count
git -C "$D" rev-list --count origin/main..HEAD         # numeric: ahead count
```
- A plugin dir is often **not a git repo** — it may be a pip package or a symlink into a
  venv's `site-packages`. Don't assume. Check first.

## 3. Repoint a clone to the fork + track upstream parent

When the local clone's `origin` points at the original upstream org (not our fork):

```bash
cd "$D"
git remote set-url origin https://github.com/<owner>/<fork>.git
git remote add upstream https://github.com/<PARENT>.git 2>/dev/null \
  || git remote set-url upstream https://github.com/<PARENT>.git
git fetch origin --quiet && git fetch upstream --quiet
# If local has no unique commits and is behind: fast-forward (no merge commit)
git merge --ff-only upstream/$PARENT_DEFAULT
git push origin "$(git symbolic-ref --short HEAD)"   # sync the fork on GitHub too
git branch --set-upstream-to=origin/"$(git symbolic-ref --short HEAD)"
```

## 4. Compare a RUNNING install against the fork

The user's "current version" is usually the *installed* package, not the clone.

1. **Don't trust `~/.hermes/plugins/<name>`** — it may be pip-installed or a symlink.
   Resolve the real install: `python -m pip show <pkg>` and read `__version__`.
2. **Clone the fork to a side-by-side dir** (`~/repos/<name>`) for diffing.
   Never overwrite the live install without explicit user approval.
3. **Diff installed dir vs fork source subdir:** `diff -rq <installed>/ <fork>/<subdir>/`.
4. **Characterize the gap direction** — is the fork newer (safe to adopt) or the installed
   one newer/custom (reverting would be a downgrade)? Compare `__version__` and line counts.
   Note: pip packages sometimes split core vs provider (e.g. `mnemosyne-memory` core +
   `hermes_memory_provider` plugin) — the fork's provider dir is the source for the plugin.

**CRITICAL diagnostic pitfall — CWD import shadowing.**
If you `cd` into the cloned fork and run `python -c "import <pkg>"` or `pip show <pkg>`,
Python resolves the *cloned* copy in the cwd, NOT the installed package. This silently
reports the fork's version as "installed" and corrupts every downstream conclusion.
Always run version checks from a neutral directory:
```bash
cd /tmp
python -m pip show <pkg> | head -4
python -c "import <pkg>,os; print(os.path.dirname(<pkg>.__file__))"   # real installed path
```

**Governance — never hot-swap a live shared backend.**
A memory / auth / DB provider is the running brain of every profile. If the running
version is behind the fork, *surface the gap and request explicit approval* before
upgrading. A multi-version jump of the memory core can break recall/store. Offer options
(upgrade now / diff changelog first / leave as-is) rather than mutating the live system.

## 5. Report format

Give the user a clear table:
| Component | Running | Fork | Status |
|---|---|---|---|
| `<pkg>` | `<ver>` | `<fork-ver>` | ✓ synced / ✗ N behind |
Plus the one-line repo topology (fork → true upstream parent → default branch).
