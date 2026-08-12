# Hub install recipes & vetting (learned 2026-08-04)

## skills.sh identifiers don't install directly

`hermes skills install skills-sh/<owner>/<repo>/<skill>` AND `<owner>/<repo>/<skill>`
both fail with "Could not fetch from any source" — the search-index entry is a
pointer, not a fetchable path. Working recipe:

1. Get the repo's default branch (may be `master`, not `main`):
   `curl -s https://api.github.com/repos/<owner>/<repo> | grep default_branch`
2. Find the SKILL.md path (skills may sit under `plugins/...`, `skills/...`,
   or `skills/.experimental/...`):
   `curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1" | grep -o '"path": "[^"]*SKILL.md"'`
3. Install the raw URL:
   `hermes skills install "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>/SKILL.md" -y`

Files land uncategorized at `<profile>/skills/<name>/` — `mv` them under a
category folder if you keep a categorized library. Reference-file siblings in
the source repo come along automatically.

## Vetting a hub skill before fleet rollout

1. Install into the orchestrator profile first — the built-in scanner runs on
   install and prints a verdict (SAFE / findings).
2. Read the files yourself:
   `grep -rinE "ignore (all )?previous|exfiltrat|webhook|base64 -d|eval\(|curl [^ ]*http" <skill-dir>`
   A hit on "system prompt" may be benign iOS permission-dialog prose — read
   the line before judging.
3. Only then `cp -R` into worker profiles.

Watch for clawdbot-era metadata (`configPaths` pointing at `~/Clawic/...`) —
inert in Hermes, but a provenance tell that the skill was authored for another
framework (see the framework-specific caveat in SKILL.md).
