---
name: multi-agent-profile-redesign
description: Design, plan, and implement a multi-profile Hermes Agent fleet — domain-based architecture, SOUL.md at scale, Kanban coordination, bot assignment, skill curation, and phased migration.
version: 1.4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, profiles, multi-agent, fleet, kanban, soul, migration, discord]
    related_skills: [hermes-soul-authoring, skill-compression, kanban-orchestrator, foreman-orchestration, profile-bootstrapping, discord-server-management]
---

# Multi-Agent Profile Redesign

Design and implement a domain-based multi-profile Hermes fleet. Covers architecture, SOUL.md authoring at scale, Kanban coordination, Discord bot assignment, skill curation, and zero-downtime migration.

## When To Use

WHENUSE: {NewFleetSetup,ProfileRedesign,MultiAgentArchitecture,FleetExpansion,MergeOverlappingProfiles}. ESPECIALLY:{ProfileCount>10,DomainOverlap,DiscordMultiBot}. NoSkip:{SingleProfile,SimpleRename}.

## Core Design Principles

### 1. Domain-Based Profiles (Not Role-Based)

Organize profiles around **skill domains**, not job titles. Each profile owns a clear domain with minimal overlap.

```
❌ Role-based: coder, debugger, reviewer (overlapping)
✅ Domain-based: code (merged), creative, research, finance
```

**Merge criteria:** If two profiles share >40% of their skill catalog, merge them.

### 2. Kanban as Coordination Layer

Don't hand-design routing protocols. Use the built-in Kanban board:
- **Board:** Single `main` board with domain tags
- **Dispatcher:** Auto-spawns assigned workers on 60s tick
- **Comments:** Inter-profile communication on tasks
- **Goal-mode:** Loop workers until acceptance criteria met

Senna creates tasks → Kanban board → Dispatcher → Workers → Results flow back.

### 3. Orchestrator vs Worker Hierarchy

| Role | Count | Responsibility |
|------|-------|---------------|
| Top orchestrator | 1 (senna) | Front door, routing, fleet management |
| Domain orchestrators | 3-5 | Decompose large tasks, manage domain workers |
| Workers | Rest | Execute specific tasks, block when stuck |
| Autonomous workers | Subset | Also run cron jobs independently |

### 4. Bot Assignment Strategy

Not every profile needs a Discord bot. Decision matrix:

| Factor | Needs Bot | No Bot (Senna-subordinated) |
|--------|-----------|---------------------------|
| User interaction frequency | Daily | Occasional/cron |
| Output complexity | Visual/interactive | Text summary |
| Domain size | Large skill catalog | Small (<10 skills) |
| Independence | Works autonomously | Receives dispatched tasks |

Typical: 6-10 bots for a 15-20 profile fleet.

## SOUL.md at Scale

### Template Hierarchy

| Pattern | Use For | Size Target |
|---------|---------|-------------|
| Full 6-section | Top orchestrator (senna) | ~3,000B |
| Specialist + Team | Domain orchestrators | ~1,500-1,900B |
| Specialist | Workers with Discord bots | ~1,300-1,900B |
| Specialist (minimal) | Senna-subordinated workers | ~1,200-1,600B |

### Compressed DSL (Proteus-Style)

For 10+ profiles, use compressed DSL to keep token costs manageable. Average 68% reduction vs prose.

**Sections to compress:**
- IDENTITY → `Trait.Trait.Trait. Name{Role}. CorePrinciple.`
- PersRubric → NEO-PI-R 30 sub-facets in ~200 chars
- STYLE/AVOID/DEFAULTS → DSL encoding + arrow conditionals
- ROUTE → Structural compression: `Design→creative|Build→code|Research→research`
- TEAM → Token packing: `{code:Impl,creative:Design,research:Data}`

**Sections to keep prose:**
- Quality Gates (operational checklists)
- Section headers (human-parseable anchors)

### Required Sections by Profile Type

| Section | Orchestrator | Worker (bot) | Worker (subordinated) |
|---------|-------------|-------------|----------------------|
| IDENTITY | ✅ | ✅ | ✅ |
| PersRubric | ✅ | ✅ | ✅ |
| STYLE/AVOID/DEFAULTS | ✅ | ✅ | ✅ |
| DISCORD | ✅ | ✅ | ❌ |
| TEAM | ✅ | ReportsTo only | ReportsTo only |
| ROUTE | ✅ | ❌ | ❌ |
| DECOMPOSE | ✅ | ❌ | ❌ |
| HANDOFF | ✅ | ❌ | ❌ |
| DECISIONS | ✅ | ❌ | ❌ |
| KANBAN | ✅ | ✅ | ✅ |
| COMPLETE/BLOCK | ❌ | ✅ | ✅ |
| GATE | ✅ | ✅ | ✅ |

### DISCORD Section Pattern

Each bot-bearing profile needs:
```
DISCORD: Channel=#channel-name. {Role description}. When @mentioned, {behavior}. {Thread creation policy}. Completion: {output format}.
```

