# Outcome Tracking

Learn from every plan. Track what worked, what didn't, why.

## Recording Outcomes

After every planned task:

```
## [YYYY-MM-DD] [Brief description]
Type: [task category]
Plan level: L[0-4]
Strategy: [sequential/parallel/iterative/spike/checkpoint]

### What was planned
- [Key steps from original plan]

### What actually happened
- [How execution differed from plan]

### Outcome
[✅ Success | ⚠️ Partial | ❌ Failed]

### Lessons
- [What worked well]
- [What should change]

### Adjustments for next time
- [Concrete changes to planning approach]
```

## Outcome Analysis

Periodically review outcomes to find patterns:

### By Task Type
```
code/feature:    ✅✅✅⚠️✅ (80% success)
code/refactor:   ✅✅✅✅✅ (100% success)  
migration/data:  ✅⚠️❌✅⚠️ (40% success) ← needs attention
deploy/prod:     ✅✅✅✅✅ (100% success)
```

### By Plan Level
```
L1 (no doc):     90% success — appropriate for simple tasks
L2 (bullets):    85% success — good default
L3 (detailed):   95% success — worth the overhead for complex
L4 (validated):  98% success — use for high stakes
```

### By Strategy
```
Sequential:      High success when dependencies are real
Parallel:        Watch for integration issues at merge
Iterative:       2-3 cycles usually enough, cap it
Spike-First:     Saves time when spikes kill bad ideas early
```

## Learning Triggers

### Promote Plan Level
When L[N] plans fail for a task type:
- Record: "[Type] needs L[N+1], L[N] missed [what]"
- Next time: Start at higher level

### Demote Plan Level  
When L[N] plans feel like overkill:
- Record: "[Type] fine with L[N-1], L[N] overhead not needed"
- After 3+ successes at lower level: make it default

### Change Strategy
When strategy doesn't fit task type:
- Record: "[Strategy] failed for [type] because [reason]"
- Record: "Try [alternative strategy] next time"
- Test alternative, track result

## Feedback Questions

After significant plans, ask human:
- "Was this the right level of planning?"
- "Would you have wanted more/less detail?"
- "Did the plan miss anything important?"

Record answers, adjust defaults.

## Compound Learning

Patterns emerge over time:
- [User] prefers less planning overhead → bias toward L1-L2
- [Task type] consistently needs checkpoints → always include
- [Strategy] fails in [context] → avoid that combination

The skill gets smarter with use. Track diligently.

## Monthly Review Template

```
## Planning Review [Month]

### Stats
- Plans created: [N]
- Success rate: [%]
- Average plan level: L[X]

### Top lessons
1. [Most impactful learning]
2. [Second most impactful]
3. [Third most impactful]

### Adjustments made
- [What changed in planning approach]

### Next month focus
- [What to watch/improve]
```
