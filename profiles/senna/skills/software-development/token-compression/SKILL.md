---
name: token-compression
description: Compress skill/config/prompt files using Proteus-style DSL — token packing, semantic normalization, DSL encoding, structural compression, state-machine loops, arrow conditionals. Reduces 40-70% on behavioral/header sections while keeping operational instructions readable.
version: 1.0.0
author: Noctis
license: MIT
platforms: [linux, macos, windows]
tags: [compression, token-optimization, dsl, proteus, prompts, system-prompts]
metadata:
  hermes:
    related_skills: [skill-compression, hermes-soul-authoring]
---

# Token Compression — Compressed DSL for Skill Files

Apply compressed DSL encoding to behavioral/header sections of skill files, prompt templates, and agent configuration. Operational instructions stay in readable prose.

## When to use

Your skill file or prompt template is getting long and you want to fit more behavioral signal into fewer tokens. Apply when:

- You have 3+ skill files loading into the same session
- Your identity/behavior section exceeds ~1,500 characters
- You want to encode complex routing logic, team rosters, or decision trees compactly
- You're building multi-agent systems where each agent's prompt needs to be lean

**Don't use this for:** step-by-step tutorials, code examples, configuration files, or anything a human needs to read verbatim. Only compress the "how the agent should behave" parts.

## Six Techniques

| # | Technique | What it does | Prose → Compressed |
|---|---|---|---|
| 1 | **Token packing** | `{a,b,c}` replaces bullet lists | `- debug\n- test\n- build` → `{Debug,Test,Build}` |
| 2 | **Semantic normalization** | Long phrases → compound primitives | `Fix before investigating` → `NoFixWOInvestigate` |
| 3 | **DSL encoding** | `Key=Value{Condition}` rules | `Respond in EN unless user writes another language` → `Lang=EN{UnlessUserOtherwise}` |
| 4 | **Structural compression** | Tables → pipe-delimited mappings | Markdown handoff table → `Design→Architect|Code→Coder|Review→Reviewer` |
| 5 | **State-machine loops** | Phase chaining with sub-steps | Multi-step workflow description → `Assess{X,Y}→Gather{A,B}→Dispatch{C}` |
| 6 | **Arrow conditionals** | `Condition→Action` | `When uncertain, say so` → `Uncertain→SayCheck` |

### Technique 1: Token Packing

Replace bullet lists with `{item1,item2,item3}` syntax. Use for unordered sets of triggers, tools, scopes, or constraints.

**Prose:**
```
When to use:
- Debugging test failures
- Investigating bugs
- Performance analysis
- Build issues
- Integration problems
```

**Compressed:**
```
WHENUSE: {TestFailures,Bugs,Perf,Builds,Integration}
```

**Rules:**
- Items should be short (1-3 words each)
- Capitalize each item as a proper noun
- Limit to ~8 items per packed set (beyond that, split into categories)
- Use for: triggers, examples, lists of tools, scope boundaries

### Technique 2: Semantic Normalization

Invent compound primitives that collapse multi-word concepts into single tokens. These become a shared vocabulary the model learns to parse.

| Original phrase | Normalized primitive |
|---|---|
| Don't fix bugs without understanding the root cause first | `NoFixWOInvestigate` |
| Pretending to know when you actually don't | `PretendKnow` |
| When 3+ fixes have failed, question the architecture | `ThreeFails→QuestionArch` |
| Don't add features you don't need yet | `YAGNI` |
| Copy-pasting code instead of extracting shared logic | `CopyPasteDRY` |

**Rules:**
- Use CamelCase for primitives (2-5 words max)
- Must be unambiguous — if you can't reconstruct the original meaning, the primitive is too compressed
- Nest well-known acronyms: DRY, YAGNI, TDD, WET
- Document the expansion in a nearby table or prose comment if the primitive isn't self-evident

### Technique 3: DSL Encoding

Use `Key=Value{Condition}` syntax for behavioral rules and defaults. The key is the behavior, the condition in `{}` narrows when it applies.

**Prose:**
```
Always respond in English unless the user writes in another language.
```

**Compressed:**
```
Lang=EN{UnlessUserOtherwise}
```

More examples:

| Prose | DSL |
|---|---|
| Route to the Architect when the task involves system design | `Route→Architect{SystemDesign}` |
| Escalate to the user if you're unsure | `Escalate→User{Uncertain}` |
| Approve PRs only if all tests pass | `Approve{TestsPass}` |

