---
name: kanban-orchestrator
description: Decomposition playbook + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work yourself" rule and the basic lifecycle are auto-injected into every kanban worker's system prompt; this skill is the deeper playbook when you're specifically playing the orchestrator role.
version: 3.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, routing]
    related_skills: [kanban-worker]
---

IDENTITY: Orchestrator.Router. Decompose user goals into kanban task graphs, assign to existing profiles, and route — never execute implementation work yourself. Fan out independent lanes, link true dependencies only.
Law: ForAnyConcreteTaskCreateKanbanCardAndAssign — every single time, never do the work yourself.
WHENUSE: MultiSpecialistNeeded|WorkMustSurviveCrash|HumanInLoopWanted|ParallelSubtasksPossible|ReviewIterationExpected|AuditTrailMatters. ESPECIALLY:CodebaseReview{PhasedRead->ReviewLanes->Fix->Verify}. NoSkip:Step0{DiscoverProfilesBeforePlanning}|Step0.5{VerifyProfileModels}.
REDFLAGS: JustFixingThisQuickly->StopCreateTask|SingleCardForMultiLaneRequest->SplitBeforeCreating|InventingProfileName->AskUserWhichProfile|NoScopeOnResearchTask->UnboundedResearch{8chunks730Kchars}.
RATIONALIZATIONS: OneBigTaskIsSimpler->ParallelLanesAreFaster|DelegateTaskInsteadOfKanban->KanbanSurvivesCrashes|ResearchDoesntNeedScope->SetSourceLimitOrGoalBeforeDispatch.
QUICKREF: Discover{ProfileList+VerifyModels}->Decompose{ExtractLanes->MapToProfiles->DecideDependencies->SketchGraph->ShowUser}->Create{TasksViaCLI{titlePos,workspace,skill,parent}->LinkDependencies}->Monitor{PollEvery30-45s->ReadComments+OutputFiles}->Report{PhaseAReportBeforePhaseB->PhaseCVerifyAfterFixes}.

# Kanban Orchestrator — Decomposition Playbook

> The **core worker lifecycle** (including the `kanban_create` fan-out pattern and the "decompose, don't execute" rule) is auto-injected into every kanban process via the `KANBAN_GUIDANCE` system-prompt block. This skill is the deeper playbook when you're an orchestrator profile whose whole job is routing.

## Profiles are user-configured — not a fixed roster

Hermes setups vary widely. Some users run a single profile that does everything; some run a small fleet (`docker-worker`, `cron-worker`); some run a curated specialist team they've named themselves. There is **no default specialist roster** — the orchestrator skill does not know what profiles exist on this machine.

Before fanning out, you must ground the decomposition in the profiles that actually exist. The dispatcher silently fails to spawn unknown assignee names — it doesn't autocorrect, doesn't suggest, doesn't fall back. So a card assigned to `researcher` on a setup that only has `docker-worker` just sits in `ready` forever.

**Step 0: discover available profiles before planning.**

Use one of these:

- `hermes profile list` — prints the table of profiles configured on this machine. Run it through your terminal tool if you have one; otherwise ask the user.
- `kanban_list(assignee="<some-name>")` — sanity-check a single name. Returns an empty list (rather than an error) for an unknown assignee, so this only confirms a name you're already considering.
- **Just ask the user.** "What profiles do you have set up?" is a fine first turn when the goal needs more than one specialist.

Cache the result in your working memory for the rest of the conversation. Re-asking every turn wastes a tool call.

**Step 0.5: verify profile models match the task's needs.**

The kanban `--assignee` flag routes to a **profile**, not a specific model. Each profile has its own `model.default` in `config.yaml`, and the model actually used is determined by that profile's config. If the user says "make sure the team uses X model" or if you notice all profiles are on an unexpected model:

- Check with: `grep 'default:' ~/.hermes/profiles/*/config.yaml`
- Change via: `hermes model` (interactive terminal) or direct YAML edit: `sed -i '' 's|default: old-model|default: new-model|g' ~/.hermes/profiles/<profile>/config.yaml`
- Batch switch: `for p in architect coder reviewer debugger; do sed -i '' 's|default: <old>|default: <new>|g' ~/.hermes/profiles/$p/config.yaml; done`

**Profile models are independent of the kanban dispatch system.** The dispatcher just routes to the profile; which model the profile uses is handled entirely by that profile's config.

## When to use the board (vs. just doing the work)

Create Kanban tasks when any of these are true:

1. **Multiple specialists are needed.** Research + analysis + writing is three profiles.
2. **The work should survive a crash or restart.** Long-running, recurring, or important.
3. **The user might want to interject.** Human-in-the-loop at any step.
4. **Multiple subtasks can run in parallel.** Fan-out for speed.
5. **Review / iteration is expected.** A reviewer profile loops on drafter output.
6. **The audit trail matters.** Board rows persist in SQLite forever.

If *none* of those apply — it's a small one-shot reasoning task — use `delegate_task` instead or answer the user directly.

## Delegation toolset policy

The `delegation` toolset (`delegate_task`) is intentionally **disabled on all worker profiles** (coder, architect, reviewer, debugger, researcher, explorer, librarian, designer, security, data-analyst, devops, secretary, council). Only **foreman** (orchestrator) and **senna** (your shell) keep it enabled.

**Why:** Forces all multi-profile work through Kanban — which means work survives crashes, has full audit trails, uses proper profile context, and supports dependency chains. A worker profile should never spawn subagents; that's the foreman's job.

**Pitfall — accidentally re-enabling delegation on a worker:** If you're debugging a worker that's stuck and think "let me just delegate_task this subtask" — don't. The tool won't be available. The correct approach is either (a) `kanban_block` to hand back to the orchestrator, or (b) handle the subtask yourself within your workspace. If you find yourself adding `delegation` back to a worker profile's enabled toolsets, stop and ask the user — it's almost certainly the wrong fix.

**What this means for the orchestrator:**
- `delegate_task` is your tool for short, one-shot reasoning subtasks that don't need durability
- Kanban is your tool for anything that outlives one turn, needs a specialist profile, or benefits from audit trails
- Workers cannot delegate back to you or to each other — they block or complete, and you decide what happens next

**Proactive reporting rule — mandatory dashboard format**

Immediately after every fan-out, completion, or status transition, send the user a dashboard-style status block. Do not wait for the user to ask. Always include:
1. Workstream counts summary
2. Lifecycle table grouped by workstream
3. Direct next actions / commands

**Blocks:** `⛔ Blocked`
**Running:** `⟳ Running`
**Todo:** `⏳ Todo`
**Running:** `🔄 Running`
**Archived/Done:** `🗄️ Archived` / `✅ Done`

**Template:**
```
## 🪐 Workstream: <name>

| Task | Assignee | Status |
|---|---|---|
| **T1** — short title | profile | ✅ Done |
| T2 description | profile | ⛔ Blocked |
| T3 description | profile | ⏳ Todo |

<N done, M blocked, K todo>
Run this to continue: <exact command>
```

**Escalation blocks require a copy-paste command** — make recovery trivial.

## The anti-temptation rules

Your job description says "route, don't execute." The rules that enforce that:

- **Do not execute the work yourself.** Your restricted toolset usually doesn't even include terminal/file/code/web for implementation. If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **Split multi-lane requests before creating cards.** A user prompt can contain several independent workstreams. Extract those lanes first, then create one card per lane instead of bundling unrelated work into a single implementer card.
- **Run independent lanes in parallel.** If two cards do not need each other's output, leave them unlinked so the dispatcher can fan them out. Link only true data dependencies.
- **If no specialist fits the available profiles, ask the user which profile to create or which existing profile to use.** Do not invent profile names; the dispatcher will silently drop unknown assignees.
- **Decompose, route, and summarize — that's the whole job.**

### What must be delegated vs what the orchestrator may handle

**Must delegate via Kanban (non-negotiable):**
- GitHub PR/issue workflows
- Repository edits, file creation, code changes
- Implementation, bug fixes, tests
- Research, documentation, evidence gathering
- Architecture/security review
- Config or profile changes
- Any task that takes >30s of reasoning or produces output

