# Batch SOUL.md Delegation — Pitfalls & Fixes

When drafting 10+ SOUL.md files in parallel via `delegate_task`, subagents introduce format inconsistencies even with detailed prompts. This documents the patterns and fixes.

## Pitfall 1: PersRubric Delimiter Drift

**Symptom:** Some files use `=` (O2E=40,I:60) while others use `:` (O2E:40 I:60).

**Root cause:** Subagents inherit format from reference examples they find in context. If any example uses `=`, they copy it. Prompt must explicitly state the canonical format.

**Fix:** Add to delegation prompt:
```
PersRubric format: ALWAYS use `:` as delimiter between facet and value.
Use spaces between facets within a group. Use `|` between groups.
Example: O2E:75 I:85 AI:60 E:70|C:85 SE:80 Ord:80
NEVER use `=` or commas between facets.
```

**Post-delivery fix:** One-pass regex in execute_code:
```python
import re
new_line = re.sub(r'(\w+)=', r'\1:', line)  # = → :
new_line = re.sub(r',(?=[A-Z])', ' ', new_line)  # comma → space
new_line = new_line.replace('{', '').replace('}', '')  # remove braces
```

## Pitfall 2: Sub-Profile Routing in Merged Profiles

**Symptom:** A merged profile (e.g., code = coder+debugger+reviewer) includes TEAM entries routing to the old sub-profiles that no longer exist.

**Root cause:** Subagents see "merged from coder+debugger+reviewer" and assume those still exist as routing targets.

**Fix:** Add to delegation prompt:
```
This profile MERGES the old profiles. There are no sub-profiles to route to.
TEAM section should show: {code:Self{Implementation+Debug+Review+Testing}}
ROUTE section should route all tasks to self, not to debugger/reviewer/tester.
```

## Pitfall 3: Legacy Name References

**Symptom:** TEAM section references old profile names (oracle instead of finance, secretary instead of knowledge).

**Root cause:** Subagents reference the source material which uses old names.

**Fix:** Add to delegation prompt:
```
Profile name mapping (use NEW names only):
- oracle → finance
- secretary → knowledge
- devops → infra
- foreman → senna (merged)
- coder/debugger/reviewer → code (merged)
- architect/designer → creative (merged)
- data-analyst/researcher → research (merged)
```

## Pitfall 4: Verbose vs Compressed Inconsistency

**Symptom:** Some files use compressed DSL (IDENTITY: Trait.Trait.), others use verbose prose (## Identity\nTrait, Trait, and more trait...).

**Root cause:** Subagents have different "comfort zones" with DSL. Some compress aggressively, others stay verbose.

**Fix:** Provide one canonical example file in the delegation prompt (e.g., the current senna SOUL.md). Say: "Match this format exactly."

## Pitfall 5: Orchestrator Sections in Worker Files

**Symptom:** Worker files include TEAM, ROUTE, ROUTE_LOOP sections that only orchestrators need.

**Root cause:** Subagents see "this is a profile" and include all sections without distinguishing orchestrator vs worker.

**Fix:** Add to delegation prompt:
```
ORCHESTRATOR profiles (senna, code, creative, research, security) get:
  TEAM, ROUTE, ROUTE_LOOP, HANDOFF, DECISIONS sections

WORKER profiles (all others) get:
  KANBAN, Output Standards sections only. NO TEAM/ROUTE/ROUTE_LOOP.
```

## Post-Delivery Consistency Pass

After receiving all drafted files, run a consistency check:

```python
# Check PersRubric format
for f in files:
    for line in f:
        if 'PersRubric' in line:
            assert '=' not in line, f"{f}: PersRubric uses = instead of :"
            assert '{' not in line, f"{f}: PersRubric has braces"

# Check for legacy names
legacy = ['oracle', 'secretary', 'devops', 'foreman', 'coder', 'debugger', 'reviewer', 'architect', 'designer', 'data-analyst', 'researcher']
for f in files:
    content = read(f)
    for name in legacy:
        # Allow in IDENTITY (describing merge history) but not in TEAM/ROUTE
        assert name not in TEAM_section_of(content), f"{f}: legacy name '{name}' in TEAM"
```

## Recommended Delegation Structure

For 17 profiles, split into 3 parallel batches:
- Batch 1: Top orchestrator + 4 domain orchestrators + 1 key worker (6 files)
- Batch 2: 6 workers (medium complexity)
- Batch 3: 5 workers (simplest, smallest skill catalogs)

Each batch gets the same format spec, legacy name mapping, and orchestrator vs worker rules.
