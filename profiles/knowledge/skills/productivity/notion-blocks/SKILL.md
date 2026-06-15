---
name: notion-blocks
description: "Append and read Notion block content — paragraphs, headings, lists, code, to-do, images, and all block types."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Notion, Blocks, Content, Rich Text]
    homepage: https://developers.notion.com
    related_skills: [notion-api-basics, notion-pages]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Blocks

Manage the content inside Notion pages — appending and reading blocks (paragraphs, headings, lists, code, images, etc.).

## Prerequisites

- `NOTION_API_KEY` set (see notion-api-basics skill)
- The page to modify must be shared with the integration

## Append Content (Add Blocks to a Page)

Use `PATCH /v1/blocks/{page_id}/children`:

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "Section Title"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "This is a paragraph of content."}}]}},
      {"object": "block", "type": "divider", "divider": {}}
    ]
  }' | jq .
```

## Read Block Children (Page Content)

```bash
curl -s "https://api.notion.com/v1/blocks/{page_id}/children?page_size=50" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq .
```

For a simplified text-only view:

```bash
curl -s "https://api.notion.com/v1/blocks/{page_id}/children?page_size=50" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq '.results[] | select(.type != "child_page" and .type != "child_database") | {type, text: .[.type].rich_text[]?.plain_text // null}'
```

## All Block Types

### Text blocks

```json
{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello world"}}]}}
{"type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "Heading 1"}}]}}
{"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Heading 2"}}]}}
{"type": "heading_3", "heading_3": {"rich_text": [{"text": {"content": "Heading 3"}}]}}
{"type": "quote", "quote": {"rich_text": [{"text": {"content": "Something wise"}}]}}
{"type": "callout", "callout": {"rich_text": [{"text": {"content": "Note"}}], "icon": {"emoji": "\uD83D\uDCA1"}}}
{"type": "toggle", "toggle": {"rich_text": [{"text": {"content": "Expand for details"}}]}}
```

### List blocks

```json
{"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Item"}}]}}
{"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"text": {"content": "Step 1"}}]}}
{"type": "to_do", "to_do": {"rich_text": [{"text": {"content": "Task"}}], "checked": false}}
```

### Code block

```json
{"type": "code", "code": {"rich_text": [{"text": {"content": "print('hello')"}}], "language": "python"}}
```

Supported languages: python, javascript, typescript, bash, json, yaml, go, rust, sql, html, css, and many more.

### Embeds & media

```json
{"type": "image", "image": {"type": "external", "external": {"url": "https://example.com/photo.png"}}}
{"type": "bookmark", "bookmark": {"url": "https://example.com"}}
{"type": "embed", "embed": {"url": "https://example.com/widget"}}
```

### Dividers

```json
{"type": "divider", "divider": {}}
```

## Rich Text Formatting

Each rich_text entry can have formatting annotations:

```json
{"rich_text": [
  {"text": {"content": "Bold and "}, "annotations": {"bold": true}},
  {"text": {"content": "italic text"}, "annotations": {"bold": true, "italic": true}},
  {"text": {"content": "code inline"}, "annotations": {"code": true}},
  {"text": {"content": "Link", "link": {"url": "https://example.com"}}}
]}
```

Available annotations: `bold`, `italic`, `strikethrough`, `underline`, `code`, `color` (colors include default, gray, brown, orange, yellow, green, blue, purple, pink, red, and _background variants)

## Reading Blocks — Text Extraction

| Type | Text location | Extra fields |
|------|--------------|--------------|
| `paragraph` | `.paragraph.rich_text` | — |
| `heading_1/2/3` | `.heading_N.rich_text` | — |
| `bulleted_list_item` | `.bulleted_list_item.rich_text` | — |
| `numbered_list_item` | `.numbered_list_item.rich_text` | — |
| `to_do` | `.to_do.rich_text` | `.to_do.checked` |
| `code` | `.code.rich_text` | `.code.language` |
| `quote` | `.quote.rich_text` | — |
| `callout` | `.callout.rich_text` | `.callout.icon.emoji` |
| `image` | `.image.caption` | `.image.file.url` or `.image.external.url` |
| `bookmark` | `.bookmark.caption` | `.bookmark.url` |
| `child_page` | — | `.child_page.title` |
| `child_database` | — | `.child_database.title` |

Rich text arrays contain objects with `.plain_text` — concatenate them for readable output.

## Notes

- Blocks are appended at the end of the page's current content (no "insert at position")
- To insert at a specific position, you'd need to delete and re-add blocks (complex — use Notion UI)
- Nested blocks (toggle contents, list sub-items) are children of the parent block and need their own API call