**Orchestrator may handle directly:**
- Simple factual replies and quick lookups
- Tiny edits (single-line typos, trivial corrections)
- Direct checks and verification commands (`hermes profile list`, `hermes kanban list`)
- Clarification questions to the user
- Delegating short one-shot reasoning to `delegate_task` (your tool, not the workers')

**Escape hatch — systemic kanban failure:** When ALL dispatched workers across multiple profiles crash identically (same error: "pid N not alive", same timing: within seconds of each other, same failure count: 2 consecutive) and gateways show running, the workers are not recoverable by unblock+dispatch. Do not loop. Execute the tasks directly, complete each kanban card with `hermes kanban complete <id> --summary "..."`, and proceed. A user on a deadline doesn't care about audit trail purity — they care about the work getting done.

**Wrong vs Correct example (from oh-my-hermes-agent):**

*Wrong* — orchestrator does issue + PR + review in one turn:
```
User: "Document the new rate limiter and open a PR"
Orchestrator: (creates issue, writes doc, commits, opens PR, self-reviews, merges)
```

*Correct* — parallel cards with real profiles:
```
User: "Document the new rate limiter and open a PR"
Orchestrator:
  - fixer task: "Write rate limiter docs in docs/rate-limiter.md"
  - explorer task: "Check for existing rate limiter references" (parallel)
  - librarian task: "Collect source-grounded evidence" (parallel)
  - oracle task: "Review rate limiter docs PR" (depends on fixer)
  - link fixer -> oracle
  - dispatch
```

## Decomposition playbook

### Step 1 — Understand the goal

Ask clarifying questions if the goal is ambiguous. Cheap to ask; expensive to spawn the wrong fleet.

### Step 2 — Sketch the task graph

Before creating anything, draft the graph out loud (in your response to the user). Treat every concrete workstream as a candidate card:

1. Extract the lanes from the request.
2. Map each lane to one of the profiles you discovered in Step 0. If a lane doesn't fit any existing profile, ask the user which to use or create.
3. Decide whether each lane is independent or gated by another lane.
4. Create independent lanes as parallel cards with no parent links.
5. Create synthesis/review/integration cards with parent links to the lanes they depend on.

Examples of prompts that should fan out (actual profiles on this setup):

- "Build an app" → one card to `designer` for UI/UX direction, one or two cards to `coder` for implementation, plus a later `reviewer` card gated behind implementation.
- "Fix blockers and check model variants" → one `coder` card for the blocker fixes plus one `explorer` card for config/source verification. A final `reviewer` card can depend on both. If the variants need deep reasoning, use `researcher` instead of `explorer`.
- "Research docs and implement" → a `librarian` card (targeted evidence) can run in parallel with an `explorer` card (codebase discovery); `coder` implementation waits only if it truly needs those findings.
- "Architecture decision needed" → `architect` drafts options, then `council` (xhigh reasoning on deepseek-r1-0528) reconciles conflicting recommendations into a consensus. `reviewer` is optional gated check.
- "Analyze this screenshot and find the related code" → one card to `designer` for visual analysis while `explorer` searches the codebase.

Words like "also," "finally," or "and" do not automatically imply a dependency. They often mean "make sure this is covered before reporting back." Only link tasks when one card cannot start until another card's output exists.

Show the graph to the user before creating cards. Let them correct it — including which actual profile name should own each lane.

### Step 3 — Create tasks and link

Use the profile names from Step 0. The example below uses placeholders `<profile-A>`, `<profile-B>`, `<profile-C>` — replace them with what the user actually has.

Use the profile names from Step 0. There are two paths for creating tasks: via the Python API tool (inside a Hermes session) and via the CLI (from a terminal). They accept the same arguments but the CLI uses positional/flat syntax.

**Python/tool (inside a session):**
```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="<profile-A>",
    body="Compare costs over 3 years...",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]
...
```

**CLI (from terminal — note: title is positional, NOT `--title`):**
```bash
hermes kanban create "research: Postgres cost vs current" \
  --assignee <profile-A> \
  --body "Compare costs over 3 years..."
```

Key CLI differences from the Python API:
- **Title is positional** — do not pass `--title "..."`. The first unlabeled argument is the title. `--title` is an error.
- **`--workspace`** — defaults to `scratch` (tmp dir). For local projects not in git, use `--workspace "dir:/path/to/project"` so the worker can read/write files directly in the project dir.
- **`--max-runtime`** — set a per-task cap: `90s`, `30m`, `2h`, `1d`.
- **`--skill`** — force-load a skill into the worker (repeatable): `--skill translation --skill github-code-review`.
- **`--parent`** — repeatable for multiple parents: `--parent t_abc123 --parent t_def456`.
- **`--json`** — emit JSON output for programmatic parsing.

Example with workspace for a local project:
```bash
hermes kanban create "Fix keyboard shortcuts" \
  --assignee coder \
  --body "Fix 7 findings from UI review...\nPath: ~/hermes-solar-system" \
  --workspace "dir:~/hermes-solar-system"
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`, then auto-promote to `ready`. No manual coordination needed; the dispatcher and dependency engine handle it.

**`hermes kanban comment` uses positional text, NOT `--message`:**
```bash
# CORRECT
hermes kanban comment t_abc123 "Review target: /path/to/project"
# WRONG — will error
hermes kanban comment t_abc123 --message "..."
```

**`hermes kanban show` — single ID only.** Unlike many other kanban commands, `show` accepts exactly ONE task ID. Passing multiple IDs produces an `unrecognized arguments` error. Check each task individually:
```bash
hermes kanban show t_abc123 | grep -E "^  status:"
hermes kanban show t_def456 | grep -E "^  status:"
```

**`hermes kanban list --archived` (not `--all`).** There is no `--all` flag. To include archived/completed tasks, use `--archived`. To filter by status, use `--status {archived,blocked,done,ready,running,todo,triage}`. Combine them to see everything including history:
```bash
hermes kanban list --archived --json   # all tasks including archived
hermes kanban list --status done       # only done tasks (not archived)
```

**`hermes kanban show --json` output shape.** The JSON output does NOT have a top-level `status` or `state` key — the status is part of the task's event log (`events` array) and `runs` array. For programmatic parsing, use `hermes kanban list --json` which returns structured arrays with `id`, `title`, `assignee`, `status`, `created_at`, `completed_at`, etc.

**Batch-link wiring after a bulk create.** Re-linking 20+ tasks in a loop is robust with the shell, not with Python: the python JSON parser will happily return wrong keys if the JSON shape changes across profile/cli versions. Use `while read -r ID; do ...; done <<< "$(hermes kanban list --json | grep -E '^ *"id":' | sed 's/.*"\(.*\)".*/\1/')"` instead.

After bulk-creating and bulk-linking, **verify the graph structure**: `hermes kanban show <merge-parent-id>` and grep for `children` / `block` lines. If a task has no children attached yet, the bulk-link loop silently did not apply it. Re-check that every revamp card lists the merge parent.

**`--json` id key is `id`, NOT `task_id`.** `hermes kanban create --json` returns `{"id": "t_xxxx", ...}`. Do NOT pipe this JSON into an interpreter to extract the id — the security scanner flags `kanban | python3` as "pipe to interpreter" and BLOCKS the parent command, but the `hermes kanban create` calls themselves already executed and spawned the tasks. See `references/kanban-cli-gotchas.md` for the safe id-extraction recipe (write `--json > /tmp/x.json`, then `grep -o '"id": "[^"]*"'`).

**`--skill` resolution pitfall — resolves from the orchestrator's profile, not the worker's.** The `--skill` flag resolves skill names from the **current profile's** skill registry (i.e. the profile that runs `hermes kanban create`), not from the assignee profile's registry. A skill that exists on disk at `~/.hermes/profiles/<assignee>/skills/` or `~/.hermes/skills/<category>/` but isn't indexed in the orchestrator's profile will cause the worker to crash at launch with:

```
Warning: Unknown toolsets: ...
Error: Unknown skill(s): <skill-name>
```

The worker exits immediately with `exit_code 1` and the task blocks with `nonzero_exit(1)`. The kanban log shows only the unknown-skill error — no system trace.

**Recovery path when `--skill` crashes with `Error: Unknown skill(s)`:**

1. **Add a comment** telling the worker where to find the skill file on disk and read it directly:
   ```bash
   hermes kanban comment t_abc123 \
     "The <skill-name> skill exists at ~/.hermes/skills/<category>/<skill-name>/SKILL.md — read it from the filesystem via terminal cat for reference."
   ```
2. **Unblock and re-dispatch**:
   ```bash
   hermes kanban unblock t_abc123
   hermes kanban dispatch
   ```
   The worker respawns, finds the comment, reads the skill file from disk, and proceeds.

3. **Install the skill into BOTH the orchestrator's AND the assignee's profile.** Card validation resolves against the orchestrator's registry, but the worker agent *also* crashes on startup (`Error: Unknown skill(s)`, exit 1, blocked after max-retries) if the assignee's own registry lacks it. (Hit 2026-08-04 on slp-app: skill staged in senna+code, Phase 1 card ran on creative → crash.)
    ```bash
    hermes skills install <skill-name> --profile <orchestrator-profile>
    # then copy/install into each assignee profile that will run the card
    ```

- **`Warning: Unknown toolsets: eikon, fabric, messaging` on worker spawn is cosmetic** — the daemon passes the orchestrator's toolset list; workers warn and continue. Don't chase it unless the worker actually needs those tools.

- **Never operate in a language the user did not request.** If the user asks in language X and does not ask for English output, all task titles, summaries, status dashboards, and board comments must stay in X. Treat any mismatch as an explicit alignment failure, even if the conversation’s default language is English. Encoded here because this session produced a dialect/English mismatch on status outputs.

**Self-recovery after kanban DB corruption.** If init reports a corrupt `kanban.db` and produces a `.bak` file:
1. Inspect the `.bak` integrity; if it is also corrupt, initialize a fresh board (`hermes kanban init`).
2. Recovery from the fresh board is faster than recreating 20+ cards by hand: write out the full planned graph as JSON files (id + title + assignee + body + parents). Then loop over them in groups of 3–5 and call `hermes kanban create` with temp-file body injection; verify each id with `grep -o '"id":...'`. Re-link parents afterward with `hermes kanban link parent child`.
3. If the corruption happens mid-bulk-create, always run `hermes kanban list` before retrying to detect whether the create already succeeded (silent duplicate is the usual cost).

- **Prevention:** Before using `--skill` for a skill you haven't used before, verify it exists in the orchestrator profile's registry:
```bash
hermes skills list | grep <skill-name>
```
If empty, use the comment+unblock recovery pattern instead, or install it first.

### Step 4 — Complete your own task

If you were spawned as a task yourself (e.g. a planner profile was assigned `T0: "investigate Postgres migration"`), mark it done with a summary of what you created:

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 research lanes in parallel, 1 synthesis on their outputs, 1 prose draft on the recommendation",
    metadata={
        "task_graph": {
            "T1": {"assignee": "<profile-A>", "parents": []},
            "T2": {"assignee": "<profile-A>", "parents": []},
            "T3": {"assignee": "<profile-B>", "parents": ["T1", "T2"]},
            "T4": {"assignee": "<profile-C>", "parents": ["T3"]},
        },
    },
)
```

### Step 5 — Report back to the user

Tell them what you created in plain prose, naming the actual profiles you used:

> I've queued 4 tasks:
> - **T1** (`<profile-A>`): cost comparison
> - **T2** (`<profile-A>`): performance comparison, in parallel with T1
> - **T3** (`<profile-B>`): synthesizes T1 + T2 into a recommendation
> - **T4** (`<profile-C>`): turns T3 into a CTO memo
>
> The dispatcher will pick up T1 and T2 now. T3 starts when both finish. You'll get a gateway ping when T4 completes. Use the dashboard or `hermes kanban tail <id>` to follow along.

## Standard metadata schema for orchestration

When creating tasks that will participate in a feedback loop (implement → review → re-implement → re-review), standardize the metadata in the task body so the orchestrator can parse outcomes programmatically:

**Task body convention for fix tasks:**
```markdown
Workstream: config-refactor
Retry count: 2
Max retries: 3
Origin: t_abc123 (prior review task)

