# Team Profile Audit — 2026-05-12

Sample output from a team profile configuration audit. Use this as a template
for structure and signal detection when auditing Hermes profile setups.

## Context

- **Design doc:** `~/Hermes Vault/Hermes/1-Projects/10-Agent Team Setup.md`
  called for 10 role-specific agent profiles with curated skill sets
- **HERMES_HOME:** `~/.hermes/profiles/senna`
- **Profile location:** `$HERMES_HOME/home/.hermes/profiles/`
- The 9 named profiles (architect, coder, debugger, reviewer, foreman, secretary,
  researcher, devops, security, data-analyst) were supposed to have dedicated
  SOUL.md, config.yaml, skills, and IDENTITY.md with assigned roles

## Intended vs Actual

| Intended (design doc) | Actual on disk | Status |
|---|---|---|
| architect | `architect/` | ✓ exists but empty |
| coder | — | ✗ never created |
| debugger | — | ✗ never created |
| reviewer | — | ✗ never created |
| foreman | — | ✗ never created |
| secretary | — | ✗ never created |
| researcher | — | ✗ never created |
| devops | — | ✗ never created |
| security | — | ✗ never created |
| data-analyst | — | ✗ never created |
| — | `swarm1/` | not in design doc |
| — | `swarm10/` | not in design doc |
| — | `swarm11/` | not in design doc |

## Profile Completeness (sampled)

All 4 existing profiles had the same stub configuration:

| Check | architect | swarm1 | swarm10 | swarm11 |
|---|---|---|---|---|
| SOUL.md | ✗ pointer only | ✗ pointer only | ✗ pointer only | ✗ pointer only |
| config.yaml | ✗ | ✗ | ✗ | ✗ |
| skills/ | ✗ | ✗ | ✗ | ✗ |
| IDENTITY Role | Unassigned | Unassigned | Unassigned | Unassigned |
| IDENTITY Specialty | Unassigned | Unassigned | Unassigned | Unassigned |
| .env | ✗ (symlinked) | ✗ (symlinked) | ✗ (symlinked) | ✗ (symlinked) |

## Stale Missions Found

**architect profile (all `executing` since May 9):**

| Mission | Objective | Status | Last Updated |
|---|---|---|---|
| `mission-moxyh0je-jmhyyz` | Create 3D solar system simulator (Three.js) | executing | 2026-05-09T06:21 |
| `mission-moym7nl4-ptnng9` | Swarm orchestrator dispatch (blocked: hermes chat command failed) | executing | 2026-05-09T17:25 |

**swarm1, swarm10, swarm11 (shared mission, all `executing` since May 9):**

| Profile | Mission | Status | Last Updated |
|---|---|---|---|
| swarm1 | `mission-moymbpdx-uj80wa` — Swarm2: solar system sim | executing | 2026-05-09T17:28 |
| swarm10 | `mission-moymbpdx-uj80wa` — Swarm2: solar system sim | executing | 2026-05-09T17:28 |
| swarm11 | `mission-moymbpdx-uj80wa` — Swarm2: solar system sim | executing | 2026-05-09T17:28 |

## Signal Summary

1. **Design doc never operationalized** — 8 of 9 named specialist profiles never
   created. Only `architect` exists as a stub.
2. **Swarm profiles are generic** — `swarm1`/`swarm10`/`swarm11` used as
   parallel workers for a Three.js task, but all have Unassigned roles and no
   role-specific training.
3. **Stale missions** — all missions from May 9 are still `executing`, meaning
   the swarm orchestrator crashed or was never cleaned up.
4. **All profiles are clones** — no profile has dedicated skills, config, or
   SOUL.md. They inherit everything from the parent, making them functionally
   identical regardless of their intended role.
5. **Orchestrator failure detected** — the architect mission log shows
   `Command failed: hermes chat -q ## Swarm Orchestrator Dispatch` indicating
   the sub-agent dispatch mechanism itself failed.
6. **Skill-to-disk gap** — The `hermes-soul-authoring` skill already documents
   compressed DSL SOUL.md templates for all 10 profiles (69% average reduction
   over prose, with PersRubric scores and ROUTE maps). These templates were
   authored as reference material within the skill but the actual SOUL.md files
   were never written to the profile directories. This is the same pattern as
   the design doc: theory exists, execution was skipped.

## Root Cause

The original "prune profiles to be role-specific" step from the design doc was
never executed. The design doc was written, the profile directories were
created (partially), but the actual configuration step — writing SOUL.md files,
assigning identities, curating skill sets, setting up config.yaml — was
skipped.
