---
name: tool-call-efficiency
description: "Minimize tool call count per task by assessing context sufficiency before reaching for tools. Cross-cutting behavioral discipline for all agent tasks."
version: 1.0.0
author: Senna (after user correction — redundant tool calls in May 2026)
license: MIT
platforms: [linux, macos]
prerequisites: []
metadata:
  hermes:
    tags: [efficiency, tool-calling, optimization, cost-reduction, discipline]
    source: "User correction — 'we need to optimise way to minimize tool calling to the least amount as possible to reach our conclusion'"
    validated_by: "Mem0 token optimization playbook (May 2026) — 'the real cost leak is not the model, it's making the model reread the same useless context every turn'"
---

IDENTITY: EfficiencyGuard{InputSufficiency,OutputComplexityAbsorption}. CoreRole: Minimize tool call count per task by checking context sufficiency before reaching and absorbing complexity into output artifacts. BehavioralContract: Ask "do I already know enough?" before every tool call. Batch independent calls. Never descend into mechanism when targeting output.
Law: Every unnecessary tool call starts a chain. The first unnecessary call is the most expensive.
WHENUSE: Every task the agent handles — cross-cutting behavioral discipline. ESPECIALLY:{ResearchTasks,Documentation,MultiStepWorkflows}. NoSkip:{AnyTask}.
REDFLAGS: SerialExploration->Parallelize|DescendingIntoMechanism->TargetOutputOnly|SufficiencyBypass->TrustContext|ConfirmingKnown->SkipIt|OpenLoopInvestigation->DefineStopCriterion.
RATIONALIZATIONS: "Let me verify one more thing"->ChainStarter|"Being thorough"->ExhaustivenessIsntProductive|"Just checking"->Noise.
QUICKREF: Check{context window|mnemosyne|env knowledge|prior outputs}->Target{minimum info for correct answer}->Parallelize{independent calls in one shot}->Proportional{effort matches task complexity}->Audit{≤50% investigatory calls}.

# Tool Call Efficiency

A cross-cutting discipline for minimizing tool call count per task. This is not a domain-specific workflow — it applies to **every** task the agent handles, from research to coding to documentation.

## Two Sides of the Same Optimization

There are two complementary levers for minimizing tool calls — one targets **input**, the other targets **output**.

### Input-Side: Check Sufficiency Before Reaching for Tools

**You already have more context than you think. Ask before grabbing.**

The Mem0 Token Optimization Playbook (May 2026) demonstrated this experimentally:
- Naive: dump ALL memory into every call = **594 tokens** per query
- Retrieval-based: ask "what's relevant here?" first = **166 tokens** per query
- Same answer quality. **72% savings.**

The equivalent at the tool-calling level: dumping ALL potential information sources into every task vs. asking "do I already know enough to produce the output?"

### Output-Side: Absorb Complexity in the Artifact

The HTML-over-Markdown argument (Thariq Shihipar, Anthropic, May 2026) introduces a complementary principle:

> *"When the AI is both generating and consuming the output, Markdown's human-readability advantage disappears. HTML wins on structure, interactivity, and shareability."*

A single HTML artifact with inline SVG, interactive diagrams, and styled layouts can convey what would otherwise require multiple round-trips of "generate → inspect → clarify → regenerate." **The richer the output format, the fewer tool calls needed to make it useful.**

Practical translation:
- A markdown doc that needs clarifying → the user asks questions → more tool calls to answer them
- An HTML artifact that embeds diagrams, clickable flows, and data inline → the user gets the picture in one render

**Apply both sides:** before reaching for a tool, check input sufficiency. When generating the output, choose a format that absorbs as much complexity as possible in a single artifact.

## The Checklist (apply before every tool call)

Before calling ANY tool, run through this mental checklist:

1. **Sufficiency check** — Do I already have the answer in:
   - My context window (current conversation)?
   - Mnemosyne memory (persistent facts)?
   - Environmental knowledge (OS, installed tools, paths)?
   - Previous tool outputs already in this turn?

2. **Output target** — What's the minimum information I need to produce a correct answer? Not "what would be interesting to know" but "what does the output actually require?"