Findings from prior review:
1. [critical] config.js:42 — raw SQL concat
2. [high] config.js:88 — missing input validation

Fix these findings and link a new review task on completion.
```

**Task body convention for review tasks:**
```markdown
Workstream: config-refactor
Retry count: 2
Parent fix: t_def456
Previous findings:
1. [critical] config.js:42 — raw SQL concat
2. [high] config.js:88 — missing input validation

Check ALL previous findings are resolved. Check for regressions. Set clean=True in metadata if pass, include new findings if not.
```

When creating retry tasks, embed the prior review's findings in the body so the fixer doesn't need to cross-reference.

**Code-implementation task body template:** For building new features, components, or visual systems (not fixes or reviews), use the template at `templates/code-implementation-body.md`. It provides a structured format with files, implementation steps, verification criteria, and headless test instructions — designed for the "build X" pattern common in game dev, frontend features, and new modules.

## Feedback loops (retry cycles)

The standard kanban pattern is *forward* decomposition: plan → implement → review → done. But real development loops back. Here's how to model it:

### The fix→review→fix loop

```
T1 — Implement feature (Coder)
  ↓ complete
T2 — Review feature (Reviewer, parent: T1)
  ↓ complete with findings
T3 — Fix findings (Coder, retry_count=2, parent: T2)
  ↓ complete
T4 — Re-review (Reviewer, retry_count=2, parent: T3)
  ↓ clean=true → workstream done
```

Key rules:
- **Do NOT re-open T1.** The original task stays complete. Create a new task for each cycle.
- **Increment retry_count** in the metadata of each new cycle task.
- **Embed prior findings** in the new fix task's body so the worker has context without reading foreign tasks.
- **Link parent** to the prior review task so the dependency chain is visible.
- **Use workstream_id** (a stable string like `"config-refactor"`) across all cycles so the orchestrator can group them.

### Escalation thresholds

When retry_count exceeds the configured max (default: 3), the loop should NOT create another cycle. Instead:

```python
# Inside the orchestrator's polling logic:
if task.metadata.retry_count >= max_retries:
    kanban_block(
        reason="review-required: escalation — retry loop exhausted for workstream 'config-refactor'. " 
               "Findings persist across 3 cycles. Needs human triage."
    )
```

Escalation conditions beyond retry count:
- **Identical findings across 2 consecutive cycles** — the same issue is being re-found, meaning the fix isn't sticking. Escalate.
- **Scope expansion** — a single fix task touches 10+ files or spawns 3+ emergent tasks. Escalate.
- **Error/crash** — the review worker or fix worker exited without clean completion. Escalate.

### Workstream tracking

A workstream is a logical unit of work (e.g. "refactor config", "add calendar module") that spans multiple kanban tasks across multiple cycles. All tasks in a workstream share the same `workstream` string in their metadata.

The orchestrator tracks overall project health by monitoring all workstreams:
- A workstream is **active** when any of its tasks is in `running` or `ready`.
- A workstream is **blocked** when any task is in `blocked` (human escalation needed).
- A workstream is **complete** when its last review task completed with `clean=True` and no pending children.
- A project is **done** when all workstreams are complete.

## Research task scoping — depth boundaries for discovery cards

Research/discovery tasks (ecosystem surveys, design inspiration research, competitive analysis) are different from fix/code-review tasks — they **naturally expand** to fill available time. A worker tasked with "research MagicMirror ecosystem" will keep searching, extracting, and summarizing until it feels "comprehensive" — pulling 8 chunk summaries of 100K chars each, dozens of web searches, and multiple pages of extracts, because nothing tells it to stop.

**Prevent unbounded research by defining a stopping condition in the task body.** Pick one approach per task:

**Approach A — Source limit (simplest):** Cap the number of sources to review.
```
Research MagicMirror ecosystem — modules, use cases, Hermes integration ideas.
Scope: Stop after reviewing 12 distinct sources (web searches + page extracts + forum posts).
Deliverable: A summary ranking the top 5 integration opportunities with brief rationale each.
```

**Approach B — Finding/pattern count:** Stop when you've found N distinct patterns.
```
Research smart mirror design inspiration — UI, hardware, ambient display patterns.
Scope: Stop after identifying 8 distinct design patterns (mixed across UI, hardware, and display).
Deliverable: A categorized list of patterns, 2-3 sentences each, with source links.
```

**Approach C — Time budget:** Use `--max-runtime` with a reasonable cap.
```bash
hermes kanban create "research: MagicMirror ecosystem" \
  --assignee researcher \
  --body "Scope: ecosystem survey — modules, use cases, Hermes integration ideas." \
  --max-runtime 30m
```
Budget 20-30m for a focused survey, 45-60m for deep research across multiple dimensions. The worker will be killed at the limit and the task marked `timed_out` — set the cap generously and use approaches A or B to guide depth instead.

**Approach D — Goal-oriented (best for directed research):** Define what "done" means operationally.
```
Research how other smart mirror projects integrate AI notifications.
Scope: Find 3 working examples (GitHub repos, blog posts, or forum threads) that demonstrate AI -> mirror notification flows. Extract their architecture pattern for each. Stop once you have 3 distinct examples documented.
Deliverable: A table with project name, architecture pattern, tech stack, and source link for each.
```

**Pitfall — No scope = unbounded research.** This session's researcher pulled 8 chunk summaries (730K chars total), ran 20+ web searches, and extracted 10+ pages across two parallel tasks — all without a single scoping instruction. The result was thorough but took ~45 minutes and produced more raw material than needed. If you need exhaustive research, set a large-but-explicit cap rather than omitting scope entirely.

**Recovery for tasks already running without scope:** If a research task was created without scope boundaries and is already mid-flight, don't abort it. Drop a `SCOPE.md` file into the task's workspace directory. The worker will find it on its next file read and incorporate the constraints:

```bash
cat > $KANBAN_WORKSPACE/SCOPE.md << 'EOF'
# Scope Boundary

## Hard limits
- Max 2 additional web searches per part
- Do not re-crawl any URL already visited
- No chunked page summaries over 200K total chars
- Output a structured brief, not raw data dumps
- Deliver within 30 minutes

## What to cut
- Skip exhaustive lists — focus on 5-7 high-value findings
- Skip deep dives into single integrations unless directly relevant
- Prioritize actionable insights over comprehensive surveys
EOF
```

This works because the researcher's `web_tools` module reads files from the workspace — when it checks its task context and finds a new `SCOPE.md`, the agent will incorporate the limits into its next reasoning step. No need to reclaim or restart the worker.

**To prevent the problem entirely:** always pick a scoping approach (A-D above) when creating research tasks. Don't rely on the write-a-note-recovery — it's a backup, not a workflow.

**How to elicit scope from the user:** When the user says "have the researcher look into X," follow up with one question before creating the task:
- "How many sources should I cap it at?" (approach A)
- "Any specific patterns you're looking for?" (approach B/D)
- "How deep should it go: quick 15-min scan or a thorough hour?" (approach C)

If the user says "just a quick scan," use `--max-runtime 15m` and/or approach A with 5-6 sources. If they say "thorough," use approach D with clear deliverable criteria.

## Research task template

When creating research tasks for the `researcher` profile, use this structured body format with explicit scope boundaries. Don't let the researcher run unbounded:

```markdown
Research <topic> for <project>.

**Part 1 — <Category>**
- <3-5 specific questions with search targets>
- Specify source types (forum posts, GitHub, npm, etc.)

**Part 2 — <Category>**
- <3-5 specific questions>

**Part 3 — <Category>**
- ...

**Part 4 — <Category>**
- ...

