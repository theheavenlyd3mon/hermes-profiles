---
name: multi-agent-orchestration
description: Complete multi-agent orchestration system — Kanban decomposition playbook for task graph creation + autonomous Foreman cron loop for execution, retry cycles, and escalation. Covers the full lifecycle from goal decomposition through worker dispatch to project completion.
version: 1.0.0
platforms: [linux, macos, windows]
tags: [kanban, foreman, orchestration, multi-agent, autonomous, cron, retry, workstream, decomposition]
metadata:
  hermes:
    tags: [kanban, foreman, orchestration, multi-agent, autonomous, cron, retry, workstream, decomposition]
    related_skills: [kanban-guru, hermes-profile-fleet, project-workspace, cron-pipeline]
---

# Multi-Agent Orchestration

This skill unifies two complementary operational modes:

| Mode | Skill Consolidated | Role |
|------|-------------------|------|
| **Decomposition & Routing** | `kanban-orchestrator` | Human-in-the-loop: you decompose goals, create task graphs, assign to specialist profiles |
| **Autonomous Execution** | `foreman-orchestration` | Hands-off: cron-driven Foreman polls board, manages retry cycles, escalates only when thresholds breached |

Use **Decomposition Mode** when you're actively planning and routing work. Use **Autonomous Mode** when you want a project to run without your involvement until it's done or needs you.

---

## Part 1: Decomposition & Routing (Kanban Orchestrator)

### When to Use the Board (vs. Just Doing the Work)

Create Kanban tasks when any of these are true:
1. **Multiple specialists needed** — research + analysis + writing = three profiles
2. **Work must survive crash/restart** — long-running, recurring, or important
3. **Human might interject** — human-in-the-loop at any step
4. **Parallel subtasks possible** — fan-out for speed
5. **Review/iteration expected** — reviewer profile loops on drafter output
6. **Audit trail matters** — board rows persist in SQLite forever

If *none* apply — small one-shot reasoning task — use `delegate_task` or answer directly.

### Step 0: Discover Profiles Before Planning

Hermes setups vary. No default specialist roster exists. The dispatcher silently fails on unknown assignees.

```bash
hermes profile list
# or just ask: "What profiles do you have set up?"
```

Cache the result. Re-asking wastes tool calls.

### Step 0.5: Verify Profile Models Match Task Needs

Kanban `--assignee` routes to a **profile**, not a model. Each profile has its own `model.default` in config.yaml.

```bash
grep 'default:' ~/.hermes/profiles/*/config.yaml
```

### Delegation Toolset Policy

`delegation` toolset is **disabled on all worker profiles** (coder, architect, reviewer, debugger, researcher, etc.). Only **foreman** (orchestrator) and **senna** (your shell) keep it enabled. This forces multi-profile work through Kanban.

### Anti-Temptation Rules

- **Do not execute work yourself** — create a Kanban task and assign it. Every single time.
- **Split multi-lane requests before creating cards** — extract independent lanes, one card per lane.
- **Run independent lanes in parallel** — link only true data dependencies.
- **If no specialist fits, ask the user which profile to use** — do not invent names.
- **Decompose, route, and summarize — that's the whole job.**

### Decomposition Playbook

#### Step 1 — Understand the Goal
Ask clarifying questions if ambiguous. Cheap to ask; expensive to spawn wrong fleet.

#### Step 2 — Sketch the Task Graph
1. Extract lanes from the request
2. Map each lane to a profile from Step 0
3. Decide independence vs. gating
4. Create independent lanes as parallel cards (no parent links)
5. Create synthesis/review cards with parent links

Show the graph to the user before creating cards.

#### Step 3 — Create Tasks and Link

**CLI (from terminal):**
```bash
# Title is POSITIONAL, not --title
hermes kanban create "research: Postgres cost vs current" \
  --assignee <profile-A> \
  --body "Compare costs over 3 years..." \
  --workspace "dir:/path/to/project"

# Link dependencies (repeatable)
hermes kanban create "synthesize: recommendation" \
  --assignee <profile-B> \
  --body "Synthesize T1 + T2..." \
  --parent t_abc123 --parent t_def456
```

**Python/tool (inside session):**
```python
t1 = kanban_create(title="...", assignee="<profile-A>", body="...", tenant=os.environ.get("HERMES_TENANT"))["task_id"]
t2 = kanban_create(title="...", assignee="<profile-B>", body="...", parents=[t1], tenant=...)["task_id"]
```

