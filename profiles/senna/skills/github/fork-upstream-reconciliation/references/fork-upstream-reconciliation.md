# Fork ↔ Upstream Reconciliation — Reference Cheat Sheet

Condensed commands + pitfalls. The SKILL.md carries the narrative; this is the copy-paste layer.

## Topology discovery
```bash
FORK=<your-github-username>/hermes-lcm
gh api repos/$FORK --jq '{fork, parent: (.parent.full_name // "none"), default_branch}'
PARENT=$(gh api repos/$FORK --jq '.parent.full_name')
PARENT_DEFAULT=$(gh api repos/$PARENT --jq '.default_branch')   # ALWAYS resolve from parent
```

## The one reconciliation call
```bash
gh api repos/$PARENT/compare/${PARENT_DEFAULT}...${FORK%/*}:$(gh api repos/$FORK --jq .default_branch) \
  --jq '{status, ahead_by, behind_by, total_commits}'
```
- `status:"identical"`, `ahead_by:0`, `behind_by:0` → fully synced.
- `behind_by>0` → pull from upstream. `ahead_by>0` → fork-only work (expected).

## Pitfalls (from real session)
1. **Fork default ≠ parent default.** `liftaris/herm` → `dev` (not `main`). Compare on `$PARENT_DEFAULT`.
2. **Local clone origin may point at the upstream org, not the fork.** `git remote -v` first; repoint (§3 of SKILL).
3. **Plugin dir may not be a git repo** — pip package or symlink into venv `site-packages`. Check `git -C <dir> rev-parse`.
4. **CWD import shadowing** — `cd` into the cloned fork, then `python -c "import <pkg>"` resolves the clone, not the install. Always `cd /tmp` and use `python -m pip show <pkg>`.
5. **Never hot-swap a live shared backend** (memory/auth/DB). Surface the gap + ask before upgrading.

## Repoint + sync sequence
```bash
cd ~/.hermes/plugins/<name>
git remote set-url origin https://github.com/<owner>/<fork>.git
git remote add upstream https://github.com/<PARENT>.git 2>/dev/null || git remote set-url upstream https://github.com/<PARENT>.git
git fetch origin --quiet && git fetch upstream --quiet
git merge --ff-only upstream/$PARENT_DEFAULT
git push origin "$(git symbolic-ref --short HEAD)"
git branch --set-upstream-to=origin/"$(git symbolic-ref --short HEAD)"
```

## Installed-vs-fork diff
```bash
cd /tmp
python -m pip show <core-pkg> | head -4          # real installed version/path
python -c "import hermes_memory_provider as h,os; print(os.path.dirname(h.__file__))"
diff -rq <installed-pkg-dir>/ <fork-clone>/<source-subdir>/
```
