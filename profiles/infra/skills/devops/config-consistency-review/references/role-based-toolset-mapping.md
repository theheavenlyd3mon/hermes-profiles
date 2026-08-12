# Role-Based Toolset Mapping

Reference for right-sizing Hermes profile toolsets. Generated from a fleet audit
of 13 profiles (May 2026). Every profile had identical toolsets — this mapping
proposes role-appropriate trimming.

## Current Anti-Pattern

Every profile had the same blob:
`browser, clarify, code_execution, fabric, file, image_gen, kanban, memory,
messaging, moa, session_search, skills, terminal, todo, vision, web`

Same story for skills directories — every profile had identical categories
(apple, creative, data-science, devops, gaming, gifs, media, mlops, smart-home,
social-media, etc.) regardless of role.

## Proposed Toolset by Role

### Coordinator — Senna
Keeps everything. Full toolset for routing, delegation, and orchestration.
`browser, clarify, code_execution, computer_use, cronjob, delegation, fabric,
file, image_gen, memory, messaging, session_search, skills, terminal, todo,
vision, web, web-search-plus`

### Orchestrator — Foreman
Task management and delegation focused. No image gen, no web research.
`file, terminal, delegation, kanban, memory, messaging, session_search, skills,
todo`

### Implementation Workers
Code-focused. No image gen, no delegation, no messaging.

| Tool | coder | debugger | reviewer | security |
|------|-------|----------|----------|----------|
| file | ✓ | ✓ | ✓ | ✓ |
| terminal | ✓ | ✓ | ✓ | ✓ |
| code_execution | ✓ | ✓ | ✓ | ✓ |
| skills | ✓ | ✓ | ✓ | ✓ |
| web | ✓ | ✓ | ✓ | ✓ |
| vision | — | — | ✓ | ✓ |
| session_search | — | — | — | — |

### Research Workers
Web and analysis focused. No code execution, no image gen.

| Tool | researcher | oracle | data-analyst |
|------|-----------|--------|-------------|
| file | ✓ | ✓ | ✓ |
| terminal | ✓ | ✓ | ✓ |
| web | ✓ | ✓ | ✓ |
| skills | ✓ | ✓ | ✓ |
| browser | ✓ | ✓ | — |
| vision | ✓ | ✓ | ✓ |
| code_execution | — | — | ✓ |
| session_search | ✓ | ✓ | — |

### Design — Designer
Image gen is the core differentiator. Browser for visual reference.

`file, terminal, image_gen, skills, web, vision, browser`

### Infrastructure — DevOps
Terminal-heavy. No image gen, no delegation.

`file, terminal, code_execution, skills, web, vision`

### Knowledge — Secretary
Memory and messaging focused. No code execution, no image gen.

`file, terminal, skills, web, memory, session_search, messaging`

### System Design — Architect
Web research and file analysis. No code execution, no image gen.

`file, terminal, skills, web, vision, session_search`

## Tool Decision Matrix

| Tool | Who needs it | Who doesn't |
|------|-------------|-------------|
| file | Everyone | — |
| terminal | Everyone | — |
| skills | Everyone | — |
| web | Most roles | Pure coders (get tasks with context) |
| browser | Research, design, oracle | Coders, devops, security |
| vision | Design, review, analysis | Coders, foreman, secretary |
| code_execution | Coders, debugger, devops, security, data | Architect, researcher, oracle, designer, secretary |
| image_gen | Designer only | Everyone else |
| delegation | Coordinator, foreman | All workers |
| kanban | Foreman only | Everyone else |
| memory | Coordinator, foreman, secretary, oracle | Workers (session-scoped) |
| messaging | Coordinator, foreman, secretary | Workers |
| clarify | Coordinator only | Workers (get clear tasks) |
| computer_use | Coordinator (macOS) | Everyone else |
| cronjob | Coordinator only | Everyone else |
| todo | Coordinator, foreman | Workers |
| fabric | Coordinator, researcher | Most roles |
| moa | Unclear value — audit usage before keeping | — |

## Plugin-Backed Tools Checklist

For each plugin-backed tool, verify ALL THREE across every profile:

1. **Tool in platform_toolsets** — `grep "<tool>" config.yaml`
2. **Plugin in plugins.enabled** — `grep "<plugin/provider>" config.yaml`
3. **Config section** — `grep -A2 "^<tool>:" config.yaml`

Known plugin-backed tools:
- `image_gen` → plugins: `image_gen/fal`, `image_gen/krea`
- `fabric` → plugin: `fabric`
- `spotify` → plugin: `spotify`
- `web-search-plus` → plugin: `web-search-plus`

## Skills Directory Audit

Every profile had identical skill categories. Proposed trimming:

| Category | Architect | Coder | Debugger | Designer | DevOps | Foreman | Oracle | Researcher | Reviewer | Secretary | Security |
|----------|-----------|-------|----------|----------|--------|---------|--------|-----------|----------|-----------|----------|
| software-dev | ✓ | ✓ | ✓ | — | — | — | — | — | ✓ | — | — |
| creative | — | — | — | ✓ | — | — | — | — | — | — | — |
| devops | — | — | — | — | ✓ | ✓ | — | — | — | — | — |
| research | — | — | — | — | — | — | ✓ | ✓ | — | — | — |
| financial | — | — | — | — | — | — | ✓ | — | — | — | — |
| github | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| security | — | — | — | — | — | — | — | — | — | — | ✓ |
| productivity | — | — | — | — | — | — | — | — | — | ✓ | — |
| hermes | — | — | — | — | — | ✓ | — | — | — | — | — |
| data-science | — | — | — | — | — | — | — | — | — | ✓ | — |
