# Notion Agent Logbook Schema and Wiring Guide

## Database Schema

The Agent Logbook uses the following property names (fetch with the data source endpoint to verify):

| Property | Type | Options |
|----------|------|---------|
| Name | Title | Short summary (max ~80 chars) |
| Agent | Select | Hermes, Kanban, Cron, Researcher |
| Type | Select | Session, Decision, Research, Task, Error |
| Date | Date | Auto-set to run time (YYYY-MM-DD) |
| Status | Select | Completed, In Progress, Failed |
| Tags | Multi-select | Freeform (memory, maintenance, setup, etc.) |
| Cost | Number | Approximate API spend (USD) |
| Summary | Rich text | Full summary, links, artifacts |

## API Pattern

```python
import os, json, datetime
from hermes_tools import terminal

api_key = os.environ.get("NOTION_API_KEY", "").strip()
db_id = "9dc914a6-6736-40af-a0b9-d1af9fc5e8a1"

payload = {
    "parent": {"database_id": db_id},
    "properties": {
        "Name": {"title": [{"text": {"content": "Entry title"}}]},
        "Agent": {"select": {"name": "Cron"}},
        "Type": {"select": {"name": "Task"}},
        "Date": {"date": {"start": datetime.date.today().isoformat()}},
        "Status": {"select": {"name": "Completed"}},
        "Tags": {"multi_select": [{"name": "tag1"}, {"name": "tag2"}]},
        "Cost": {"number": 0.0},
        "Summary": {"rich_text": [{"text": {"content": "Full summary text"}}]}
    }
}

import subprocess
result = subprocess.run([
    "curl", "-s", "-X", "POST", "https://api.notion.com/v1/pages",
    "-H", f"Authorization: Bearer {api_key}",
    "-H", "Notion-Version: 2025-09-03",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload)
], capture_output=True, text=True)

if result.returncode != 0 or 'error' in result.stdout:
    print(f"ERROR: {result.stdout}")
```

## Schema Verification

Before writing, fetch the data source to confirm property names:

```bash
NOTION_API_KEY=... curl -s "https://api.notion.com/v1/data_sources/b84b6d1e-443a-4c49-aba7-72c4ac88a7ee" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

Response will contain `properties` object mapping IDs to names:
- `Name` (title)
- `Agent` (select)
- `Type` (select)
- `Date` (date)
- `Status` (select)
- `Tags` (multi_select)
- `Cost` (number)
- `Summary` (rich_text)