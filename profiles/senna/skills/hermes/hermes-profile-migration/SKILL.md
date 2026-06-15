---
name: hermes-profile-migration
description: Execute a multi-profile Hermes migration — create profiles, deploy SOUL.md, seed skills, pin critical skills, remap cron, update Discord, restart gateway. Covers rollback strategy and validation.
version: 1.1.0
author: Senna / Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [migration, profiles, multi-agent, fleet, deployment]
    related_skills: [hermes-soul-authoring, hermes-agent, profile-bootstrapping, hermes-maintenance, gateway-fleet-ops]
---

# Hermes Profile Migration

Execute a coordinated migration from an old set of profiles to a new one. Covers the full lifecycle: backup → create → deploy → seed → pin → remap → update Discord → restart → verify → cleanup.

## When to Use

- Renaming profiles (oracle → finance, secretary → knowledge)
- Merging profiles (coder + debugger + reviewer → code)
- Splitting profiles (security → cyber-red + cyber-blue-*)
- Adding new profiles to an existing team
- Restructuring Discord channels alongside profile changes

## Prerequisites

- SOUL.md files drafted for all new profiles (see hermes-soul-authoring)
- Skill-to-profile mapping documented
- Discord server layout planned
- Bot token assignments decided
- Kanban board design documented

## Migration Phases

### Phase 1: Backup (5 min)
```bash
tar -czf ~/Desktop/hermes-backup-pre-migration-$(date +%Y%m%d).tar.gz ~/.hermes/
hermes cron list > /tmp/cron-jobs-pre-migration.txt
hermes profile list > /tmp/profiles-pre-migration.txt
```
**Rollback point.** Everything below can be reverted from this backup.

### Phase 2: Create Profiles (10 min)
```bash
for profile in <list>; do
  hermes profile create "$profile" --no-skills
done
```
Use `--no-skills` to prevent bundled skill bloat. Seed skills selectively in Phase 4.

### Phase 3: Deploy SOUL.md (5 min)
```bash
for profile in <list>; do
  cp "$SOUL_DIR/$profile.md" ~/.hermes/profiles/$profile/SOUL.md
done
```
Write SOUL.md files in the parent terminal context, NOT via subagents (see subagent-file-isolation reference in hermes-soul-authoring).

### Phase 3.5: API Key Audit & .env Deployment (10 min)

**Do NOT copy every possible key into every profile.** Audit what each profile actually needs.

**Audit process:**
1. Read each profile's `config.yaml` → `platform_toolsets.cli` list
2. Map toolsets to key requirements (see table below)
3. Ignore skill file references — builtin catalog skills mention dozens of services that the profile doesn't use
4. Group profiles by LLM provider (Xiaomi vs OpenRouter) for key distribution

**Toolset → Key mapping:**

| Toolset | Key needed? | Notes |
|---------|-------------|-------|
| `image_gen` | No | FAL via Nous subscription |
| `browser` | No | Browserbase via Nous subscription |
| `spotify` | Yes | `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI` |
| `discord` | Yes | `DISCORD_BOT_TOKEN` (unique per bot) |
| `file`, `terminal`, `skills`, `web`, `vision` | No | Internal or Nous-managed |
| `fabric`, `memory`, `kanban`, `delegation`, `todo` | No | Internal to Hermes |
| `messaging` | Depends | Platform-specific (Telegram needs bot token if used) |
| `cronjob`, `session_search` | No | Internal |

**LLM provider keys (always needed):**
- `XIAOMI_API_KEY` + `XIAOMI_BASE_URL=https://token-plan-sgp.xiaomimimo.com/v1` — for profiles on mimo-v2.5
- `OPENROUTER_API_KEY` — for profiles on free OpenRouter models (owl-alpha, deepseek-v4-flash)

**Common mistake:** Adding keys for services referenced in builtin SKILL.md files (Linear, Notion, HuggingFace, W&B, Together, Anthropic, OpenAI) that the profile never actually uses. The toolsets tell the truth, not the skill files.

**Template approach:** Create a single `template.env` in `~/Documents/` with only the keys the fleet actually uses. User fills in values once, then distribute to profiles. See `references/env-key-distribution.md`.

### Phase 4: Seed Skills (15 min)
Per-profile skill seeding. See skill-curation-strategy or equivalent document.
Key: don't dump all root skills into every profile. Seed domain-specific skills only.

### Phase 5: Pin Critical Skills (5 min)
```bash
for skill in <list>; do
  hermes --profile <name> curator pin "$skill"
done
```
Pin all core skills so the auto-curator never archives them.

