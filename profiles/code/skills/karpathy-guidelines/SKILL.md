---
name: karpathy-guidelines
description: Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make surgical changes, surface assumptions, and define verifiable success criteria.
triggers:
  - "refactor"
  - "review code"
  - "code review"
  - "simplify"
  - "overcomplicated"
  - "code quality"
  - "best practice"
  - "clean code"
  - "surgical"
  - "goal driven"
  - "think before coding"
  - "success criteria"
  - "infrastructure"
  - "dependency"
  - "prefer tools"
  - "karpathy"
license: MIT
---

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls. For deeper background on the jagged intelligence that causes these failure modes, see the [[ghosts-vs-animals]] concept in the LLM wiki.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## The Three Failure Modes (Why These Principles Exist)

Karpathy identified three recurring problems when LLMs generate code autonomously. See `references/karpathy-agent-failure-modes.md` for the full Karpathy quotes.

| Failure Mode | What It Looks Like | Fixed By |
|---|---|---|
| **Silent assumptions** | Makes wrong assumptions on your behalf without surfacing them | Think Before Coding |
| **Overengineering** | Bloated APIs, unnecessary abstractions, 1000 lines when 100 would do | Simplicity First |
| **Collateral edits** | Changes/removes code it doesn't understand as side effects | Surgical Changes |

The root cause: LLMs exhibit **jagged intelligence** — genius polymath and confused grade-schooler simultaneously. The principles below catch the 10-year-old mistakes while letting the PhD-level reasoning run.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Prefer Native Tools Over External Infrastructure

**Don't build scripts, databases, or repos when the tools you already have can do the job.**

A common failure pattern: a skill or workflow depends on infrastructure that doesn't exist — a SQLite database, a Python script directory, a self-evolution repo, a cron job. Before adding any external dependency:

- Does an existing tool already cover this? (session_search, skill_manage, memory, delegate_task, web_search)
- Could the workflow run inside the conversation instead of as a standalone script?
- Is the external dependency actually installed/set up on this system, or would you be writing code for an imaginary runtime?

**The test:** If removing the external dependency would collapse the approach, the approach was wrong. A Karpathy-style solution uses only tools that exist. It does not require setup steps, installation, or infrastructure provisioning.

Examples:
  • Instead of "query state.db for past failures" → use session_search
  • Instead of "run a Python script to classify errors" → use the agent's own reasoning
  • Instead of "clone a self-evolution repo" → use skill_manage(patch) directly
  • Instead of "write metrics to a JSON file" → use mnemosyne_remember

## 4. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 5. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
