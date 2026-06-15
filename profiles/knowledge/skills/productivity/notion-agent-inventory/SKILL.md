---
name: notion-agent-inventory
description: "Track Hermes agent profiles, their roles, models, and tools in the Notion Agent Inventory database."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Agents, Profiles, Inventory]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-pages]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Agent Inventory

Track Hermes agent profiles in the Notion Agent Inventory — one entry per profile.

## Database

- **Name:** 🤖 Agent Inventory
- **Database ID:** `2572f2f1-0a78-4dc0-858e-91ba19ef2584`
- **Data source ID:** `0e0b01c5-93e4-4e52-8c13-d13884b241f0`

## Schema

| Property | Type | Options |
|----------|------|---------|
| Name | Title | Profile name |
| Profile | Select | senna |
| Role | Select | Primary, Kanban, Researcher, Cron, Utility |
| Status | Select | Active, Idle, Disabled |
| Model | Rich_text | Current model assignment |
| Provider | Rich_text | AI provider |
| Tools | Multi_select | terminal, web, file, notion, memory, delegation, cron |
| Notes | Rich_text | Additional info |

## ⚠️ Critical: Always verify model assignments before populating

When registering profiles in the Agent Inventory, **load the `profile-model-fleet` skill first** to get accurate model assignments. Do NOT use placeholder values like "default (deepseek/deepseek-v4-flash)" — each profile has a purpose-fit model based on cost analysis.

The fleet skill is at `devops/profile-model-fleet` and contains:
- Exact model ID per profile (e.g. `deepseek/deepseek-v3.2`, not just `v3.2`)
- Pricing per million tokens (prompt + completion)
- Context window sizes
- Provider assignment (all on `nous`)

**Pitfall:** If you use placeholder values, every entry needs a PATCH to correct later. Always check the authoritative source first.

## Register a Profile

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "2572f2f1-0a78-4dc0-858e-91ba19ef2584"},
    "properties": {
      "Name": {"title": [{"text": {"content": "architect"}}]},
      "Profile": {"select": {"name": "senna"}},
      "Role": {"select": {"name": "Kanban"}},
      "Status": {"select": {"name": "Active"}},
      "Model": {"rich_text": [{"text": {"content": "default (deepseek/deepseek-v4-flash)"}}]},
      "Provider": {"rich_text": [{"text": {"content": "nous"}}]},
      "Tools": {"multi_select": [{"name": "terminal"}, {"name": "file"}, {"name": "notion"}]}
    }
  }' | jq .
```

## Update Status

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": {"select": {"name": "Idle"}},
      "Model": {"rich_text": [{"text": {"content": "anthropic/claude-sonnet-4"}}]}
    }
  }' | jq .
```
