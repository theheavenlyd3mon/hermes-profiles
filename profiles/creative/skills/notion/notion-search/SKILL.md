---
name: notion-search
description: "Search across a Notion workspace — find pages, databases, and content by query."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Search, Discovery]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-pages, notion-databases]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Search

Search across your Notion workspace to find pages, databases (data sources), and content.

## Prerequisites

- `NOTION_API_KEY` set (see notion-api-basics skill)
- Only pages shared with the integration are searchable

## Basic Search

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title or keyword"}' | jq .
```

## Search with Filters

Filter by object type:

```bash
# Search only pages
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "research",
    "filter": {"value": "page", "property": "object"}
  }' | jq .

# Search only databases (data sources)
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "logbook",
    "filter": {"value": "data_source", "property": "object"}
  }' | jq .
```

## Sort Results

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "agent",
    "sort": {"direction": "descending", "timestamp": "last_edited_time"}
  }' | jq .
```

## Paginated Search (get all results)

```bash
#!/bin/bash
SEARCH_QUERY="notion"
HAS_MORE=true
START_CURSOR=""

while [ "$HAS_MORE" = true ]; do
  if [ -z "$START_CURSOR" ]; then
    RESULT=$(curl -s -X POST "https://api.notion.com/v1/search" \
      -H "Authorization: Bearer $NOTION_API_KEY" \
      -H "Notion-Version: 2025-09-03" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$SEARCH_QUERY\", \"page_size\": 100}")
  else
    RESULT=$(curl -s -X POST "https://api.notion.com/v1/search" \
      -H "Authorization: Bearer $NOTION_API_KEY" \
      -H "Notion-Version: 2025-09-03" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$SEARCH_QUERY\", \"page_size\": 100, \"start_cursor\": \"$START_CURSOR\"}")
  fi

  echo "$RESULT" | jq '.results[] | {id: .id, type: .object, title: .title?.[0]?.plain_text? // .properties?.Name?.title?.[0]?.plain_text?}'
  HAS_MORE=$(echo "$RESULT" | jq -r '.has_more')
  START_CURSOR=$(echo "$RESULT" | jq -r '.next_cursor // empty')
done
```

## Find Items in a Database (Targeted Query)

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Name", "title": {"contains": "keyword"}},
    "page_size": 20
  }' | jq '.results[] | {id: .id, name: .properties.Name.title[0].plain_text}'
```

## List Everything

Use an empty query to list ALL pages and databases shared with the integration:

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "", "page_size": 100}' | jq '.results[] | {id: .id, type: .object, title: .title?.[0]?.plain_text? // .properties?.Name?.title?.[0]?.plain_text?}'
```

## Notes

- Workspace search respects integration permissions — only shared pages appear
- In API 2025-09-03, databases return as `"object": "data_source"` with `data_source_id`
- Default page_size is 100, max is 100