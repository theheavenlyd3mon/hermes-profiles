---
name: notion
description: "Notion API + agent integration patterns: databases, pages, MCP, External Agents API, agent logbook, research landing zone, decision log, task inbox, cost tracker, cron registry, agent inventory. Routes to focused sub-skills."
version: 3.1.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Productivity, Notes, Database, API, Integration, Agents]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-databases, notion-pages, notion-blocks, notion-search, notion-agent-logbook, notion-decision-log, notion-research-zone, notion-cron-registry, notion-cost-tracker, notion-task-inbox, notion-agent-inventory, native-mcp]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Integration

The Notion skillset is decomposed into focused sub-skills for specific operations. Load this skill for overview and routing.

## Quick Reference

| Task | Load this skill |
|------|----------------|
| Auth setup, curl basics, property types | `notion-api-basics` |
| Create/query/update databases | `notion-databases` |
| CRUD pages and database entries | `notion-pages` |
| Append/read page content blocks | `notion-blocks` |
| Search workspace | `notion-search` |
| Log agent activity to Notion | `notion-agent-logbook` |
| Log decisions (config/model changes) | `notion-decision-log` |
| Log research results | `notion-research-zone` |
| Register/track cron jobs | `notion-cron-registry` |
| Track API costs | `notion-cost-tracker` |
| Manage task inbox | `notion-task-inbox` |
| Track agent profiles | `notion-agent-inventory` |
| Notion MCP setup | `references/notion-mcp-setup.md` |
| Notion Workers platform | `references/notion-workers-platform.md` |

## Connection Methods

| Method | When to use | Setup |
|--------|-------------|-------|
| REST API via curl | Ad-hoc tool calls, cron jobs | NOTION_API_KEY in .env |
| Notion MCP (hosted) | Full workspace via MCP clients | OAuth + config.yaml |
| External Agents API (alpha) | Embed Hermes inside Notion | Waitlisted |

## Reference Files

- `references/agent-integration-patterns.md` — Research Zone, Decision Log, Task Inbox patterns
- `references/notion-mcp-setup.md` — Notion MCP OAuth + config.yaml
- `references/notion-workers-platform.md` — Notion Workers reference
- `references/block-types.md` — All block type structures

## Hermes-Senna Notion Databases

Under the **Hermes** page (ID: `361742dc-20c6-80d6-90c4-fe3a7764431c`):

| Database | DB ID | Data Source ID |
|----------|-------|---------------|
| Agent Logbook | `9dc914a6-6736-40af-a0b9-d1af9fc5e8a1` | `b84b6d1e-443a-4c49-aba7-72c4ac88a7ee` |
| Research Vault | `89dea93d-4a26-49f1-9966-f01610cb66c6` | `09c1e28e-2fcd-48fc-bb5b-ff52922b038d` |
| Cost Tracker | `95127f7b-030c-4932-8930-c3baab0acac7` | `e891050f-e4f3-4bde-8285-f90809b93f2a` |
| Task Inbox | `6f9d9ab2-1f95-445a-8382-2bd3e796f1b4` | `7e4181de-54bc-46da-b2da-a40b1adfa2b2` |
| Agent Inventory | `2572f2f1-0a78-4dc0-858e-91ba19ef2584` | `0e0b01c5-93e4-4e52-8c13-d13884b241f0` |
| Cron Job Registry | `4961d68b-4ef2-4640-8204-4e79923118f5` | `2e28108d-ce8f-493f-b196-6a215b41ee8e` |
| Incident Log | `15e78a6f-16b6-4fc3-b7f8-875b8c60d90f` | — |
| Runbook Index | `455a7025-de4d-45f0-99fe-e8c96933bcf5` | — |
| Decision Log | `5e6f2237-d111-456d-b996-7a42ecd71e2d` | `8c666062-8889-40c1-8966-1affe7ec95d6` |
