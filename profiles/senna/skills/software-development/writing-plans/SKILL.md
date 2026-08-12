---
name: writing-plans
description: "Write implementation plans: bite-sized tasks, paths, code."
triggers:
  - "plan"
  - "implementation"
  - "roadmap"
  - "steps"
  - "how to"
  - "approach"
  - "task breakdown"
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, design, implementation, workflow, documentation]
    related_skills: [subagent-driven-development, test-driven-development, requesting-code-review]
---

IDENTITY: PlanAuthor{ZeroContextAssume,QuestionableTaste}. CoreRole: Write implementation plans so precise implementation becomes obvious. BehavioralContract: Assume implementer knows nothing about codebase and has questionable taste. Every task 2-5 min. DRY. YAGNI. TDD. Frequent commits.
Law: If someone has to guess, the plan is incomplete.
WHENUSE: Multi-step features, delegation to subagents, complex requirements. ESPECIALLY:{DelegatingToSubagent,MultiStepFeature,FeatureBreakdown}. NoSkip:{SimpleFeature,FutureSelf,GuestDeveloper}.
REDFLAGS: VagueTaskNames->NotBiteSize|MissingFilePaths->Incomplete|NoTestSteps->SkipTDD|CopyPasteCode->DRYViolation|FutureFlexibility->YAGNIViolation|NoVerification->Unverifiable|TaskExceeds5Min->TooLarge.
RATIONALIZATIONS: "Feature is simple"->AssumptionsCauseBugs|"I'll remember details"->FutureYouWon't|"Working alone"->DocumentationMatters.
QUICKREF: Understand{requirements,criteria,constraints}->Explore{project,similar features,tests}->Design{arch,files,deps,strategy}->WriteTasks{setup->core->edge->integration->cleanup}->Review{sequential,bite-size,exactPaths,completeCode}.

# Writing Implementation Plans

## Overview

Write comprehensive implementation plans assuming the implementer has zero context for the codebase and questionable taste. Document everything they need: which files to touch, complete code, testing commands, docs to check, how to verify. Give them bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume the implementer is a skilled developer but knows almost nothing about the toolset or problem domain. Assume they don't know good test design very well.

**Core principle:** A good plan makes implementation obvious. If someone has to guess, the plan is incomplete.

### Granularity note for creative/3D/visual projects

The 2-5 minute task guideline applies well to code features (add a model, write a test, wire an API). For **creative, 3D, and visual projects** (shader implementation, particle systems, cinematic sequences, scene composition), tasks are typically **15-30 minutes per task** because they involve: a design phase (what should this shader look like), an implementation phase (write the GLSL + wire uniforms), and a tuning phase (adjust parameters until it looks right).

If you're planning a Three.js/creative project, allow larger tasks and split at natural "it works" boundaries rather than strict time limits. Still enforce DRY/YAGNI/TDD where applicable — shaders especially benefit from isolated testing.

## When to Use

**Always use before:**
- Implementing multi-step features
- Breaking down complex requirements
- Delegating to subagents via subagent-driven-development

**Don't skip when:**
- Feature seems simple (assumptions cause bugs)
- You plan to implement it yourself (future you needs guidance)
- Working alone (documentation matters)

## Bite-Sized Task Granularity

**Each task = 2-5 minutes of focused work.**

Every step is one action:
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

**Too big:**
```markdown
### Task 1: Build authentication system
[50 lines of code across 5 files]
```

**Right size:**
```markdown
### Task 1: Create User model with email field
[10 lines, 1 file]

### Task 2: Add password hash field to User
[8 lines, 1 file]

### Task 3: Create password hashing utility
[15 lines, 1 file]
```

## Plan Document Structure

### Header (Required)

Every plan MUST start with:

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### Task Structure

Each task follows this format:

````markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67` (line numbers if known)
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Writing Process

### Step 1: Understand Requirements

Read and understand:
- Feature requirements
- Design documents or user description
- Acceptance criteria
- Constraints

### Step 2: Explore the Codebase

Use Hermes tools to understand the project:

```python
# Understand project structure
search_files("*.py", target="files", path="src/")

# Look at similar features
search_files("similar_pattern", path="src/", file_glob="*.py")

# Check existing tests
search_files("*.py", target="files", path="tests/")

