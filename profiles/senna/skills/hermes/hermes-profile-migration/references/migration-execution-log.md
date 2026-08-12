# Migration Execution Log — 17-Profile Mac Redesign (2026-06-12)

## What Happened

Migrated from 14 old profiles to 17 new domain-based profiles. Full redesign: new SOUL.md files, new Discord layout, Kanban coordination, skill curation.

## Phases Executed

| Phase | Status | Notes |
|---|---|---|
| 1. Backup | ✅ | Tar.gz of ~/.hermes/ |
| 2. Create profiles | ✅ | 17 new + 4 cyber-blue sub-profiles created with --no-skills |
| 3. Deploy SOUL.md | ✅ | 21 files deployed (17 main + 4 cyber-blue sub-profiles) |
| 4. Seed skills | ⏳ | Documented in skill-curation-strategy.md, execution pending |
| 5. Pin skills | ⏳ | Pending |
| 6. Init kanban | ✅ | Board `main` already existed |
| 7. Remap cron | ✅ | 9 old jobs removed, 3 remaining |
| 8. Update Discord | ✅ | 6 categories renamed, 1 created, 9 topics updated, 1 archived |
| 9. Gateway config | ⏳ | Pending — bot token remapping needed |
| 10. Restart & verify | ❌ | Blocked — can't restart gateway from inside gateway process |
| 11. Archive old | ✅ (SOUL.md) | 9/11 old profiles archived to ~/soul-archive/ (oracle + designer had no SOUL.md) |

## Session: 2026-06-15 — SOUL.md Archive + Auxiliary Provider Fix

### What was done
1. Archived 9 SOUL.md files from old profiles to `~/soul-archive/`:
   - architect, coder, data-analyst, debugger, devops, foreman, researcher, reviewer, secretary
   - oracle and designer had no SOUL.md — skipped
2. Fixed auxiliary provider error: `auxiliary.title_generation` and `auxiliary.vision` were set to `provider: nous` with no `NOUS_API_KEY`. Switched both to `provider: xiaomi`, `model: mimo-v2.5-pro`, `base_url: https://token-plan-sgp.xiaomimimo.com/v1`.

## Session: 2026-06-15 — Profile Cleanup

### What was done
1. Verified `~/soul-archive/` had 9 archived SOUL.md files from prior session
2. `designer` profile was already removed (renamed to `creative`) — SOUL.md was lost before archival
3. Removed 10 deprecated profiles from `~/.hermes/profiles/`:
   - architect, coder, debugger, reviewer, data-analyst, researcher, secretary, devops, foreman, general
4. Confirmed `ue5` profile doesn't exist on Mac (UE5 dev is on Windows PC with separate Hermes)
5. Final state: 20 profiles remain (17 base + 3 cyber-blue sub-profiles)

### Key lesson
**Archive SOUL.md before renaming/deleting profiles, not after.** The designer SOUL.md was lost because the profile was renamed to creative before the archival step ran. Phase 11 should happen immediately after backup, not as a week-later cleanup.

### Commands used
```bash
# SOUL.md archival
mkdir -p ~/soul-archive
for p in architect coder debugger reviewer data-analyst researcher foreman secretary devops; do
  cp ~/.hermes/profiles/$p/SOUL.md ~/soul-archive/${p}.SOUL.md
done

# Auxiliary provider fix
hermes config set auxiliary.title_generation.provider xiaomi
hermes config set auxiliary.title_generation.model mimo-v2.5-pro
hermes config set auxiliary.title_generation.base_url https://token-plan-sgp.xiaomimimo.com/v1
hermes config set auxiliary.vision.provider xiaomi
hermes config set auxiliary.vision.model mimo-v2.5-pro
hermes config set auxiliary.vision.base_url https://token-plan-sgp.xiaomimimo.com/v1
```

## Issues Encountered (Original Migration, 2026-06-12)

### 1. Subagent File Isolation
Subagents writing to `~/Downloads/soul-drafts/` created files in their own sandbox, not the parent terminal's filesystem. Had to rewrite all 21 SOUL.md files directly using `write_file` tool in parent context.

**Lesson:** Never delegate file creation for deployment artifacts. Write them directly.

### 2. Discord API Endpoint Gotcha
Initial PATCH calls used `PATCH /guilds/{guild}/channels/{channel_id}` — returned 404 despite the bot having MANAGE_CHANNELS permission and GET working on the same channel.

**Root cause:** Discord REST API uses different endpoints for create vs modify:
- POST (create): `/guilds/{guild}/channels`
- PATCH (modify): `/channels/{channel_id}`

**Fix:** Changed all PATCH calls to use `/channels/{channel_id}`. All subsequent calls succeeded.

### 3. Gateway Restart Blocked
`hermes gateway restart` and `hermes gateway stop` both refused to execute from inside the running gateway process. User must restart from a separate terminal.

### 4. PersRubric Format Drift
Parallel subagents produced inconsistent PersRubric formats:
- Some used `:` (O2E:75 I:85) — correct
- Some used `=` (O2E=40,I=60) — incorrect

**Fix:** Ran a consistency pass with execute_code to standardize all files to `:` format.

### 5. Code SOUL.md Had Sub-Profile Routing
The code profile's TEAM section referenced debugger/reviewer/tester as separate profiles. But code IS the merged profile — it handles all three internally.

**Fix:** Replaced TEAM with `{code:Self{Implementation+Debug+Review+Testing}}` and updated ROUTE to self-referential.

### 6. Senna Had Oracle Duplicate
Senna's TEAM referenced both `finance` and `oracle`. Oracle was renamed to finance — duplicate.

**Fix:** Removed the oracle entry.

### 7. Auxiliary Provider Misconfiguration (2026-06-15)
After migration, `auxiliary.title_generation` and `auxiliary.vision` still pointed to `provider: nous` with no `NOUS_API_KEY` set. Caused title generation failures on every session.

**Fix:** Switched both to xiaomi/mimo-v2.5-pro with explicit base_url. Auxiliary services don't inherit base_url from main model config — must set it explicitly.

## Files Produced

- `~/soul-archive/*.SOUL.md` (9 files) — archived SOUL.md from old profiles
- Implementation plan, skill curation strategy, kanban board design (in senna cache)

## Discord Changes

| Change | Before | After |
|---|---|---|
| Category | RESEARCHER | RESEARCH |
| Category | CODER | CODE |
| Category | ARCHITECT | CREATIVE |
| Category | SECRETARY | KNOWLEDGE |
| Category | FOREMAN | INFRA |
| Category | ORACLE | FINANCE |
| Category | (new) | SECURITY |
| Channel | (new) | #security-ops |
| Channel | #architecture | Archived (moved to pos 99) |
