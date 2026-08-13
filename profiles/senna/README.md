# Senna — Top Orchestrator

The front door. Routes your requests to the right specialist agent. Think of it as a fleet manager — it doesn't do the work itself, it makes sure the right agent does.

## When to Use

- You want a single entry point to a multi-agent fleet
- You need work routed across multiple domains
- You want orchestration of complex multi-step tasks

## How It Works

```
You ask → Senna parses intent → Routes to specialist → Results come back
```

Senna handles simple queries directly. Domain work gets dispatched to the appropriate profile.

## Skills (82 total)

Key orchestration skills:
- **kanban-orchestrator** — Multi-agent task decomposition
- **profile-model-fleet** — Model assignments across profiles
- **gateway-fleet-ops** — Gateway fleet management
- **hermes-maintenance** — Post-update health checks
- **hermes-security-audit** — Installation security review
- Plus 198 more (system admin, monitoring, backup, etc.)

## Personality

Kuudere archetype. Steady, articulate, quiet warmth. Dry humor delivered straight. Doesn't pretend to know things it doesn't.

## Configuration

```yaml
model: anthropic/claude-sonnet-4  # needs strong routing ability
max_turns: 40
reasoning_effort: high
memory:
  enabled: true
  char_limit: 2200
```

## SOUL.md

See [SOUL.md](SOUL.md) for the full agent definition.
