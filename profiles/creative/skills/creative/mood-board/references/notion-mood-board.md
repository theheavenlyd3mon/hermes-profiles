# Notion Mood Board Delivery Pattern

Verified block-level pattern for delivering a mood board as a Notion page (built for the Tokyo Ghoul / Ken Kaneki board, Aug 2026).

## Setup

- Auth: `Authorization: Bearer $NOTION_API_KEY` + `Notion-Version: 2025-09-03` (required header).
- New top-level content needs an accessible parent page. Discover one via `POST /v1/search` (filter `object=page`, look for `parent.type == "workspace"`). Known root in this workspace: the "Hermes" page `361742dc-20c6-80d6-90c4-fe3a7764431c`.
- In execute_code, load the key from the profile dotenv (sandbox does not inherit terminal env):
  ```python
  KEY = next(l.split("=",1)[1].strip() for l in open("~/.hermes/profiles/<profile>/.env") if l.startswith("NOTION_API_KEY="))
  ```

## Page Creation (icon + cover + title in one POST)

```python
POST /v1/pages
{
  "parent": {"page_id": "<parent_page_id>"},
  "icon":  {"type": "emoji", "emoji": "🎭"},
  "cover": {"type": "external", "external": {"url": "<official_art_url>"}},   # AniList image.large works well
  "properties": {"title": {"title": [{"text": {"content": "Mood Board"}}]}}
}
```

## Content Blocks (PATCH /v1/blocks/{page_id}/children)

Proven layout, ~15 top-level blocks in one call (limit 100):

1. **Intro callout** — `gray_background`, subject line bold, emphasis character name in `"color": "red"` annotation.
2. **heading_2** — section title.
3. **Image grid** — one `column_list` with 3 `column` children, each holding 3 `image` blocks:
   ```json
   {"type": "image", "image": {"type": "external", "external": {"url": "..."},
     "caption": [{"text": {"content": "art by <artist>"}, "annotations": {"italic": true}}]}}
   ```
   `column_list → column → image` = exactly 2 nesting levels, the API max per call.
4. **heading_2** — palette section.
5. **Swatches** — second `column_list`, 3 columns × 2 `callout` blocks each. Map each hex to the nearest Notion background color; put the true hex in a `code` annotation:
   ```json
   {"type": "callout", "callout": {"color": "red_background", "icon": {"type": "emoji", "emoji": "🎨"},
     "rich_text": [
       {"text": {"content": "#D7263D  "}, "annotations": {"code": true, "bold": true}},
       {"text": {"content": "Kagune Crimson — "}, "annotations": {"bold": true}},
       {"text": {"content": "rinkaku kagune, the ghoul eye"}}]}}
   ```
   Notion background colors: default, gray, brown, orange, yellow, green, blue, purple, pink, red (each `_background`). Map dark hexes → gray/brown, vivid reds → red, muted blues → blue, etc.
6. **heading_2** — motifs section, then `bulleted_list_item`s with bold motif name + dash + meaning.
7. **divider**, **quote** (`red_background` for punch), and a small gray italic attribution `paragraph` (sources, date).

## Verify

Run `scripts/verify_notion_board.py <page_id>` — prints title/icon/cover, walks nested columns, counts images. Expected: image count matches intended grid size.

## Caveats

- Images are **external embeds** — Notion links the CDN URL rather than storing the file. Dead source link = broken tile. Mention this to the user.
- Danbooru CDN (`cdn.donmai.us`) and AniList CDN (`s4.anilist.co`) both render fine as external blocks.
- To reposition blocks later, the API only appends at the end — reordering is a Notion-UI task.
