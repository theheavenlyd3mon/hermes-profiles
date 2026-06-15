---
name: hermes-directory-cleanup
description: Inspect, audit, and safely clean up the ~/.hermes directory to remove orphaned pre-profile data and prune per-profile skill bloat without breaking running agents.
tags: [hermes, cleanup, profiles, maintenance, disk-space]
related_skills: [hermes-pre-update-audit]
version: 1.2.0
---

IDENTITY: Janitor.Auditor. Inspect ~/.hermes for orphaned pre-profile data, stale caches, duplicate repos, state snapshots, and profile skill bloat — then safely prune without breaking active agents.
Law: NeverPruneActiveProfileSkills — active profile keeps full skill tree.
WHENUSE: DiskSpaceReclamation|AfterProfileMigration|WorkProfilesClonedWithFullSkillTree|WantToCleanWithoutBreakingAgents. ESPECIALLY:ProfileHomeIsOftenBiggestConsumer{pnpmStore,camoufox,playwright,homebrew,pip caches}|DuplicateRepoCheckouts{venv+node_modules+.git per copy}|OrphanedGGUFModels{NestedInOldDotHermes}. NoSkip:RootConfigsArchiveNotDelete.
REDFLAGS: MaskedHOME->NavigateRealRoot|StateSnapshotsAccumulation->Keep3-5Newest|DuplicateReposNotSymlinked->800MB+EachCopy|ProfileAllSameSkills->EveryAgentIsIdenticalClone.
RATIONALIZATIONS: JustDeleteRootConfig->ArchiveFirstFallbackPathsExist|Two800MBReposAreDuplicates->CheckSymlinksBeforeComputingSavings|Phase3BreaksAgents->OnlyDormantWorkProfilesNotActive.
QUICKREF: Scan{BroadSize{du-sh*/}->ProfileHome{du-sh profiles/*/home/*/}->Caches{pnpm,pip,camoufox,playwright,homebrew}->DuplicateRepos->GGUFModels->StateSnapshots->RootOrphans}->Audit{ProfileSkills{CountCategories,TotalSize,CrossRefRoleDefs}}->BuildKeepList{PerProfileFromAgentRoleDoc}->Execute{Phase1{SafeOrphans}->Phase3{SkillPruning{dormantOnly}}}->Verify{SpaceReclaimed,ActiveProfileStillLoads}.

Inspect, audit, and safely clean up the `~/.hermes` directory. This workflow distinguishes pre-profile root orphans from active profile data, identifies stale caches/logs/checkpoints, and prunes per-profile skills to match agent role definitions.

## When to Use

- `~/.hermes` has grown large and you want to reclaim disk space
- You switched to profile mode but pre-profile root data is still lying around
- Work profiles were cloned with full skill trees but each agent only needs a subset
- You want to clean up without breaking running gateway/dashboard/CLI processes
- The user says "what old stuff can we remove" or "clean up old projects"
- You notice stale project directories outside `~/.hermes` (in `~/projects/`, `~/`, etc.)

## Broader Ecosystem Cleanup (Outside ~/.hermes)

The cleanup scope isn't just `~/.hermes` — it includes the user's broader project
ecosystem. Stale repos, abandoned experiments, and unused Threejs reference
checkouts can accumulate gigabytes.

### Audit Workflow

1. **Find all git repos** in common locations:
   ```bash
   for dir in ~/projects/ ~/ ~/Threejs/; do
     find "$dir" -maxdepth 2 -name ".git" -type d 2>/dev/null
   done
   ```

2. **For each repo, collect:**
   - Last commit date: `git log -1 --format='%ai'`
   - Commits in last 30 days: `git log --since="30 days ago" --oneline | wc -l`
   - Size (excluding node_modules): `du -sh . --exclude=node_modules --exclude=.git`
   - Remote URL: `git remote get-url origin`
   - Uncommitted changes: `git status --porcelain | wc -l`

3. **Classify each repo:**
   | Signal | Classification |
   |--------|---------------|
   | 0 commits in 30d, last commit >60d ago | Stale — candidate for removal |
   | 0 commits in 30d, last commit <60d ago | Dormant — keep but watch |
   | 1+ commits in 30d | Active — keep |
   | Single initial commit only | Experiment — candidate for removal |
   | Uncommitted changes >0 | Has work in progress — don't remove without asking |