**Rules:**
- Key should be the action/behavior
- `{Condition}` in braces — only include when behavior changes based on context
- Omit `{}` for unconditional rules
- Chain with `→` for sequences: `Route→Reviewer{CodeChanges}`

### Technique 4: Structural Compression

Replace full markdown tables with pipe-delimited inline mappings. Use for team rosters, handoff maps, and routing tables.

**Prose table:**
```
| Teammate | How you work with them |
|---|---|
| Architect | Send design requests to before coding |
| Coder | Dispatch implementation tasks with specs |
| Reviewer | Pull in before merge. Verdict binding. |
```

**Compressed:**
```
ROUTE: Design→Architect|Implement→Coder|MergeGate→Reviewer
```

**Rules:**
- Use `|` to separate entries
- Use `→` for mapping (input → output)
- Keep each mapping under ~60 chars
- Prefix with the domain: `ROUTE:`, `HANDOFF:`, `TEAM:`, `DECISIONS:`

### Technique 5: State-Machine Loops

Encode multi-phase workflows as chained phases with sub-steps in `{...}`.

**Prose:**
```
First, assess the intent by parsing what the user said, checking what tools are available, and reviewing the current context. Then gather information by recalling relevant memories, searching past sessions, and loading the right skills. Then match the task to the right handler...
```

**Compressed:**
```
ROUTE_LOOP: Assess{ParseIntent,ScopeTools,CheckCtx}→Gather{RecallMem,SearchSessions,LoadSkills}→Match{TaskToSpec,VerifyAvail}→Dispatch{PrepContext,OneLineSummary,StepAside}→Verify{ConfirmReceipt,TrackDone,ReportBack}
```

**Rules:**
- Phases are verbs (Assess, Gather, Match, Dispatch, Verify)
- `{...}` packs sub-steps as a comma-separated list within that phase
- `→` chains phases in execution order
- Nested braces allowed: `Prep{Workspace,Paths,Context}`
- Max ~8 phases, ~5 sub-steps each

### Technique 6: Arrow Conditionals

Replace if/then/else logic with `Condition→Action` patterns. Use for red flags, rationalizations, and decision trees.

**Prose:**
```
If you see a quick fix that looks obvious, stop and investigate anyway. Obvious fixes hide root causes.
```

**Compressed:**
```
REDFLAGS: QuickFixNow→Phase1Rerun
```

Multi-condition example:
```
REDFLAGS: QuickFixNow→Phase1Rerun|SkipTest→RejectChange|MultiFixesSameBug→CantIsolate|EachFixRevealsNewProblem→QuestionArchitecture
```

**Rules:**
- Condition before `→`, Action after
- Use `|` to separate multiple conditionals
- Keep each pair under ~50 chars
- Group by domain: `REDFLAGS:`, `RATIONALIZATIONS:`, `GUARDRAILS:`

---

## What To Compress vs Keep Prose

| Compress these ✅ | Keep in prose ❌ |
|---|---|
| YAML/TOML frontmatter (triggers → packed list) | Step-by-step instructions (Phase 1, Phase 2…) |
| Overview / Core principles (DSL encode) | Code blocks and shell commands |
| When to use / Don't use (arrow conditionals) | Configuration / setup instructions |
| Red flags / Anti-patterns (normalize to primitives) | API references |
| Tables — rationalizations, handoffs, references | Diagrams and architecture sketches |
| Quick reference tables (DSL chain) | Anything the human must read exactly |

---

## Compressed Header Block Format

For skill files and agent prompts, add this block right after the frontmatter:

```
IDENTITY: {Trait.Trait}. {CoreRole}. {BehavioralContract}.
Law: {InviolableRule}.
WHENUSE: {ScopePacked}. ESPECIALLY:{Conditions}. NoSkip:{Exemptions}.
REDFLAGS: {Condition→Action}|{Condition→Action}|...
RATIONALIZATIONS: {Excuse→Reality}|{Excuse→Reality}|...
QUICKREF: Phase1(SubSteps)→Phase2(SubSteps)→Phase3(SubSteps).
```

Then the operational sections below remain in full prose.

---

## Workflow

### Step 1: Read the source file

Read the full content. Identify which sections are behavioral (identity, style, when-to-use, red flags) and which are operational (step-by-step instructions, code, configs).

### Step 2: Add the compressed header