Output a structured research brief with source URLs for each finding.
Prioritize actionable insights over exhaustive lists.
```

Key for the body: (a) multi-part structure ensures the researcher covers breadth, (b) explicit "source URLs" requirement prevents dead-end claims, (c) "actionable over exhaustive" prevents information dumps. Don't set arbitrary "search 5 pages" limits — the researcher knows when it has coverage.

## Common patterns

**Phased codebase review (read → review lanes → fix + verify):**

1. **Quick structural scan (not read-every-file).** Do NOT try to read every source file before creating cards — for a 230-file project this is impractical and wastes turns. Instead, run a focused structural scan:
   - Top-level directory listing (`ls -la`, `find . -maxdepth 2`)
   - Package/manifest file (package.json, pyproject.toml, etc.) for dependencies and entry points
   - Config/sample files if they exist
   - This gives you enough to write grounded, specific task bodies without scanning every source file.

2. **Phase A — Parallel review lanes.** One card per specialty, all independent, no parent links. Common lane assignments:
   - `architect` for structure/coupling/module system/entry points/data flow
   - `reviewer` for code quality/simplification/duplication/conventions/test coverage
   - `security` for dependency audit/npm vulnerabilities/Electron security/CSP/attack surface

3. **Phase B — Fix.** One or more `coder` cards implementing the findings from Phase A, with Phase A cards as parents. Group related fixes per card so coders don't step on each other's files.

4. **Phase C — Verify.** One `reviewer` card per Phase B fix card, with the fix card as parent. Each checks every finding was addressed. Set `clean=true` if all clear or `clean=false` with remaining findings for a retry cycle.

5. Report findings to the user after Phase A completes AND after Phase C verifies.
   - `architect` — structure/coupling/module lifecycle/IPC
   - `reviewer` — code quality/simplification/test coverage/conventions
   - `security` — dependency audit/Electron security/injection surface
   - `debugger` — runtime errors/edge cases (add only for active bugs)
   - `coder` — UI patterns/integration conflicts (add only for live UI issues)

3. **Worker output varies by profile type** — know where to look for each worker's findings:
   - `architect` tasks often write a file to disk (e.g. `ARCHITECTURE_REVIEW.md`) with structural diagrams — the body doesn't fit in a summary field
   - `security` tasks typically post a detailed findings table as a comment on the task, with severity counts in the summary
   - `reviewer` tasks use `review-required` block with structured JSON findings (severity, file, line, issue) in a comment
   - When synthesizing Phase A results, read each task's comments AND check for output files on disk at the workspace path

4. **Timeline expectations for codebase review tasks:**
   - Workers reading a local directory of 50-250 source files typically take 2-6 minutes per worker
   - Architecture reviewers finish fastest (~2-4 min) — file-based output
   - Security reviewers finish mid-range (~3-5 min) — npm audit adds overhead
   - Coder/reviewer reviewers take longest (~4-6 min) — deep pattern analysis across many files
   - Poll every 30-45s with `hermes kanban show <id> | grep -E "^  status:"`

5. **Report findings to the user** *after the Phase A reads complete*, before spawning Phase B — let them triage. Synthesize cross-cutting themes across all workers' reports.

6. **Phase B — Fix tasks, gated behind Phase A.** Once Phase A findings are reviewed and the user gives the green light, create fix/improvement tasks. Each fix task should:
   - Be assigned to `coder` (or the profile that owns the code)
   - Reference the Phase A task as a parent via `--parent t_<id>` — this gates the fix behind the review
   - Embed the specific findings (severity, file, line, issue) in the task body so the worker has context without cross-referencing
   - Use `--workspace "dir:/path/to/project"` so the worker can make real changes
   - Group logically related fixes together, but keep them scoped enough that a single worker can complete them in one pass
   - Example grouping: one task for all security fixes (cert bypass + dep update + CSP), another for all code quality fixes (monolith split + duplication + convention fixes)

   ```bash
   # Security fix card, gated behind security audit review
   hermes kanban create "fix: security — cert bypass, CSP, CORS, dep update" \
     --assignee coder \
     --body "$(cat /tmp/body.md)" \
     --workspace "dir:~/projects/Example" \
     --parent t_<security_review_id>
   ```

7. **Phase C — Verification tasks, gated behind fixes.** For any fix task that produces multiple changes, create a verification card assigned to `reviewer` that checks every fix point against the original findings. This creates a complete traceable chain:
   ```
   T1 (review) ──→ T2 (fix) ──→ T3 (verify)
   ```
   The verification card body should list every original finding and ask the reviewer to confirm each is resolved, reporting `clean=true` in metadata if all pass.

   ```bash
   hermes kanban create "verify: security fixes" \
     --assignee reviewer \
     --body "Check each fix from t_<fix_id>:\\n1. Cert bypass — removed/restricted?\\n2. Dep updated?\\n3. CSP enabled?\\n..." \
     --workspace "dir:~/projects/Example" \
     --parent t_<fix_id>
   ```

   The dependency engine handles promotion automatically: Phase A → done → Phase B auto-promotes to ready → dispatched → Phase B → done → Phase C auto-promotes to ready → dispatched. No manual coordination needed after the initial task graph is created.

Example body texts for Phase A review cards:

**Architecture review card:**
```
Review the project at ~/projects/<project>.
Focus: overall architecture — module system, Electron/process shell, server/client split, IPC patterns, dependency graph, module lifecycle, config system, socket communication.
Provide your findings with file paths and a structural diagram of how components connect.
This is read-only analysis — do not make changes.
```

**Code quality review card:**
```
Review the project at ~/projects/<project>.
Focus: code quality — JavaScript/Python patterns, module structure, error handling, test coverage, duplication across modules, adherence to project conventions.
Check each module for consistent patterns.
This is read-only analysis — do not make changes.
```

**Security audit card:**
```
Audit the project at ~/projects/<project>.
Focus: security — npm/pip audit of production dependencies, Electron/process security practices, input validation, IP access control, dependency vulnerabilities, attack surface.
Run: npm audit --omit=dev (or equivalent)
Check main process for secure defaults.
This is read-only analysis — do not make changes.
```

**Fan-out + fan-in (research → synthesize):** N research-style cards with no parents, one synthesis card with all of them as parents.

**Parallel research review (content survey pattern):** When the user asks you to review a large collection of content (a list of articles, a catalog of use cases, a batch of PRs, a site with many pages), use this sequence:

1. **Extract the full dataset** — scrape or collect all items into a single structured file (JSON/CSV) on disk. This is the shared source of truth all workers will read from.
2. **Split by category or slice** — partition the items into logical groups (by category tag, by page, by author, etc.). Create one kanban task per slice.
3. **Point workers at the file, not inline data** — the task body should reference the shared file path and list which slice to review. The file stays on disk and isn't lost in context truncation:
   ```bash
   hermes kanban create "Review DEV WORKFLOW stories" \
     --assignee researcher \
     --body "Read /tmp/stories.json. Review all DEV WORKFLOW stories. For each: source link, interesting? why. Rate interesting/maybe/skip." \
     --workspace scratch
   ```
4. **Fan out all slices at once** — create all tasks first, then dispatch once. The dispatcher will parallelize across available workers.
   ```bash
   hermes kanban dispatch   # repeat until no new spawns
   ```
5. **Poll and collect** — since `hermes kanban show` accepts only ONE ID at a time, poll individually:
   ```bash
   hermes kanban show t_abc123 | grep -E "^  status:"
   ```
   Check every 30-60s. Workers reading a local file typically take 60-180s per task depending on slice size.
6. **Synthesize** — once all tasks complete, read each task's `Latest summary` from `kanban show` and present a unified report organized by category with cross-cutting themes.

**Pitfall — task body too large.** Don't inline 50+ story descriptions in the task body — the worker loses context. Use a shared file on disk instead. If the content is from an external URL the worker can't access (behind auth, JS-rendered), save it locally first.

**Pitfall — scratch workspace output vanishes on completion.** Scratch workspaces are GC'd immediately when the task completes (or shortly after). If the worker writes artifacts to a scratch workspace, those files may be gone before you can read them. Recovery: workers that post their output as a **kanban comment** (visible via `hermes kanban show <id>`) survive GC. When creating brainstorm/research tasks, instruct workers to post findings as a comment in addition to (or instead of) writing files. For durable artifacts, use `--workspace dir:/path/to/persistent/dir` instead of scratch.

**Parallel implementation + validation:** one implementer card makes the change while one explorer/researcher card verifies config, docs, or source mapping. A reviewer card can depend on both. Do not make the implementer own unrelated verification just because the user mentioned both in one sentence.

**Pipeline with gates:** `planner → implementer → reviewer`. Each stage's `parents=[previous_task]`. Reviewer blocks or completes; if reviewer blocks, the operator unblocks with feedback and respawns.

**Same-profile queue:** N tasks, all assigned to the same profile, no dependencies between them. Dispatcher serializes — that profile processes them in priority order, accumulating experience in its own memory.

**Human-in-the-loop:** Any task can `kanban_block()` to wait for input. Dispatcher respawns after `/unblock`. The comment thread carries the full context.

## Large / destructive content revamps — audit-before-create gate

When the goal is a vault- or repo-wide content revamp where the user must review what stays / merges / drops before anything changes (e.g. "upgrade all docs to UE 5.8 conventions, remove what doesn't belong"), do NOT create cards from a guess. The user's standing preference is *full analysis before implementation — present the diagnosis, don't restructure until they review.* Encode it as a hard gate:

1. **Map the actual content first (read-only).** Use `execute_code` to walk the tree: per-top-level-category file counts, scan for stale-version tokens (regex `\b5\.(?:4|5|6|7)\b`), detect duplicate basenames, find `UNVERIFIED`/`TODO`/`placeholder` markers, and flag misplaced tooling folders (e.g. a `Hermes/` or `templates/` that is authoring tooling, not content). Reference recipe + runnable scan: `references/content-revamp-audit.md`.
2. **Present a concrete curation draft** — specific file paths + line numbers for every suspect item, with a per-item keep / merge / drop / relocate recommendation, a per-category stale-ref count table, and overlap/repetition clusters (tutorials covering the same subsystem). The user reviews *file-level detail*, not summaries — give them concrete material to read, then gate.
3. **Gate via `clarify` with explicit per-decision options BEFORE creating any card.** Never restructure, rename, delete, or relocate until they've signed off on the curation draft.
4. **Only after sign-off, decompose:** `T0` curation report (`knowledge`) → user approves → `T1` canonical standard (`research` deep-search + `knowledge` consolidate the conventions everyone cites) → `T2…Tn` per-category revamp (`knowledge`), each parented to `T1`.

**Pitfall — blanket version find-replace corrupts history.** "Deprecated in UE 5.5" is a *true* statement about 5.5, not a 5.8 error. A `sed` of `5.7`→`5.8` over the whole vault poisons those. Revamp is per-file judgment (read the line, decide), not mechanical replacement. The `ue_version:` frontmatter is the field to reconcile; body prose mentioning older versions may stay if historically accurate.

**Pitfall — folder rename breaks wikilinks.** A version-pinned folder like `UE5_7_Starter_Course/` must not be renamed to `UE5_8_...` wholesale — every `[[...]]` link to its notes breaks. Recommend an alias note / successor path in the curation draft instead of a filesystem rename.

**Pitfall — wrong workspace path → phantom "done" tasks (board done ≠ disk real).** If `--workspace "dir:/path"` points to a directory that does not exist (or a path the worker can't reach), workers may still *complete* with phantom/empty output — and the board will show `done`. A `done` label only means the worker process exited cleanly; it proves nothing about files. This is the single most dangerous failure because it looks legitimate.

**Verify against disk, not board labels.** After any bulk wave, run the git/disk check in `references/verify-kanban-output-on-disk.md`: `git status --short`, `git diff --stat`, `grep` for the expected annotation, `ls` the claimed file. If `git status` is empty but the board shows 20+ done, those cards are phantoms.

**Pilot-wave before scaling — catch systemic errors after 4 tasks, not 28.** A full wave against a wrong `--workspace`, wrong schema, or wrong assignee completes "cleanly" on the board but produces nothing real — and you only learn via post-hoc `git status`. Instead: after the audit gate + schema lock, fire 4 *representative* tasks first (1 tiny, 1 medium, 1 that must scan a known deprecated symbol, 1 with special handling like a move/alias). Wait for `done`, then verify on disk (git diff per category + spot-check one patched file's frontmatter). Only if those 4 produced real edits do you create + dispatch the remaining ~20. This caught a wrong-path bug (tasks ran against `~/Unreal-Engine-Obsidian` instead of `~/Documents/Unreal-Engine-Obsidian`) after 4 tasks in one session instead of after a full 28-task wave. Concrete recipe: `references/pilot-wave-verify.md`.

**Scrub phantoms before rebuilding.** Archive the whole stale wave (`hermes kanban archive t_aaa t_bbb ...`) and re-create against the *correct* `--workspace`. Don't trust `hermes kanban list` counts from a wave that ran on a wrong path — recount after scrub. Never claim a task "done" until you've verified the artifact on disk.

**Purging stale/archived cards = direct SQLite (no `delete`/`purge` CLI verb).** Archived phantom waves (wrong path, superseded) can only be removed by editing the board `.db` directly — `hermes kanban gc` only trims event/log retention, it does NOT delete tasks. Boards are **separate** DB files: `main` → `~/.hermes/kanban/boards/main/kanban.db`, `default` → `~/.hermes/kanban.db`. Schema quirk: `task_links` uses `parent_id`/`child_id` (NOT `source_id`/`target_id`) — a wrong column name aborts the whole delete and rolls back. Always back up first, scope strictly by id/signature, and `PRAGMA wal_checkpoint(TRUNCATE)` so `hermes kanban list` reflects the delete. Full recipe: `references/kanban-purge-stale-cards.md`.

Prevention: always `ls` or `stat` the workspace once before bulk-creating cards against a new project path (see also the "derived/historical paths" pitfall below).

**Pitfall — derived/historical paths may not be the live vault.** User memory or prior sessions often reference paths like `~/Documents/Unreal-Engine-Obsidian/`, but the actual live docs may live elsewhere or the path may not map onto the local machine. Before any bulk create, verify the workspace path exists AND contains the expected project signature. Mere existence (`ls <path>`) is NOT enough — a stale, empty, or alternate directory can sit at a remembered path and silently swallow a whole wave. Check for markers the user's description implies (known top-level folders, a sentinel file like `CHANGELOG.md`, or a file they named). If the signature is missing, stop and confirm the real path with the user before creating any cards. Concrete recipe + the pilot-wave pattern that catches wrong-path bugs after 4 tasks instead of 28: `references/pilot-wave-verify.md`.

**Pitfall — never fabricate completion summaries.** Only report artifacts/outputs as complete after verifying them on disk (`ls`/`grep`/`read_file`). If unsure, say so and verify first. Acceptable: "I don't have confirmation yet; checking now." Not acceptable: claiming a file/doc/task is done when only an in-context summary asserted it.

**Pitfall — competing annotation schemas poison a wave.** If a partial earlier run wrote a *different* frontmatter/annotation schema than the canonical standard you're about to enforce, every later worker that follows the standard diverges from the file(s) already written. Gate: before firing the per-category revamp wave, (1) pick ONE canonical schema (lock it in the `T1` standard doc), (2) re-align any note already written with a divergent schema to match, (3) only then create the wave. Otherwise the vault ends up with two incompatible frontmatter dialects and you rework it anyway. In one UE 5.8 revamp, three dialects existed (curation-proposal / standard-draft / one real MOC that landed) — consolidated to the canonical standard + optional `deprecated_symbols`/`migration_hint`/`historical_notes`, then re-patched the already-written MOC.

**Pitfall — workers REPLACE the whole frontmatter block instead of MERGING, silently wiping original metadata.** When a revamp task says "apply this frontmatter schema to every note," workers often overwrite the existing `---` block with the template, destroying fields the originals had (`source:` URLs, `title:`, `tags:`, `video_id:`). The board shows `done` and `git diff` is non-empty (so the naive "verify on disk" check passes) — but the original provenance is gone. In one UE 5.8 vault revamp, 28 notes ended up with `source: ""` (URL destroyed) and 30 had `title:` pushed out of the frontmatter into the body. **Verify MERGED not REPLACED:** after any bulk frontmatter wave, (a) `grep -rl 'source: ""' --include='*.md' .` should be ~0 for content notes, (b) confirm `title:` still sits inside the first `---` block, (c) count notes missing `ue_version:` only among intended targets. **Recovery:** rebuild each file's frontmatter by merging the canonical fields ON TOP of the `git HEAD` version (which still has the originals), keeping the current body. Reusable script: `scripts/frontmatter-merge-recover.py <vault-path>`. It restores original `source`/`title`/metadata and re-applies canonical fields, body untouched. Run it, then re-audit.

## Pitfalls

**Silent duplicate creation when a downstream step "fails" (CRITICAL, easy to miss).** A `hermes kanban create` invocation does its work even if the *surrounding* shell command later errors. The canonical trap: you write a one-liner that creates a task AND extracts its id (e.g. `ID=$(hermes kanban create ... --json | python3 -c "...")`). If the extraction step is blocked by the security scan (pipes to interpreters are flagged) or throws, you see an error and assume creation failed — but the task was already created. If you then re-run the create, you get a DUPLICATE. Worse: if you were chaining parents via a shell variable that never got populated (`$A1` empty because the parse failed), the duplicate is created with **no `--parent`** and the dispatcher runs it as a parallel orphan. A stray orphan release/integration task can push to git before the real chain finishes. Two non-negotiable habits: (1) NEVER pipe `hermes kanban` stdout into a Python/shell interpreter for parsing — write `--json > /tmp/x.json` and `grep` the id out; (2) ALWAYS run `hermes kanban list` after any create that "errored" to confirm whether the task exists. If you detect a phantom parallel chain with empty parents, `hermes kanban archive` the orphans immediately and reconcile (a stray release may have already pushed a tag/commit — see `references/kanban-cli-gotchas.md` and the full step-by-step reconciliation recipe in `references/kanban-orphan-release-reconciliation.md` for when the orphan already pushed a premature GitHub release/tag and swept in unrelated files). JSON key is `id`, not `task_id`.

**Workspace/body mismatch — task body referencing files not in the workspace.** Using `--workspace dir:/path/to/project` sets the worker's working directory, but the task **body** is the worker's primary instruction. If the body lists file paths that don't exist in the workspace (e.g. copying paths from a previous task's output on a different project), the worker will find an empty workspace, detect the mismatch via `kanban_show`, and block asking for clarification. This is the worker behaving correctly — the error is in the task body, not the workspace flag.

To prevent this:
- **Verify file paths before writing the task body.** If you're creating a fix task based on findings from a review task, check whether those file paths exist in the target project. Don't just copy paths from the review output.
- **When unsure, audit the project structure first** — scan the project tree for the relevant files before creating tasks that reference them.
- **If the user corrects the project path, update the task comment and unblock** rather than recreating from scratch: `hermes kanban comment <id> "Target: /the/correct/path"` then `hermes kanban unblock <id>`.
- **The `--workspace` flag alone is not enough.** The body must be grounded in paths that actually exist at that workspace.

**Inventing profile names that don't exist.** The dispatcher silently fails to spawn unknown assignees — the card just sits in `ready` forever. Always assign to a profile from your Step 0 discovery; ask the user if you're unsure.

**Bundling independent lanes into one card.** If the user asks for two independent outcomes, create two cards. Example: "fix blockers and check model variants" is not one fixer task; create a fixer/engineer card for the fixes and an explorer/researcher card for the variant check, then optionally gate review on both.

**Over-linking because of wording.** "Finally check X" may still be parallel with implementation if X is static config, docs, or source discovery. Link it after implementation only when the check depends on the implementation result.

**Forgetting dependency links.** If the task graph says `research -> implement -> review`, do not create all tasks as independent ready cards. Use parent links so implement/review cannot run before their inputs exist.

**Tasks without a body will block asking for context.** If a task is created with an empty or null body (`kanban_create(body="")` or no `body` kwarg), the worker connects, authenticates, and then immediately calls `kanban_block("No codebase or project to review — workspace is empty and task body is null")`. This is the worker behaving *correctly* — it has no input to act on. The distinction from a protocol_violation is the `blocked {'reason': '...'}` event in the task log vs a clean exit. To prevent this: always include at minimum a repo path, file list, or project description in the task `body`. For code-review cards, use the Phased Codebase Review pattern's example body text (which includes `Read all source files in /path/to/project/`).

If you inherit blocked tasks with empty bodies, add context via `hermes kanban comment <id> "point me at /path/to/project"` and then `hermes kanban unblock <id>` (or use `kanban_comment` followed by `kanban_unblock` from within a session). The worker will pick up the comment thread on respawn.

Reassignment vs. new task. If a reviewer blocks with "needs changes," create a NEW task linked from the reviewer's task — not a re-run. The new task is assigned to the original implementer profile.

**Worker testing launches GUI apps (Electron, desktop).** When a fix task is dispatched to projects that have an Electron/desktop GUI (smart mirrors, desktop apps, game engines), the worker may run `npm start` or equivalent to test its changes. This can launch a full-screen GUI on the user's machine unexpectedly.

Prevent this by adding explicit testing instructions in the task body:

```markdown
**Test your changes with headless commands only:**
- Use `npm run server` for HTTP/API testing (no GUI)
- Use `npm test` for test suite verification
- Use `npm run lint:js` for lint checks
- NEVER use `npm start` — it launches the Electron desktop app full-screen
```

For projects where this is a recurring risk, add a `### DO NOT launch GUI` section to the project's `AGENTS.md` file. List the specific headless testing commands that workers should use instead of the GUI launch command. Reference this AGENTS.md convention in every task body for that project.