#### Step 4 — Dispatch & Monitor
```bash
hermes kanban dispatch
# Poll: hermes kanban show <id> | grep -E "^  status:"
```

#### Step 5 — Report Back
Tell the user what you created in plain prose with actual profile names.

### Feedback Loops (Retry Cycles)

Standard pattern: `implement → review → fix → re-review`

```bash
T1 — Implement (coder, retry_count=1)
  ↓ complete
T2 — Review (reviewer, retry_count=1, parent: T1)
  ↓ findings, clean=false
T3 — Fix (coder, retry_count=2, parent: T2)
  ↓ complete
T4 — Re-review (reviewer, retry_count=2, parent: T3)
  ↓ clean=true → done
```

**Rules:**
- Do NOT re-open T1 — create new task for each cycle
- Increment `retry_count` in metadata
- Embed prior findings in new fix task body
- Link parent to prior review task
- Use `workstream` string across all cycles

### Escalation Thresholds

When `retry_count >= max_retries` (default 3):
```python
kanban_block(reason="review-required: escalation — retry loop exhausted for workstream 'X'. Findings persist across 3 cycles. Needs human triage.")
```

Other escalation triggers:
- Identical findings across 2 consecutive cycles
- Scope expansion (≥3 emergent cards OR ≥10 files touched)
- Error/crash — worker exited uncleanly

### Research Task Scoping — Prevent Unbounded Research

Research tasks naturally expand. Define stopping condition in task body:

**Approach A — Source limit:** "Stop after 12 distinct sources"
**Approach B — Finding count:** "Stop after 8 distinct patterns"
**Approach C — Time budget:** `--max-runtime 30m`
**Approach D — Goal-oriented:** "Find 3 working examples with architecture patterns"

**Recovery for running unbounded tasks:** Drop `SCOPE.md` into task's workspace.

---

## Part 2: Autonomous Execution (Foreman Orchestration)

### Setup

Install the cron job that runs the Foreman loop:
```bash
hermes cronjob create \
  --name "foreman-autonomous-loop" \
  --schedule "every 10m" \
  --skills multi-agent-orchestration \
  --prompt "Poll the kanban board and manage the autonomous project execution loop. Escalate when retries exhausted or scope exceeds thresholds." \
  --deliver origin
```

**Optional gate script** (skips LLM call when no work):
```bash
#!/usr/bin/env bash
# ~/.hermes/profiles/senna/scripts/kanban-gate.sh
KANBAN_DB="~/.hermes/kanban.db"
[ ! -f "$KANBAN_DB" ] && exit 0
ACTIVE=$(sqlite3 "$KANBAN_DB" "SELECT COUNT(*) FROM tasks WHERE status IN ('ready', 'running')" 2>/dev/null || echo "0")
[ "$ACTIVE" -eq 0 ] 2>/dev/null && exit 0
sqlite3 -separator ' | ' "$KANBAN_DB" "SELECT id, title, status, assignee FROM tasks WHERE status IN ('ready', 'running') ORDER BY created_at;"
```
```bash
hermes cronjob update <job-id> --script kanban-gate.sh
```

### The Polling Loop (Every Tick)

#### Step 1: Read the Board
```bash
hermes kanban list --json
```

#### Step 2: Handle Completed Review Tasks
For each `assignee == "reviewer"` and `status == "done"`:

```python
if task.metadata.get("clean") == True:
    record_workstream_done(workstream)
else:
    new_retry = (task.metadata.get("retry_count") or 1) + 1
    if new_retry > MAX_RETRIES:
        escalate(workstream, task, "retry loop exhausted")
        continue
    # Create fix task
    fix_id = hermes kanban create f"Fix {workstream} (retry {new_retry})" \
        --assignee coder --body "Workstream: {workstream}\nRetry: {new_retry}\nFindings: ..." \
        --parent task.id --workspace dir:/path/to/project
    # Create review task gated behind fix
    hermes kanban create f"Review {workstream} (retry {new_retry})" \
        --assignee reviewer --body "..." --parent fix_id
```

#### Step 3: Dispatch Ready Tasks
```bash
hermes kanban dispatch
```

#### Step 4: Handle Blocked Tasks

**A. `review-required` blocks** (worker asked for human input):
- `review-required: escalation` → retry loop exhausted, Foreman notes for user
- Normal `review-required` → first-cycle review, normal handoff

**B. `gave_up` blocks** (dispatcher exhausted retries on non-review task):
Read run history, match failure pattern:

