---
name: hermes-profile-staleness-audit
description: Read-only audits of Hermes profile directories — activity/staleness verdicts (ACTIVE/DORMANT/STALE/CANDIDATE-FOR-REMOVAL), clone-pair detection, duplicate cron pipelines, live-gateway checks, reclaimable-space estimates, plus feature-fit audits (which profiles should have which MCP servers / plugins / hub skills).
tags: [hermes, profiles, audit, maintenance, disk-space]
version: 1.0.0
---

# Hermes Profile Staleness Audit

Audit a set of `~/.hermes/profiles/<name>` directories and report activity verdicts
with evidence. Default mandate is READ-ONLY — report and recommend, never
delete/move/modify unless the user explicitly asks.

## Verdict scale

- **ACTIVE** — real message traffic in the last few days
- **DORMANT** — sessions exist, quiet for weeks
- **STALE** — never or barely used, no cron jobs
- **CANDIDATE-FOR-REMOVAL** — empty shell or exact duplicate of another profile

## Core procedure

1. **Size**: `du -sh profiles/<p>` plus `du -sh profiles/<p>/* profiles/<p>/.[!.]*` (hidden dirs!) for breakdown.
2. **True activity** — sqlite, NOT mtimes (gateways/cron touch files constantly):
   ```bash
   sqlite3 profiles/<p>/state.db "SELECT datetime(MAX(timestamp),'unixepoch') FROM messages;"
   sqlite3 profiles/<p>/state.db "SELECT COUNT(*) FROM sessions;"
   ```
3. **Cron**: parse `cron/jobs.json` for job names/schedules; missing jobs.json = no scheduled work.
4. **Config sanity**: config.yaml + .env present? `.env` key NAMES only (`grep -oE '^[A-Z_]+='`), never values. Test referenced `*_PATH`/`*_DIR` values with `[ -e ]`, report OK/DEAD only.
5. **Live gateways**: `cat profiles/<p>/gateway.pid` (JSON with `pid`) → `ps -p <pid>`. An unused profile can still burn RAM on a running gateway — stop it before any removal.
6. **Verdict + reclaimable estimate** per profile, compact markdown report.

## Key signals (see references/profile-staleness-audit.md for full recipes)

- **Never-used shell**: state.db ~12K, 0 sessions, `MAX(timestamp)` = none; logs are gateway boot noise only (agent.log ~4.7K / gateway.log ~1.5K / errors.log ~847B).
- **Clone pair**: byte-identical .env key lists AND skills dirs; identical log byte sizes = batch-created, not real use. config.yaml diffs of model/skin/channel are cosmetic. Refinement (2026-07-28): md5-identical .env across N profiles with ~50 NON-empty values = batch-stamped fleet template — report "provisioned but never customized", NOT "missing config". True bare = file absent entirely. A "copy config to the bare profiles" request may turn out to have no bare targets.
- **Duplicate cron pipeline**: same jobs.json content on two profiles = double daily LLM spend, zero disk cost to fix — consolidate onto one profile.
- **Pitfall**: sqlite timestamp column is `timestamp REAL` (unix epoch), NOT `created_at` — `MAX(created_at)` errors.
- **Stock-vs-custom skills**: to tell whether a profile is actually specialized or just a renamed shell, diff its installed skill dirs against `skills/.bundled_manifest`:
  ```bash
  cd profiles/<p>/skills
  find . -name SKILL.md -exec sh -c 'basename $(dirname "$1")' _ {} \; | sort > /tmp/actual.txt
  cut -d: -f1 .bundled_manifest | sort > /tmp/bundled.txt
  comm -23 /tmp/actual.txt /tmp/bundled.txt   # custom skills; empty = 100% stock
  ```
  Empty output + factory-default SOUL.md (~513B, "You are Hermes Agent, an intelligent AI assistant...") = the profile was never specialized, whatever its name implies. Note: profile names can be misleading — e.g. a profile named "architect" had zero architecture skills, only the generic bundled `creative/architecture-diagram` (SVG diagram rendering, not system design).
- **Archive convention**: when the user asks to archive a profile, `mv profiles/<p> profiles/.archived/<p>-$(date +%Y%m%d)` — date-suffix because the same profile name may already exist in `.archived/` from a previous cleanup. A duplicate in `.archived/` is itself a signal the profile keeps getting recreated and should probably be deleted instead of re-archived.

## Report shape

Size table (total, top items, state.db, session count, last message, verdict) →
key findings (pairs, duplicate cron, config sanity) → recommendation table with
per-action reclaimable space and total → "user reviews before any deletion".

## References

- `references/profile-staleness-audit.md` — full command recipes, clone-detection diffs, jobs.json parser, typical reclaimable items with real sizes from a 5-profile audit.
- `references/skill-library-audit.md` — content-level audit of a profile's skill library (empty category dirs, cross-profile duplicates, overlap/merge candidates, staleness). Use when the user asks "audit my skills" rather than "audit my profiles".
- `references/profile-feature-fit-audit.md` — capability-mapping audit: which profiles should have which MCP servers / plugins / hub skills. Covers the fleet-clone-config pattern, yaml-parsing recipes (dict-vs-list normalization), `--source official` hub filtering, codegraph-fit, husk-profile and roster-drift detection. Use when the user asks "which features/tools should each profile have".
