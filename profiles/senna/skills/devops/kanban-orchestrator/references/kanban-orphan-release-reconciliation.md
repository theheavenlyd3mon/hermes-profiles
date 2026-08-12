# Reconciling a premature orphan release (kanban + git)

When the pipe-to-interpreter gotcha bites AND an orphan task already ran far enough to
push a git tag/release, the proper chain's final release will collide with the orphan's
tag. This is the verified recovery recipe from a session where an orphan `code` release
card pushed `v1.5.0` to GitHub before the real chain reached its own release step.

## Symptom
- First `hermes kanban create` "errored" on the pipe-to-python security scan, but the
  `create` calls themselves executed — tasks were spawned anyway.
- Duplicate orphan tasks spawned with EMPTY `--parent` (the shell var the orphan would
  have referenced was never populated) → the dispatcher ran them as parallel `ready` orphans.
- One orphan was a release card that ran `gh release create`, `git tag`, and a commit,
  pushing to the remote before the proper chain reached its own release step.
- The orphan commit also swept in unrelated untracked files (local lint baselines, helper
  guides) because they happened to be in the tree.

## Reconciliation (verified order)
1. Confirm what the orphan pushed and bundled:
   ```bash
   gh release list | grep 1.5.0
   git fetch origin --tags && git tag -l v1.5.0
   git show --stat <orphan_commit>      # see which files it bundled
   ```
2. **Decide with the user** — two clean options:
   - **Delete** the orphan release + tag and let the proper chain re-release the same
     version (accurate — points at the fully-integrated commit). Preferred when the orphan
     release is mislabeled/incomplete.
   - **Bump** the proper chain's final release to the next patch (e.g. v1.5.1) and leave the
     orphan as-is. Preferred only if you want zero force-delete and don't mind a mislabeled
     release staying public.
   - Do NOT let the proper chain's release fail silently on a re-tag collision.
3. Delete the GitHub release:
   ```bash
   gh release delete v1.5.0 -y
   ```
4. Delete the tag locally + remotely:
   ```bash
   git tag -d v1.5.0
   git push origin :refs/tags/v1.5.0
   ```
5. Strip the misleading CHANGELOG block the orphan added — it often describes work the
   orphan never actually did. Patch the file so the proper chain doesn't duplicate or ship
   a false release entry.
6. Untrack the unrelated files the orphan swept in:
   ```bash
   git rm --cached .vault_lint_baseline "Hermes/Hermes-Terminal-Guide.md"
   printf "\n# local tooling artifacts (not vault content)\n.vault_lint_baseline\nHermes/Hermes-Terminal-Guide.md\n" >> .gitignore
   ```
   This keeps them out of the proper chain's release commit.
7. Commit the cleanup as a NON-release commit (so it doesn't accidentally become the version
   marker):
   ```bash
   git add CHANGELOG.md .gitignore && git add -u
   git commit -m "chore: reconcile premature v1.5.0 — revert CHANGELOG block, untrack local tooling files"
   ```
8. Verify clean:
   ```bash
   git tag -l | grep 1.5.0 || echo "clean: no v1.5.0 tag"
   gh release list | grep 1.5.0 || echo "no v1.5.0 release on remote"
   ```
9. Archive the orphan tasks: `hermes kanban archive <orphan_id> ...` (soft, recoverable).
10. The proper chain's release step (gated on its own parents) now runs cleanly and creates
    the real, accurate v1.5.0.

## Notes
- `git add -u` also stages legitimate in-tree changes from the proper chain's earlier steps
  (e.g. the real research brief). That's fine — those belong in the tree.
- The dispatcher treats empty-parent orphans as `ready` and runs them, so duplicate work
  (e.g. research briefs) may run twice. Harmless when idempotent, but a release/integration
  orphan is dangerous — archive orphans before they reach a git-push step.
- `hermes kanban tail <id>` can hang (60s timeout observed) on tasks with very long event
  logs. Prefer `hermes kanban show <id> | grep -E "^  status:"` for status checks.
- This is the worst case of the "silent duplicate creation" pitfall in SKILL.md. The
  non-negotiable prevention still applies: never pipe `hermes kanban` stdout into an
  interpreter — write `--json > /tmp/x.json` and `grep -o '"id": "[^"]*"' it out.
