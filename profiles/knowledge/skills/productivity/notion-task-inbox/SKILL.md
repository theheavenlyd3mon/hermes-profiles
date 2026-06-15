---
name: notion-task-inbox
description: "Manage the Notion Task Inbox — create tasks from GitHub, chat, Obsidian, and manual entry. Central triage point."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Tasks, Inbox, Triage]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-pages, notion-search, github-issues]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Task Inbox

Central inbox where any input (GitHub issue, chat mention, verbal idea, Obsidian note) lands as a task row. Triaged from one place.

## Database

- **Name:** 📥 Task Inbox
- **Database ID:** `6f9d9ab2-1f95-445a-8382-2bd3e796f1b4`
- **Data source ID:** `7e4181de-54bc-46da-b2da-a40b1adfa2b2`

## Schema

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Task description |
| Source | Select | Options: github, chat, notion, obsidian, manual, cron, email |
| Priority | Select | Options: low, medium, high, urgent |
| Status | Select | Options: inbox, triaged, assigned, in-progress, done |
| Date | Date | Auto-stamped |
| Tags | Multi-select | Labels for grouping |
| Notes | Rich text | Context, links, attachments |

## Create a Task

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "6f9d9ab2-1f95-445a-8382-2bd3e796f1b4"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Investigate Notion MCP setup for multi-agent access"}}]},
      "Source": {"select": {"name": "manual"}},
      "Priority": {"select": {"name": "medium"}},
      "Status": {"select": {"name": "inbox"}},
      "Date": {"date": {"start": "'$(date -u +%Y-%m-%d)'"}},
      "Tags": {"multi_select": [{"name": "notion"}, {"name": "mcp"}]},
      "Notes": {"rich_text": [{"text": {"content": "Set up Notion MCP server so Claude Code and Cursor can also access Notion workspace."}}]}
    }
  }' | jq .
```

## Feeding the Inbox

Three paths:
1. **Manual** — Create tasks via API during conversations (ideas, bug reports, feature requests)
2. **Cron poll** — A cron job checks Obsidian inbox, GitHub issues, etc. and creates rows
3. **Webhook** — Future: GitHub webhook → create task page

## Triage Pattern

Query inbox items to see what needs attention:

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/7e4181de-54bc-46da-b2da-a40b1adfa2b2/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "inbox"}},
    "sorts": [{"property": "Priority", "direction": "descending"}]
  }' | jq '.results[] | {name: .properties.Name.title[0].plain_text, priority: .properties.Priority.select.name, source: .properties.Source.select.name}'
```

## Update Task Status

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": {"select": {"name": "in-progress"}}
    }
  }' | jq .
```