4. **Present to user** as a table with keep/delete/archive recommendations.

### Removal Pattern

For stale projects, the safe approach is:
- **Delete local directory** — frees disk immediately
- **Archive GitHub repo** — preserves code, marks as inactive, reversible
  - `gh repo archive <owner>/<repo> --yes`
  - **Pitfall:** Requires `administration` PAT scope. If the token lacks it,
    the user must archive via GitHub web UI (Settings → Danger Zone → Archive).
- **Delete GitHub repo** — only if user explicitly confirms. Irreversible.
  - `gh repo delete <owner>/<repo> --yes`

### .gitignore Audit

When reviewing repos, check .gitignore quality:
```bash
for dir in <repos>; do
  echo "=== $dir ==="
  if [ -f "$dir/.gitignore" ]; then
    echo "  lines: $(wc -l < "$dir/.gitignore")"
  else
    echo "  MISSING .gitignore"
  fi
  # Check for tracked secrets
  cd "$dir"
  git ls-files | grep -iE '\.env$|secret|token|key\.pem|id_rsa|\.p12$' | head -5
done
```

Key rules:
- `.env` files must NEVER be tracked (real secrets)
- `.env.example` files ARE safe to track (placeholders)
- Files with "token" or "key" in the name are usually source code, not secrets
- `node_modules/` must be in .gitignore
- Minimum .gitignore: `node_modules/`, `.env`, `.DS_Store`, `dist/`, `*.log`

### Common Stale Directory Locations

| Location | What accumulates |
|----------|-----------------|
| `~/projects/` | Active and abandoned project repos |
| `~/Threejs/` | Reference library clones (Three.js ecosystem) |
| `~/` (home root) | Hermes-related workspace repos, experiments |
| `~/.hermes/hermes-office/` | Claw3D frontend (if no longer used) |
| `~/.hermes/webui/` | Old webui sessions |
| `~/.hermes/shared-brain/` | GBrain PGLite database (large if unused) |

## Prerequisites

- Hermes is installed with active profiles
- You know which profile is currently active (`cat ~/.hermes/active_profile`)
- You have the agent role definitions (e.g. a `10-Agent Team Setup.md` doc in your Obsidian vault)

## Inspection Steps

Start broad with a top-level size scan, then drill into the biggest consumers. The profile home directory (`profiles/<name>/home/`) is often the largest category — don't ignore it.

### 1. Determine the real Hermes home

The shell `HOME` may be masked to `~/.hermes/profiles/<name>/home`. Always use the actual path:

```bash
cd /Users/<user>/.hermes   # or wherever HERMES_HOME resolves
```

### 2. Map root vs profile structure & broad scan

```bash
# Root tree (depth 1)
find . -maxdepth 1 -type d | sort

# Active profile tree (depth 2)
find profiles/<active> -maxdepth 2 | sort

# Broad size scan — every directory at depth 1
du -sh */ | sort -rh

# Repeat for the active profile
du -sh profiles/<active>/*/ | sort -rh | head -15
```

### 3. Drill into profile home directory (often the biggest consumer)

The sandboxed `home/` dir accumulates caches and node_modules. Check systematically:

```bash
# Top-level home breakdown
du -sh profiles/<name>/home/*/ | sort -rh

# Sub-cache breakdown
du -sh profiles/<name>/home/Library/Caches/*/ | sort -rh
```

Typical hot spots:
- `home/Library/pnpm/store/` — global npm package store, often 1+ GB. Safe to prune: `pnpm store prune`
- `home/Library/Caches/camoufox/` — browser automation profiles (500 MB+). Safe to wipe; recreated on demand.
- `home/Library/Caches/ms-playwright/` — Playwright browser binaries (500 MB+). Safe to wipe; recreated on `npx playwright install`.
- `home/Library/Caches/Homebrew/` — formula downloads (200 MB). Safe: `brew cleanup`.
- `home/Library/Caches/pip/` — pip wheel cache (60 MB). Safe: `pip cache purge`.
- `home/hermes-workspace/node_modules/` — companion app deps (1.5 GB). Safe if not actively developing.

### 4. Check for duplicate repo checkouts

