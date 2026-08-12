# Orchestrator fan-out protocol (book-pipeline)

User-corrected workflow. Encode so the next session does not re-learn it.

## Default mode
When scope spans craft + models + tooling + market + publish:
1. **Present a short plan** (lanes + deliverables + what is NOT being built yet).
2. **Wait for go-ahead** if the user is in deliberate-planner mode ("don't restructure until user reviews").
3. **Dispatch specialists** via `delegate_task` / profiles — **do not solo the domain work**.
4. **Hold the report** until all lanes return, then **one synthesis** — not five partial dumps.
   User phrase: *"after get all back then report to me"*.

## Dispatch hygiene
- Max concurrent children is limited (often 3). Batch 3 + N if needed.
- Each task prompt must be self-contained: paths, constraints, deliverable format, "no fiction" when designing systems.
- Tell code agents: **one** CLI, not two alternatives, unless comparing is the goal.
- Tell design agents: design docs only — **do not invent skill files or patch skills** unless the task says so.
- Prefer writing under a single project root when building tools.

## When results land
1. Inventory artifacts (paths).
2. Reconcile conflicts (duplicate CLIs, contradicting model pairs, two publish docs).
3. Surface **conflicts + pick recommendations** before more building.
4. Re-smoke-test any claimed "working" CLI yourself before calling it done.
5. Lock decisions into this skill's `references/locked-decisions.md` once the user picks.

## Pitfalls seen this session
- Parallel code agents produced **two** assemblers (stdlib + deps). User had to pick. Prevent by specifying the stack in the task prompt.
- Parallel creative agents may **patch skills unprompted**. Verify skill tree after fan-out.
- Parallel mlops agents may re-recommend dual-model stacks the user cannot run. Always filter through "what model does the user actually have?"
- Do not promise full novel automation until: book-writer profile, narrative project-mode/ledger, loop wiring, and Windows Darwin stack exist.
