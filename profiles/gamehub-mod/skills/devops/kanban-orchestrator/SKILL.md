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

## The anti-temptation rules

Your job description says "route, don't execute." The rules that enforce that:

- **Do not execute the work yourself.** Your restricted toolset usually doesn't even include terminal/file/code/web for implementation. If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **Split multi-lane requests before creating cards.** A user prompt can contain several independent workstreams. Extract those lanes first, then create one card per lane instead of bundling unrelated work into a single implementer card.
- **Run independent lanes in parallel.** If two cards do not need each other's output, leave them unlinked so the dispatcher can fan them out. Link only true data dependencies.
- **If no specialist fits the available profiles, ask the user which profile to create or which existing profile to use.** Do not invent profile names; the dispatcher will silently drop unknown assignees.
- **Decompose, route, and summarize — that's the whole job.**

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

Examples of prompts that should fan out (using placeholder profile names — substitute whatever exists on the user's setup):

- "Build an app" → one card to a design-oriented profile for product/UI direction, one or two cards to engineering profiles for implementation, plus a later integration/review card if the user has a reviewer profile.
- "Fix blockers and check model variants" → one implementation card for the blocker fixes plus one discovery/research card for config/source verification. A final reviewer card can depend on both.
- "Research docs and implement" → a docs-research card can run in parallel with a codebase-discovery card; implementation waits only if it truly needs those findings.
- "Analyze this screenshot and find the related code" → one card to a vision-capable profile for the visual analysis while another searches the codebase.

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

**Pitfall: task body too large.** Don't inline 50+ story descriptions in the task body — the worker loses context. Use a shared file on disk instead. If the content is from an external URL the worker can't access (behind auth, JS-rendered), save it locally first.

**Parallel implementation + validation:** one implementer card makes the change while one explorer/researcher card verifies config, docs, or source mapping. A reviewer card can depend on both. Do not make the implementer own unrelated verification just because the user mentioned both in one sentence.

**Pipeline with gates:** `planner → implementer → reviewer`. Each stage's `parents=[previous_task]`. Reviewer blocks or completes; if reviewer blocks, the operator unblocks with feedback and respawns.

**Same-profile queue:** N tasks, all assigned to the same profile, no dependencies between them. Dispatcher serializes — that profile processes them in priority order, accumulating experience in its own memory.

**Human-in-the-loop:** Any task can `kanban_block()` to wait for input. Dispatcher respawns after `/unblock`. The comment thread carries the full context.

## Pitfalls

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

**CLI body too large for inline --body.** When a task body is long (1,500+ chars), has bullet lists with markdown formatting, or contains characters the shell interprets (arrows, ampersands, backticks, nested quotes), the CLI may reject it. The error message says "Foreground command uses '&' backgrounding" even when no ampersand is present. The fix is to write the body to a temp file and inject it:

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

See `references/goban-comparison.md` for a structured comparison with Goban, a standalone Go-based Kanban server with a web UI and human+AI RBAC. It occupies a different point in the design space (collaboration surface vs orchestration engine) and is not a supplement to Hermes Kanban for this user's setup.

**Argument order for links.** `kanban_link(parent_id=..., child_id=...)` — parent first. Mixing them up demotes the wrong task to `todo`.

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
| Provider credentials exist | `grep -l <PROVIDER>_API_KEY ~/.hermes/.env ~/.hermes/profiles/<assignee>/.env 2>/dev/null` | Is the API key set for the profile's provider? |
| Profile auth.json exists | `ls ~/.hermes/profiles/<assignee>/auth.json 2>/dev/null || echo "no auth.json"` | For OAuth-based providers (Nous, Copilot), worker needs per-profile auth.json |
| All profiles' credentials | `for p in ~/.hermes/profiles/*/; do echo "=== $p ==="; grep -n '^model:' "$p/config.yaml" 2>/dev/null; done` | Quick audit of the whole team's provider setup |
| Recently changed config? | `ls -lt ~/.hermes/profiles/<assignee>/config.yaml ~/.hermes/.env` | Was something modified since these tasks were created? |

### Subclass A: Provider / credential mismatch

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

**Recovery:** Fix the toolset/skill/plugin reference in the profile's `config.yaml`, then reclaim + dispatch.

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