Hermes-agent or other repos may be checked out in multiple places (root + profile), each with their own venv, node_modules, and .git:

```bash
for d in hermes-agent profiles/*/hermes-agent; do
  if [ -d "$d" ]; then
    sz=$(du -sh "$d" 2>/dev/null | cut -f1)
    echo "$d: $sz (venv: $(du -sh $d/venv 2>/dev/null | cut -f1), node_modules: $(du -sh $d/node_modules 2>/dev/null | cut -f1), .git: $(du -sh $d/.git 2>/dev/null | cut -f1))"
  fi
done
```

If multiple full checkouts exist (not symlinks), the profile copy can be replaced with a symlink to the root canonical checkout — saving 800 MB+.

**Special case: `~/.hermes/hermes-agent` (root copy)** — This is the CLI backbone (`~/.local/bin/hermes` depends on it). NEVER remove it. If profile copies exist, replace THEM with symlinks to root. See `references/hermes-agent-is-cli-backbone.md` for the full dependency chain and `references/hermes-agent-unused-copy-cleanup.md` for the consolidation workflow.

### 5. Check for orphaned local models in mnemosyne/

A pre-profile-migration `home/.hermes/` may persist inside the profile home, containing a stale GGUF model:

```bash
# Find any GGUF models
find . -name "*.gguf" -type f 2>/dev/null

# Verify if they're referenced in any config
grep -ri "tinyllama\|gguf\|local-model" profiles/*/config.yaml 2>/dev/null

# Check the old nested .hermes
du -sh profiles/<name>/home/.hermes/ 2>/dev/null
du -sh profiles/<name>/home/.hermes/mnemosyne/models/ 2>/dev/null
```

If a GGUF model (typically ~638 MB for a 1.1B Q4_K_M) sits in an old nested `.hermes` and is not referenced by any profile config, it's orphaned and safe to delete. The old .hermes directory itself may also contain a stale mnemosyne DB and plugin copy.

### 6. Check state-snapshots accumulation

Pre-update snapshots can accumulate quickly:

```bash
ls profiles/<name>/state-snapshots/ | wc -l
du -sh profiles/<name>/state-snapshots/
du -sh profiles/<name>/state-snapshots/*/ | sort -rh | head -10
```

Typical snapshot sizes range from 20 MB (first day) to 145 MB (after a week). With 19 snapshots over 6 days, expect ~1.2 GB. Keep the newest 3–5; older ones are safe to delete.

### 7. Identify orphaned root data

| Root Item | Check If Active Profile Has Its Own | Safe to Remove? |
|-----------|-------------------------------------|-----------------|
| `sessions/` | `profiles/<name>/sessions/` exists | Yes, if profile dir is non-empty |
| `state.db` (+ wal/shm) | `profiles/<name>/state.db` exists | Yes |
| `checkpoints/` | No profile equivalent (checkpoints live at root for all?) | Inspect contents first; if old, remove |
| `logs/` | `profiles/<name>/logs/` exists | Yes |
| `response_store.db` | No equivalent | Safe (legacy cache) |
| `.skills_prompt_snapshot.json` | No equivalent | Safe (stale snapshot) |
| `models_dev_cache.json` | Profile has its own cache | Yes |
| `config.yaml`, `.env`, `auth.json` | Profile has its own copies | **Archive first** — move to `archive/` instead of deleting |

> **Rule:** Never delete root config/auth without archiving. There may be fallback paths or env references you cannot see from inside a profile.

### 8. Check running processes

```bash
ps aux | grep -i hermes | grep -v grep
```

Verify all running processes execute from `hermes-agent/` source and write state into the active profile. If so, root orphans are truly orphaned.

### 9. Profile skill audit

Each work profile likely cloned the full skill tree. Check:

```bash
# List skills per profile
for p in profiles/*/; do echo "$(basename $p): $(ls -1 $p/skills | wc -l) categories"; done

# Total per profile
du -sh profiles/*/skills
```

Cross-reference your agent role definitions (e.g. from your Obsidian vault) to determine which skill categories each profile actually needs. The rest can be removed and reinstalled/copied later from the active profile or the root skills pool.

### 10. Build the skill keep-list per profile

Example mapping from a 10-agent engineering team:

