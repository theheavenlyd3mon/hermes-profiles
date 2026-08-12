---
name: git-upstream-tracking
description: "Set up and repair git branch-to-remote upstream tracking, especially when `remote.<name>.fetch` refspecs are narrowed (e.g. to main only) so `git branch --set-upstream-to` / `git push -u` fail with 'the requested upstream branch does not exist' even though the branch is already on the remote."
version: 1.0.0
author: senna
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, upstream, tracking, refspec, fetch, push, remote]
    related_skills: [github, git-master, git-divergence-reconcile]
---

# Git Upstream Tracking (narrowed fetch refspec gotcha)

Set up and repair the link between a LOCAL branch and its REMOTE-tracking
counterpart (so `git status -sb` shows `ahead/behind`, and plain `git push`
works). The headline trap this skill covers: **the upstream link silently
refuses to set when `remote.<name>.fetch` is narrowed to a single branch.**

## Trigger
- User asks to "push my branch to GitHub" / "set the upstream" / "track origin".
- `git branch --set-upstream-to=origin/<b>` fails with:
  `fatal: the requested upstream branch 'origin/<b>' does not exist`
  ...even though `git ls-remote origin <b>` shows the branch IS on the remote.
- `git push -u origin <b>` reports `up-to-date` but `git status -sb` still shows
  no `...origin/<b>` and `git rev-parse --abbrev-ref --symbolic-full-name @{u}`
  still errors with "not stored as a remote-tracking branch".

## Diagnosis (run in order)
```bash
cd <repo>
git branch --show-current                 # local branch name
git rev-parse HEAD                        # local tip SHA
git ls-remote origin <b> 2>&1 | grep <b>  # is it REALLY on the remote? prints SHA if yes
git config --get-regexp 'remote\.origin\.fetch'   # THE key check — see root cause
git branch -r                             # which remote-tracking refs exist locally?
```

## Root cause
If `git config --get-regexp 'remote.origin.fetch'` returns ONLY
`+refs/heads/main:refs/remotes/origin/main`, git is told to fetch *just main*.
Consequences:
- `git fetch` / `git fetch origin` will NOT create `refs/remotes/origin/<b>`.
- `git fetch origin <b>` pulls the commit into `FETCH_HEAD` but does NOT write a
  `refs/remotes/origin/<b>` tracking ref.
- Without that tracking ref, `--set-upstream-to` and `git push -u` cannot
  establish the link and fail with "does not exist" — even though the branch is
  safely on the server.

This pattern is common when someone deliberately narrowed the fork's fetch to
avoid pulling every branch (e.g. `git config remote.origin.fetch ...main`).

## Fix (add a per-branch fetch refspec — do NOT broaden to all branches)
```bash
# 1. Tell git to track THIS branch specifically
git config --add remote.origin.fetch \
  '+refs/heads/<b>:refs/remotes/origin/<b>'

# 2. Materialize the tracking ref
git fetch origin <b>

# 3. Now the upstream link takes. Nothing to push if SHAs already match:
git push -u origin <b>          # says "up-to-date" but now wires the link
git status -sb                  # shows  ## <b>...origin/<b>
git rev-parse --abbrev-ref --symbolic-full-name @{u}   # -> origin/<b>
git rev-list --left-right --count @{u}...HEAD          # 0   0 (in sync)
```

### Manual fallback (if `push -u` still won't set it)
```bash
git config branch.<b>.remote origin
git config branch.<b>.merge refs/heads/<b>
git update-ref refs/remotes/origin/<b> $(git rev-parse HEAD)
git fetch origin <b>            # re-affirm
```

## Pitfalls
- **`up-to-date` is NOT proof the link is set.** `git push -u` returning
  `up-to-date` only means the commit is already on the server. If the fetch
  refspec is narrow, the upstream config is STILL absent afterward. Verify with
  `git status -sb` (look for the `...origin/<b>` suffix) before declaring done.
- **`git fetch origin <b>` alone is not enough.** It updates `FETCH_HEAD` but
  not `refs/remotes/origin/<b>`. You must add the fetch refspec first.
- **Don't broaden the refspec to `+refs/heads/*:refs/remotes/origin/*`** unless
  the user explicitly wants every branch tracked — that defeats the original
  narrowing. Adding one narrow `+refs/heads/<b>:refs/remotes/origin/<b>` entry is
  the surgical fix and coexists with the existing main-only entry.
- **No commits to push?** If `git ls-remote origin <b>` shows the SAME SHA as
  local HEAD, the branch is already fully on the remote — this is a pure
  link/refspec repair, not a content push. Don't rewrite or force anything.

## When to escalate
If the branch on the remote has a DIFFERENT tip SHA than local (ahead/behind,
not just unlinked), this is divergence, not a tracking-link issue — see
`git-divergence-reconcile` (and check it isn't the parallel-restructure case).

## Reference
Exact reproduction transcript (mnemosyne repo case): `references/narrow-fetch-refspec-upstream.md`.
