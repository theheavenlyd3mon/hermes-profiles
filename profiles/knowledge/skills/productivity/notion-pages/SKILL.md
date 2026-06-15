---
name: notion-pages
description: "Create, read, update, and archive Notion pages — both standalone pages and database entries."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Pages, CRUD, Properties]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-databases, notion-blocks, notion-search]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Pages

Create, read, update, and archive Notion pages via the API. This covers both standalone pages (under a parent page) and database items (rows in a database).

## Prerequisites

- `NOTION_API_KEY` set (see notion-api-basics skill)
- Target pages/databases shared with the integration

## Get a Page

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq .
```

To extract just the properties:

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq '.properties | to_entries[] | {name: .key, type: .value.type, value: .value}'
```

## Create a Page in a Database

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "YOUR_DATABASE_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}},
      "Date": {"date": {"start": "'$(date -u +%Y-%m-%d)'"}},
      "Tags": {"multi_select": [{"name": "automation"}]}
    }
  }' | jq .
```

### Alternative parent reference (API 2025-09-03)

You can also use data_source_id as the parent:
```json
"parent": {"type": "data_source_id", "data_source_id": "YOUR_DATA_SOURCE_ID"}
```

### Title property name note

The title column is `"Name"` by default. If you used a different name during database creation, verify first:

```bash
curl -s "https://api.notion.com/v1/data_sources/{data_source_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq '.properties | keys'
```

## Create a Standalone Page

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "page_id", "page_id": "PARENT_PAGE_ID"},
    "properties": {
      "title": {"title": [{"text": {"content": "My New Page"}}]}
    }
  }' | jq .
```

## Update Page Properties

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": {"select": {"name": "Done"}},
      "Tags": {"multi_select": [{"name": "completed"}, {"name": "automation"}]}
    }
  }' | jq .
```

## Archive/Unarchive a Page

```bash
# Archive
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"archived": true}' | jq .

# Unarchive
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"archived": false}' | jq .
```

## Property Value Patterns

```json
{
  "Name": {"title": [{"text": {"content": "Entry title"}}]},
  "Rich Text": {"rich_text": [{"text": {"content": "Longer body text here\u2026"}}]},
  "Select": {"select": {"name": "Option"}},
  "Multi-select": {"multi_select": [{"name": "Tag1"}, {"name": "Tag2"}]},
  "Date": {"date": {"start": "2026-01-15"}},
  "Date Range": {"date": {"start": "2026-01-15", "end": "2026-01-20"}},
  "Checkbox": {"checkbox": true},
  "Number": {"number": 42.5},
  "URL": {"url": "https://example.com"},
  "Email": {"email": "user@example.com"},
  "Phone": {"phone_number": "+1-555-0123"},
  "Relation": {"relation": [{"id": "target_page_id"}]}
}
```

## Tips

- Property values are case-sensitive for `select` — they must match exactly
- The response from POST includes the new page ID — save it for later updates
- For Rich text with multiple segments, chain text objects with different annotations