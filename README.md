# Hermes Agent — Profile Collection

A curated set of [Hermes Agent](https://hermes-agent.nousresearch.com/docs) profiles — specialized AI agents with distinct personalities, methodologies, and skills. Mix, match, or use individually.

## What's In Here

```
profiles/
  senna/          — Top orchestrator. Routes work to specialists. Fleet manager.
  code/           — Implementation, debugging, code review. Tests are contracts.
  creative/       — Design, art, UI/UX, media generation. Aesthetics matter.
  research/       — Investigation, data gathering, academia. Evidence-based.
  security/       — Audit, vulnerability management, compliance. Assume breach.
  finance/        — Trading, market analysis, trade signals. Probabilistic.
  knowledge/      — Obsidian vaults, docs, wikis. Structured knowledge.
  infra/          — DevOps, containers, networking, monitoring. Runbook-style.
  communication/  — Email, messaging, meeting summaries. Discreet.
  social/         — Social media, content creation, engagement. Authentic voice.
  homelab/        — Smart home, IoT, monitoring. Set and forget.
  mlops/          — ML training, fine-tuning, inference, evaluation. Reproducible.
  business/       — Strategy, marketing, product. Framework-driven.
  media/          — Media library, music, gaming. Quality curation.
  cyber-red/      — Offensive security. Pen testing, red team, exploit dev.
  cyber-blue/     — Defensive security. SOC, IR, forensics, compliance.
  cyber-blue-cloud/     — Cloud security. IAM, misconfiguration, runtime signals.
  cyber-blue-compliance/ — Compliance & audit. Policy-as-code, evidence packs.
  cyber-blue-forensics/ — Forensics & IR. Preservation, acquisition, timeline.
  cyber-blue-soc/       — SOC & detection. Triage, rule tuning, runbooks.
  educate/        — Teaching design. Adaptive tutoring, lessons, workshops.
```

Each profile contains:
- **SOUL.md** — The agent's identity, personality, methodology, and output standards
- **skills/** — Domain-specific skills that give the agent its capabilities

## Quick Start

### 1. Pick a profile

Browse the directories above. Each has a README.md explaining what it does and when to use it.

### 2. Create the profile in Hermes

```bash
hermes profile create <profile-name>
```

### 3. Copy the SOUL.md

```bash
cp profiles/<profile-name>/SOUL.md ~/.hermes/profiles/<profile-name>/SOUL.md
```

### 4. Install the skills

Copy the skills directory into your Hermes profile:

```bash
cp -r profiles/<profile-name>/skills/* ~/.hermes/profiles/<profile-name>/skills/
```

Or install individual skills from the [Hermes skill registry](https://hermes-agent.nousresearch.com/docs):

```bash
hermes skill install <skill-name> --profile <profile-name>
```

### 5. Configure

Edit `~/.hermes/profiles/<profile-name>/config.yaml`:

```yaml
model: deepseek/deepseek-chat    # or anthropic/claude-sonnet-4, openai/gpt-4o, etc.
max_turns: 30
reasoning_effort: high
memory:
  enabled: true
```

### 6. Run

```bash
hermes chat --profile <profile-name>
```

## Multi-Agent Fleet

The real power is running multiple profiles together. Senna acts as the front door — it routes your request to the right specialist.

```
You ask a question
    → Senna parses intent, identifies the domain
    → Routes to the right specialist profile
    → Specialist does the work
    → Results flow back through Senna to you
```

To set up a fleet:
1. Create the profiles you need
2. Copy SOUL.md and skills for each
3. Run Senna as your primary profile
4. Other profiles run as workers/orchestrators on their domains

## Profiles: Orchestrators vs Workers

| Type | Role | Examples |
|------|------|----------|
| **Orchestrator** | Manages a domain, delegates to workers | code, creative, research, security, infra, mlops |
| **Worker** | Does focused work, reports up | finance, knowledge, homelab, media, social, communication, business, cyber-red, cyber-blue, cyber-blue-cloud, cyber-blue-compliance, cyber-blue-forensics, cyber-blue-soc, educate |
| **Top Orchestrator** | Routes across all domains | senna |

## Customization

Every SOUL.md is meant to be edited. The personality rubric, routing rules, and quality gates are starting points — tune them to your workflow.

Common customizations:
- Change `Report→Orchestrator` to point at your actual orchestrator name
- Adjust the `PersRubric` personality scores (0-100 per trait)
- Add/remove skills for your specific needs
- Modify `DEFAULTS` for your environment
- Add `Cron Duties` sections for scheduled tasks

## Guides

- [Getting Started With Hermes Profiles](guides/getting-started-with-hermes-profiles.md) — Beginner orientation: profiles, model choices, fleet composition, `PersRubric`, token compression, `educate` usage
- [Research Profile Guide](guides/research-profile-guide.md) — Full walkthrough for setting up a research agent

## What's NOT In Here

- No personal paths, Discord channels, or API keys
- No environment-specific config (your config.yaml stays in your ~/.hermes)
- No runtime state (logs, databases, session history)

Everything here is portable. Copy what you need, customize what you use.

## Third-Party Skills

This repo includes skills from the following open-source projects:

### Anthropic Cybersecurity Skills
- **Author:** Mahipal (mukul975)
- **Repo:** [github.com/mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)
- **License:** [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- **Used in:** cyber-red, cyber-blue profiles
- **Description:** 753 cybersecurity skills covering pen testing, forensics, threat intel, IR, cloud security, and more.

## License

MIT for the profile definitions (SOUL.md files, READMEs, guides). Third-party skills retain their original licenses (see above).