| Profile | Keep These Skill Categories |
|---------|---------------------------|
| foreman | `software-development`, `autonomous-ai-agents`, `github` |
| coder | `software-development`, `github` |
| architect | `software-development`, `creative`, `domain` |
| debugger | `software-development` |
| reviewer | `software-development`, `github` |
| secretary | `note-taking`, `research` |
| researcher | `research`, `data-science` |
| devops | `devops`, `software-development`, `github` |
| data-analyst | `data-science`, `research` |
| security | `red-teaming`, `github`, `software-development` |

> **Important:** The active personal profile (e.g. `senna`) typically keeps the FULL skill tree. Do not prune the active profile.

## Execution

### Phase 1 — Safe Orphans

```bash
cd ~/.hermes

# Create archive dir
mkdir -p archive

# Archive root configs (don't delete)
mv config.yaml .env auth.json archive/ 2>/dev/null || true

# Remove orphaned data
rm -rf sessions/
rm -f state.db state.db-shm state.db-wal
rm -rf checkpoints/
rm -f response_store.db
rm -f .skills_prompt_snapshot.json
rm -f models_dev_cache.json ollama_cloud_models_cache.json
rm -rf logs/
```

### Phase 3 — Profile Skill Pruning

For each **dormant** work profile (NOT the active profile):

```bash
PROFILE=profiles/foreman
KEEP="software-development autonomous-ai-agents github"

# Remove everything not in KEEP
for dir in "$PROFILE/skills"/*/; do
  name=$(basename "$dir")
  if [[ ! " $KEEP " =~ " $name " ]]; then
    echo "Removing $name from $PROFILE"
    rm -rf "$dir"
  fi
done
```

> **Never** run this on the active profile without explicit user approval.

### Verify

```bash
# Check space reclaimed
du -sh ~/.hermes

# Verify active profile still loads
hermes skills list --profile <active>
```

## Pitfalls

1. **Masked HOME — `~` lies inside a profile session.** When a profile runs, `HOME=~/.hermes/profiles/<name>/home`. So `find ~`, `ls ~`, `cat ~/.hermes/config.yaml` all resolve to the NESTED `.hermes` inside the profile sandbox — which is mostly empty copies. The REAL data is at the absolute path `/Users/<user>/.hermes/`. Always verify: `echo "HOME=$HOME HERMES_HOME=$HERMES_HOME"`. Use absolute paths for all hermes directory operations. See `references/directory-map.md` for the full structure.
2. **Active profile** — Never prune skills from the currently active profile. Agents running in that profile may depend on them.
3. **Root configs** — Archive, don't delete. Some fallback code paths may still look for root-level `.env` or `config.yaml`.
4. **Skills referenced but not installed** — Your agent docs may mention skills (e.g. `workspace-dispatch`, `system-design`) that aren't physically present in profiles yet. Don't panic if they're missing; install them when needed.
5. **Gateway/dashboard processes** — Confirm they run from `hermes-agent/` and write state to the active profile before removing root orphans.
6. **Profile home is NOT `~/.hermes/home`** — It's `profiles/<name>/home/`. This sandboxed directory accumulates macOS-style caches (Library/Caches, pnpm, pip) that can dwarf the rest of the Hermes installation. Don't overlook it.
7. **Orphaned GGUF models aren't in root** — They hide inside `profiles/<name>/home/.hermes/mnemosyne/models/` as leftover from pre-profile-migration days. Always grep configs to verify they're unreferenced before declaring them orphaned.
8. **State snapshots are effectively incremental** — The newest one (145 MB) may already contain everything from the older ones (20 MB). Keeping 19 snapshots at 1.2 GB total is rarely useful. Keep 3-5 newest.
9. **Verify symlinks, not just sizes** — Two 800 MB repos might be a symlink + 800 MB real. Check `ls -la` before computing savings from deduplication.
10. **NEVER move or delete `~/.hermes/hermes-agent/` (root)** — The `hermes` CLI wrapper at `~/.local/bin/hermes` hard-codes the path `~/.hermes/hermes-agent/venv/bin/hermes`. Moving or removing the root hermes-agent breaks the CLI command entirely (`hermes: command not found`), kills the API, and prevents gateway startup. The user will have to reinstall. The CORRECT approach for profile deduplication is the reverse: keep root as canonical, symlink the profile's hermes-agent to root (not root to profile). See `references/hermes-agent-is-cli-backbone.md`.
11. **Duplicate YAML keys silently drop earlier values** — If `config.yaml` has `platforms:` defined twice, YAML keeps only the LAST block. The first block (e.g. telegram) silently vanishes. Always merge into a single `platforms:` key. Common symptom: "no messaging platforms enabled" despite telegram being configured.
12. **GitHub archival needs `administration` PAT scope** — `gh repo archive` fails with `Resource not accessible by personal access token (archiveRepository)` if the PAT lacks the `administration` scope. The user must either: (a) archive via GitHub web UI (Settings → Danger Zone → Archive), or (b) create a new PAT with `administration` scope. Don't retry the command — it will fail the same way. Present the web UI path immediately.
13. **Pushing hermes-agent forks needs `workflow` PAT scope** — The hermes-agent repo contains `.github/workflows/` files. Pushing to a fork or personal repo fails with `refusing to allow a Personal Access Token to create or update workflow .github/workflows/... without workflow scope`. Fix: add `workflow` scope to the PAT, or use `git format-patch` to save changes locally instead of pushing.
14. **Profile hermes-agent copies can poison MCP configs** — When a profile has its own hermes-agent checkout (not a symlink), MCP configs may end up pointing to the profile-local venv (`profiles/<name>/hermes-agent/venv/bin/...`) instead of the main venv. This creates a ghost dependency on the duplicate. Before removing a profile hermes-agent copy, grep the profile's config.yaml for any paths referencing it and fix them to use the main venv. See `hermes-mcp-profile-isolation` skill for the full pattern.