If a worker launches the GUI anyway, reclaim the task immediately and check `git status` — the worker's code changes are still in the working tree. Complete the fix manually or re-dispatch with explicit testing instructions in the body.

**Worker appears dead but is still running.** Kanban workers are subprocesses spawned by the dispatcher. They do NOT appear in `ps aux` from a parent agent's terminal sandbox because the sandbox has a separate process namespace. A task showing `status: running` with a non-expired claim lock is actively working — do not reclaim it.

The reliable indicators of a live worker:
- `hermes kanban show <id> | grep "status:"` → `running` (not `blocked`)
- `hermes kanban show <id> | grep "Runs"` → run count has not changed to a new number
- The claim timestamp in `spawned` events has not expired (usually 15-min TTL)

A legitimate crash produces `blocked` status with `protocol_violation` in the event log — not `running` state lingering with a dead process. Workers reading a local codebase of 50-250 files typically take 2-6 minutes. Poll every 30-45s with `hermes kanban show <id> | grep -E "^  status:"` and look for the status transition. Do NOT reclaim until the status changes to something other than `running`.

**Recovery reference:** See `references/gateway-stopped-recovery-pattern.md` for a validated recovery walkthrough when multiple profiles show `Gateway: stopped` and crash with `nonzero_exit(1)`.

