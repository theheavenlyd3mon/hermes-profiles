# Skill Propagation Procedure

## When to use

- A task like "Propagate compressed skills from senna to specialist profiles" lands on the board
- Workers on specialist profiles crash with `Error: Unknown skill(s): kanban-worker` in the worker log
- The `.bundled_manifest` hash for a skill doesn't match the actual file on disk

## The flow

Senna is the canonical skill source. Specialist profiles (architect, coder, researcher, reviewer, etc.) have copies of shared skills. When [PERSON_NAME]'s version gets compressed or updated, those copies must be propagated.

## Step-by-step

### 1. Identify shared skills

Not all senna skills are shared. Specialist profiles carry a curated subset (30-35 skills each vs senna's ~220). The shared set typically includes:

- `devops/kanban-worker/SKILL.md`
- `devops/kanban-orchestrator/SKILL.md`
- `software-development/writing-plans/SKILL.md`
- `software-development/systematic-debugging/SKILL.md`
- `software-development/test-driven-development/SKILL.md`
- `software-development/spike/SKILL.md`
- `software-development/requesting-code-review/SKILL.md`
- `software-development/subagent-driven-development/SKILL.md`
- `software-development/python-debugpy/SKILL.md`
- `software-development/node-inspect-debugger/SKILL.md`
- `software-development/hermes-agent-skill-authoring/SKILL.md`
- `software-development/debugging-hermes-tui-commands/SKILL.md`
- `software-development/plan/SKILL.md` (foreman + architect only)

To discover the actual set:
```bash
for profile in architect coder data-analyst debugger devops foreman researcher reviewer secretary security; do
  echo "=== $profile ==="
  ls ~/.hermes/profiles/$profile/skills/*/kanban-worker/ 2>/dev/null && echo "  has kanban-worker"
done
```

### 2. Copy compressed files

```bash
SENNA="~/.hermes/profiles/senna/skills"
SPECIALISTS="architect coder data-analyst debugger devops foreman researcher reviewer secretary security"

for skill_rel in \
  "devops/kanban-orchestrator/SKILL.md" \
  "devops/kanban-worker/SKILL.md" \
  "software-development/writing-plans/SKILL.md" \
  ...  # list all shared skills
do
  for profile in $SPECIALISTS; do
    target="~/.hermes/profiles/${profile}/skills/${skill_rel}"
    if [ -f "$target" ]; then
      cp "$SENNA/$skill_rel" "$target"
      echo "OK  ${profile}/${skill_rel}"
    else
      echo "MISS  ${profile}/${skill_rel}"  # profile doesn't carry this skill — skip
    fi
  done
done
```

### 3. Update `.bundled_manifest` hashes

Every specialist profile's `skills/.bundled_manifest` maps skill names to md5 content hashes. After replacing files, the hashes are stale. The dispatcher may fail to load skills with stale hashes even though the files exist on disk and the CLI `hermes -p <profile> --skills <name> --version` works fine.

```bash
MANIFEST="~/.hermes/profiles/<profile>/skills/.bundled_manifest"

for skill_rel in "devops/kanban-worker/SKILL.md" ...; do
  sk_name=$(basename "$(dirname "$skill_rel")")
  new_hash=$(md5 -q "~/.hermes/profiles/<profile>/skills/${skill_rel}")
  sed -i '' "s/^${sk_name}:.*/${sk_name}:${new_hash}/" "$MANIFEST"
done
```

Run this for every specialist profile that received copies.

### 4. Unblock and re-dispatch

```bash
hermes kanban unblock <task_id_1> <task_id_2> ...
hermes kanban dispatch
```

Verify the tasks transition to `running` (not immediately back to `blocked`):
```bash
hermes kanban show <task_id> | grep "status:"
```

### 5. Verify worker log is clean

```bash
cat ~/.hermes/kanban/logs/<task_id>.log
```

If the log shows no `Error: Unknown skill(s):` lines and the worker is making progress, the propagation succeeded.

## Diagnostic: distinguishing stale-skill from credential issues

Both produce immediate worker crashes with similar symptoms. Key differentiator:

| Symptom | Stale skill manifest | Missing credential [PERSON_NAME]Error: Unknown skill(s)` in log | ✅ Yes | ❌ No |
| Worker runs briefly then times out | ❌ No — crashes at startup | ❌ No — crashes at startup |
| `protocol_violation` in event log | ❌ No | ✅ Yes |
| `hermes -p <profile> --skills kanban-worker -z "OK"` works | ✅ Yes (CLI bypasses manifest) | ❌ Also fails |
| Same crash pattern across multiple profiles | ✅ Yes (all specialists affected) | ❌ Only profiles with broken config |
| Fix takes effect immediately after manifest update | ✅ Yes | ❌ No (needs credential fix) |

## Prevention

When creating self-assigned tasks that write to skill files, the foreman task body should include a note to update `.bundled_manifest` as a verification step. Currently the manifest update is a manual step that's easy to miss.

## Verification checklist (for human/acceptance reviewers)

When a propagation task blocks with `review-required`, verify completion before marking done. This checklist is for the verifier (Senna, the user, or whichever authority accepts the foreman's handoff).

### 1. Hash sample against senna originals

Pick 3-5 representative files spanning different profiles and skill categories. Compare their hashes to the senna canonical:

```bash
cd ~/.hermes/profiles

# Example: systematic-debugging across 3 profiles
md5 -q senna/skills/software-development/systematic-debugging/SKILL.md
md5 -q architect/skills/software-development/systematic-debugging/SKILL.md
md5 -q coder/skills/software-development/systematic-debugging/SKILL.md

# humanizer across 4 profiles
md5 -q senna/skills/creative/humanizer/SKILL.md
md5 -q researcher/skills/creative/humanizer/SKILL.md
md5 -q security/skills/creative/humanizer/SKILL.md
md5 -q secretary/skills/creative/humanizer/SKILL.md

# obsidian (secretary-specific — only one copy to check)
md5 -q senna/skills/note-taking/obsidian/SKILL.md
md5 -q secretary/skills/note-taking/obsidian/SKILL.md
```

**Pass: all hashes for a given skill match across sourced and target profiles.**
**Fail: any hash differs → do not mark done. The propagation was incomplete.**

### 2. Confirm backups exist

```bash
ls -la architect/skills/software-development/systematic-debugging/SKILL.md.bak
ls -la secretary/skills/note-taking/obsidian/SKILL.md.bak
```

**Pass: `.bak` file exists with reasonable file size** (the pre-overwrite original). The worker creates a backup before every `cp` [PERSON_NAME]: `.bak` missing** — first-time write (never had a file there before), not a problem. Verify otherwise.

### 3. Spot-check DSL header integrity

Read the first 15-25 lines of at least one propagated file from each category (devops, creative, software-development). Confirm all compressed DSL headers are present:

- `IDENTITY:` — present with `{CurlyBrace}` compressed identity
- `REDFLAGS:` — present with `||` separated conditions
- `RATIONALIZATIONS:` — present with `|` separated reason pairs
- `QUICKREF:` — present with `→` separated pipeline steps

### 4. Report and mark done

Report results to the user with a summary table before [PERSON_NAME] Profiles Checked | Hash Match | Backup | DSL Headers |
|---|---|---|---|---|
| systematic-debugging | senna ↔ architect [PERSON_NAME] coder | ✅ | ✅ (11[PERSON_NAME]) | ✅ [ADDRESS] humanizer | senna ↔ researcher ↔ security ↔ secretary | ✅ | ✅ | ✅ |
| obsidian | [PERSON_NAME] secretary | ✅ | ✅ (2.9[PERSON_NAME]) | ✅ |
```

Mark complete:
```bash
hermes kanban complete <task_id> --result success --summary "32/32 files hash-verified. Backups preserved. All DSL headers intact. User approved."
```