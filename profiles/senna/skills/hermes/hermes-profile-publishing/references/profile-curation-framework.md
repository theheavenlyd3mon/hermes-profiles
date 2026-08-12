# Profile Curation Framework

Decision framework for what skills belong in a public profile repo vs a live profile. From the hermes-profiles build (2026-06-15).

## The Core Question

For each skill, ask: **Does this help someone who ISN'T me?**

- YES → include in repo
- NO → remove from repo, keep on live profile

## Three Categories

### Always Include (General-Purpose)

These skills work for anyone, regardless of their specific setup:

- **Domain methodology:** github, docker, arxiv, research-pipeline, test-driven-development, clean-code, clean-architecture
- **Framework skills:** strategy models (blue-ocean, lean-startup, jobs-to-be-done), design patterns, debugging protocols
- **Tool integrations with broad adoption:** spotify, himalaya, jupyter, comfyui, excalidraw
- **Hermes meta-skills:** hermes-security-audit, profile-bootstrapping, gateway-fleet-ops (people using Hermes need these)

### Consider Removing (Personal/Niche)

These skills are tied to the publisher's specific setup:

| Pattern | Reason | Example |
|---------|--------|---------|
| Platform-specific | Excludes users on other platforms | apple/* (Mac-only), windows-isolated-dev-environment |
| Internal tooling | Publisher-specific workflow | dogfood, iknowkungfu-contrib |
| Personal infrastructure | Tied to publisher's hardware/services | yuanbao (specific chat platform), custom integrations |
| Skills user doesn't use | May have quality issues if never tested | — |

### Consider Keeping (General-Purpose Even If User Doesn't Use)

These seem personal but serve a community:

| Pattern | Reason to Keep | Example |
|---------|---------------|---------|
| API integrations for tools the user doesn't use | Other users of those tools benefit | notion-* in knowledge profile |
| Niche domain skills | Small but dedicated community | UE5, game-dev, blender |
| Third-party skill collections | High quality, well-maintained | Anthropic Cybersecurity Skills |

## Orchestrator Curation

The orchestrator (senna) is the hardest profile to curate because it inherits everything.

**Live orchestrator:** Needs all domain skills to route work correctly. 200+ skills is normal.

**Public orchestrator:** Should be lean. Keep:
- Orchestration skills (hermes/*, devops/orchestrator, kanban)
- Cross-domain utilities (github, software-development/*)
- Meta-skills (profile management, security audit)

Strip from public orchestrator:
- Domain-specific skills (creative/*, mlops/*, gaming/*, financial-markets/*, unreal-engine/*)
- These belong on the domain profiles, not the orchestrator

**Why:** Someone grabbing a public orchestrator wants a fleet manager, not a dump of every skill. They'll install domain skills on their domain profiles.

## Profile-by-Profile Curation Notes (hermes-profiles repo)

| Profile | Removed | Reason |
|---------|---------|--------|
| senna | apple/*, unreal-engine/*, game-dev/*, notion-*, yuanbao, dogfood, iknowkungfu-contrib | Personal/niche for orchestrator |
| code | hermes-s6-container-supervision, debugging-hermes-tui-commands | Hermes-specific infra |
| cyber-blue | (kept light at 2 skills) | Full Anthropic set available separately |
| knowledge | (kept notion-*) | General-purpose for Notion users |
| cyber-red | (kept all 162 Anthropic skills) | Apache 2.0 licensed, valuable collection |

## Live vs Repo Divergence

**This is intentional, not a problem.** After publishing, the live profile will have more skills than the repo version. That's correct:

- Live: has everything the user actually needs
- Repo: has what's useful and appropriate for public sharing

Don't try to sync them. Don't feel pressure to remove skills from the live profile just because they're not in the repo.
