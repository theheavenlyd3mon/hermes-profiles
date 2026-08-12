# Pilot-wave + path-signature verification (content revamp waves)

## Why this exists
A full 28-task wave against a wrong `--workspace` path completes "cleanly" on the
board but touches nothing real. Two cycles were burned this way. Post-hoc
`git status` catches it — but only after the whole wave is wasted. The pilot
pattern catches systemic errors (wrong path, wrong schema, wrong assignee) after
~4 tasks instead of 28.

## Step 0 — path signature check (BEFORE any bulk create)
Existence (`ls`) is NOT enough. A stale / empty / alternate directory can sit at a
remembered path and silently swallow a whole wave. Verify the path contains the
expected project signature — markers the user's description implies.

```bash
V=~/Documents/Unreal-Engine-Obsidian   # the REMEMBERED path
# existence alone is insufficient:
[ -d "$V" ] && echo "dir exists (not proof it is the right vault)"
# signature check — expected markers from the user's description:
ls "$V" | grep -qE "UE5_CPP|CHANGELOG" && echo "signature OK" || echo "WRONG PATH — confirm with user"
[ -f "$V/CHANGELOG.md" ] && echo "sentinel present" || echo "sentinel missing — likely wrong vault"
```
If the signature is missing, STOP. Confirm the real path with the user. Do not
trust a path that merely exists — a wrong-but-present dir is the dangerous case.

## Step 1 — pilot wave (4 representative tasks)
Pick 4 categories spanning the risk surface:
- 1 tiny (few files) — confirms the worker can write frontmatter at all
- 1 medium — confirms bulk handling
- 1 that must scan a known deprecated symbol — confirms the schema/scan logic
- 1 with special handling (move / alias / legacy) — confirms non-trivial ops

Create + dispatch. Wait for `done`.

## Step 2 — verify on disk (NOT board labels)
```bash
cd "$V"
git add -A
for c in UE5_AI UE5_Materials UE5_Audio UE5_Enhanced_Input; do
  echo "--- $c ---"; git diff --cached --stat "$c/" 2>/dev/null | tail -3
done
# spot-check one patched file's frontmatter matches the canonical schema
f=$(git diff --cached --name-only UE5_AI/ | head -1)
git show :"$f" 2>/dev/null | head -8
```
If `git status` is empty but the board shows done → phantom path. Stop, scrub,
fix `--workspace`, re-pilot. Never trust the board's `done` label.

## Step 3 — scale only after pilots verified real
Create the remaining wave (parented to the standard/foundation doc). Re-run the
same git-diff check at the end. Report the real changed-file count, not the
board's task count.

## Real-world catch (this session)
Tasks were created against `~/Unreal-Engine-Obsidian/` (missing
`Documents/`). The dir existed, so `ls` would have passed. The board showed 28
"done". `git status` in the REAL vault was empty → phantoms. Root cause: a
remembered path that existed but was the wrong vault. The pilot pattern (4 tasks
first) would have surfaced it after 4, not 28.
