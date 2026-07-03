# Example: Second Brain / LLM Agent Knowledge Schema

This is a concrete SCHEMA.md created for an LLM wiki focused on "second brain /
LLM agent knowledge." Use as a template for similar domains.

## Domain

LLM Agent knowledge — a persistent second brain for agents, architectures, tools,
security, and research in the LLM agent ecosystem.

## Tag Taxonomy (20 tags, 5 categories)

### Models & Architectures
- `model` — specific LLM or AI model
- `architecture` — model or system architecture pattern
- `training` — training methods, data, compute
- `inference` — serving, optimization, quantization

### Agents & Systems
- `agent-pattern` — agent design patterns (ReAct, Plan-and-Execute, etc.)
- `multi-agent` — multi-agent systems, orchestration, delegation
- `tools` — tool use, function calling, MCP
- `memory` — memory systems, RAG, KV cache

### Infrastructure
- `security` — hardening, threat model, secrets management
- `deployment` — deployment, hosting, scaling
- `monitoring` — observability, logging, alerting
- `config` — configuration, env setup, toolchains

### Knowledge
- `research` — papers, benchmarks, findings
- `concept` — foundational concept or term
- `entity` — person, organization, product, project
- `comparison` — side-by-side analysis

### Operations
- `workflow` — processes, pipelines, routines
- `handoff` — agent-to-agent or agent-to-human handoff protocols
- `decision` — architectural or design decisions with rationale
- `convention` — conventions, style guides, standards

## Hermes Multi-Agent Integration

This wiki lives inside a shared Obsidian vault that all Hermes agents access:

- **Agent access:** Every Hermes profile (Senna, Foreman, Coder, etc.) shares
  the same `OBSIDIAN_VAULT_PATH` and `WIKI_PATH`. The wiki is readable and
  writable by all agents.
- **Secretary role:** The Secretary agent owns index.md and log.md maintenance.
  Other agents write knowledge pages; Secretary handles navigation upkeep.
- **Icarus promotion:** Durable facts from Icarus fabric entries that survive
  multiple sessions should be promoted to wiki pages.
- **Team-Wiki boundary:** `Team-Wiki/` covers operational structure (agents,
  handoffs, protocols). `LLM-Wiki/` covers knowledge (concepts, research,
  entities). They cross-link via `[[wikilinks]]` where useful.
- **Curator pre-approval:** The human curator wants to approve new pages before
  they are created. Present proposed additions as a categorized list; do not
  write pages until explicitly approved.