### Phase 6: Initialize Kanban (5 min)
```bash
hermes kanban init
hermes kanban boards create main --name "Main"
hermes kanban boards switch main
```

### Phase 7: Remap Cron Jobs (10 min)
```bash
hermes cron list
hermes cron update <job_id> --profile <new_profile>
```
Map old profile names to new ones. Most cron jobs deliver to Discord channels by ID (stable), but profile references need updating.

### Phase 8: Update Discord (10 min)
Rename categories and channels in place (preserves message history). Create new channels for new profiles. Update channel topics with @mention guidance.

**Bot-to-channel reassignment (critical for token reuse):** When a profile is renamed and reuses the old bot token, the bot retains access to all its previous Discord channels. After creating new channels, you MUST also:
1. Remove bots from old channels they shouldn't be in (or archive those channels)
2. Verify bots appear in their intended new channels — check with `send_message(action='list')`
3. Don't rely on gateway config alone; Discord channel membership is a server-side permission, not a gateway setting
4. **Channel cleanup must be done manually by the user** — there is no `hermes discord` CLI command, and `discord_admin` is only available inside gateway sessions. Instruct the user to right-click → Delete Channel or Edit Channel → Archive in Discord. The agent cannot do this from a CLI session.

**Common mistake:** Assuming a bot only shows up in channels you've configured. Reused tokens carry the old bot's full channel access. A security bot using the architect's old token will appear in both #architecture (old) and #security-ops (new) unless explicitly removed from the old channel.

### Phase 9: Update Gateway Config (10 min)
```yaml
gateway:
  platforms:
    discord:
      bots:
        new_name: { token: <existing-token-for-old-name> }
```
Map new profile names to existing bot tokens.

### Phase 10: Restart & Verify (10 min)
```bash
hermes gateway restart  # MUST run from outside the gateway process
```
Verify each profile loads correctly. Check kanban, cron, Discord.

### Phase 11: Archive & Remove Old Profiles (Day 7+)

Keep old profiles for 7 days. If no issues, archive SOUL.md then delete.

**⚠️ Do NOT skip SOUL.md archival.** SOUL.md files are the only irreplaceable artifacts — skills, config, and memories are either migrated or disposable. Deleting a profile directory without archiving its SOUL.md means losing its identity permanently.

**Step 1: Inventory what still exists.** Old profiles get renamed/removed across sessions. Always check what's actually present before archiving.

```bash
# List all profiles — old and new side by side
ls ~/.hermes/profiles/

# Verify which deprecated profiles still exist
for p in <old-profile-list>; do
  [ -d ~/.hermes/profiles/$p ] && echo "EXISTS: $p" || echo "GONE:   $p"
done
```

**Step 2: Archive SOUL.md files.**

```bash
mkdir -p ~/soul-archive
for profile in <old-profiles>; do
  if [ -f ~/.hermes/profiles/$profile/SOUL.md ]; then
    cp ~/.hermes/profiles/$profile/SOUL.md ~/soul-archive/${profile}.SOUL.md
    echo "✅ archived ${profile}.SOUL.md"
  else
    echo "❌ $profile — no SOUL.md (already removed or never existed)"
  fi
done
```

**Step 3: Delete the profile directories.**

```bash
for profile in <old-profiles>; do
  rm -rf ~/.hermes/profiles/$profile
  echo "Removed: $profile"
done
```

**Step 4: Verify final state.**

```bash
ls ~/.hermes/profiles/  # Confirm only intended profiles remain
ls ~/soul-archive/       # Confirm all SOUL.md files archived
```

**Profiles that may already be gone:** Renamed profiles (oracle→finance, designer→creative, secretary→knowledge) often get removed during the rename step, before archival. Check for them first — if gone, their SOUL.md may have been lost. The `general` profile (Hermes default) is sometimes present and not part of the migration — confirm with user before deleting.

## Pitfalls

