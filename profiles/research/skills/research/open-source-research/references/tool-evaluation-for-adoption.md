# Tool Evaluation for Personal Adoption

A variant of the open-source-research workflow. Unlike general repo analysis (which answers "how does this project work?"), this variant answers **"should I install this on my machine?"**

## When to use

The user asks about a tool, terminal, CLI, GUI, library, or framework and wants to know if it's worth installing — not just what it does.

## Workflow

### Step 1: Quick overview (you)

Provide the user with an immediate high-level answer covering:

- What is it? (one-liner)
- What problem does it solve for *this user's setup* (not generic)
- How would they use it day-to-day?
- Install method (brew, npm, pip, download, etc.)
- OS/platform requirements
- Any immediate compatibility concerns (Apple Terminal vs OpenTUI, Intel vs ARM, macOS version)

### Step 2: Delegate deep-dive to researcher

Create a kanban task for the researcher profile to gather community sentiment and practical experiences. Use the Research Task Scoping pattern from kanban-orchestrator (approach A — source limit, or approach D — goal-oriented).

**Task body template:**

```markdown
Research <Tool> — community sentiment, real-world experiences, and compatibility concerns.

**Part 1 — Community sentiment**
- What do developers on Reddit, HN, and review sites say? Pros/cons?
- Any recurring complaints or dealbreakers?

**Part 2 — Compatibility with this user's setup**
- macOS compatibility (Intel Mac, macOS 15.6)
- Terminal/TUI support — will it render properly in Apple Terminal?
- Known conflicts with installed software

**Part 3 — Comparison with alternatives**
- How does it compare to <main alternatives>?
- Is it worth switching?

**Limits:**
- Max N sources
- Synthesize into 3-4 paragraph summary
- Do NOT install or download anything
```

### Step 3: Practical usage guide (you, while researcher works)

Write a quick "how you'd use this" section covering the first-run experience:

- Install command or download steps
- Launch command
- First things to try
- Configuration (if any)
- How to make it the default (if replacing something)

### Step 4: Decision gate

When the researcher's findings come back, synthesize with your overview:

- What's the consensus? Positive/negative/mixed?
- Any dealbreakers for this user's specific setup?
- Recommendation: install now, skip, or try alongside existing setup?
- If the user's preference is TUI over GUI, weight terminal-compatible options higher in the recommendation.

## User Preferences to Embed

- This user explicitly prefers TUI over GUI ("i enjoy using tui more"). When comparing alternatives or recommending tools, give TUI-friendly options a higher ranking. If the tool being evaluated is GUI-only, acknowledge this as a potential negative.
- The user wants the full landscape before committing — not to be rushed. Provide the overview, community sentiment, and practical guide *before* asking if they want to install.
- Never install without first presenting the full evaluation. The "evaluate first, install second" pattern was established after a prior correction.