3. **Parallelization** — If I genuinely need 3 independent facts, can I fire all 3 calls in one shot instead of waiting for each to complete before deciding on the next?

4. **Proportional effort** — Does the complexity of my investigation match the complexity of the task? Writing a markdown doc does not require reverse-engineering the database schema.

5. **Trust the high-level query** — A single `mnemosyne_stats` or `lcm_status` gives you aggregate state. Don't descend into table schema inspection unless the task specifically requires it.

## Common Anti-Patterns

### ❌ Serial exploration
```
tool1 → inspect output → decide → tool2 → inspect → tool3 → inspect → tool4
```
Replace with parallel batches when calls are independent:
```
tool1 + tool2 + tool3 (parallel) → inspect → tool4 (if needed)
```

### ❌ Descending into mechanism when targeting output
Task: "document how Mnemosyne works"
- WRONG: read every table schema, check WAL files, count rows per table, verify column constraints (7+ tool calls)
- WRONG especially: investigating a WAL/checkpoint discrepancy that turned out to be irrelevant to the output
- RIGHT: `mnemosyne_stats` for counts, `lcm_status` for architecture context, existing memory for preferences. That's enough. (2-3 tool calls)

### ❌ The sufficiency bypass
You already know the answer from context but call a tool to "verify" or "be thorough." If the tool's output won't change your answer, the call is noise. The user flagged this exact pattern — trust the context you were given.

### ❌ Confirming what you already know
If you ran `find . -name '*.db'` and already know the path from `lcm_status`, you're confirming. Skip it.

### ❌ The open-loop investigation
Starting with "let me check X" without a clear stopping criterion. Before every tool call, define: "If the output shows Y, I'm done. If it shows Z, I need one more call. If it shows anything else, I'll stop anyway because I have enough context."

### ❌ Serial GitHub page scrapes for a full skill inventory
Task: "full list of every skill and how it works" across a skill-pack repo.
- WRONG: web_extract README then each skill URL or raw.githubusercontent one-by-one (truncation, rate limits, huge call count).
- RIGHT: one `git clone --depth 1` (or recursive git trees API) plus local parse of every SKILL.md in one code pass. README is overview-only.
- Same idea for multi-URL research: batch independent fetches first; escalate to clone when depth needs full trees.

## Pitfalls

- **Exhaustiveness feels productive but isn't.** 13 calls to write a markdown file is 8 more than necessary. The extra calls gave zero additional value to the output.
- **Tool calls compound.** One unnecessary call leads to inspecting its output, which suggests another call, which suggests another. The first unnecessary call is the most expensive one — it starts a chain.
- **"Just checking" is a trap.** Every "let me just verify one more thing" adds the same latency as a necessary call. If the answer won't change your output, it's noise.
- **Memory is not a CYA mechanism.** You don't need to independently verify every fact that's already in your context window. Trust the context you were given.

## Verification

After each task, audit your own tool usage:

- Did I make any call whose answer I could have inferred from existing context?
- Could I have parallelized any independent calls?
- Did I descend into implementation detail that didn't affect the output?
- How many calls did I actually need vs. how many did I make?

Target: for any task, ≤ 50% of calls should be investigatory. The rest should be direct writes, edits, or output generation.

## JSON Parsing in execute_code

When parsing JSON files inside `execute_code` scripts, always use `jq` via `terminal()` — never `read_file()` + `json.loads()` (line numbers break JSON) or `terminal("cat")` + `json.loads()` (control characters break parsing). See `references/execute-code-json-parsing.md` for the full failure mode analysis and jq patterns.

- `references/mem0-2026-token-optimization.md` — The Mem0 playbook that validated the input-side approach: 72% savings from retrieval-based vs. naive context usage
- `references/thariq-html-effectiveness.md` — The Thariq/Anthropic article on HTML as an output format: absorbing complexity into the artifact to reduce round-trips
- `references/cli-vs-mcp-token-efficiency.md` — CLI vs MCP token efficiency research: 35x token reduction, 28% higher task completion. Validates CLI-first tool selection as an architectural complement to behavioral efficiency.
- `references/skill-pack-inventory-bulk-path.md` — Clone-once + parse every SKILL.md for third-party skill-pack full inventories (vs serial GitHub scrapes); import shortlist hygiene.
