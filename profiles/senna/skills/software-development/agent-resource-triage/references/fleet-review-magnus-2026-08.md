# Fleet-wide review: magnus919/agent-skills (2026-08-03)

Full fleet-gap mapping for the GitHub mirror of the Forgejo source
(git.brandyapple.com/magnus/agent-skills, reviewed 2026-05/06).
Repo state at review: 114 top-level SKILL.md + 7 bundles, 494 commits,
v0.6.0, MIT, active daily, heavily agent-assisted. Growth since May:
~40 skills → 132 SKILL.md total; bundles + plugin packaging (codex/claude)
+ CI + eval_runner Python eval harness + evals.json in 30+ skills.

## Already in fleet (27 — no action, versions current)
- business: brand-designer, confluence-cli, ghost-cli, jira-cli, jira-jql,
  raleigh, yc-default-alive-calculator, yc-weekly-growth-compass
- code: cli-builder, forgejo-cli, software-architecture-analysis,
  systematic-debugging
- creative: nous-branding (TWO copies: 1.1.0 keep, 1.0.0 stale)
- finance: data-scientist
- infra: kanban-guru, tempest-cli
- knowledge: epub, gutenberg, linear, openlibrary-cli
- media: jellyfin-cli, lastfm, peertube, tmdb-cli, trakt, transistor
- mlops: dspy
- research: data-architect, data-scientist
- senna: cli-builder, systematic-debugging
- llama-cpp: secretary, mlops, all four cyber-blue profiles

## Tier-A adds (agreed recommendation, not yet installed)
- code: backend-engineering, frontend-engineering, api-design-and-evolution,
  qa-methodology, spec-driven-development, implementation-planning,
  secure-software-engineering, verification-methodology,
  programming-principles, adr-authoring, c4-diagramming,
  opensource-contributions
- infra: kubernetes, docker-compose, traefik, grafana, restic,
  cncf-landscape, remote-systems-administration, site-reliability-
  engineering, production-readiness, release-engineering,
  incident-learning, resilience-and-recovery, capacity-and-cost-engineering,
  migration-engineering, technology-radar
- homelab: docker-compose, restic, esp32-development, crowdsec,
  remote-systems-administration
- mlops: agent-evals-and-observability, ml-engineering, langchain,
  llamaindex, pydanticai, langgraph, verification-methodology
- research: research-methodology, artifact-pyramids, flaresolverr,
  flaresolverr-cli, de-spin
- knowledge: technical-documentation, mermaid-diagrams, c4-diagramming,
  open-knowledge-format
- finance: financial-modeling
- business: go-to-market, strategy-frameworks, financial-modeling,
  legal-strategy, technology-radar
- creative: color-management
- novel: cyberpunk (Sprawl literary-mode skill — fiction craft)
- security: security-audit-methodology, secure-software-engineering
- cyber-blue-compliance: privacy-engineering
- cyber-red + cyber-blue-forensics: binary-analysis (Ghidra CLI wrapper)
- communication: fireflies
- senna: verification-methodology, agent-evals-and-observability,
  technology-radar, adr-authoring, opensource-contributions

## Bundles (owner profile)
- agent-production-operations → senna (runtime control plane, 7 evals)
- neckbeard → code (change-delivery w/ evidence ledger)
- production-excellence → infra
- research-and-vault → research + knowledge
- workflow-architect → senna (low priority)
- product-lifecycle → business (optional, big pile)
- tailscale → infra only if self-hosting Headscale

## Fleet hygiene noted (separate from repo)
Duplicates inside single profiles: code (codebase-inspection x2,
systematic-debugging x3, github-auth x2, subagent-driven-development x2),
creative (nous-branding x2, baoyu-* x2, design-md x2, manim-video x2),
knowledge (obsidian x2, ocr-and-documents x2, vault-audit x2),
finance (oracle-* x2-4), media (several x2), gamehub-mod/security
(godmode x2).

## Verified techniques
- Regex frontmatter parse misses folded `>-` descriptions — unfold by
  accumulating indented lines.
- Overlap must be computed against union of ALL profile skill dirs, not
  the current profile; senna-only diff said "112 new" when true
  fleet-wide novelty was ~87 with 27 already placed.
- Version check: remote SKILL.md often has NO version field — compare
  file sizes; local copies of the overlaps were all current.
