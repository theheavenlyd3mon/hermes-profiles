# SOUL.md Compression — Patterns & Case Study

## Oracle Profile (2026-05-21)

**Before:** 1,961 chars, 34 lines, prose-only SOUL.md
**After:** 1,315 chars, ~12 lines, compressed DSL (-33%)

### What was compressed

| Section | Technique | Example |
|---|---|---|
| Identity | DSL encoding | `Oracle{MarketAnalyst,TrendForecaster}. DeduceKeyDetails{VastData}. NOT{FinancialAdvice,TradeExecution,Guarantees}` |
| Style | Semantic normalization | `Data>Narrative. DryHumor=Straight. Intuition→FlagExplicitly{ExplainReasoning}` |
| Avoid | Arrow conditionals | `EmotionalFraming{FearGreed}. FalseCertainty→AlwaysProbFrame. PretendKnow→SayInsufficientSignal` |
| Defaults | DSL encoding + arrow chains | `SignalFirst→LeadFinding→ThenEvidence. Corrected→Ack→Diagnose→Fix→Persist` |
| Decisions | Structural compression | `Decide{TrendAnalysis,PatternID,ProbAssessment,SignalExtract}. Escalate→Senna{...}` |
| Quality Gates | Kept prose (operational checklist) | `[ ] KeyFindingUpFront? EvidenceCited? ProbAssigned?` |

### What stayed prose

- Quality Gates — checklist items are operational, not behavioral
- Section headers (IDENTITY, STYLE, etc.) — human-parseable anchors

### Key pattern: PersRubric injection

The compressed SOUL.md gained 30 personality facets (NEO-PI-R) that were absent in prose:

```
PersRubric(NEO-PI-R,0-100): O2E:85 I:90 AI:80 E:25 Adv:50 Int:95 Lib:60|C:90 SE:85 Ord:80 Dt:95 AS:80 SD:90 Cau:90|E:20 W:55 G:25 A:50 AL:45 ES:15 Ch:30|A:60 Tr:55 SF:50 Alt:70 Comp:75 Mod:65 TM:60|N:20 Anx:20 Ang:15 Dep:15 SC:50 Immod:15 V:20
```

This is more behavioral signal in fewer tokens than the prose version ever had.

### SOUL.md compression rules

1. **Identity line stays human-parseable** — don't over-compress the first line
2. **Style/Avoid/Defaults → full DSL** — these are pure behavioral rules
3. **Decision Authority → structural compression** — `Decide{X}. Escalate→Y{Z}`
4. **Quality Gates → prose or checkbox** — operational, not behavioral
5. **PersRubric → always include** — 30 facets in ~200 chars is efficient
6. **Section headers → keep** — IDENTITY, STYLE, AVOID, DEFAULTS, DECISIONS, GATE

### Verification

After compressing a SOUL.md, smoke test with:
```bash
hermes --profile <name> chat -q "What's your role?" -Q
```

The agent should parse the compressed DSL and articulate its identity correctly. If it can't, the compression is too aggressive.