- **Can't restart gateway from inside gateway process.** `hermes gateway restart` is blocked when called from within the running gateway. Must restart from a separate terminal or shell session. If stuck, schedule a one-shot cron job to restart, or ask the user to run it manually.
- **Subagent file writes don't persist.** Files written by subagents via delegate_task are in an isolated sandbox — they won't exist in the parent terminal. Write deployment files (SOUL.md copies, config changes) directly in the parent context.
- **Cron jobs reference profile names, not IDs.** Unlike Discord channel IDs (stable), cron job `--profile` flags use profile names. Renaming profiles breaks these references. Always remap cron before restarting.
- **Gateway restart drops active sessions.** Schedule migration during low-activity window. All bots go offline during restart.
- **PersRubric format drift in batch drafting.** When spawning parallel subagents to draft SOUL.md files, each may use different delimiter conventions (`:` vs `=`). Always run a consistency pass after batch drafting.\n- **Discord API: PATCH uses `/channels/{id}`, not `/guilds/{guild}/channels/{id}`.** When renaming categories or updating topics via curl, the endpoint must be `PATCH /channels/{channel_id}`. Using `/guilds/{guild}/channels/{channel_id}` returns 404 even though GET works on the same path. POST (create) uses `/guilds/{guild}/channels` — the guild prefix is only for creation.\n- **Sandbox isolation on file writes.** The `write_file` tool and subagent sandboxes use different HOME directories. Files written to `~/Downloads/` by subagents don't appear in the parent terminal. Use `terminal` + `cat` or `write_file` directly in the parent context for deployment files.
- **Old profiles still have gateway entries.** Even after creating new profiles, the gateway config still points bots to old profile names. Phase 9 (gateway config update) must happen before Phase 10 (restart), or bots come up pointing to old profiles.
- **Token reuse carries full bot identity — name AND channel access.** When security reuses architect's bot token, the bot still displays as "Hermes Architect" in Discord AND still has access to #architecture. Gateway restarts don't fix this — the identity is on Discord's side, not yours. The user will see the wrong bot name in the old channel and think the migration is broken. Fix: (1) rename the bot in Discord Developer Portal, or (2) create a fresh bot token for the new profile, or (3) remove the bot from old channels via server settings. Always verify bot identity after token reuse by checking `curl -s https://discord.com/api/v10/users/@me -H 'Authorization: Bot <token>'` — if the returned `username` doesn't match the new profile name, flag it.
- **Renamed profiles vanish before archival.** When a profile is renamed (oracle→finance, designer→creative), the old directory often gets deleted as part of the rename. If Phase 11 runs later, those profiles are already gone and their SOUL.md is lost. Fix: archive SOUL.md BEFORE any rename/merge operation, not after. Treat archival as Phase 2.5 (right after backup), not Phase 11.
- **Orphan profiles outside the migration plan.** Profiles like `general` (Hermes default) may exist alongside migration targets. Always ask the user which profiles to keep vs delete — don't assume the migration plan covers everything in `~/.hermes/profiles/`.
- **Platform-specific profiles.** Some profiles only exist on certain machines (e.g., `ue5` on Windows PC, not Mac). Don't flag their absence as an error — confirm with user whether they're expected.
- **Users may want to keep profiles marked for deletion.** The migration plan may mark old profiles (architect, designer, etc.) for decommission, but the user might change their mind mid-migration. Always confirm with the user before archiving/deleting old profiles. If they want to keep one, it needs its own bot token (not shared with its replacement), its own channel, and its own slot in the gateway fleet.
- **Auxiliary provider errors after migration.** If `auxiliary.title_generation` or `auxiliary.vision` use `provider: nous` but no `NOUS_API_KEY` is set, session startup throws errors. Fix: switch to the profile's main LLM provider. Example for xiaomi: `hermes config set auxiliary.title_generation.provider xiaomi`, `hermes config set auxiliary.title_generation.model mimo-v2.5-pro`, `hermes config set auxiliary.title_generation.base_url https://token-plan-sgp.xiaomimimo.com/v1`. Repeat for `auxiliary.vision`. The `base_url` must be set explicitly — auxiliary services don't inherit it from the main model config.

## Rollback Strategy

**Full rollback:** Restore from Phase 1 tar.gz backup.
**Partial rollback:** Revert gateway config to old profile names, restart. Old profiles are untouched — new ones sit alongside them unused.

## Verification Checklist

After restart:
- [ ] `hermes profile list` shows all new profiles
- [ ] Each profile loads its SOUL.md: `hermes --profile <name> chat -q "What's your role?" -Q`
- [ ] Kanban board exists: `hermes kanban boards list`
- [ ] Cron jobs point to new profiles: `hermes cron list`
- [ ] Discord bots come online in correct channels (check with `send_message(action='list')` — bots using reused tokens may appear in old channels too)
- [ ] Bot display names match new profile names (verify via Discord API: `curl -s https://discord.com/api/v10/users/@me -H 'Authorization: Bot <token>'` — mismatched names = token reuse identity drift, fix in Discord Developer Portal)
- [ ] No old profile names referenced in active config

## References

- `references/migration-execution-log.md` — Real migration execution: 17-profile Mac redesign (2026-06-12), phases executed, issues encountered, timing
- `references/env-key-distribution.md` — API key audit methodology and distribution map for the 21-profile fleet (5 keys total, grouped by provider)
