# Profile Audit Workflow

When the user asks "what profiles do we have" or "which ones should we remove", use this systematic approach.

## Step 1: List All Profiles

```bash
hermes gateway list
```

This shows every registered profile and whether its gateway is running (PID) or stopped.

## Step 2: Identify Discord Bot Profiles

```bash
ls /Users/<user>/Library/LaunchAgents/ai.hermes.gateway-*.plist
```

Profiles with a launchd plist have their own Discord bot. These are typically off-limits for removal unless the user explicitly says otherwise.

## Step 3: Collect Per-Profile Metadata

For each profile, gather:

```bash
# SOUL.md — first 5 lines (persona/identity)
head -5 /Users/<user>/.hermes/profiles/<name>/SOUL.md

# config.yaml — model and platform config
cat /Users/<user>/.hermes/profiles/<name>/config.yaml

# Disk usage
du -sh /Users/<user>/.hermes/profiles/<name>/
```

## Step 4: Classify Each Profile

| Category | Criteria | Action |
|----------|----------|--------|
| Active Discord bot | Has launchd plist + running PID | Leave alone |
| Custom persona | SOUL.md has unique IDENTITY/personality rubric | Consider keeping |
| Generic boilerplate | SOUL.md is default "You are Hermes Agent..." | Strong delete candidate |
| No SOUL.md | Profile dir exists but empty/minimal | Strong delete candidate |

## Step 5: Present Summary

Format: numbered list with profile name, disk size, SOUL.md status (custom vs generic), model, and a one-line purpose. Group into "has Discord bot" and "no Discord bot". End with a recommendation.

## Common Patterns

- **Council/Explorer/Librarian/Designer**: Often created as experiments, left with generic SOUL.md. Usually safe to delete.
- **Data-Analyst/Debugger/DevOps/Reviewer/Security**: Often have custom SOULs with real specializations. These CAN be useful but Senna can route to subagents for the same work. Keep only if the user wants them as independent Discord bots.
- **Default profile**: Usually empty or minimal. The root `~/.hermes/` config serves as the effective default.

## Decision Framework

Ask the user:
1. Do you want these as independent Discord bots with their own channels? (If no → delete)
2. Do they have custom personas worth preserving? (If yes → keep or migrate SOUL to a skill)
3. Are they eating meaningful disk? (Usually <100MB total for non-bot profiles)

Before deleting, check if the profile has unique skills, plugins, or memory worth migrating to the active profile.