# Read key files
read_file("src/app.py")
```

### Step 3: Design Approach

Decide:
- Architecture pattern
- File organization
- Dependencies needed
- Testing strategy

### Step 4: Write Tasks

Create tasks in order:
1. Setup/infrastructure
2. Core functionality (TDD for each)
3. Edge cases
4. Integration
5. Cleanup/documentation

### Step 5: Add Complete Details

For each task, include:
- **Exact file paths** (not "the config file" but `src/config/settings.py`)
- **Complete code examples** (not "add validation" but the actual code)
- **Exact commands** with expected output
- **Verification steps** that prove the task works

### Step 6: Review the Plan

Check:
- [ ] Tasks are sequential and logical
- [ ] Each task is bite-sized (2-5 min)
- [ ] File paths are exact
- [ ] Code examples are complete (copy-pasteable)
- [ ] Commands are exact with expected output
- [ ] No missing context
- [ ] DRY, YAGNI, TDD principles applied

### Step 7: Save the Plan

```bash
mkdir -p docs/plans
# Save plan to docs/plans/YYYY-MM-DD-feature-name.md
git add docs/plans/
git commit -m "docs: add implementation plan for [feature]"
```

## Principles

### DRY (Don't Repeat Yourself)

**Bad:** Copy-paste validation in 3 places
**Good:** Extract validation function, use everywhere

### YAGNI (You Aren't Gonna Need It)

**Bad:** Add "flexibility" for future requirements
**Good:** Implement only what's needed now

```python
# Bad — YAGNI violation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # Not needed yet!
        self.metadata = {}     # Not needed yet!

# Good — YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### TDD (Test-Driven Development)

Every task that produces code should include the full TDD cycle:
1. Write failing test
2. Run to verify failure
3. Write minimal code
4. Run to verify pass

See `test-driven-development` skill for details.

### Frequent Commits

Commit after every task:
```bash
git add [files]
git commit -m "type: description"
```

## Common Mistakes

### Vague Tasks

**Bad:** "Add authentication"
**Good:** "Create User model with email and password_hash fields"

### Incomplete Code

**Bad:** "Step 1: Add validation function"
**Good:** "Step 1: Add validation function" followed by the complete function code

### Missing Verification

**Bad:** "Step 3: Test it works"
**Good:** "Step 3: Run `pytest tests/test_auth.py -v`, expected: 3 passed"

### Missing File Paths

**Bad:** "Create the model file"
**Good:** "Create: `src/models/user.py`"

## Execution Handoff

After saving the plan, offer the execution approach:

**"Plan complete and saved. Ready to execute using subagent-driven-development — I'll dispatch a fresh subagent per task with two-stage review (spec compliance then code quality). Shall I proceed?"**

When executing, use the `subagent-driven-development` skill:
- Fresh `delegate_task` per task with full context
- Spec compliance review after each task
- Code quality review after spec passes
- Proceed only when both reviews approve

## Post-Implementation: Evolving the Plan into an Architecture Document

Once all tasks in a plan are complete, the PLAN.md file becomes stale — it describes *what to build* but no longer reflects *what exists*. Convert it to a living architecture document so it stays useful for collaborators, future feature planning, and Hermes context.

### Signals the Plan is Stale

- References files that no longer exist (e.g., a monolithic `ui.js` that was refactored into `ui/*`)
- Mentions "create: file.js" instructions for files that already exist
- TDD steps and review checklists that are checked off
- Task numbers (T1, T2…) that refer to completed work
- Execution order sections describing what *was done* rather than what the code *does*

### What to Replace It With

Replace the implementation plan with a document that a reader (contributor, future-you, Hermes agent) can use to understand the project at a glance:

| Section | Content |
|---------|---------|
| **Quick Start** | Exact `npm install` / `npm run dev` commands |
| **File Map** | Actual file tree with one-line purpose per file |
| **Data Flow** | How the main loop wires modules together (text diagram) |
| **Feature Catalog** | Each feature described with controls/API/caveats |
| **Architecture Decisions** | Key tradeoffs and *why* they were made (e.g., "labels are children of meshes to auto-follow orbits") |
| **Lessons Learned** | Hard-won API gotchas, version-specific workarounds — the stuff you don't want to rediscover |
| **Controls Reference** | Keyboard/mouse bindings table |
| **Build & Deploy** | Exact commands and expected output |
| **Future Ideas** | What you'd do next — living wishlist, not a commitment |

### How to Identify Drift

Before rewriting, diff the plan against the actual codebase:

