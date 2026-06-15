---
name: config-consistency-review
description: >-
  Systematic review for orphaned services, duplicate processes, stale config
  files, and other state inconsistencies left behind by profile migrations,
  gateway setup changes, or config consolidation. Run after any config
  migration or when troubleshooting unexpected behavior like "gateway shutting
  down" loops.
category: devops
triggers:
  - cleanup after migration
  - check for orphaned config
  - review for leftover services
  - duplicate processes
  - anything fighting each other
  - stale launchd plists
  - config consistency check
  - what might be left behind
  - audit team profiles
  - profile definition check
  - verify profiles against design doc
  - profile completeness review
  - check for stale missions
  - what profiles exist
  - role-specific skill pruning audit
---

IDENTITY: Auditor.Diagnostician. Find orphaned state after config changes — {plists,env,gateways,profiles,plugins,auth} then fix with idempotent commands.
Law: NeverDeleteRootConfigWithoutArchiving.
WHENUSE: After{profileMigration,gatewayReconfig,consolidation}|Troubleshooting{UnexpectedBehavior,PortConflict,ServiceLoop}|Periodic{MonthlyOrPostUpdate}. ESPECIALLY:GatewayFightingOn8642|DuplicatePlist|ProfileGapVsDesignDoc. NoSkip:StaleMissionCheck|RoleSkillPruningCheck.
REDFLAGS: SIGTERM>5InRecentLogs->FightLoop|TwoGatewayProcesses->InvestigateDuplicate|ProfileAllMarks✗->StubNotAgent|SameKeyInBothEnvWithDifferentValues->Bug|BrokenSymlink->TargetDeleted.
RATIONALIZATIONS: JustDeletePlist->LaunchdCachesItMustBootoutFirst|QuickFixRemoveReplace->ResolveCauseNotSymptom|IgnoreStaleMissions->OrchestratorDiedLeavingZombies.
QUICKREF: Audit{LaunchdPlist->DuplicateGateway->OrphanedConfig->AuthSymlinks->PluginDirs->LogSanity->PortMap}->ProfileDefAudit{MapExpectedVsActual->CompletenessCheck{Soul,Config,Skills,Identity,Env}->StaleMissionCheck->SkillPruningCheck->CrossRefEpisodes}->Cleanup{RemoveOrphanedPlist{bootoutThenDelete}->KillDuplicateGateway->FixBrokenSymlink->ConsolidateEnvVars}.

# Config Consistency Review

Review for operational artifacts that persist after configuration changes.
The canonical example is leaving an old `ai.hermes.gateway.plist` in
`~/Library/LaunchAgents/` after switching from the default profile to Senna —
both gateways start on boot and fight over port 8642.

## When to Use

- **After any profile migration** — switching default profile, moving keys
  between `.env` files, consolidating auth files
- **After gateway reconfiguration** — changing gateway profile, stopping one
  gateway and starting another
- **When troubleshooting unexpected behavior** — services crashing in loops,
  "gateway shutting down" messages, port conflicts
- **Periodic maintenance** — run monthly or after major Hermes updates

## Profile Definition Audit

After any profile migration or periodically, audit that each Hermes profile is
properly defined — has a SOUL.md, config.yaml, assigned role/specialty, and no
stale missions. This catches the common pattern of "the design doc was written,
but the profiles were never actually configured."

### 1. Map Intended Profiles vs Actual

Start with the reference (a design doc, a mental model, or the 10-Agent Team
Setup from the example at `references/team-profile-audit-2026-05-12.md`).

List all expected profiles, then enumerate what actually exists:

```bash
hermes profile list 2>/dev/null || ls ~/.hermes/profiles/
```

Expected vs actual gap table.

### 2. Profile Completeness Checklist

For each profile that exists, check SOUL.md, config.yaml, skills/, IDENTITY.md, .env. A profile that shows all ✗ marks is a stub, not a working agent.

### 3. Stale Mission Check

Profiles accumulate missions that never completed. Check for missions stuck in `executing` status.

### 5. Plugin-Backed Tool Verification

Some tools (image_gen, fabric, spotify, web-search-plus) are **plugin-backed** —
they require THREE things to work, not just one. Check all three for each
plugin-backed tool across all profiles:

| Check | What to grep | Why it fails |
|-------|-------------|--------------|
| Tool in `platform_toolsets` | `grep "image_gen" config.yaml` | Tool never loads |
| Plugin in `plugins.enabled` | `grep "image_gen/fal" config.yaml` | No provider registered |
| Config section exists | `grep -A2 "^image_gen:" config.yaml` | Provider settings missing |

