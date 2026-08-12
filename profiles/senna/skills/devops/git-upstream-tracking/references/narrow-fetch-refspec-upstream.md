# Reproduction: narrow fetch refspec breaks upstream tracking

Real case (2026-07-14, mnemosyne repo, branch `<user>_adjustments`).

## Symptom
User asked to push their adjustments to GitHub as a branch. The branch was
ALREADY on `origin` at the same commit, but had no upstream tracking link.

## Commands run and what each revealed

```bash
# 1. Branch confirmed, but upstream resolution fails → 128
git branch --show-current
# <user>_adjustments
git rev-parse --abbrev-ref --symbolic-full-name @{u}
# fatal: upstream branch 'refs/heads/<user>_adjustments' not stored
#        as a remote-tracking branch   (exit 128)

# 2. The branch DOES exist on the remote, same SHA as local
git fetch origin
git ls-remote origin | grep <user>_adjustments
# 1e123103cc2014a03cf6e6087bbcbee805283f04  refs/heads/<user>_adjustments
git rev-parse HEAD
# 1e123103cc2014a03cf6e6087bbcbee805283f04   <- IDENTICAL

# 3. set-upstream-to fails even after fetch
git branch --set-upstream-to=origin/<user>_adjustments
# fatal: the requested upstream branch 'origin/<user>_adjustments' does not exist

# 4. ROOT CAUSE — origin.fetch is narrowed to main only
git config --get-regexp 'remote.origin.fetch'
# remote.origin.fetch +refs/heads/main:refs/remotes/origin/main

# 5. Remote-tracking refs reflect the narrow refspec
git branch -r
# origin/HEAD -> origin/main
# origin/main
# (no origin/<user>_adjustments despite it being on the server)
```

## The fix that worked
```bash
git config --add remote.origin.fetch \
  '+refs/heads/<user>_adjustments:refs/remotes/origin/<user>_adjustments'
git fetch origin <user>_adjustments
git push -u origin <user>_adjustments     # "up-to-date" + now links
git status -sb                            # ## <user>_adjustments...origin/<user>_adjustments
git rev-parse --abbrev-ref --symbolic-full-name @{u}   # origin/<user>_adjustments
git rev-list --left-right --count @{u}...HEAD           # 0   0
```

## Notes
- `git fetch origin <user>_adjustments` updated FETCH_HEAD but did NOT create
  `refs/remotes/origin/<user>_adjustments` until the explicit refspec was added.
- Adding the per-branch refspec coexists with the existing main-only entry; we
  deliberately did NOT broaden to `+refs/heads/*:*` to preserve the original
  narrowing (avoid pulling the whole fork).
- `git push -u` reporting `up-to-date` is NOT sufficient proof the link is set;
  only `git status -sb` showing the `...origin/<b>` suffix confirms it.