### PersRubric Calibration by Role

| Role Type | High Facets | Low Facets |
|-----------|------------|------------|
| Coordinator | C:SE(80), C:Ord(80), E:A(55) | N:Anx(25), E:ES(30) |
| Implementation | C:Ord(90), C:SE(85), C:SD(85) | O:Adv(30), E:ES(20) |
| Design/Creative | O2E(85), O:I(90), A:Alt(80) | E:ES(25), N:Immod(25) |
| Research/Investigation | O:Int(95), O:O2E(85), C:Cau(85) | E:ES(20), N:Immod(20) |
| Review/Audit | C:Cau(95), C:SD(90), C:AS(85) | E:ES(15), N:Immod(15) |
| Operations | C:Cau(90), C:Ord(90), C:Dt(85) | E:ES(20), N:Immod(20) |
| Knowledge | C:Ord(95), C:SE(90), A:TM(70) | E:ES(15), N:Ang(15) |
| Trading/Finance | O:Int(90), C:Cau(90), C:Dt(85) | E:ES(20), N:Immod(20) |

## Migration Strategy

### 9-Phase Zero-Downtime Migration

```
Phase 1: Create new profiles (--no-skills) — no disruption
Phase 2: Install SOUL.md files
Phase 3: Install skills (selective seed + pinning)
Phase 4: Configure models per profile
Phase 5: Discord restructure (channels + bots)
Phase 6: Initialize Kanban board
Phase 7: Migrate cron jobs
Phase 8: Testing (per-profile + integration + Discord)
Phase 9: Decommission old profiles (7-day hold)
```

**Critical rule:** Never remove old profiles until new ones are verified working. Keep backups at every phase.

### Skill Curation for New Profiles

1. `hermes profile create <name> --no-skills` — start clean
2. Copy only relevant skills from source profiles
3. Evaluate external skill repos (Magnus, iknowkungfu, community) — see `references/external-skill-repo-evaluation.md` for the evaluation framework and case study
4. Pin critical skills: `hermes --profile <name> curator pin <skill>`
5. Let curator manage lifecycle (stale 30d → archive 90d)

### Large Profile Handling (100+ skills)

For profiles with massive skill catalogs (cyber-red: 230, cyber-blue: 530):
- Use `--no-skills` + selective seeding
- Organize into subdirectories by sub-domain
- Agent sees only relevant subdirectory when navigating
- Pin top 5 most critical skills
- Consider splitting into sub-profiles if token budget exceeds limits

## Skill Installation (Phase 3)

Phase 3 is the heaviest lift. Skills live in 3 locations (root, existing profiles, senna) and can be nested 2-3 levels deep. Use `find` to discover actual paths before writing copy commands — never trust the curation strategy document's paths verbatim.

For the full installation patterns, discovery scripts, batch copy approach, nested path gotchas, and Anthropic cybersecurity skills handling, see `references/skill-installation-patterns.md`.

## Pitfalls