**CLI body too large for inline --body.** When a task body is long (1,500+ chars), has bullet lists with markdown formatting, or contains characters the shell interprets (arrows, ampersands, backticks, nested quotes, **parentheses and hash signs** — e.g. hex colors like `#1A1A2E` inside double-quoted `--body "$(...)"`), the CLI may reject it. Common error messages:
- `"Foreground command uses '&' backgrounding"` — even when no ampersand is present
- `"unrecognized arguments: match"` followed by `"syntax error near unexpected token '(' "` — caused by parentheses inside the body string being parsed by the shell before reaching hermes

The fix in both cases is the same: write the body to a temp file and inject it:

```bash
# Write body to a temp file
cat > /tmp/task-body.md << 'BODYEOF'
Fix the critical findings from the review:
1. Certificate bypass in electron.js - remove blanket accept handler
2. systeminformation package to latest - npm install
3. CSP headers disabled in server.js - enable with restrictive policy

Workspace: ~/projects/Example
Parent review: t_abc123
BODYEOF

# Create task with file-injected body
hermes kanban create "fix: security issues" \
  --assignee coder \
  --body "$(cat /tmp/task-body.md)" \
  --workspace "dir:~/projects/Example" \
  --parent t_abc123
```

Clean up the temp file afterward (`rm /tmp/task-body.md`). This pattern also makes the body text reusable if you need similar tasks for other projects with minor edits.
</artifacts>

## Alternative tools

See `references/goban-comparison.md` for a structured comparison with Goban. See `references/visual-consistency-audit.md` for the visual consistency audit pattern (creative spec → code fix chain for rendered video inconsistencies).

**Argument order for links.** `kanban_link(parent_id=..., child_id=...)` — parent first. Mixing them up demotes the wrong task to `todo`.

**`hermes kanban dispatch` takes NO task-id — it spawns all `ready` tasks on the active board.** `dispatch t_abc123` errors with `unrecognized arguments`. To run specific tasks, get them to `ready` first (next pitfall), then `dispatch` (no args) and read `Spawned: N`. Multiple boards exist — `dispatch` only touches the active board (`hermes kanban boards list` / `switch`). To inspect queued tasks, `hermes kanban list` is the read path; `dispatch` is the spawn path, separate verbs.

**New children sit in `todo`, not `ready` — gated by parent `done` (and `dispatch` SKIPS `todo`).** After `kanban_create --parent t_X`, the child is `todo` and `dispatch` will NOT spawn it. The dependency engine auto-promotes `todo → ready` only when **every** parent reaches `done`. If a child won't spawn, check the parent status — you may need `hermes kanban complete <parent>` first (the parent's work is finished; completing it is what releases the gate), then `dispatch` again (expect `Promoted: N`). This bit in a session where 3 EXEC children were stuck in `todo` because review parents were left `running`/`blocked`; completing the parents unblocked them. Do NOT `promote` a `todo` child manually unless `--force` past an unsatisfied parent — that defeats the gate.

**Worker "findings" are self-reports, not ground truth — re-verify before relaying or acting.** A review/analysis task may post a confident claim that is simply wrong. This session: a knowledge worker claimed `UE5_GAS/` notes were a *duplicate* of `Architecture/GASDocumentation.md` (false — the latter is a 1.1K external pointer to the tranek/GASDocumentation bible; the former are applied tutorials, complementary not redundant), and claimed the vault had *zero packaging notes* (false — 2 existed, both 5.7). Both caught only because the orchestrator checked the actual files, not the worker prose. **Rule:** when a worker reports a factual content claim (counts, duplicates, "doesn't exist", "is deprecated"), verify it against disk/git before (a) relaying it to the user as fact, or (b) spawning follow-up tasks on it. If the worker was wrong, `hermes kanban comment` the correction onto the task so the board doesn't carry the error.

**Scope drift — workers perform unrequested edits beyond the approved body.** A worker's content claims can be *correct* while its edits still exceed authorization. This session: a `knowledge` worker was told to fold a 9-note RPG series + add 4 specific cross-links; it did all that AND edited 3 `Architecture/` notes with reciprocal links it was never told to touch. The board said `done` and `git diff` was non-empty (so the naive "verify on disk" check passed) — but the **changed file set exceeded approval**. **Rule:** after any worker that edits files completes, run `git diff --cached --name-only` (or `git status --short`) and diff the *actual* file set against the task body's approved scope. Anything outside the body is drift. **Keep the work UNCOMMITTED** (working tree only) so the user can review the diff before you commit. When drift is found, surface it explicitly ("3 edits beyond your approval — X, Y, Z") rather than silently committing or reverting; let the user pick commit-all vs commit-approved-only. Board `done` + non-empty `git diff` only proves the worker ran — it does NOT prove the change matches scope.

