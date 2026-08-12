---
name: hermes-skills-hub
description: Use the Hermes Skills Hub via the local CLI (hermes skills search/inspect/install) — not web search, not the MCP iknowkungfu registry. Covers the command surface, result interpretation, the framework-specific caveat, and inspect-before-install discipline.
triggers:
  - "skills hub"
  - "search the skills hub"
  - "hermes skills"
  - "find a skill for"
  - "discord skills"
  - "browse skills"
version: 1.0.0
author: Senna
license: MIT
---

# Hermes Skills Hub

The "Skills Hub" is primarily a **local CLI subsystem** (not the MCP iknowkungfu registry), with a **docs web front-end** at https://hermes-agent.nousresearch.com/docs/skills that renders the same index. Know which one the user means (see below).

## The correction that matters

When the user says "search the skills hub" / "Hermes skills hub" / "find a skill for X", they mean:

```bash
hermes skills search <term>
```

NOT the MCP `iknowkungfu` registry (`mcp__iknowkungfu__search`) — that is a separate small registry (9 skills by samuelgudi).

There IS a web front-end: https://hermes-agent.nousresearch.com/docs/skills renders the same hub index (filter-counts bar + built-in catalog by category). When the user says "the skills that are here" / "the Hermes Skill Hub" / "Nous portal / Nous Research documents", they often mean THAT page, not `hermes skills browse` (verified 2026-08-03: user pointed at the URL after I gave the CLI rundown). Page anatomy in `references/docs-skills-page.md`. Division of authority: CLI = what's installable, docs page = what's built-in/optional per source.

## Command surface

```bash
hermes skills search <term>          # query skills.sh + clawhub + GitHub registries
hermes skills inspect <id>           # preview a skill (SKILL.md + files) before installing
hermes skills install <id>           # install into the ACTIVE profile (see targeting below)
hermes skills browse                 # paginated browse of all available skills
hermes skills list                   # installed skills
hermes skills check / update         # update installed hub skills
hermes skills audit                  # re-scan installed hub skills
hermes skills uninstall <id>
```

Search output columns: Name, Description, Source (skills.sh / clawhub / github), Trust (community), Identifier (e.g. `skills-sh/steipete/clawdis/discord`, `clawhub/discord-communities`). Use the **Identifier** with `install` / `inspect`.

## Ambiguous short names

`search` / `inspect` / `install` by short name can hit "Multiple skills named X found" (e.g. comfyui, imagegen, peer-review, midjourney each have 2-3). Resolve with the full Identifier from the search table; clawhub entries often resolve with a `clawhub/<short>` prefix (e.g. `clawhub/comfyui`). Short-name inspect may also resolve to a different source than intended — confirm the Source column in the ambiguity table before installing.

## Installing into a specific (non-active) profile

`hermes skills install` always targets the ACTIVE profile — `HERMES_PROFILE=<name>` does NOT retarget it (verified 2026-07-28: install with HERMES_PROFILE=finance landed in senna). To install into another profile, point HERMES_HOME at the profile dir:

```bash
HERMES_HOME=~/.hermes/profiles/<name> hermes skills install <id> -y
```

The skill lands at `<profile>/skills/<category>/<skill>/` — verify with `find`, and check the same install didn't also pollute the active profile (clean up if it did). Note a hub skill may turn out to be already bundled in the target profile (e.g. axolotl ships under mlops/training/) — "already installed" is a pass, not a failure.

## ⚠️ Framework-specific caveat (install discipline)

Most hub results are community-authored for **other agent frameworks** — Clawdbot, OpenClaw, Claude Code, etc. They reference those frameworks' slash-command / API idioms, which do **not** match Hermes's native tool/action model (e.g. Hermes uses the `hermes-discord` toolset + `discord_admin` actions, not another bot's DSL).

**Rule: always `hermes skills inspect <id>` before installing into a Hermes profile.** If the skill's body assumes a non-Hermes framework, either skip it or adapt its steps to Hermes-native tools. Installing a framework-specific skill blindly can inject conflicting instructions into the profile's SOUL/context.

## CLI quirks (learned 2026-08-03)

- **Tables truncate.** `browse`/`search` truncate Name and Identifier (~13 chars) regardless of terminal width; `COLUMNS=240` helps but some names still end in `…`. Get full names from `hermes skills search <term>` rows, or inspect directly.
- **awk parsing.** Row shape is `│ 1 │ name │ desc ...` so with `-F'│'` the NAME is field **$3** — field $2 is the row number. Strip trailing `…` before matching. (First attempt grabbed the numbers column — wrong column, wrong diff.)
- **Per-source browse-header counts are misleading** (page-count shaped: "611 skills loaded, page 1/611"). Authoritative per-source totals live on the docs page count bar at https://hermes-agent.nousresearch.com/docs/skills — see `references/docs-skills-page.md` for observed values.
- **`--source official` and `--source well-known` resolve to the SAME set** — the 111 Nous first-party optional skills. Don't browse both expecting different content.
- **Official identifier quirk:** browse/search may print a shortened identifier (e.g. `official/mlops/stable-diffusion`) that `inspect` REJECTS. Use the full skill name in the identifier (`official/mlops/stable-diffusion-image-generation`). If inspect fails, search the full name and try the name spelled out.

## When to use the hub vs built-in skills

- Built-in / profile-authored skills (e.g. `discord-server-management`) are purpose-built for Hermes — prefer those first.
- Use the hub to discover capabilities not already in your skill library (e.g. `discord-communities` for guild management, `discord-channel-auditor` for auto-maintaining an info channel).

## References

- `references/discord-skills-search.md` — condensed results of `hermes skills search discord` (25 hits) with the relevant ones flagged and the framework caveat applied.
- `references/docs-skills-page.md` — anatomy of the docs web front-end (/docs/skills): counts bar, built-in catalog by category, plus framework-caveat evaluation notes for creative-writing and image-generation hub searches.
- `references/hub-install-recipes.md` — working install recipe for `skills-sh/...` identifiers (they don't fetch directly; resolve SKILL.md path via GitHub tree API, install the raw URL) + hub-skill vetting checklist before fleet rollout.
