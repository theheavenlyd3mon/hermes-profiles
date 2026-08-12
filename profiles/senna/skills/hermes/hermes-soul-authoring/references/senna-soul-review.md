# Senna SOUL.md — Critical Review (May 2026)

This records the actual weaknesses discovered during a real SOUL.md review session. Use as a case study for future audits.

## Senna's Original Sections

Current sections: Identity, Role, Voice and Tone, Principles (×5), Handoffs, Quality Gate (Personal), Collaboration Note, Closing line.

Missing vs required standard: Team Roster, Collaboration Matrix, Decision Authority, operational quality gates, Team Camaraderie.

## Concrete Failures Linked to SOUL.md Gaps

| Failure | Root Cause in SOUL.md |
|---------|----------------------|
| Chinese response to English-speaking user | No language guardrail in Voice/Tone or Principles |
| Kanban tasks with wrong file paths | No "verify before acting" principle |
| Kanban tasks with empty bodies | No quality gate for task completeness |
| "You are enough" vs handoff contradiction | Identity tension never resolved |

## Specific Section Critiques

### Identity
Entirely temperament-based with no operational boundary. Compare Foreman: "You do not write production code yourself" — that's a hard boundary.

### Role
"You handle daily life, casual exploration, and lighter work" — inaccurate to what Senna actually does (GitHub setup, kanban orchestration, auth troubleshooting, code review). Creates expectation of casualness that conflicts with critical tasks.

### Principles (×5)
Missing: verification principle, language matching, error recovery, prioritization.

### Quality Gate (Personal)
Three questions, all emotional. No operational check.

### Collaboration Note
Only lists three examples (security, architecture, code review) → implies everything else is Senna's scope. Misleadingly narrow.

## What the Team Profiles Do Better

- Foreman: "You do not write production code yourself" — clear negative boundary.
- Coder: "No production code without a failing test first" — iron law, not suggestion.
- All team profiles: Decision Authority table (decide vs escalate), Quality Gates with [ ] checklists, Collaboration Matrix with specific teammate interactions.

## Recommended Fixes

1. Add language guardrail to Voice and Tone.
2. Add Team Roster listing all 11 profiles.
3. Add Decision Authority section.
4. Add operational checks to Quality Gate.
5. Add "verify before dispatching" to Principles.
6. Add error recovery protocol.
7. Resolve "you are enough" / handoff tension explicitly.
