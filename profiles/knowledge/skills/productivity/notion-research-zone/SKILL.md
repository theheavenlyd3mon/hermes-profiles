---
name: notion-research-zone
description: "Log research results to the Notion Research Vault database — from cron jobs, subagents, and investigate sessions."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Research, Subagents, Investigation]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-pages]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Research Vault

Log research results to the Notion Research Vault — from cron jobs, subagents, and investigate sessions. Each page = one research topic or investigation.

## Database

- **Name:** 🔬 Research Vault
- **Database ID:** `89dea93d-4a26-49f1-9966-f01610cb66c6`
- **Data source ID:** `09c1e28e-2fcd-48fc-bb5b-ff52922b038d`

## Schema

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Research question / topic |
| Agent | Select | Which agent produced it (hermes, cron, researcher) |
| Date | Date | When the research was done |
| Findings | Rich text | Detailed findings |
| Sources | Rich text | Links/references used |
| Tags | Multi-select | Domain keywords |
| Topic | Rich text | Brief topic description |
| Verdict | Rich text | Key conclusions / recommendation |

## Log Research via curl

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "89dea93d-4a26-49f1-9966-f01610cb66c6"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Three.js Shader Performance on M1 Macs"}}]},
      "Agent": {"select": {"name": "cron"}},
      "Date": {"date": {"start": "'$(date -u +%Y-%m-%d)'"}},
      "Findings": {"rich_text": [{"text": {"content": "M1 Macs handle up to 50 concurrent shader programs before frame drop. WebGL2 is 2x faster than WebGL1 on M1."}}]},
      "Sources": {"rich_text": [{"text": {"content": "https://threejs.org/docs, WebGL2 spec, M1 GPU benchmarks"}}]},
      "Tags": {"multi_select": [{"name": "threejs"}, {"name": "performance"}, {"name": "m1"}]},
      "Topic": {"rich_text": [{"text": {"content": "Three.js WebGL vs WebGL2 shader performance on Apple Silicon"}}]},
      "Verdict": {"rich_text": [{"text": {"content": "Use WebGL2 for all new Three.js projects targeting M1. Reduces draw calls by 40%."}}]}
    }
  }' | jq .
```

## Wire Into Subagent Tasks

When delegating research via `delegate_task`, include in the context:

> "After returning your findings, log them to the Notion Research Vault. Database ID: 89dea93d-4a26-49f1-9966-f01610cb66c6. Create a page with Name, Agent='researcher', Date=today, Findings=your detailed findings, Sources=links used, Tags=relevant keywords, Verdict=your conclusion."

## Wire Into Investigate Sessions

When running a research/investigate session, log findings as a final step before wrapping up.
