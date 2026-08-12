# Purging stale / phantom kanban cards (board housekeeping)

## The problem
There is **no `delete` / `purge` verb** in the kanban CLI. `hermes kanban gc` only
trims old task_events / worker log files by retention days — it does NOT remove tasks.
So cards that are stale, phantom, or fully superseded (e.g. a corrupted-session wave
that ran against a phantom workspace) can only be removed by editing the board SQLite
store directly.

## Boards are SEPARATE database files
Each board slug is its own `.db`. In this setup:

- `main`  board → `~/.hermes/kanban/boards/main/kanban.db`
- `default` board → `~/.hermes/kanban.db`

Switch with `hermes kanban boards switch <slug>`, but a purge edits one file only.
Inspect both before assuming all phantoms live on the active board — they may be split.

## Schema (verified)
```
tasks(id TEXT, title, body, assignee, status, ...)        -- status 'archived' = parked
task_links(parent_id, child_id)                            -- NOTE: parent_id/child_id, NOT source_id/target_id
task_events(id, task_id, run_id, kind, payload, created_at)
task_comments(task_id, ...)
task_runs(id, task_id, ...)
```
`journal_mode` is `wal` — uncommitted deletes may not reflect in `hermes kanban list`
until you run `PRAGMA wal_checkpoint(TRUNCATE)`.

## Procedure (scoped, recoverable)
1. **Identify the phantom set by signature** (do not blanket-delete):
   ```sql
   SELECT id, title, status FROM tasks
   WHERE title LIKE 'revamp:%'
      OR title LIKE 'knowledge: scaffold Legacy%'
      OR title LIKE 'knowledge: merge duplicates%';
   ```
2. **BACK UP the db before touching it:**
   ```bash
   cp ~/.hermes/kanban/boards/main/kanban.db \
      ~/.hermes/kanban/boards/main/kanban.db.pre-purge-$(date +%Y%m%d-%H%M%S).bak
   ```
3. **Delete in one transaction, dependency tables first**, and checkpoint:
   ```python
   import sqlite3, datetime
   db = "~/.hermes/kanban/boards/main/kanban.db"
   ids = [r[0] for r in c.execute(
       "SELECT id FROM tasks WHERE title LIKE 'revamp:%' OR "
       "title LIKE 'knowledge: scaffold Legacy%' OR "
       "title LIKE 'knowledge: merge duplicates%'")]
   q = ",".join("?"*len(ids))
   for tbl, col in [("task_links","parent_id"), ("task_links","child_id"),
                    ("task_events","task_id"), ("task_comments","task_id"),
                    ("task_runs","task_id"), ("tasks","id")]:
       c.execute(f"DELETE FROM {tbl} WHERE {col} IN ({q})", ids)
   c.commit()
   c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
   ```
4. **Verify:**
   ```bash
   hermes kanban list | grep -cE "revamp:|knowledge: scaffold|knowledge: merge"   # expect 0
   python3 -c "import sqlite3; c=sqlite3.connect('$db'); print('tasks:', c.execute('SELECT COUNT(*) FROM tasks').fetchone()[0])"
   ```

## Pitfalls encountered (and how they bite)
- **`OperationalError: no such column: source_id`** — the #1 trap. `task_links` columns
  are `parent_id` / `child_id`, NOT `source_id` / `target_id`. A delete referencing
  `source_id` raises and **rolls back the whole transaction** (leaving phantoms in
  place, no harm, but no cleanup). Fix the column names and re-run — your backup is safe.
- **WAL mode hides the delete.** After a correct delete, `hermes kanban list` may still
  show the old cards until a checkpoint flushes the WAL. Always `wal_checkpoint(TRUNCATE)`
  and verify via the CLI, not just by re-reading the python connection.
- **Two-step confirmation.** Dry-run (print the id list + linked-row counts) BEFORE the
  delete. Confirm the count matches your expectation, then execute. A stray `DELETE FROM
  tasks` with no WHERE wipes the whole board.
- **Real tasks must survive.** Scope strictly to the phantom id set; re-check that the
  canonical/real task ids (e.g. T0/T1a/T1b + the REAL wave) are NOT in the deleted set
  before commit.

## Related gotcha — zsh glob in verify greps
Under zsh, `grep -rl 'source: ""' --include=*.md .` fails with `no matches found:
--include=*.md`. **Quote the glob**: `--include='*.md'`. The same applies to the
`verify-kanban-output-on-disk.md` recipe's grep commands when run under zsh.
