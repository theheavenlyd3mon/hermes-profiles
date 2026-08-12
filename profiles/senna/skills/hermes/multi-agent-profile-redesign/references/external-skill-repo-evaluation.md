# External Skill Repository Evaluation

Pattern for evaluating third-party skill repos and mapping skills to fleet profiles.

## Evaluation Framework

When a user shares an external skill repository (Forgejo, GitHub, etc.), evaluate each skill on three axes:

| Axis | Question | Scale |
|------|----------|-------|
| **Relevance** | Does this skill cover a domain the fleet actually operates in? | ⭐-⭐⭐⭐⭐⭐ |
| **Uniqueness** | Does this add capability we don't already have? | High/Medium/Low/Duplicate |
| **Quality** | Is the SKILL.md well-structured? Does it have scripts/references? | Rich/Standard/Minimal |

### Relevance Tiers

| Tier | Meaning | Action |
|------|---------|--------|
| ⭐⭐⭐⭐⭐ Must-Have | Core infrastructure or universal methodology | Install immediately |
| ⭐⭐⭐⭐ High | Directly useful for active projects/domains | Install, assign to profile |
| ⭐⭐⭐ Medium | Useful in specific contexts, not daily driver | Install if capacity allows |
| ⭐⭐ Low | Niche, enterprise-only, or outside fleet scope | Skip |
| ⭐ Very Low | Domain not in fleet stack at all | Skip |

### Profile Assignment Process

1. **List all fleet profiles** and their domains
2. **For each high-relevance skill**, ask: "Which profile's domain does this serve?"
3. **Check for duplicates** — does the fleet already have an equivalent skill?
4. **Check platform compatibility** — does the skill require tools/OS the target profile has?
5. **Map skill → profile** with rationale
6. **Generate sync commands** for installation

## Case Study: Magnus Agent-Skills (June 2026)

**Repo:** `git.brandyapple.com/magnus/agent-skills` — 40 curated skills, MIT licensed.

### Installation Results (Mac Fleet)

| Magnus Skill | Installed To | Rationale |
|---|---|---|
| systematic-debugging | 11 profiles (all coding + analytical) | Universal 4-phase debugging methodology. "Rule of Three" (3+ failed fixes → question architecture). |
| data-scientist | oracle | PhD-level statistics for market analysis. Causal inference, power analysis, experimental design. |
| software-architecture-analysis | coder | Reverse-engineer codebases, produce design docs, Mermaid diagrams. |
| epub | secretary | Ebook → Obsidian knowledge pipeline via `epub-extract-knowledge --format atoms`. |
| cli-builder | senna | Design patterns for agent-built CLI tools (non-interactive, --json, --dry-run). |
| agent-skills | senna | Foundation standard reference for the Agent Skills spec. |
| opensource-contributions | senna | Contribution etiquette + agent transparency disclosure requirement. |
| forgejo-cli | senna | Forgejo API wrapper for the fleet's own git infrastructure. |
| nous-branding | senna | Nous Research brand identity guide (cyber-classical aesthetic). |

### Skills Evaluated But Not Installed (Mac)

| Magnus Skill | Why Skipped |
|---|---|
| confluence-cli, jira-cli, jira-jql | Enterprise tools not in fleet stack |
| ghost-cli, peertube, transistor | Platforms not in use |
| raleigh, tempest-cli | Niche hardware/location-specific |
| brand-designer | Low priority — branding not daily work |
| kanban-guru | Process-heavy methodology, fleet prefers terse/TUI |
| lastfm, openlibrary-cli | Fun but not core work domains |
| data-architect | Enterprise/organizational, not personal trading |

### Skills Useful for Windows Team (Game Dev Profiles)

Windows profiles: ue5-coder, blender-coder, threejs-coder, designer

| Magnus Skill | Useful? | Notes |
|---|---|---|
| systematic-debugging | ✅ Yes | Universal. "Rule of Three" essential for UE5 debugging loops. |
| software-architecture-analysis | ✅ Yes | UE5 plugin/module analysis, reference implementation study. |
| cli-builder | ✅ Yes | If building CLI tools or scripts on Windows side. |
| agent-skills | ✅ Yes | Foundation standard for creating new skills. |
| opensource-contributions | ⚠️ Maybe | If contributing to UE5 plugins, Blender addons, Three.js libs. |
| forgejo-cli | ⚠️ Maybe | Only if using Forgejo for game project repos (vs GitHub). |
| data-scientist | ❌ No | Trading/statistics focused, not game dev. |
| epub | ❌ No | Obsidian pipeline, Windows team doesn't maintain vault. |
| nous-branding | ❌ No | Nous Research specific, not game dev. |
| Tailscale bundle (7 skills) | ✅ Yes | Mesh VPN for remote access to Windows PC. Critical infra. |

### High-Value Clusters Not Yet Installed

These Magnus skill clusters were identified as high-value but not yet installed:

1. **Media Pipeline:** tmdb-cli → trakt → arr-cli (Radarr/Sonarr) + lidarr-cli → prowlarr-cli → jellyfin-cli — Full media discovery/acquisition/playback stack. Install when media server is set up.

2. **Tailscale Bundle:** tailscale-client → headscale-deploy → headscale-node-lifecycle → tailnet-policy → headscale-routing → headscale-derp → headscale-backup — Complete self-hosted VPN. Install when remote fleet access is needed.

## Output Format

When presenting evaluation results to the user, use this structure:

1. **Summary table** — all skills grouped by relevance tier
2. **Installation map** — skill → profile with rationale
3. **Skipped skills** — with reason (prevents re-evaluation later)
4. **Deferred clusters** — high-value groups to install when prerequisites are met
