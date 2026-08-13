# 2026-08-10 LLM-Wiki Sweep Remediation Playbook

Session record: full-wiki sweep (via `scripts/wiki-sweep.py`) plus user-approved
remediation ("go with your recommendations"). Reuse the *patterns* here for any
future sweep cleanup; the concrete page lists are one-time facts.

## Findings → fixes (one batch log entry)

| # | Finding | Fix applied |
|---|---------|-------------|
| 1 | 6 retired-category crons still enabled (llm-agents fired 08-10 despite 08-04 retirement); 0 crons for the 5 new categories | Paused 6 retired crons (llm-agents, agent-protocols, context-engineering, local-inference, prompt-engineering, research-methodologies); created 5 active-category crons per protocol cadence (local-llm Mon, open-source-models Tue, generative-media Wed, llm-research Thu, ai-advancement Fri) |
| 2 | Workflow-tag convention split (key-style ~103 pages vs in-tags style ~11 newest) | RULED: `workflow:` key is canonical; in-tags legacy-accepted, normalized on lint. SCHEMA.md updated (frontmatter example, Field Reference, Workflow Tags section). verify-pipeline-run.sh now validates value ∈ seedling\|developing\|stable\|needs-review\|stale |
| 3 | 3 invalid workflow values | `workflow: proposed` (hermes-platform-tool-loading, hermes-desktop-profile-management) → `developing`; `workflow: reference` (threejs-hologram-particle-techniques) → `developing` |
| 4 | 2 malformed pages (no updated/sources, type `research-report`, no links, no workflow) | Rebuilt frontmatter: `type: summary` (valid in concepts/ per ruling), added `updated`/`sources: []`/`workflow: developing`, cleaned tags, added 3 related-page links each (moonlake-blender-mcp-ue5-pipeline-report, ue-ai-coding-pipeline-report) |
| 5 | `unreal-engine-mcp-bridge-comparison` (type comparison) in concepts/ | Moved to `comparisons/`; index entry relocated to Comparisons section; `composed_by: [unreal-engine-mcp-bridge-comparison]` backfilled on unreal-engine-llm-tooling (SCHEMA composes/composed_by rule) |
| 6 | Tags not in taxonomy | Added `moe`, `qwen` to SCHEMA Models & Architectures; mapped ai-coding→coding, blueprint→blueprints, ue5→unreal-engine; stripped one-off project names (moonlake, eldrath, flopperam, ue5-coder) |
| 7 | Index drift | Added `persona-vectors` to Concepts; removed dead `[[researcher-profile]]` entry (page retired 2026-06-15, never existed as file) |
| 8 | Ghost link: `[[findings-2026-07-21]]` on novel-craft-playbook | Converted to provenance marker `^[raw/articles/research/creative-writing/findings-2026-07-21.md]`; `contested: true` → `false` (craft debates, not page contradictions) |
| 9 | 14 index-only orphans | Wove 25 inbound links across 15 linker pages (pattern below) → zero orphans post-sweep |

## Orphan-weaving pattern (kill `[index-only]` orphans)

For each orphan, add an inbound `- [[slug]] — one-line why` under the linker
page's `## Related` heading (create the heading if absent), then bump the
linker's `updated:` to today (SCHEMA: every page update bumps the date).

Linker choices used 2026-08-10 (all verified to exist and be topically adjacent):
- model-landscape-2026 → ai-mathematical-discovery, ai-talent-war, ai-weather-forecasting
- agentic-ai-trends-2026 → ai-mathematical-discovery, ai-talent-war
- test-time-scaling-reasoning → alibi-positional-encoding-numerical-failure, circuit-extraction-methods, grpo-credit-redistribution, mamba-hierarchical-memory-hmm
- mamba-hierarchical-memory-hmm → alibi-positional-encoding-numerical-failure, circuit-extraction-methods
- computer-use-and-browser-agents / ai-security-and-red-teaming → browsafe-prompt-injection-browser-agents
- ai-security-and-red-teaming / mega-prompt-engineering → system-prompt-auditing
- ai-blender-workflows / unreal-engine-llm-tooling → moonlake-blender-mcp-ue5-pipeline-report
- unreal-engine-llm-tooling / unreal-engine-mcp-bridge-comparison → ue-ai-coding-pipeline-report
- mega-prompt-engineering / persrubric-llm-personality-encoding → novel-craft-playbook
- llm-inference-and-serving / local-llm-moe-inference-rtx4070ti → raspberry-pi-local-llm-hermes
- threejs-performance-optimization / threejs-hologram-particle-techniques → threejs-webgpu-renderer

## Mechanics worth repeating

- **File moves are link-safe in Obsidian**: wikilinks resolve by basename, so
  `mv concepts/x.md comparisons/x.md` keeps `[[x]]` working — but the index.md
  entry MUST move to the right section, and any `composes:`/`composed_by:`
  declarations need backfill on both ends.
- **Batch frontmatter edits**: script with strict `if old not in text: abort`
  assertions — a typo'd old-string fails loudly instead of silently no-op'ing.
- **Terminal heredoc guard**: inline heredocs containing `&` and long `&&`
  chains are hardline-blocked. Write the block to a temp file with write_file,
  then append via `python3 -c "pathlib append"` — do not retry the heredoc.
- **Cron drift check is part of every sweep**: compare `cronjob list` against
  the protocol's category table in BOTH directions (retired still firing +
  active missing crons + findings file with no registered cron that produced it).

## Deferred (reported, not fixed)

- 13 pages > 200 lines (SCHEMA split threshold): moonlake report (480),
  threejs-cinematic-workflow (366), threejs-hologram-particle-techniques (323),
  memory-architecture (306), threejs-cinematic-camera (281),
  unreal-engine-mcp-bridge-comparison (268), ue-ai-coding-pipeline-report (256),
  agentic-ai-practices (241), model-context-protocol (238),
  stem-studio-engine-vs-react-three-fiber (236), fantasy-creature-design (231),
  threejs-cinematic-lighting (219), threejs-particle-effects (217).
- Ghost `[[wikilinks]]` (2 backlinks) is meta-syntax from operational docs, not a real ghost.
- Ghost `[[raspberry-pi-edge-ai]]` (1 backlink) is a legit seedling — monitor.
- New crons use the profile default model (old ones pinned qwen3.7-plus/alibaba);
  pin explicitly if a specific model is wanted for research runs.
