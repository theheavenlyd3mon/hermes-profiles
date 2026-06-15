---
name: karpathy-coding-discipline
description: "Four Karpathy-derived principles for surgical, simple, goal-driven coding. Fight silent assumptions, overengineering, and collateral edits."
triggers: [code,implement,write code,refactor,feature,add,modify,change,simplify,cleanup,surgery,goal-driven,assumption]
version: 1.0.0
author: Senna (derived from forrestchang/andrej-karpathy-skills, sourced from Andrej Karpathy's observations)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding, discipline, simplicity, quality, behavior, karpathy]
    related_skills: [test-driven-development, systematic-debugging, writing-plans, requesting-code-review, tool-call-efficiency]
---

# Karpathy Coding Discipline
IDENTITY: SurgicalCoder{MinimalChanges,ExplicitThinking,GoalDriven}. Law=TouchOnlyWhatWasAsked. Violation=DriveByRefactor.
Law: Every changed line must trace directly to the user's request. If it doesn't, don't change it.
TRADE: These guidelines bias toward caution over speed. For trivial tasks (single-line fixes, known-correct boilerplate), use judgment — but document where you deviated and why.
WHENUSE: AlwaysDuringCoding{Features,Bugfixes,Refactors,CodeReview}. ESPECIALLY:{ComplexMultiStep,UnfamiliarCodebase,AmbiguousSpec,HighRiskChanges}. UseJudgment:{TrivialFixes,Renames,KnownPatterns}→StateWhySkipped.
REDFLAGS: {SilentAssumption||ChangedUnrelatedCode||TouchedFormatting||AddedUnrequestedFlexibility||ImportedUnusedDep||DeletedExistingComments||UnknownSideEffect||SkippedVerificationStep||CantStateWhatChanged||OneHundredWhenTwenty}→Pause→Reassess.
RATIONALIZATIONS: WhileImHere→Surgical=False|ThisIsCleaner→MatchExistingStyle|TheyllWantItLater→NoSpeculative|ThisDocsWrong→MentionDontFix|JustOneImport→DirectTrace|TestsPassSoFine→MissingEdgeCases|ItsObvious→StateAssumptionExplicitly|BetterPattern→NotRequested|Trivial→IsItReally|EveryoneDoesIt→Irrelevant.
QUICKREF: ThinkBeforeCoding(StateAssumptions→SurfaceAmbiguity→PushBack)→SimplicityFirst(MinCode→NoAbstractions→NoErrorHandlingForImpossible)→SurgicalChanges(TouchOnlyRequested→MatchStyle→MentionNotFix)→GoalDriven(Task→VerifiableCriteria→PlanWithChecks).
---

## The Four Principles

### 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**

**What to do:**
- State your assumptions explicitly. If uncertain, ask — don't guess.
- If multiple interpretations exist for a requirement, present them. Don't silently pick one.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask for clarification.

**What to avoid:**
- Starting implementation while vague on what's wanted
- Assuming you know the user's intent without checking
- Silently resolving ambiguity in your favor

**Verification:** Before writing code, can you state in one sentence what the user asked and the approach you're taking?

---

### 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**

**What to do:**
- Write the smallest change that satisfies the requirement
- Prefer flat code over abstractions
- If 200 lines could be 50, rewrite it
- Apply the senior engineer test: "Would a senior say this is overcomplicated?"

**What not to add:**
- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- No performance optimization without evidence of a bottleneck
- No comments explaining what the code does (the code should say that)

**The test:** If you removed every line that isn't strictly required to satisfy the user's request, what's left? That's what should be there.

---

### 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**

**What to do:**
- Edit only the lines necessary to fulfill the request
- Match existing code style, even if you'd do it differently
- When your changes orphan code (unused imports, variables, functions), remove those only

**What not to do:**
- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken
- Don't delete existing comments unless they're wrong about what your changes do
- Don't rename variables or functions that aren't part of the change
- Don't run a formatter on the whole file

**If you notice unrelated issues:**
- Mention them verbally ("I also noticed X is dead code / this comment is stale")
- Do NOT fix them in this change
- Let the user decide if they want a separate task

**The test:** Every changed line should trace directly to the user's request. If you can't say which part of the request required that change, remove it.

---

### 4. Goal-Driven Execution
**Define success criteria. Loop until verified.**

**The core insight (Karpathy):** *"LLMs are exceptionally good at looping until they meet specific goals. Don't tell it what to do, give it success criteria and watch it go."*

**What to do:**
- Transform imperative instructions into verifiable goals

  | Instead of | Transform to |
  |---|---|
  | "Add validation" | "Write tests for invalid inputs, then make them pass" |
  | "Fix the bug" | "Write a test that reproduces it, then make it pass" |
  | "Refactor X" | "Ensure tests pass before and after" |
  | "Optimize Y" | "Benchmark before, benchmark after, show improvement" |
  | "Add feature Z" | "Write integration test proving Z works, then implement" |

- For multi-step work, state a brief plan with verification checkpoints:

  ```
  1. [Add endpoint]    → verify: curl returns 200 with expected body
  2. [Add validation]  → verify: invalid input returns 422
  3. [Write tests]     → verify: pytest passes, coverage ≥ 80%
  ```

**Why this works:** Strong success criteria let the agent loop independently. Weak criteria ("make it work", "do it right") require constant clarification and lead to thrashing.

**The test:** Can someone else look at the success criteria and know, unambiguously, whether the task is done?

---

## Hermes Agent Integration

### Loading this skill

This skill pairs naturally with other coding skills. In your SOUL.md, add a ROUTE_MAP entry:

```yaml
ROUTE_MAP: Codify→{Load:karpathy-coding-discipline,test-driven-development}
```

### With delegate_task

When dispatching subagents for implementation, include the discipline in context:

```python
delegate_task(
    goal="[implement X, fix Y, refactor Z]",
    context="""
    Follow karpathy-coding-discipline:
    1. Think Before Coding — state your assumptions, surface ambiguity
    2. Simplicity First   — minimum code, no speculative abstractions
    3. Surgical Changes   — touch only what was requested
    4. Goal-Driven        — transform task into verifiable success criteria

    Project context: [paths, test commands, conventions]
    """,
    toolsets=['terminal', 'file']
)
```

### With test-driven-development

The Karpathy principles and TDD reinforce each other:
- Goal-Driven Execution → RED phase (define what success looks like as a failing test)
- Simplicity First → GREEN phase (minimum code to pass)
- Surgical Changes → REFACTOR phase (touch only what needs cleaning)

### With code review

When reviewing code, use the four principles as a rubric:
- **Think:** Did they surface assumptions or hide them?
- **Simplicity:** Is every line necessary?
- **Surgery:** Are there unrelated changes in the diff?
- **Goal:** Is there a verification path for each claimed fix?

---

## Verification Checklist

Before marking a coding task complete:

- [ ] I stated my assumptions explicitly and got alignment before coding
- [ ] Every line I wrote is strictly necessary for the request
- [ ] I did NOT change anything outside the scope of what was asked
- [ ] If I noticed unrelated dead code/docs, I mentioned it — didn't fix it
- [ ] I have a verifiable success criterion — not just "it works"
- [ ] I matched existing code style, even where I'd prefer differently
- [ ] I removed only what my changes made unused (no pre-existing cleanup)

**Can't check all boxes?** You deviated from the discipline. State why.

---

## Edge Cases

| Situation | Apply |
|---|---|
| User explicitly asks for refactoring + cleanup | Full scope — this IS the request |
| User says "clean this up" | Ask what specifically they want cleaned. If they say "everything", all bets are off |
| Bug fix in unfamiliar code | Extra caution on Surgery — more likely to touch unrelated things |
| Emergency / prod fire | State: "Following discipline would slow this down. Skipping [principles] because [reason]." |
| Trivial one-line change | Can skip full process. Still verify: does this line trace to the request? |
| Ambiguous requirement | Don't guess — state interpretations and ask |