```bash
# Audit all profiles for a specific plugin-backed tool
TOOL="image_gen"
PLUGIN="image_gen/fal"
for p in ~/.hermes/profiles/*/config.yaml; do
  name=$(echo "$p" | sed 's|.*/profiles/||;s|/config.yaml||')
  in_toolset=$(grep -q "$TOOL" "$p" && echo "✓" || echo "✗")
  in_plugins=$(grep -q "$PLUGIN" "$p" && echo "✓" || echo "✗")
  has_section=$(grep -q "^${TOOL}:" "$p" && echo "✓" || echo "✗")
  echo "$name: toolset=$in_toolset plugins=$in_plugins section=$has_section"
done
```

**Common pattern:** Profile was set up with `image_gen` in toolset but plugins
and config section were never added. The tool loads but has no provider — silent
failure. See `references/role-based-toolset-mapping.md` for the full audit table.

### 5b. Role-Based Toolset Audit

Most multi-profile setups copy-paste the same toolset blob into every profile.
This wastes context tokens and gives workers tools they shouldn't have (e.g.,
image_gen on a debugger, delegation on a coder).

**Audit method:**
```bash
for p in ~/.hermes/profiles/*/config.yaml; do
  name=$(echo "$p" | sed 's|.*/profiles/||;s|/config.yaml||')
  tools=$(grep -A20 'platform_toolsets:' "$p" | grep 'cli:' -A20 | grep '^ *- ' | sed 's/.*- //' | tr '\n' ',' | sed 's/,$//')
  echo "$name: $tools"
done
```

If every profile has the same tool list, the setup was copy-pasted. Trim each
to role-appropriate tools. See `references/role-based-toolset-mapping.md` for a
proposed mapping by role.

**Principle:** Workers (coder, debugger, reviewer, security, devops, data-analyst)
don't need `clarify` (they get clear tasks), `messaging` (coordinator handles
comms), or `memory` (session-scoped). The coordinator (senna, foreman) keeps
the full set.

### 6. Stale Mission Check

Recent episodic activity tells you whether a profile is actively being used.

## Pitfall: HERMES_HOME Nesting

Profiles can be nested under the acting profile's `home/.hermes/profiles/` directory. Always check both `$HERMES_HOME/home/.hermes/profiles/` and `~/.hermes/profiles/`.

## Checklist — Run in Order

### 0. Gateway Health Check

Before auditing configs, check if gateways are actually running and healthy. A gateway with exit=1 or exit=256 is crashing; one with a missing profile directory has nothing to load.

```bash
# Quick status of all hermes gateways
launchctl list | grep hermes | awk '{printf "%-40s PID=%s Exit=%s\n", $NF, $1, $2}'

# Detailed view per gateway (shows LastExitStatus, PID, OnDemand, log paths)
launchctl list ai.hermes.gateway-<name>

# Verify profile directory exists
ls ~/.hermes/profiles/<name>/ 2>/dev/null || echo "MISSING"
```

**Exit codes:** 0=healthy, 1/256=crashed, -15=SIGTERM'd, -=not running. Empty log files on a running gateway = failing before logger init. See `references/gateway-health-check-2026-05-26.md` for full diagnostic table.

### 1. Launchd Plist Audit

Check for orphaned gateway plists. Expected: one plist per active gateway profile.

### 2. Duplicate Gateway Processes

`ps aux | grep "gateway run" | grep -v grep` — expected: one process per active gateway. Check `lsof -i :8642` for port conflicts.

### 2b. Duplicate YAML Keys in config.yaml

The `hermes config set` command appends new sections rather than editing in-place. This creates duplicate root-level YAML keys. Python's YAML parser silently keeps only the LAST occurrence — earlier sections are dropped without warning.

```bash
# Find all root-level keys that appear more than once
for p in ~/.hermes/profiles/*/config.yaml ~/.hermes/config.yaml; do
  [ -f "$p" ] || continue
  dupes=$(grep -cE '^[a-z_]+:' "$p" 2>/dev/null)
  top_keys=$(grep -E '^[a-z_]+:' "$p" 2>/dev/null | sort | uniq -d)
  if [ -n "$top_keys" ]; then
    echo "DUPLICATE KEYS in $p:"
    echo "$top_keys"
  fi
done
```

**Specifically check for duplicate `platforms:` keys:**
```bash
grep -n "^platforms:" ~/.hermes/config.yaml 2>/dev/null
# If > 1 match, YAML keeps only the LAST one — earlier platform configs are silently dropped
```

**Example of the bug:**
```yaml
platforms:              # ← FIRST occurrence (DROPPED by YAML parser)
  telegram:
    enabled: true
# ... comments or other keys ...
platforms:              # ← SECOND occurrence (this one WINS)
  api_server:
    enabled: true
```

**Result:** Telegram config is silently lost. Gateway starts with only api_server.

**Fix:** Merge duplicate sections into one, or use `patch` tool to edit the existing key instead of `hermes config set`.

### 2c. Mixed hermes-agent Venv Usage

