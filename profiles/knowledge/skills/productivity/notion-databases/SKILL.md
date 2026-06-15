---
name: notion-databases
description: "Create, query, update schema, and manage Notion databases (data sources) via the API."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Database, Data Source, Schema]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-pages, notion-search]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Databases

Create, query, and manage database schemas via the Notion API. In API version 2025-09-03, databases are called **data sources**.

## Prerequisites

- `NOTION_API_KEY` set (see notion-api-basics skill)
- Parent page to create databases under — share it with the integration
- For querying: the database has been shared with the integration

## Create a Database

**⚠️ API version 2025-09-03 changed how this works.** Top-level `properties` are silently dropped. Use `initial_data_source.properties`:

```bash
curl -s -X POST "https://api.notion.com/v1/databases" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "page_id", "page_id": "PARENT_PAGE_ID"},
    "title": [{"text": {"content": "My Database"}}],
    "initial_data_source": {
      "properties": {
        "Name": {"title": {}},
        "Status": {"select": {"options": [{"name": "Todo"}, {"name": "In Progress"}, {"name": "Done"}]}},
        "Date": {"date": {}},
        "Tags": {"multi_select": {"options": [{"name": "research"}, {"name": "task"}]}}
      }
    }
  }' | jq .
```

**Pitfall — block IDs may differ from creation response IDs:** The `id` returned by `POST /v1/databases` may not match the child block ID visible via `GET /v1/blocks/{parent_id}/children`. When you need the canonical database ID, always fetch the children:

```bash
curl -s "https://api.notion.com/v1/blocks/{parent_page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq '.results[] | select(.type=="child_database") | {id, title: .child_database.title}'
```

## Get Database Metadata

Gets the database object including data sources list:

```bash
curl -s "https://api.notion.com/v1/databases/{database_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq .
```

Useful for getting both `database_id` and the corresponding `data_source_id`:

```bash
curl -s "https://api.notion.com/v1/databases/{database_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq '{database_id: .id, data_source_id: .data_sources[0].id, title: .title}'
```

## Get Data Source Schema

Fetch the actual property names and types:

```bash
curl -s "https://api.notion.com/v1/data_sources/{data_source_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq '.properties'
```

## Query a Database

**Note:** Use `data_source_id` for queries, not `database_id`.

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Done"}},
    "sorts": [{"property": "Date", "direction": "descending"}],
    "page_size": 10
  }' | jq '.results[] | {id: .id, properties}'
```

### Query with compound filter

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "and": [
        {"property": "Status", "select": {"equals": "Todo"}},
        {"property": "Priority", "select": {"equals": "High"}}
      ]
    }
  }' | jq .
```

## Add/Update Properties (Schema)

If you created a database with missing properties (e.g. used old API pattern), or need to add columns later, PATCH the data source directly:

```bash
DS_ID=$(curl -s "https://api.notion.com/v1/databases/{database_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq -r '.data_sources[0].id')

curl -s -X PATCH "https://api.notion.com/v1/data_sources/$DS_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Agent": {"select": {"options": [{"name": "Hermes"}, {"name": "Cron"}, {"name": "Researcher"}]}},
      "Status": {"select": {"options": [{"name": "Completed"}, {"name": "Failed"}, {"name": "In Progress"}]}},
      "Cost": {"number": {"format": "dollar"}}
    }
  }' | jq .
```

## Archive a Database

There is no `DELETE` endpoint. To archive (soft-delete):

```bash
curl -s -X PATCH "https://api.notion.com/v1/databases/{database_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"archived": true}' | jq .
```

Note: this API redirect is unreliable in 2025-09-03. For guaranteed deletion, use the Notion UI.

## Troubleshooting

- **"Property doesn't exist"** → Fetch the schema as shown above, verify property names match exactly (case-sensitive)
- **Database created with only "Name" property** → You used the old top-level `properties` pattern. Recreate with `initial_data_source.properties`, or patch the data source to add columns
- **Can't find database by ID** → The integration hasn't been shared with the parent page