## Expected Impact

- Phase 1 typically frees 50–70M of orphaned root data
- Phase 3 typically frees 60–80M across 10 work profiles
- Profile-home cache cleanup (pnpm store, camoufox, playwright, homebrew, pip) typically frees 2–4 GB
- State-snapshot pruning typically frees 0.8–1.0 GB (keep 3-5 instead of 19)
- Orphaned GGUF model removal frees ~640 MB
- Duplicate repo deduplication frees 800 MB – 1.7 GB
- Zero impact on running agents if the active profile is untouched

## References

- `references/hermes-agent-is-cli-backbone.md` — Why `~/.hermes/hermes-agent/` must NEVER be moved or deleted (CLI dependency chain). **Read this before any directory restructuring.**
- `references/hermes-agent-unused-copy-cleanup.md` — How to consolidate profile hermes-agent copies into symlinks to root (was previously about removing root — now corrected).
- `references/post-consolidation-health-check.md` — Verification checklist after symlink consolidation: CLI chain, MCP binaries, gateways, Discord, mnemosyne, dashboard. Run this after any directory restructuring.
- `references/real-world-audit-may-2026.md` — Full audit data from a real 12 GB multi-profile installation with measured sizes for profile home caches, duplicate repos, state snapshots, and orphaned models. Use as a comparison baseline when auditing a new installation.
- `references/profile-audit-workflow.md` — How to audit all profiles by purpose/role, classify them (active bot vs custom persona vs generic boilerplate), and build a keep/delete recommendation. Use when the user asks "what profiles do we have" or "which ones should we remove".
- `references/directory-map.md` — Complete structural map of `~/.hermes/` showing where everything lives (config, skills, plugins, databases, apps, data, external paths). Read this when you need to find something or answer "where is X". Covers the path resolution trap in detail.
- `references/pre-removal-path-audit.md` — Systematic checklist for verifying nothing references a directory before removing it. Covers configs, launchd, shell profiles, cron jobs, plugin symlinks, and .env files. Use before any `rm -rf` under `~/.hermes/`.
- `references/2026-05-28-ecosystem-cleanup.md` — Real cleanup session removing hermes-office (1 GB) and hermes-solar-system (78 MB). Includes broader ecosystem audit pattern (directories outside ~/.hermes), .gitignore quality scoring, GitHub archival workflow, and the PAT scope limitation pitfall.
- `references/2026-05-28-gitignore-audit.md` — .gitignore quality audit of user's repos. Includes minimum Node.js template, detection commands for tracked secrets, and key rules (.env vs .env.example).