**Pre-push remote divergence — never force a non-fast-forward.** After committing worker output locally, `git push` can be rejected with `! [rejected] main -> main (fetch first)` if the remote advanced while you worked (CI, another machine, or an earlier session's hackathon push). This session: local was 10 commits behind `origin/main`, which had already shipped a structural v1.5.0 upgrade that *deleted* folders our commit was reorganizing — a `git merge` attempt produced 78 conflicts. **Rule:** before pushing, `git fetch origin` and check `git log HEAD..origin/main` for divergence; if the remote moved, inspect WHAT changed (`git ls-tree -r --name-only origin/main | grep <area>`) *before* merging — a structural upstream change can make your local commit obsolete or already-superseded. Attempt a non-destructive `git merge --no-commit --no-ff origin/main`, inspect conflicts, then either resolve or `git merge --abort` and surface the divergence to the user (characterize it: "remote deleted the folder you were editing"). **NEVER `git push --force`** to clear the rejection — that rewrites shared history and can clobber the upstream work. If the local commit is built on a stale base, the disciplined move is usually to rebase/rederive the change onto the new upstream (or discard + re-apply), not fight the merge.

**Don't pre-create the whole graph if the shape depends on intermediate findings.** If T3's structure depends on what T1 and T2 find, let T3 exist as a "synthesize findings" task whose own first step is to read parent handoffs and plan the rest. Orchestrators can spawn orchestrators.

**Tenant inheritance.** If `HERMES_TENANT` is set in your env, pass `tenant=os.environ.get("HERMES_TENANT")` on every `kanban_create` call so child tasks stay in the same namespace.

## Common failure: protocol_violation

Protocol violation is the catch-all crash mode when a spawned worker exits with `rc=0` without calling `kanban_complete` or `kanban_block`. The dispatcher marks the task `blocked`. Most instances fall into one of three root cause classes — diagnose before recovering.

**Symptoms (same for all subclasses):**
- `hermes kanban show <task_id>` shows: `worker exited cleanly (rc=0) without calling kanban_complete or kanban_block — protocol violation`
- No active worker processes (`ps aux | grep kanban` returns nothing)
- `hermes kanban dispatch` reports `Spawned: 0`

**Diagnostic checklist — narrow the cause:**

| Check | Command | Tells you |
|---|---|---|
| Profile model config | `grep -A3 'model:' ~/.hermes/profiles/<assignee>/config.yaml` | Is the provider+model combo valid? |
| Profile gateway status | `hermes profile list \\| grep <assignee>` | Shows `Gateway: running` or `stopped`. **Check which crash pattern you're seeing:** |
| Provider credentials exist | `grep -l <PROVIDER>_API_KEY ~/.hermes/.env ~/.hermes/profiles/<assignee>/.env 2>/dev/null` | Is the API key set for the profile's provider? |
| Profile auth.json exists | `ls ~/.hermes/profiles/<assignee>/auth.json 2>/dev/null || echo "no auth.json"` | For OAuth-based providers (Nous, Copilot), worker needs per-profile auth.json |
| All profiles' credentials | `for p in ~/.hermes/profiles/*/; do echo "=== $p ==="; grep -n '^model:' "$p/config.yaml" 2>/dev/null; done` | Quick audit of the whole team's provider setup |
| Recently changed config? | `ls -lt ~/.hermes/profiles/<assignee>/config.yaml ~/.hermes/.env` | Was something modified since these tasks were created? |

### Crash patterns after the diagnostic table

After running the diagnostic checklist, match the crash pattern to narrow root cause:

| Crash signature | Event log shows | Root cause | Recovery |
|---|---|---|---|
| **"pid NNNN not alive"** | All runs: `crashed {pid: N, error: "pid N not alive"}` at consistent durations (~17-200s) | Profile's gateway is `stopped` (launchd OnDemand). Workers spawn but the gateway process isn't running to receive them. **Contrary to the old note — this IS the cause.** | `hermes -p <assignee> gateway status` → if stopped, run `hermes -p <assignee> gateway start`. Then unblock + dispatch. |
| **"pid NNNN not alive" with gateway RUNNING** | All runs: `crashed {pid: N, error: "pid N not alive"}` but `hermes -p <assignee> gateway status` shows active PIDs and launchd supervision | **Systemic spawn failure** — not a gateway issue. Multiple profiles crash identically despite gateways showing healthy. Likely environmental: venv mismatch, Python path, shared workspace contention, or provider auth the worker can't resolve. Unblock+dispatch will just crash again. | **Do NOT loop.** Execute the tasks directly from the orchestrator. `hermes kanban complete <id> --summary "..."` to close the kanban task, then do the work yourself. See escape hatch below. |
| **"protocol_violation"** | `worker exited cleanly (rc=0) without calling kanban_complete or kanban_block` | Provider/credential mismatch, config change mid-sprint, or missing skill reference. Profile starts, can't init LLM, exits silently. | See Subclass A/B/C above. |
| **"nonzero_exit(1)"** | `worker exited with code 1` | Runtime error inside worker code (file not found, import error, tool failure). | Read the task log (`hermes kanban log <id>`) for the actual error. |

**Critical distinction:** "pid not alive" and "protocol_violation" have different root causes and different fixes. Do not conflate them.

### Serial dispatch workaround for gateway crashes

When multiple same-profile tasks crash with "pid not alive" and restarting the gateway doesn't fix the batch dispatch, workers may be dying from spawn contention. Workaround:

```bash
# Instead of unblocking all then dispatching once:
hermes kanban unblock t_abc123
hermes kanban dispatch
# Wait for completion or confirmed crash
hermes kanban show t_abc123 | grep -E "^  status:"

hermes kanban unblock t_def456
hermes kanban dispatch
# Repeat per task
```

This avoids the dispatcher claiming multiple workers simultaneously against a gateway that's warming up.

### Worker output survives "pid not alive" crashes

When a worker crashes with "pid not alive" after running 60-200s, its code changes may still be in the working tree. The worker wrote files before the handoff failed. Before re-dispatching or abandoning:

```bash
cd /path/to/workspace
git status              # check for uncommitted worker output
git diff --stat         # see what was changed
```

If code was written, commit it (`git add -A && git commit -m "feat: ..."`), mark the task complete manually with `hermes kanban complete <id> --summary "..."`, and skip the re-dispatch. Only re-dispatch if the output is incomplete.

**Root cause:** The profile's config specifies a `provider` whose API key is not set anywhere — not in the root `~/.hermes/.env`, not in the profile's `.env`. The worker starts, attempts to initialize the LLM provider, can't authenticate, and exits cleanly before reaching any kanban lifecycle code. Every spawned worker fails identically.

**Signs:**
- All tasks assigned to profiles using the same provider fail identically in the same minute.
- The profile's `provider:` field (e.g. `nous`) doesn't match any key in `~/.hermes/.env`.
- `grep 'provider:' ~/.hermes/profiles/<assignee>/config.yaml` shows a provider name but `grep -l $(echo <PROVIDER>_API_KEY | tr 'a-z' 'A-Z') ~/.hermes/.env` returns nothing.

**Example** (this session):
```
architect: provider: nous, base_url: https://inference-api.nousresearch.com/v1
→ NOUS_API_KEY not set in ~/.hermes/.env or any profile .env
→ 5 workers, all crashed with protocol_violation at the same timestamp
```

**Recovery path (choose one):**

**For API-key-based providers** (OpenRouter, DeepSeek, Anthropic, etc.):
1. **Switch the profile to a working provider** (one whose key IS set). Edit `~/.hermes/profiles/<assignee>/config.yaml`:
   - Change `model.provider` from the broken provider to e.g. `openrouter` (or whatever provider has credentials).
   - Remove `model.base_url` unless the new provider requires a custom one.
2. **Add the missing key** to root `~/.hermes/.env`: `PROVIDER_API_KEY=<your_key>`.
3. **Unblock + dispatch** — blocked tasks are NOT running, so `reclaim` won't work (`cannot reclaim <id> (not running or unknown id)`). Use `unblock` instead:
   ```
   hermes kanban unblock t_db2d0522 t_1773e74a t_04a4bf36   # one or many IDs
   hermes kanban dispatch
   ```

**For OAuth-based providers** (Nous Portal, OpenAI Codex, etc.):
The credential pool is **per-profile**. OAuth tokens obtained via `hermes login --provider <name>` are stored in the **current profile's** `auth.json` only. Team profiles (architect, coder, etc.) have their own separate credential pools that start empty. Diagnostics:
```
for p in architect coder debugger reviewer; do
  echo "=== $p ===" && ls ~/.hermes/profiles/$p/auth.json 2>/dev/null || echo "  no auth.json"
done
```
If team profiles lack `auth.json` entirely (only an empty `auth.lock` exists), that profile has no credential pool.

1. **Replicate the OAuth token** to each profile that needs it:

   ```bash
   # Option A: Copy auth.json from the profile that has the token
   cp ~/.hermes/profiles/<source-profile>/auth.json \
      ~/.hermes/profiles/<target-profile>/
   ```
   ```bash
   # Option B: Run OAuth login per profile (requires device-code flow each time)
   # Note: `hermes login` was removed — use `hermes auth add` instead
   hermes -p architect auth add nous --type oauth
   hermes -p coder auth add nous --type oauth
   ```
   ```bash
   # Option C (preferred by many users): symlink auth.json to root so all profiles share one canonical source
   # Mirrors the plugins-symlink pattern — single source of truth, auto-syncs.
   cp ~/.hermes/profiles/<source>/auth.json ~/.hermes/auth.json
   mv ~/.hermes/profiles/<source>/auth.json ~/.hermes/profiles/<source>/auth.json.bak
   ln -s ~/.hermes/auth.json ~/.hermes/profiles/<source>/auth.json
   for p in architect coder debugger reviewer; do
     ln -s ~/.hermes/auth.json ~/.hermes/profiles/$p/auth.json
   done
   # Verify: each profile now has a symlink to the same canonical file
   for p in architect coder debugger reviewer senna; do
     readlink ~/.hermes/profiles/$p/auth.json
   done
   ```

2. **Unblock + dispatch** all affected tasks:
   ```
   hermes kanban unblock t_db2d0522 t_1773e74a t_04a4bf36   # one or many IDs
   hermes kanban dispatch
   ```

**Key command distinction: reclaim vs unblock.**
- `hermes kanban reclaim <task_id>` — use when a task is **running** (has an active worker claim). Aborts the worker and resets to `ready`.
- `hermes kanban unblock <task_id>` — use when a task is **blocked** (worker already exited/crashed). Moves it back to `ready`.
- `hermes kanban reclaim` says `cannot reclaim <id> (not running or unknown id)` on blocked tasks — don't confuse the two. Check status first with `hermes kanban list` or `hermes kanban show <id>`.

**Verification:** After the fix, check that the profile's credential pool has the provider:
```bash
hermes -p <profile> auth list <provider>   # should show the credential
# Or for a quick check across all profiles:
for p in architect coder debugger reviewer; do
  echo "=== $p ===" && ls ~/.hermes/profiles/$p/auth.json 2>/dev/null || echo "  no auth.json"
done
```

### Subclass B: Config changes made mid-sprint

**Root cause:** A profile's model or config was modified while Kanban tasks were already queued or in-flight. Workers spawned after the change may:
- Start with a cached/stale config that no longer matches the running system, or
- Receive a config update mid-initialization that causes the agent loop to terminate before reaching any kanban lifecycle tool.

**Signs:**
- Timestamps of `hermes profile list` model column (or modtime on `config.yaml`) are more recent than task creation times.
- Only one or two tasks fail, not the whole board.

**Recovery path:**

1. **Check task state first** — `hermes kanban list` or `hermes kanban show <task_id>` tells you if tasks are `running` (have an active worker claim) or `blocked` (already gave up / crashed).
   - If **running**: use `hermes kanban reclaim <task_id>` to abort the worker and reset to `ready`.
   - If **blocked** (already hit `gave_up`, `cannot reclaim <id> (not running or unknown id)`): use `hermes kanban unblock <task_id>` instead.
2. **Verify** the profile's config is correct: `grep 'default:' ~/.hermes/profiles/<assignee>/config.yaml`
3. **Dispatch** again: `hermes kanban dispatch`

**Prevention:** Make all profile model/config changes *before* creating Kanban tasks, not after. If a change is needed mid-sprint, reclaim all in-flight tasks first, update configs, then recreate.

**Key command distinction:** `hermes kanban reclaim` only works on `running` tasks (those with an active worker claim). `hermes kanban unblock` works on `blocked` tasks. Use `hermes kanban list` to see the current state before picking a recovery command. If reclaim returns `cannot reclaim <id> (not running or unknown id)`, switch to unblock instead — do not retry reclaim.

### Subclass C: Missing skill or misconfigured toolset

**Root cause:** The profile references a toolset, skill, or plugin that doesn't exist, is misspelled, or has unmet dependencies (e.g. a binary the toolset expects isn't on PATH).

**Signs:**
- `hermes kanban show` has tool/spawn errors in the event log beyond the protocol_violation line.
- `hermes doctor` or `hermes -p <assignee> status` reports missing tools/plugins.
- Worker log (`hermes kanban log <id>`) shows `Error: Unknown skill(s): kanban-worker` at startup. **This error is non-fatal** — the kanban-worker skill is built into the dispatcher, not a separately installable skill. `hermes skills install kanban-worker --profile <name>` will fail with "No skill named 'kanban-worker' found." The worker runs fine without it.

**Recovery:** Fix the toolset/skill/plugin reference in the profile's `config.yaml`, then reclaim + dispatch.

## Fleet-Wide Worker Crash Fallback

When **3+ workers across different profiles crash identically** ("pid not alive" despite running gateways), continuing to reclaim/unblock/redispatch is a loop. The underlying cause is often spawn contention, resource exhaustion, or a silent gateway restart loop — not an individual task issue.

### Decision threshold
If dispatch spawns 0 new workers OR all spawned workers crash within 60 seconds, **stop dispatching and switch to direct execution:**

1. **Complete the highest-priority task yourself** (orchestrator directly, or `delegate_task` for reasoning-heavy work). The orchestrator CAN handle implementation tasks directly when the Kanban fleet is down — this is the explicit override to the "don't do the work yourself" rule.
2. **Mark crashed tasks complete** with a summary of what you did: `hermes kanban complete <id> --summary "Handled directly — fleet unavailable."`
3. **Do NOT** create a task for "fix the fleet" during a hackathon/tight deadline — that's a separate session's problem.
4. **After the session**, investigate: check `launchctl list | grep hermes` for exit codes, `ps aux | grep gateway` for actual running vs reported, and profile model configs.

### Anti-pattern
```
Worker crashes → unblock → dispatch → crashes → unblock → dispatch → crashes
```
This burns time and produces no output. Stop after 2 attempts per profile.

