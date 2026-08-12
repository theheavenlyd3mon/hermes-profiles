# Planning Strategies

Different goal types need different planning approaches. Match strategy to task.

## Strategy Templates

### Sequential
Best for: Linear workflows, dependencies
```
1. A (blocks B)
2. B (blocks C)  
3. C (final output)
```
Use when: Each step needs previous step's output

### Parallel
Best for: Independent components
```
Track 1: A1 → A2 → A3
Track 2: B1 → B2 → B3
Merge: Combine A3 + B3
```
Use when: Work can happen simultaneously

### Iterative
Best for: Uncertain requirements, creative work
```
Cycle 1: Draft → Feedback → Revise
Cycle 2: Draft → Feedback → Revise
Cycle N: Until acceptable
```
Use when: Can't get it right first try

### Spike-First
Best for: Technical unknowns
```
1. Spike: Prove feasibility (timeboxed)
2. Decide: Continue or pivot based on spike
3. Execute: Full implementation if spike succeeded
```
Use when: Not sure if approach will work

### Checkpoint
Best for: Long tasks, high stakes
```
1. Milestone A → Validate with human
2. Milestone B → Validate with human
3. Milestone C → Final delivery
```
Use when: Course correction needed mid-flight

## Strategy Selection

| Task characteristic | Recommended strategy |
|---------------------|---------------------|
| Clear steps, dependencies | Sequential |
| Multiple independent parts | Parallel |
| Subjective output (writing, design) | Iterative |
| Technical risk | Spike-First |
| >1 day duration | Checkpoint |
| High stakes, novel | Checkpoint + Iterative |

## Strategy Combinations

Complex tasks often combine strategies:

**Feature development:**
- Spike-First (validate approach)
- Sequential (API → logic → UI)
- Checkpoint (validate after each layer)

**Content creation:**
- Iterative (drafts until good)
- Checkpoint (human feedback per section)

**Migration:**
- Sequential (backup → transform → validate → deploy)
- Checkpoint (human approval before deploy)

## Adapting Strategy

Track which strategies work for which goals:

```
### [Task Type]: [Strategy] → [Outcome]
code/api: Sequential → ✅ consistently works
code/refactor: Parallel → ⚠️ merge conflicts, try Sequential
writing/docs: Iterative → ✅ 2 cycles usually enough
migration/schema: Checkpoint → ✅ essential, never skip
```

When a strategy fails for a task type, record why and try alternative next time.

## Minimum Viable Plan

Not every plan needs every component. Match detail to risk:

| Risk level | Include |
|------------|---------|
| Low | Steps only |
| Medium | Steps + outputs + time estimate |
| High | Steps + outputs + risks + rollback + checkpoints |

Don't over-plan low-risk tasks. Don't under-plan high-risk ones.
