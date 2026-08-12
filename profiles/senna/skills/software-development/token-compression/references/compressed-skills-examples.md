# Compressed Skills — Before/After Examples

Concrete results from the 2026-05-14 compression pass. Each skill's behavioral headers were replaced with a compressed DSL block while operational instructions remained in prose.

## systematic-debugging

**Before:** Overview (6 lines prose), Iron Law (3 lines), When to Use (20 lines with lists), Red Flags (20 lines), Rationalizations table (8 rows), Quick Reference table (6 rows) — ~2,120 chars of behavioral prose.

**After:** Single compressed header block — ~805 chars (62% reduction on headers).

```
IDENTITY: RootCauseHunter{FixAtSource,NoSymptomPatches}. Law=NoFixW/OInvestigation.
Law: NO PRODUCTION CODE WITHOUT ROOT CAUSE INVESTIGATION FIRST.
WHENUSE: {AnyTech:TestFailures,Bugs,Unexpected,Perf,Builds,Integration}.
  ESPECIALLY:{TimePressure,ObviousFix,MultipleFails,PreviousFixFailed,UnclearIssue}.
  NoSkip:{SeemsSimple,InHurry,SomeoneWantsNow}→ProcessStillRequired.
REDFLAGS: {QuickFixNow||JustTryChange||MultiChangesWTest||...}→Phase1Rerun. {3+FixesFailed}→QuestionArchitecture.
RATIONALIZATIONS: SimpleIssue→RootCauseToo|Emergency→SystematicFaster|TryFirst→SetsPattern|...
QUICKREF: Phase1(Read→Reproduce→CheckChanges→GatherEvidence→TraceFlow)→Phase2(...)→...
```

**Kept in prose:** All 4-phase debugging instructions, code blocks, shell commands.

## test-driven-development

**Before:** Overview (4 lines), Iron Law (7 lines including sub-bullets), When to Use (14 lines), Red Flags (12 items), Rationalizations table (11 rows) — ~1,800 chars of behavioral prose.

**After:** Single compressed header block — ~720 chars (60% reduction on headers).

```
IDENTITY: TestFirst{RedGreenRefactor}. Law=NoCodeWithoutFailingTest.
Law: DELETE any code written before its test.
WHENUSE: Always{NewFeatures,BugFixes,Refactoring,BehaviorChanges}.
  Exceptions:{ThrowawayProto,GeneratedCode,ConfigFiles}→AskUserFirst.
REDFLAGS: {CodeBeforeTest||TestAfterImpl||...}→DeleteCode→RestartTDD.
RATIONALIZATIONS: TooSimple→SimpleBreaksTest30sec|TestLater→PassingImmediatelyProvesNothing|...
```

**Kept in prose:** RED-GREEN-REFACTOR cycle, code examples, verification checklist.

## foreman-orchestration

**Before:** Overview (10 lines of prose describing the cron loop), Pitfalls section (10 detailed bullet points) — ~800 chars.

**After:** Compressed IDENTITY + PITFALLS — ~350 chars (56% reduction).

```
IDENTITY: CronPoller{Autonomous,NoUserUnlessEscalated}. Loop: ReadBoard→HandleReviews{Clean→Done,NotClean→SpawnCycle}→DispatchReady→EscalateThreshold→Report→TerminateAllResolved.
PITFALLS: OneCronPerBoard{NotPerProject}|MAX_RETRIES≥3|Interval≥10m{WorkersNeedTime}|...
```

**Kept in prose:** Architecture diagram, setup instructions, polling loop pseudocode, escalation rules, metadata schema.

---

## Pattern summary

| Skill | Header chars before | Header chars after | Reduction |
|---|---|---|---|
| systematic-debugging | ~2,120 | ~805 | 62% |
| test-driven-development | ~1,800 | ~720 | 60% |
| foreman-orchestration | ~800 | ~350 | 56% |