After a profile migration that copies/moves hermes-agent into the profile directory, gateway processes may end up using different Python binaries:

```bash
ps aux | grep 'gateway run' | grep -v grep | \
  awk '{for(i=1;i<=NF;i++) if($i ~ /venv/) print $0}'
```

If some gateways use `~/.hermes/hermes-agent/venv/bin/python` and others use `~/.hermes/profiles/senna/hermes-agent/venv/bin/python`, they're running different code versions. This causes subtle incompatibilities in tool schemas, adapter behavior, and plugin interfaces.

**Fix:** Consolidate to one hermes-agent checkout. Remove or symlink the duplicate.

### 3. Orphaned Config Files After Consolidation

Check for duplicate keys across .env files. Profile .env takes precedence at runtime.

### 4. Auth File Symlink Integrity

Symlinks should point to `~/.hermes/auth.json`. Standalone files won't auto-update.

### 5. Plugin Directory Consistency

Cross-reference `hermes plugins list` with actual plugin directories.

### 6. Log File Sanity

Runaway log files from a crashed loop are a telltale sign. >5 SIGTERM entries = fight loop.

### 7. Port Conflict Map

When running 5+ Discord bot gateways, each with `api_server` enabled, they all try to bind port 8642. **Fix: Disable `api_server` for bot-only profiles** (all except Senna). See `references/launchd-service-registration.md` for details.

## Cleanup Actions

### Remove orphaned launchd plist

```bash
launchctl bootout gui/$(id -u)/<label> 2>/dev/null
rm ~/Library/LaunchAgents/<plist-name>.plist
kill <PID> 2>/dev/null
```

### Register a new launchd service (macOS 10.10+)

**Do NOT use `launchctl load`** — deprecated.
**Do NOT use `launchctl bootstrap`** — fails with I/O error if old process running.

Reliable method (verified 2026-05-26):
```bash
pkill -f "profile <name> gateway" 2>/dev/null; sleep 2
launchctl enable gui/$(id -u)/ai.hermes.gateway-<name>
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway-<name>
```

See `references/launchd-service-registration.md` for full plist template and multi-gateway strategy.

### Kill duplicate gateway
Kill the wrong PID. Verify: one gateway process per active profile.

### Fix broken auth symlink
```bash
rm ~/.hermes/profiles/<name>/auth.json
ln -sf ~/.hermes/auth.json ~/.hermes/profiles/<name>/auth.json
```

## Token Writing Technique

When writing Discord bot tokens (or any credential containing special characters like `*`, `=`, `.`) to `.env` files, the shell and `write_file` tool may interpret or truncate the value. **Reliable method: write via hex encoding.**

```bash
echo -n 'TOKEN_HERE' | xxd -p  # encode
echo '<hex>' | xxd -r -p > /tmp/token.txt  # decode to file
# Then use Python byte-level replacement (no interpretation)
```

**Why this is needed:** `write_file` interprets `...` as a special truncation sequence. Shell heredocs have the same issue.

## Platform Enablement Gotcha

**Telegram auto-enables when `TELEGRAM_BOT_TOKEN` env var is present.** The gateway code auto-enables Telegram when it finds the env var — even if you only want Discord. To disable: comment out `TELEGRAM_BOT_TOKEN` in `.env`, or set `telegram: enabled: false` in `config.yaml`.

## Pitfalls

1. **Don't remove a plist while the service is still loaded** — Always `bootout` first.
2. **The `--replace` flag sends SIGTERM** — If the other gateway is under KeepAlive, restart loop begins.
3. **`write_file` truncates tokens containing `...`** — Use `xxd -r -p` hex writing for credentials.
4. **`launchctl load` is deprecated** — Use `launchctl enable + kickstart -k` instead.
5. **Gateway log paths depend on the launchd plist's WorkingDirectory** — May be relative.
6. **Multi-gateway api_server port collision** — Disable `api_server` for bot-only profiles.
7. **Dual hermes-agent source trees** — After moving hermes-agent into a profile dir, the root `~/.hermes/hermes-agent/` may remain. Gateway processes can end up using different venvs/code versions. Always check with `diff <(cd ~/.hermes/hermes-agent && git log --oneline -1) <(cd ~/.hermes/profiles/<name>/hermes-agent && git log --oneline -1)`. See `gateway-health-check` skill's references for a case study.

## References

- `references/team-profile-audit-2026-05-12.md`
- `references/launchd-service-registration.md` — Modern macOS launchd registration, plist template, multi-gateway port strategy, Telegram disable
- `references/gateway-health-check-2026-05-26.md` — Exit code table, diagnostic red flags, single-command status summary
- `references/role-based-toolset-mapping.md` — Role-based toolset and skills audit for multi-profile fleets. Includes plugin-backed tool verification checklist and proposed per-role trimming.