Write the IDENTITY → QUICKREF block. Focus on:
- **IDENTITY** — who the agent is + core behavioral contract (2-3 sentences worth, packed)
- **Law** — one inviolable rule the agent must never break
- **WHENUSE** — triggers packed with `{}`, exceptions after `NoSkip:`
- **REDFLAGS** — every common failure mode mapped to corrective action
- **RATIONALIZATIONS** — every excuse the agent might tell itself, mapped to the truth
- **QUICKREF** — the entire workflow as a state-machine chain

### Step 3: Compress the overview sections

Apply token packing and DSL encoding to:
- "When to use" sections → arrow conditionals
- Overview / principles → DSL encode
- Tables → structural compression

### Step 4: Keep operational prose

Leave step-by-step instructions, code blocks, and verification checklists in full readable prose.

### Step 5: Verify

1. Read the compressed header and reconstruct the original meaning in your head
2. If any meaning is lost or ambiguous → that section stays prose
3. If the compressed version is unambiguous → ship it
4. Read the full file back and check for orphaned section headers (e.g., a `## When to Use` that now has no content after the header replaces it)

---

## Pitfalls

- **Don't over-compress Identity.** The first line anchors personality — keep it human-parseable. Compress the sections below it aggressively.
- **Mix the DSL vocabulary.** `{a,b,c}` for unordered sets, `→` for sequences, `=` for assignments, `:` for key-value pairs. Don't force everything into one delimiter.
- **Test on the target model.** GPT-4 and Claude handle compressed DSL well; smaller open-source models may stumble. Verify before deploying.
- **Don't pack code blocks or shell commands** — they must stay runnable.
- **Don't remove YAML frontmatter** — it's structural, not behavioral.
- **Watch for orphaned section headers.** When you replace a prose section with a compressed alternative, old `## Section Name` markers can remain with no content underneath. Always check for these.
- **For files with ASCII diagrams or architecture sketches**, insert the compressed header block before the diagram, not in place of it — the diagram is operational, not behavioral.

## Verification

After compressing a file:

1. Read the compressed header. Can you reconstruct the original instructions?
2. If any meaning is lost or ambiguous → revert that section to prose
3. If the compressed version is unambiguous → it passes
4. Read the full file once more — any orphaned section headers? Any code blocks accidentally compressed?

> **Note for iknowkungfu registry submissions:** See `references/iknowkungfu-submission-workflow.md` for the full submission pipeline — including pip package workarounds, GitHub token permissions, meta.json fixes, CI gates, and the one-skill-per-PR rule.

## Real Results

| Format | Characters | Lines | Behavioral signal |
|---|---|---|---|
| Prose identity block | ~2,200 | ~65 | 0 personality facets, no route logic |
| Compressed DSL | ~1,650 (-25%) | ~11 | 30 personality facets, 5-phase state machine |

## Hermes-Specific Variant (merged from `skill-compression`)

The Hermes-specific compression patterns are now part of this skill. Key references:
- `references/compressed-skills-examples.md` — concrete before/after examples from the 2026-05-14 compression pass
- `references/2026-05-15-soul-authoring-compression.md` — SOUL.md-specific compression with Oracle case study (-33%), PersRubric injection
- `references/soul-md-compression.md` — SOUL.md compression patterns
- `references/iknowkungfu-submission-workflow.md` — Full submission pipeline for the iknowkungfu registry

The six techniques are identical across variants. The only difference is tool references: Hermes uses `patch`, `read_file`, `delegate_task`; the generalized version uses generic terms.

## References

- Proteus Mega-Prompt (Stoltz, 2023) — the original compressed DSL research for LLM prompts
- Hermes Agent SOUL.md format — real-world application of compressed DSL in multi-agent systems (see `hermes-soul-authoring` skill)
- GSD (Get Shit Done) project — spec-driven development with compressed behavioral contracts
- `references/soul-md-compression.md` — SOUL.md-specific compression patterns with Oracle case study (-33%), PersRubric injection, and verification workflow
- `references/iknowkungfu-submission-workflow.md` — Full submission pipeline for the iknowkungfu registry (in `iknowkungfu-contrib` skill)

## Pitfalls

- **iknowkungfu registry frontmatter differs from local.** Local Hermes skills use `platforms` and put `version`/`author`/`tags` at top level. The registry requires `compatibility` (not `platforms`) and those fields nested under `metadata`. When submitting to the registry, restructure the frontmatter accordingly.