- **`--no-skills` still installs bundled category directories.** `hermes profile create <name> --no-skills` creates ~20-30 category subdirectories (apple, creative, software-development, etc.) with `DESCRIPTION.md` files but no actual skill content. This is expected — don't treat it as "something went wrong." The profile is ready for selective seeding.
- **Skills can be nested 2-3 levels deep.** The curation strategy may list `mlops/llama-cpp` but the actual path is `mlops/inference/llama-cpp/`. Common in mlops (inference/training/evaluation/models/research subdirectories). Always `ls` the category directory before writing copy commands. See `references/skill-installation-patterns.md` for the full gotcha table.
- **Many skills exist ONLY in senna's profile, not in root.** Senna accumulates skills from all domains. Skills like `coding-size-limits`, `debug-artifact-cleanup`, `look-before-edit`, `pre-commit-security-checklist`, and all 27 `unreal-engine/ue-*` skills are only in `~/.hermes/profiles/senna/skills/`. When installing to new profiles, check senna as a source, not just root.
- **Gateway can go down mid-redesign.** Long multi-session work via Discord is vulnerable to gateway restarts (hermes update, crashes, manual shutdown). BEFORE any gateway-sensitive operation: (1) save all drafted files to filesystem, (2) save planning state to Mnemosyne + legacy memory, (3) write strategy/implementation docs to `~/.hermes/profiles/<coordinator>/cache/documents/`. The Discord session is ephemeral — the files persist.
- **Review Hermes docs before finalizing profile designs.** New features (kanban, delegation roles, MCP filtering, `--no-skills`, curator pinning) may change the architecture. Pull docs from `hermes-agent.nousresearch.com/docs` and the `hermes-agent` skill before locking decisions. User explicitly said: "before we do anything, lets review the hermes agent docs completely to see whats all in hermes that could be newer than our last setup."
- **Defer non-blocking decisions explicitly.** UE5 server (separate vs section), voice channel (ElevenLabs TBD), cyber-blue split strategy — mark as `[DEFERRED]` with rationale, don't block the redesign on unresolved questions. User said: "if it flags issues then we will address it."
- **Don't rename profiles while cron jobs reference them.** Update cron first, then rename.
- **Don't assume all profiles need a bot.** Most workers are Senna-subordinated.
- **Don't over-plan.** Start, flag issues, address them. "If it flags issues then we will address it."
- **Don't skip the backup step.** Always create a full backup before migration phases.
- **When delegating bulk SOUL.md drafting, lock format spec in the prompt.** Subagents will inject inconsistencies: PersRubric `=` vs `:` delimiters, sub-profile routing in merged profiles, legacy name references. Always specify: (1) PersRubric uses `:` and spaces, (2) merged profiles don't route to sub-profiles that no longer exist, (3) team rosters use new profile names only. Run a consistency pass after batch delivery.
- **`read_file` in execute_code deduplicates.** If you read a file, then write it, then try to read it again in the same execute_code script, `read_file` returns `content_returned: false` with a "file unchanged" message. Use `terminal("cat <path>")` instead for re-reads within scripts.
- **`find` output can be garbled in `execute_code`.** The `find` command's output sometimes gets mangled when run inside `execute_code` scripts — line counts appear as `1F 1D:` prefixes instead of clean paths. Use `terminal()` directly for discovery commands.
- **`maxdepth` filter affects skill counts.** When counting skills in cyber-red/cyber-blue, `find -maxdepth 2` shows only 6-7 directories because the Anthropic skills are nested deeper. Use `maxdepth 1` on the Anthropic skills subdirectory itself to get the real count (755).
- **Cron jobs use channel IDs, not profile names.** The `deliver` field in cron jobs uses Discord channel IDs (e.g., `discord:1508955965087551745`), not profile names. Changing profile names or assignments doesn't break cron delivery. This contradicts earlier risk assessments — the actual migration risk for cron is **none**.
- **Discord admin requires gateway session.** The `discord_admin` toolset is only available through the Discord gateway adapter where the bot token is accessible. CLI sessions can't access the bot token. Workaround: prepare commands for user to paste in Discord where the gateway has admin access.
- **Don't forget cross-profile memory design.** Mnemosyne private vs shared, Fabric, kanban comments — each has different visibility.
- **Token budget matters.** cyber-blue with 530 skills will blow up context. Use progressive disclosure + subdirectory organization.
- **Model assignment per profile.** Not all profiles need the same model. Use cheaper models for lightweight workers.
- **The user wants Senna as single reporting channel.** All specialist output flows through Senna. Don't set up direct user-to-worker paths unless explicitly asked.
- **`hermes profile create` seeds builtin skills but NOT config.yaml or .env.** The create command gives you SOUL.md and category directories with builtin skill stubs, but config.yaml and .env must be written manually. If `hermes profile list` shows a profile with a default model, that's Hermes' fallback — not a real config. Always write config.yaml explicitly. See `profile-bootstrapping` skill's `references/batch-config-generation.md` for the batch generation pattern.
- **Hermes has an internal secrets store separate from .env files.** API keys stored via `hermes config set` or the setup wizard are visible via `hermes config show` but not readable as plaintext. Profiles may access these keys without .env files. Don't block on missing .env — verify with a smoke test instead.
- **Nous Portal free tier (deepseek-v4-flash:free) is no longer available (as of June 2026).** Use OpenRouter free models instead. OpenRouter has 26 free models including Owl Alpha (1M context, tools) and DeepSeek V4 Flash. Rate limits: 20 req/min, 200 req/day per model.
- **Magnus skills come from a separate git repo.** `git.brandyapple.com/magnus/agent-skills` — not in the iknowkungfu registry. Clone, then copy to profile's `skills/magnus/` directory. See `profile-bootstrapping` skill's `references/magnus-skill-installation.md` for the full inventory and installation pattern.

## References

See `references/17-profile-case-study.md` for the full case study: profile list, SOUL.md samples, Discord architecture, Kanban design, implementation plan.

See `references/external-skill-repo-evaluation.md` for the evaluation framework when assessing third-party skill repos (Magnus, iknowkungfu, community), including the Magnus case study with per-profile installation results and Windows team applicability matrix.

See `references/batch-soul-drafting-pitfalls.md` for pitfalls and fixes when delegating bulk SOUL.md drafting to subagents — format inconsistency, legacy names, orchestrator vs worker sections, and the post-delivery consistency pass.

See `references/skill-installation-patterns.md` for the actual skill discovery process, batch installation scripts, nested path gotchas, and Anthropic cybersecurity skills handling.

See `references/gateway-interruption-recovery.md` for the save-before-restart checklist and recovery playbook when the gateway goes down mid-redesign — what to save, where, and how to resume.

See the `hermes-soul-authoring` skill for SOUL.md templates, PersRubric calibration, compressed DSL techniques, and the 16-point critical review checklist.