1. **File list check** — `ls -R src/` vs the plan's file map. Note files the plan mentions that don't exist (deleted/refactored) and files that exist but the plan doesn't mention (added during implementation).
2. **Import graph check** — read `main.js` / entry point imports vs what the plan says should be wired. Function signatures and export names often drift.
3. **API surface check** — for any feature the plan specifies a particular API (e.g., `createPostProcessing(renderer, scene, camera)`), check whether the actual module exports that signature. Implementation often refactors for cleanliness.
4. **Control flow check** — the plan's animate loop pseudocode vs the actual animate loop. Real code may have different ordering, additional calls (resize handlers, selection ring sync), or conditionals the plan simplified.

### What to Preserve

Some parts of the original plan should survive the rewrite:

- **Pitfalls sections** — these are hard-won. Move them into the architecture doc under the relevant feature.
- **Verification checklist** — mark the ✅ items as proven, keep the list as a smoke test reference.
- **Architecture diagrams (ASCII or Mermaid)** — these describe structure, not process, so they often stay accurate.

### What to Drop Without Guilt

- **Task numbers and execution ordering** — these described the *build process*, not the *product*
- **TDD steps** — the tests exist now (or were transient), the steps are irrelevant
- **Review checklists** — reviews are done; keep only the checklist criteria that inform future contributions
- **Plan-specific metadata** — subagent context like "For Hermes: Use subagent-driven-development..."

### Example

Before (stale plan section):
```
### T2 — CSS2DRenderer Planet Labels
**Objective:** Add floating HTML labels...
**Step 1: Create src/labels.js**
```js
export function createLabels(scene, camera, planets) { ... }
```
**Step 2: Wire into src/main.js**
Add import: `import { createLabels } from './labels.js';`
```

After (architecture doc section):
```
### CSS2D Planet Labels
Floating HTML labels above each planet showing name, orbit, and period.
Glass-morphism styling with backdrop-filter blur. Labels are children of
planet meshes (auto-follow orbits). Render AFTER the WebGL pass:
`labelRenderer.render(scene, camera)`.
- pointer-events: none on both div and renderer domElement
- z-index: 1 to sit above the WebGL canvas
- Window resize forwarded to labelRenderer.setSize()
```

## Plan Mode

Use this skill when the user wants a plan instead of execution.

### Core behavior

For this turn, you are planning only.

- Do not implement code.
- Do not edit project files except the plan markdown file.
- Do not run mutating terminal commands, commit, push, or perform external actions.
- You may inspect the repo or other context with read-only commands/tools when needed.
- Your deliverable is a markdown plan saved inside the active workspace under `.hermes/plans/`.

### Output requirements

Write a markdown plan that is concrete and actionable.

Include, when relevant:
- Goal
- Current context / assumptions
- Proposed approach
- Step-by-step plan
- Files likely to change
- Tests / validation
- Risks, tradeoffs, and open questions

If the task is code-related, include exact file paths, likely test targets, and verification steps.

### Save location

Save the plan with `write_file` under:
- `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`

### Non-code planning (adaptation)
Plan Mode's task template is built for code (write-failing-test → implement → verify). It also serves
*research/decision* plans (e.g. hackathon rule-capture, build-formulation) where "tasks" are read-only
research + scoring steps, not TDD cycles. In that case: keep the Goal/context/approach/risks structure,
but the steps are investigation + a decision framework. The real implementation plan is written later,
after the user picks a direction. Do not force TDD steps onto non-code planning.

Treat that as relative to the active working directory / backend workspace. Hermes file tools are backend-aware, so using this relative path keeps the plan with the workspace on local, docker, ssh, modal, and daytona backends.

### Interaction style

- If the request is clear enough, write the plan directly.
- If no explicit instruction accompanies `/plan`, infer the task from the current conversation context.
- If it is genuinely underspecified, ask a brief clarifying question instead of guessing.
- If the build hinges on an unanswered user decision, SURFACE THE QUESTIONS IN YOUR REPLY as numbered items — do NOT only bury them in the plan file. User signal (Spark session): "how about you tell me the questions for me to answer" — they want the questions in front of them, not hidden in a doc they must open.
- After saving the plan, reply briefly with what you planned and the saved path.

**Competition/hackathon entries:** If the user hasn't yet chosen WHAT to build (problem not formulated, rules not extracted), use the `web3-hackathon-entry` skill first for Phase A (requirements-capture + build-formulation + scoring matrix). Only invoke this skill's Plan Mode for Phase B — the actual implementation task breakdown — once the build is chosen.

## Remember

```
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
```

**A good plan makes implementation obvious.**
