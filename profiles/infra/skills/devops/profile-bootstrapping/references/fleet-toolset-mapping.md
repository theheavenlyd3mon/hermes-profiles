# Fleet Toolset Mapping (2026-05-27)

Role-based toolset assignments for the 8 Discord bots. Each profile's `platform_toolsets.cli`, `plugins.enabled`, and `known_plugin_toolsets.cli` are aligned to its role.

## Toolset Matrix

| Tool | senna | architect | coder | designer | foreman | oracle | researcher | secretary |
|------|-------|-----------|-------|----------|---------|--------|------------|-----------|
| browser | ✓ | — | — | ✓ | — | ✓ | ✓ | — |
| clarify | ✓ | — | — | — | — | — | — | — |
| code_execution | ✓ | — | ✓ | — | — | — | — | — |
| computer_use | ✓ | — | — | — | — | — | — | — |
| cronjob | ✓ | — | — | — | — | — | — | — |
| delegation | ✓ | — | — | — | ✓ | — | — | — |
| fabric | ✓ | — | — | — | — | ✓ | ✓ | ✓ |
| file | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| image_gen | ✓ | — | — | ✓ | — | — | — | — |
| kanban | — | — | — | — | ✓ | — | — | — |
| memory | ✓ | — | — | — | ✓ | ✓ | — | ✓ |
| messaging | ✓ | — | — | — | ✓ | — | — | ✓ |
| moa | — | — | — | — | — | — | — | — |
| session_search | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| skills | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| terminal | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| todo | ✓ | — | — | — | ✓ | — | — | — |
| vision | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| web | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| web-search-plus | ✓ | — | — | — | — | — | — | — |

## Plugins per Profile

| Profile | plugins.enabled |
|---------|----------------|
| senna | browser/browser_use, browser/browserbase, browser/firecrawl, dashboard_auth/nous, disk-cleanup, hermes-lcm, icarus, image_gen/fal, image_gen/krea, katana, rtk-rewrite, web-search-plus, web/brave_free |
| architect | disk-cleanup, icarus, hermes-lcm |
| coder | disk-cleanup, icarus, hermes-lcm |
| designer | disk-cleanup, icarus, hermes-lcm, image_gen/fal, image_gen/krea |
| foreman | disk-cleanup, icarus, hermes-lcm |
| oracle | disk-cleanup, icarus, hermes-lcm, fabric |
| researcher | disk-cleanup, icarus, hermes-lcm, fabric |
| secretary | disk-cleanup, icarus, hermes-lcm, fabric |

## Decision Rationale

- **messaging** — only foreman (dispatching tasks, notifying about blockers) and secretary (pushing docs/summaries). Worker bots respond when called, they don't initiate.
- **memory** — only foreman (project state, conventions), secretary (knowledge base, user preferences), oracle (watchlists, trade history, market context). Workers' work is in the codebase, not memory.
- **fabric** — only oracle (market analysis patterns), researcher (content extraction, summarization), secretary (document processing). Specialized prompt framework, not a general need.
- **browser** — only designer (checking design references), oracle/researcher (navigating live sites for market data and research).
- **image_gen** — only designer. The UI/Graphics specialist.
- **delegation** — only foreman and senna. Workers should never spawn children.
- **kanban** — only foreman. Task board management is orchestration.
- **vision** — roles that process images: designer, oracle, researcher, secretary, plus architect/coder for diagrams.
- **moa** — dropped from all workers. Mixture-of-Agents is a coordinator-level capability.
- **clarify** — dropped from all workers. Workers get clear tasks from the foreman, they don't ask questions.
- **spotify** — dropped from all workers. Not relevant to any role's core function.
- **todo** — only foreman. Task tracking is orchestration.