| Pattern | Likely Cause | Next Step |
|---------|-------------|-----------|
| `timed_out` → `crashed` | Runtime limit tight, then provider init issue on retry | Increase `--max-runtime` on re-dispatch |
| `crashed` → `crashed` (same error) | Provider/credential issue | Check profile config & API key |
| `timed_out` → `timed_out` | Runtime limit too tight | Increase `--max-runtime` |
| All `protocol_violation` | Model/provider misconfigured | Audit profile config & credentials |

#### Step 5: Report Summary

**Workstream table** — group by logical workstream
**Dispatcher result** — spawned/blocked/promoted counts
**Escalation check** — explicit verification of each threshold
**Active tasks** — in-progress work with timing

**No-op tick handling:** 7/8 ticks are idle. Skip deep analysis on unchanged boards.

### Retry Counting Convention

```text
T1 — Implement (coder, retry_count=1)
  ↓ complete
T2 — Review (reviewer, retry_count=1)
  ↓ findings
T3 — Fix (coder, retry_count=2, parent: T2)
  ↓ complete
T4 — Re-review (reviewer, retry_count=2, parent: T3)
  ↓ clean=true → done
```

`retry_count` = current iteration of the **work pair** (fix + review).

### Worker Metadata Schema (Required)

| Field | Type | Required | Source |
|-------|------|----------|--------|
| `workstream` | string | Yes | Identical across all tasks in unit |
| `clean` | bool | Review tasks | `true` = no findings, workstream done |
| `findings` | list[dict] | Review tasks | `{severity, file, line, issue}` |
| `retry_count` | int | Yes | Current iteration number |
| `changed_files` | list[str] | Coder tasks | Files modified |
| `created_cards` | list[str] | Any | Emergent tasks spawned |

---

## Escalation Rules

Foreman escalates to user under:

1. **Retry loop exhausted:** `retry_count > MAX_RETRIES` (default 3)
2. **Identical findings:** ≥80% overlap between cycles
3. **Scope expansion:** Single task produces ≥3 emergent cards OR touches ≥10 files
4. **Dispatcher gave_up:** Non-review task failed all retries
5. **Unexpected worker failure:** Exited without `kanban_complete`/`kanban_block`

---

## Design Decisions

### A2A Protocol Plugin — Evaluated, Deferred
Google's A2A protocol (hermes-a2a-preview) is point-to-point with no chaining, orchestration, or persistent board. Existing Kanban system covers full need with traceability. A2A only worth revisiting for real-time cross-machine agent communication.

### Common Pitfalls

- **Desktop GUI projects:** Task body must specify headless test commands (`npm run server`, `npm test`) — never `npm start`
- **One Foreman cron per board** — not per project. Workstreams distinguish projects.
- **Cron interval ≥10m** — gives workers time to finish
- **Research tasks run 20-60 min** — don't flag as stuck
- **Same-profile tasks serialize** — two researcher cards on same profile run sequentially
- **Running tasks with valid claim = alive** — don't reclaim based on `ps aux`
- **Fix profile config BEFORE unblocking** — re-dispatching broken config just burns runs
- **Foreman task itself can block** — diagnose and fix directly, don't escalate

---

## Verification

Test the loop:
```bash
# 1. Create test workstream
hermes kanban create "test: verify loop" --assignee coder --body "Create /tmp/foreman-test.txt with 'hello'"
hermes kanban create "test: verify file" --assignee reviewer --body "Check /tmp/foreman-test.txt exists" --parent <task_id>

# 2. Wait for next cron tick (≤10 min)

# 3. Check completion
hermes kanban list --archived

# 4. Clean up
hermes kanban archive <id1> <id2>
```

---

## Related Skills

- `kanban-guru` — Virtual Kanban expert for flow diagnosis, WIP limits, multi-portfolio design (consulting mode)
- `hermes-profile-fleet` — Profile lifecycle, model assignments, workspace conventions
- `project-workspace` — Shared filesystem layout, AGENTS.md conventions
- `cron-pipeline` — Overnight pipeline patterns, catch-up batches

---

## Reference Files

- `references/skill-propagation.md` — Propagating compressed skills from senna to specialists
- `references/nous-profile-model-assignment.md` — Nous model availability, pricing, per-profile recommendations
- `references/goban-comparison.md` — Comparison with Goban (standalone Go Kanban server)
- `references/gateway-stopped-recovery-pattern.md` — Recovery when profiles show `Gateway: stopped`