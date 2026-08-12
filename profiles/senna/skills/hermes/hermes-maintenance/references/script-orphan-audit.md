# Script Orphan Audit — find scripts unused by cron or skills

Verified 2026-08-03 during the fleet migration cleanup (removed 35 stale files: 9 senna/root scripts + 26 gamehub-mod scratch files).

## When to use
User asks "review stale scripts", "what scripts can we delete", or cleanup passes over `~/.hermes/**/scripts/`.

## Hard rule (user preference)
Audit and REPORT first; the user decides deletions. Never delete during the audit pass itself.

## Method

1. **Inventory all script dirs:**
   - `~/.hermes/profiles/*/scripts/` (per-profile; cron scripts resolve here for that profile's gateway)
   - `~/.hermes/scripts/` (root)
   - Skill-bundled copies live INSIDE skills: `~/.hermes/profiles/*/skills/*/*/scripts/`

2. **Build the REFERENCED set from three sources:**
   - **Cron stores**: `profiles/*/cron/jobs.json` — read EVERY profile's store, not just the current one. The `cronjob` tool lists only the current profile's jobs. Extract `script:` fields (no_agent jobs especially).
   - **Skill references**: `grep -rl "<scriptname>" profiles/<p>/skills` (exclude `.curator_backups/`)
   - **Config/SOUL/plugins**: `grep -rl "<scriptname>" profiles/<p>/config.yaml profiles/<p>/SOUL.md profiles/<p>/plugins`

3. **Classify each script:**
   - **IN USE** — referenced by cron or a skill → keep
   - **STALE** — zero references → deletion candidate; list for user with size + one-line purpose
   - **STATE FILE** — runtime state the skill reads/writes by path (`audit_state.json`, `.watchdog_state.json`, `created_roles.json`, `enforcement_policy.md`) → KEEP, not stale
   - **BROKEN REF** — cron job references a script that exists NOWHERE on disk → decision: recreate script or remove job

## Pitfalls

- **Skill-bundled copies vs profile copies differ.** gamehub-mod example: skill `discord-moderation-bot` bundles its own newer `audit_watch.sh` (4.2K) while the cron job runs the profile copy (3.6K). If they differ, the cron may run stale logic. Compare with `cmp -s` before declaring the profile copy redundant.
- **Whole-tree grep times out.** `grep -rl X ~/.hermes` crawls venv/node_modules and hangs (180s timeout hit). Scope to skills/plugins/configs/SOUL only.
- **Missing-script cron jobs can silently "succeed".** A no_agent job whose script file was deleted reports `last_status: ok` under older gateway code (empty stdout = silent run). Verify the file exists on disk; cross-check `profiles/<p>/cron/executions.db` for what actually ran. After a Hermes update, the same job may START erroring (new scheduler returns "Script not found").
- **Cron script resolution**: relative script paths resolve against `HERMES_HOME/scripts/` (= `profiles/<p>/scripts/` for that profile). Absolute paths must stay inside that dir or the run is blocked (`Script path resolves outside the scripts directory`).
- **0-byte file = deletion candidate** by inspection (hermes-desktop-version-check.py was 0B).

## Report shape
Three groups: IN USE (no action), STALE candidates (size + purpose), BROKEN refs (need decision). Total the sizes so the user sees the payoff. Ask before deleting.
