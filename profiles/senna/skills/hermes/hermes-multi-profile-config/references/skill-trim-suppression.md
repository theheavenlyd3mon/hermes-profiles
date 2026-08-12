# Per-Profile Skill Trimming — Suppression Mechanism (verified 2026-07-28)

## Why plain deletion fails

`hermes update` re-seeds bundled skills into EVERY profile:
`profiles.seed_profile_skills(profile_dir)` → subprocess → `tools/skills_sync.sync_skills()`
with `HERMES_HOME=<profile_dir>`. Any bundled skill folder you `rm -rf` from a
profile's `skills/` comes back on the next update.

## The two supported levers

1. **Per-profile suppression list (surgical — use this for trims)**
   - File: `<profile>/skills/.curator_suppressed` (one skill name per line).
   - skills_sync reads it (`_read_suppressed_names()`) and skips re-seeding
     those names. This is the same file the curator writes when it prunes
     built-ins (`curator.prune_builtins: true` is the default).
   - Trim procedure per unwanted skill folder:
     a. `mkdir -p <profile>/skills/.archive && mv <profile>/skills/<name> <profile>/skills/.archive/`
     b. append `<name>` to `<profile>/skills/.curator_suppressed`
   - Recovery: remove the line, move the folder back. Nothing is destroyed.

2. **`.no-bundled-skills` marker (nuclear — rarely right)**
   - Empty file at profile ROOT (written by `hermes profile create --no-skills`).
   - Skips ALL bundled seeding for that profile forever, including future new
     bundled skills. Manual `hermes skills install` still works.
   - Rejected for routine trims: blocks improvements you didn't evaluate.

## Notes

- Category folders (e.g. `apple/`, `smart-home/`, `social-media/`) are seeded
  wholesale; suppress by the folder's skill names as seeded.
- The curator ALSO auto-archives long-unused built-ins (stale 30d / archive 90d,
  usage telemetry from first sighting) — manual suppression is for immediate,
  deliberate trims the curator hasn't reached yet.
- Verify after next `hermes update`: suppressed folders should stay in
  `.archive/` and not reappear in `skills/`.