## Recovering stuck workers

When a worker profile keeps crashing, hallucinating, or getting blocked by its own mistakes (usually: wrong model, missing skill, broken credential), the kanban dashboard flags the task with a ⚠ badge and opens a **Recovery** section in the drawer. Three primary actions:

1. **Reclaim** (or `hermes kanban reclaim <task_id>`) — abort the running worker immediately and reset the task to `ready`. The existing claim TTL is ~15 min; this is the fast path out.
2. **Reassign** (or `hermes kanban reassign <task_id> <new-profile> --reclaim`) — switch the task to a different profile (one that exists on this setup) and let the dispatcher pick it up with a fresh worker.
3. **Change profile model** — the dashboard prints a copy-paste hint for `hermes -p <profile> model` since profile config lives on disk; edit it in a terminal, then Reclaim to retry with the new model.

Hallucination warnings appear on tasks where a worker's `kanban_complete(created_cards=[...])` claim included card ids that don't exist or weren't created by the worker's profile (the gate blocks the completion), or where the free-form summary references `t_<hex>` ids that don't resolve (advisory prose scan, non-blocking). Both produce audit events that persist even after recovery actions — the trail stays for debugging.

## Post-unblock follow-through (review-required lifecycle)

When you unblock `review-required` tasks, the work isn't done at dispatch — you need to see them through to completion. Missing this step leaves child tasks stranded in `todo`.

Follow this checklist after every batch unblock:

1. **Unblock** → `hermes kanban unblock <id_1> <id_2> ...` (accepts multiple IDs)
2. **Dispatch** → `hermes kanban dispatch` — verify `Spawned: N` matches the number of tasks you unblocked
3. **Poll for completion** — `hermes kanban show` accepts only ONE ID, so check individually:
   ```bash
   hermes kanban show t_abc123 | grep -E "^  status:"
   ```
   Workers typically take 30s–3min for review-required tasks (they read the prior run's output, confirm, and complete). Poll every 15-30s rather than flooring timers.
4. **Check for auto-promoted child tasks** — when a parent task completes, the dependency engine promotes children from `todo` → `ready` automatically. Run `hermes kanban dispatch` again — it will report `Promoted: N` and `Spawned: M` for any newly-ready children.
5. **Repeat monitoring** for any spawned children until all tasks in the dependency chain resolve.

---

## Worker Playbook

This section covers the worker perspective — pitfalls, examples, and edge cases for Hermes Kanban workers.

### Workspace Handling

Your workspace kind determines how you should behave inside `$HERMES_KANBAN_WORKSPACE`:

| Kind | What it is | How to work |
|---|---|---|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely; it gets GC'd when the task is archived. |
| `dir:<path>` | Shared persistent directory | Other runs will read what you write. Treat it like long-lived state. |
| `worktree` | Git worktree at the resolved path | If `.git` doesn't exist, run `git worktree add <path> <branch>` from the main repo first. |

### Good Summary + Metadata Shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "decisions": ["user_id primary, IP fallback for unauthenticated requests"],
    },
)
```

**Coding task that needs human review (review-required):**
```python
kanban_comment(
    body="review-required handoff:\n" + json.dumps({
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "diff_path": "/path/to/worktree",
        "decisions": ["user_id primary, IP fallback for unauthenticated requests"],
    }, indent=2),
)
kanban_block(
    reason="review-required: rate limiter shipped, 14/14 tests pass — needs eyes on the user_id/IP fallback choice before merging",
)
```

**Research task:**
```python
kanban_complete(
    summary="3 competing libraries reviewed; vLLM wins on throughput, SGLang on latency, Tensorrt-LLM on memory efficiency",
    metadata={
        "sources_read": 12,
        "recommendation": "vLLM",
        "benchmarks": {"vllm": 1.0, "sglang": 0.87, "trtllm": 0.72},
    },
)
```

### Claiming Cards You Actually Created

If your run produced new kanban tasks (via `kanban_create`), pass the ids in `created_cards` on `kanban_complete`. The kernel verifies each id exists and was created by your profile; any phantom id blocks the completion with an error.

```python
# GOOD — capture return values, then claim them.
c1 = kanban_create(title="remediate SQL injection", assignee="security-worker")
c2 = kanban_create(title="fix CSRF middleware", assignee="web-worker")

kanban_complete(
    summary="Review done; spawned remediations for both findings.",
    metadata={"pr_number": 123, "approved": False},
    created_cards=[c1["task_id"], c2["task_id"]],
)
```

### Block Reasons That Get Answered Fast

Bad: `"stuck"` — the human has no context.

Good: one sentence naming the specific decision you need.

```python
kanban_comment(
    task_id=os.environ["HERMES_KANBAN_TASK"],
    body="Full context: I have user IPs from Cloudflare headers but some users are behind NATs.",
)
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth, skips anonymous endpoints)?")
```

### Heartbeats Worth Sending

Good heartbeats name progress: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`.

Bad heartbeats: `"still working"`, empty notes, sub-second intervals.

### Retry Scenarios

If you open the task and `kanban_show` returns `runs: [...]` with one or more closed runs, you're a retry. The prior runs' `outcome` / `summary` / `error` tell you what didn't work. Don't repeat that path.

- `outcome: "timed_out"` — the previous attempt hit `max_runtime_seconds`. Chunk the work or shorten it.
- `outcome: "crashed"` — OOM, segfault, or provider/auth failure. Read the exit_kind and exit_code.
- `outcome: "spawn_failed"` — usually a profile config issue. Ask the human via `kanban_block`.

### Worker Pitfalls

1. **Task state can change between dispatch and your startup.** Always `kanban_show` first.
2. **Workers are invisible to `ps aux` from the parent session.** A task showing `status: running` with a non-expired claim is actively working.
3. **Workspace may have stale artifacts.** Read the comment thread.
4. **Don't use `delegate_task` as a substitute for `kanban_create`.** Workers should never spawn subagents.
5. **Don't modify files outside `$HERMES_KANBAN_WORKSPACE`** unless the task body says to.
6. **Don't complete a task you didn't actually finish.** Block it instead.

---

## Codex Lane Pattern

Use when a Hermes Kanban worker wants to run Codex CLI as an isolated implementation lane.

### When to Use

Use the Codex lane when all of these are true:
- The task is a coding, refactor, documentation, test, or mechanical migration task with clear acceptance criteria.
- A bounded diff can be evaluated by Hermes in one run.
- The repo can be copied or checked out in an isolated git worktree/branch.
- Hermes can run the relevant tests itself after Codex exits.

### Ownership Rules

1. Hermes owns the Kanban lifecycle. Codex must never call `kanban_complete`, `kanban_block`, `kanban_create`.
2. Hermes owns final acceptance. Treat Codex commits/diffs as untrusted patches until reviewed and verified.
3. Hermes owns test execution. Codex may run tests, but those runs are advisory.
4. Hermes owns safety. If Codex changes safety boundaries, reject the lane even if tests pass.
5. Hermes owns cleanup. Kill stuck Codex processes and remove temporary worktrees.

### Required Worktree Pattern

Never run Codex directly in a shared dirty checkout.

```bash
TASK_ID="${HERMES_KANBAN_TASK:-t_manual}"
REPO="/path/to/repo"
BASE="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
SAFE_TASK="$(printf '%s' "$TASK_ID" | tr -cd '[:alnum:]_-')"
BRANCH="codex/${SAFE_TASK}/$(date -u +%Y%m%d%H%M%S)"
WORKTREE="/tmp/${SAFE_TASK}-codex-lane"

git -C "$REPO" fetch --all --prune
git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "$BASE"
```

### Prompt Construction

Every Codex prompt must include:
- `task_id`, title, and full Kanban acceptance criteria.
- Repo path, worktree path, branch name, and allowed file scope.
- Explicit statement: Hermes owns Kanban lifecycle; Codex is an input lane only.
- Required output: concise summary, files changed, commits, tests run, and known risks.
- Prohibited actions: secrets access, external messaging, board mutation, unrelated refactors.

### Reconciliation Checklist

Hermes must perform this checklist before accepting any Codex lane result:

- [ ] `git -C <WORKTREE> status --short --branch` shows only expected files.
- [ ] `git -C <WORKTREE> diff --stat` and `git diff` were reviewed by Hermes.
- [ ] No secrets, credentials, generated caches, unrelated data, or local artifacts are included.
- [ ] Codex commits are small enough to cherry-pick or squash cleanly.
- [ ] Hermes ran the canonical tests itself.
- [ ] Accepted commits/diffs were applied to the Hermes-owned workspace/branch.

Acceptance outcomes:
- `accepted`: Codex diff/commits were reviewed, applied, and verified.
- `partial`: Some Codex work was accepted after edits or cherry-picks.
- `rejected`: No Codex changes were accepted; reason is documented.
- `timed_out`: Codex exceeded the lane budget.

**Status reporting format.** When reporting board state to the user, group tasks by workstream and show the full lifecycle table with status icons:

```
## 🪐 Workstream: hermes-solar-system

| Task | Assignee | Status |
|---|---|---|
| **T1** — Architecture review | architect | ✅ Done |
| **T2** — Fix keyboard shortcuts | coder | 🗄️ Archived |
| **Refactor ui.js** | coder | ⛔ Blocked |
| Verify refactor | reviewer | ⏳ Todo |

Completed: checkmark (✅). Blocked: stop-sign (⛔). Running: spinner (⟳). Todo: hourglass (⏳). Archived: archive-box (🗄️). Done: checkmark.
```

Start with a quick status-line summary (e.g. "7 done, 3 archived, 2 blocked, 1 todo") above the tables so the user gets the shape immediately.

**Handling review-required tasks that block again.** A worker that uses `kanban_block(reason="review-required: ...")` will, on respawn after unblock, call `kanban_complete` (not `kanban_block` again) — the review-required block is a one-shot handoff. If it blocks again with review-required, it means the worker re-ran its work from scratch and is asking for a second review cycle. This is unusual — inspect the run log (`hermes kanban show <id>`) to understand why.
