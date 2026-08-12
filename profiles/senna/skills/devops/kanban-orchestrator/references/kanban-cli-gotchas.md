# Kanban CLI — id extraction & orphan reconciliation

## Extracting task ids WITHOUT piping to an interpreter (security scan trips on pipes to python)

```bash
hermes kanban create "title" --assignee X \
  --workspace "dir:/path" --body "$(cat /tmp/body.md)" --json > /tmp/t.json
ID=$(grep -o '"id": "[^"]*"' /tmp/t.json | head -1 | sed 's/"id": "//;s/"//')
echo "$ID"
# JSON key is `id`, NOT `task_id`.
```

Parent linking (repeatable `--parent`):
```bash
hermes kanban create "child" --assignee Y --parent "$ID" --body "$(cat /tmp/child.md)" --json > /tmp/c.json
```

## After a create "errored" on JSON parse — VERIFY before retrying
The create likely SUCCEEDED. Do not re-run it (that makes more duplicates):
```bash
hermes kanban list | grep "research: UE 5.8"   # grep the board for the title
```

## Orphan cleanup (duplicate chain with empty parents)
```bash
# Confirm the phantom has no parents:
hermes kanban show <orphan_id> --json | grep -A3 '"parents"'   # expect []
# Archive orphans — non-destructive, keeps the audit trail:
hermes kanban archive <orphan_id_1> <orphan_id_2> ...
```

## Reconciling a premature release an orphan pushed to GitHub
If a stray release task already pushed tag `vX.Y.Z` (and/or a GitHub release):
```bash
gh release delete vX.Y.Z -y
git fetch origin --tags
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z          # delete remote tag
# Revert unwanted CHANGELOG/repo changes the orphan committed; untrack unrelated files:
git rm --cached <unrelated-file>
printf '\n<unrelated-file>\n' >> .gitignore   # stop it being re-swept into the real release
git add -A && git commit -m "chore: reconcile premature vX.Y.Z — revert <scope>, untrack local files"
# Confirm clean before the real chain's release task runs:
git tag -l | grep vX.Y.Z || echo "clean: no vX.Y.Z tag"
```
Note: the orphan *commit* stays in history; only the tag/release pointer and working-tree state are reconciled. The proper chain's release re-tags `vX.Y.Z` at the end so it points at the fully-integrated commit.

## Self-recovery after kanban DB corruption

If `hermes kanban` reports a corrupt DB (`database disk image is malformed`):

1. **Inspect backups:** `ls -la ~/.hermes/kanban/boards/main/*.bak` and `sqlite3 <backup> "PRAGMA integrity_check;"`. If the backup also fails integrity_check the original data is lost; re-initialize. If the backup passes, use it.
2. **Reinitialize when both are corrupt:** `mv ~/.hermes/kanban/boards/main/kanban.db ~/.hermes/kanban/boards/main/kanban.db.dead.bak` then `hermes kanban init`. This discards state and gives you a clean board.
3. **Recover from JSON dump (fast):** if you can, rewind the plan/body lists that were used to create the original cards and bulk-create in groups of 3–5 with temp-file body injection (`$(cat /tmp/bN-M.md)`), verifying ids with `grep -o '"id": "..."'`. Re-attach dependency links with `hermes kanban link parent child` afterwards.
4. **Stop creating blindly after a corruption event.** Always run `hermes kanban list` first to confirm what already exists; re-creating everything from scratch is the usual duplicate trap.
