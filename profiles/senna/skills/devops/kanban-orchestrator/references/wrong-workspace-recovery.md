# Wrong-Workspace Recovery

## Symptom
After bulk-creating kanban cards, workers complete with summaries that don't match reality — e.g. a canonical doc is reported as written but doesn't exist on disk, or files unchanged but the summary claims edits were made.

Diagnosis:
1. Verify the workspace path exists on the machine the workers run on.
2. If it doesn't: every card in the chain ran in a phantom workspace and their output is unreliable.
3. `hermes kanban list` will still show tasks as `done`/`running`, but no real vault artifacts exist.

## Recovery
1. Confirm the real project path with the user (or by listing likely roots).
2. Re-create the failed foundation tasks against the verified path.
3. Unblock any downstream revamp tasks that are blocked because the parent artifacts never arrived, then re-dispatch.
4. Verify disk artifacts with `ls`/`stat`/`grep` before reporting anything as done.

## Prevention
Run this exact sequence before bulk-creating cards against a new project:
```bash
ls "$WORKSPACE_PATH"
ls "$WORKSPACE_PATH/UE5_CPP"   # or any must-exist subdir of the vault
```
If either fails, do not create cards — confirm the path first.

## User teaching moment
If the user says "this all works" while prior output was derived from the wrong workspace, stop and verify before continuing. Do not accept implicit confirmation; surface the mismatch explicitly and wait.
