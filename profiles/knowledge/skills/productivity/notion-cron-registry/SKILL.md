---
name: notion-cron-registry
description: "Register and track cron jobs in the Notion Cron Job Registry database."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Cron, Registry, Scheduler]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-pages, notion-agent-logbook]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Cron Job Registry

Register and track cron jobs in the Notion Cron Job Registry. One entry per cron job (not per run).

## Database

- **Name:** ⏰ Cron Job Registry
- **Database ID:** `4961d68b-4ef2-4640-8204-4e79923118f5`
- **Data source ID:** `2e28108d-ce8f-493f-b196-6a215b41ee8e`

## Schema

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Cron job name |
| Description | Rich text | What the job does |
| Schedule | Rich_text | Cron schedule expression |
| Status | Select | Options: active, paused, retired |
| Last Run | Date | Last execution date |
| Next Run | Rich_text | Next scheduled time |

## Register a Cron Job

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "4961d68b-4ef2-4640-8204-4e79923118f5"},
    "properties": {
      "Name": {"title": [{"text": {"content": "overnight-wiki-research"}}]},
      "Description": {"rich_text": [{"text": {"content": "Researches and updates the LLM-wiki with new findings. Runs nightly at 2am."}}]},
      "Schedule": {"rich_text": [{"text": {"content": "0 2 * * *"}}]},
      "Status": {"select": {"name": "active"}},
      "Last Run": {"date": {"start": "2026-05-15"}},
      "Next Run": {"rich_text": [{"text": {"content": "2026-05-16 02:00"}}]}
    }
  }' | jq .
```

## Update Last Run (after each tick)

To update the Last Run date for an existing entry:

Find the page via search or query, then PATCH:

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Last Run": {"date": {"start": "'$(date -u +%Y-%m-%d)'"}},
      "Next Run": {"rich_text": [{"text": {"content": "2026-05-17 02:00"}}]}
    }
  }' | jq .
```
