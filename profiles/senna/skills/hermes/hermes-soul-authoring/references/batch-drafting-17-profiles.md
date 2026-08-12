# 17-Profile Batch Drafting — Lessons Learned (2026-06-12)

## Context
Drafted 17 SOUL.md files for a full fleet redesign using 3 parallel subagents. Profiles: 1 top orchestrator (senna), 4 domain orchestrators (code, creative, research, security), 12 workers (finance, knowledge, infra, ue5, media, cyber-red, cyber-blue, business, mlops, homelab, social, communication).

## What Went Right
- Parallel drafting (3 subagents, 5-6 files each) completed in ~2.5 minutes
- Each subagent received full context: profile role, skill list, PersRubric calibration, AVOID/DEFAULTS specifics
- All 17 files produced with correct content and domain-specific anti-patterns

## What Went Wrong

### 1. PersRubric Format Drift
- Subagent 1 used `:` (O2E:75 I:85) — correct
- Subagent 2 used `=` (O2E=40,I=60) — wrong
- Subagent 3 used mixed brace notation (O{O2E:50|I:55}) — wrong
- **Root cause:** Format spec said "use PersRubric" but didn't include a concrete example line
- **Fix:** Always include one fully-written example file in subagent context, not just format description

### 2. Section Structure Drift
- Orchestrators (code) added sub-profile routing to non-existent profiles (debugger, reviewer, tester)
- Workers (finance) included DISCORD section when they don't have Discord bots
- Some workers had ROUTE sections (orchestrator behavior, not worker behavior)
- **Root cause:** The format spec described "orchestrator" and "worker" patterns but subagents interpreted the boundary differently
- **Fix:** Explicitly state which sections are REQUIRED and FORBIDDEN per role type

### 3. Verbosity Drift
- homelab.md: 1,907 chars with verbose prose sections
- media.md: 1,171 chars with tight DSL
- 62% size variance across files that should be ~1,300 chars
- **Root cause:** "Target ~1,300 chars" was a suggestion, not enforced
- **Fix:** Set a hard ceiling (e.g., "under 1,500 chars") and mention it multiple times in the prompt

### 4. Legacy Name References
- Senna's TEAM roster included `oracle:Worker{...}` when oracle was renamed to finance
- **Root cause:** Subagent used the old profile name from the existing SOUL.md it read as reference
- **Fix:** When renaming profiles, explicitly list the name mapping in the subagent context

## Recommended Batch Drafting Protocol

1. **Write ONE reference file first** — draft a single SOUL.md manually (senna or the most complex profile), verify it's correct, then include it as a concrete example in all subagent prompts
2. **Separate orchestrators from workers** — different subagents for different role types to prevent structure drift
3. **Include explicit format spec** — list every section with REQUIRED/FORBIDDEN per role type
4. **Set hard size ceiling** — "under 1,500 chars, no exceptions"
5. **Run consistency pass** — after all subagents complete, check: PersRubric delimiter, section presence, size variance, name references
6. **Include name mapping** — if profiles were renamed, list old→new in the context

## PersRubric Calibration That Worked

| Role Type | High | Low |
|-----------|------|-----|
| Top Orchestrator (senna) | C:Ord(85), C:Dt(85), A:Tr(70) | N:25, E:ES(30) |
| Domain Orchestrator (code) | C:Ord(90), C:SD(85), O:Int(85) | E:ES(20), N:Immod(20) |
| Domain Orchestrator (creative) | O2E(90), O:AI(85), A:Alt(80) | E:ES(25), N:Immod(25) |
| Domain Orchestrator (research) | O:Int(90), C:Cau(85), C:Dt(85) | E:ES(20), N:Immod(20) |
| Domain Orchestrator (security) | C:Cau(90), C:Ord(85) | E:ES(15), O:Adv(25) |
| Worker (finance) | O:Int(85), C:Cau(85), C:Dt(80) | E:W(20), N:Anx(20) |
| Worker (ue5) | C:Ord(90), C:SD(85), O:Int(85) | O:Adv(30), E:ES(20) |
| Worker (knowledge) | C:Ord(90), C:SD(85), O:Int(80) | E:ES(20), N:Immod(20) |
| Worker (infra) | C:Ord(90), C:Cau(85), C:SD(85) | E:ES(20), N:Immod(20) |
| Worker (homelab) | C:Ord(80), C:SD(75) | E:ES(15), N:Immod(15), O2E(50) |

## Size Results

| Profile | Chars | Role |
|---------|-------|------|
| senna | 2,883 | Top orchestrator (large due to 17-profile TEAM roster) |
| code | 1,785 | Domain orchestrator |
| creative | 1,752 | Domain orchestrator |
| research | 1,586 | Domain orchestrator |
| security | 1,673 | Domain orchestrator |
| finance | 1,457 | Worker + autonomous |
| knowledge | 1,242 | Worker |
| infra | 1,350 | Worker + autonomous |
| ue5 | 1,245 | Worker |
| media | 1,171 | Worker |
| cyber-red | 1,388 | Worker (230 skills flagged) |
| cyber-blue | 1,460 | Worker (530 skills CRITICAL flag) |
| business | 1,645 | Worker |
| mlops | 1,728 | Worker |
| homelab | 1,907 | Worker + autonomous |
| social | 1,682 | Worker |
| communication | 1,799 | Worker |

**Average (excluding senna):** 1,511 chars. Target was ~1,300. Acceptable but tighter prompts would get closer.
