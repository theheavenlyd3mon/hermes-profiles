---
name: notion-cost-tracker
description: "Log API usage costs and model spending to the Notion Cost Tracker database."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Costs, Budget, API Spending]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-pages, notion-agent-logbook]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Cost Tracker

Log API usage costs and model spending to the Notion Cost Tracker. One entry per task/session.

## Database

- **Name:** 💰 Cost Tracker
- **Database ID:** `95127f7b-030c-4932-8930-c3baab0acac7`
- **Data source ID:** `e891050f-e4f3-4bde-8285-f90809b93f2a`

## Schema

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Cost entry description |
| Agent | Select | Which agent incurred the cost |
| Cost | Number | USD cost |
| Date | Date | When the cost was incurred |
| Model | Rich_text | Model used (e.g. deepseek/deepseek-v4-flash) |
| Task | Rich_text | Task description |
| Tokens In | Number | Input tokens |
| Tokens Out | Number | Output tokens |

## Log Cost via curl

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "95127f7b-030c-4932-8930-c3baab0acac7"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Wiki research run"}}]},
      "Agent": {"select": {"name": "cron"}},
      "Cost": {"number": 0.12},
      "Date": {"date": {"start": "'$(date -u +%Y-%m-%d)'"}},
      "Model": {"rich_text": [{"text": {"content": "deepseek/deepseek-v4-flash"}}]},
      "Task": {"rich_text": [{"text": {"content": "Researched and updated 3 wiki pages on LLM agent architectures"}}]},
      "Tokens In": {"number": 15000},
      "Tokens Out": {"number": 4000}
    }
  }' | jq .
```

## Log via execute_code

```python
from hermes_tools import terminal
import json, datetime

cost = 0.12
tokens_in = 15000
tokens_out = 4000
task = "Wiki research run"
model = "deepseek/deepseek-v4-flash"

payload = {
    "parent": {"database_id": "95127f7b-030c-4932-8930-c3baab0acac7"},
    "properties": {
        "Name": {"title": [{"text": {"content": task[:80]}}]},
        "Agent": {"select": {"name": "cron"}},
        "Cost": {"number": cost},
        "Date": {"date": {"start": datetime.date.today().isoformat()}},
        "Model": {"rich_text": [{"text": {"content": model}}]},
        "Task": {"rich_text": [{"text": {"content": task[:2000]}}]},
        "Tokens In": {"number": tokens_in},
        "Tokens Out": {"number": tokens_out}
    }
}

result = terminal(f'''curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{json.dumps(payload)}' ''')
print("Cost logged:", result)
```

## When to Log

- After each cron job run (approximate cost)
- After significant interactive sessions
- At end of day for batch jobs
- Track monthly spend against budget
