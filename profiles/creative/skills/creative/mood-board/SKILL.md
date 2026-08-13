---
name: mood-board
description: "Use when building a mood board. Images, palette, Notion."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [MoodBoard, Notion, Anime, Palette, References, Creative]
    related_skills: [notion, notion-blocks, notion-pages, unsplash-asset-images]
prerequisites:
  env_vars: [NOTION_API_KEY]  # only when delivering to Notion
---

# Mood Board Creation

Class workflow for building visual mood boards: parse brief → source images → design palette → deliver → verify.

## When to Use

Trigger on any request to build a mood board, visual reference board, inspiration board, or palette board — anime, brand, or project. Also use when the user asks to "grab images and colors" for a subject into Notion or an HTML page.

## 1. Parse the Brief

Extract: subject (character/franchise/brand), emphasis (one character? an arc? a texture?), and delivery target (Notion page, HTML artifact, image grid file). If the user names a brand (e.g. Cheonma), apply that brand's palette DNA; otherwise stay neutral.

## 2. Source Images (Free, Keyless APIs)

| Source | Endpoint | Key | Best for |
|--------|----------|-----|----------|
| Jikan (MyAnimeList) | `GET api.jikan.moe/v4/characters?q=<name>` then `/v4/characters/{id}/pictures` | No | Official anime character galleries |
| Danbooru | `GET danbooru.donmai.us/posts.json?tags=<tag>%20rating:g&limit=40` | No (2-tag limit anonymous) | Fan art — sort client-side by `score` |
| AniList | `POST graphql.anilist.co` `{ Character(search:"<name>") { image { large } } }` | No | One official character portrait (great page cover) |
| Unsplash/Pexels | see unsplash-asset-images skill | varies | Photographic subjects, textures |

Rules:
- Always caption images with the artist (`tag_string_artist` on Danbooru).
- Prefer `rating:g`/`rating:s` content.
- Skip multi-MB PNG originals for web embeds; prefer JPGs under ~2 MB.
- Check `image_width`/`image_height` — mix orientations for grid interest.

## 3. Design the Palette

Derive 5–7 named swatches from the subject's *canon* aesthetic, not generic color theory. Each swatch: hex + evocative name + one-line usage note (e.g. `#D7263D Kagune Crimson — rinkaku kagune, the ghoul eye`). For anime, mine the source material: signature items, transformations, locations, other characters' influence.

## 4. Deliver

- **Notion** (when the user has Notion access): full pattern — page + cover + 3×3 `column_list` image grid + colored callout swatches — in `references/notion-mood-board.md`. Verify with `scripts/verify_notion_board.py`.
- **HTML artifact**: image grid + swatch row as a one-off page (see `sketch` skill for throwaway mockup conventions).

## 5. Verify

Read back the delivered artifact. For Notion: fetch page (title/icon/cover set?) then walk block children including nested columns — count embedded images against what you intended. Report the live URL.

## Pitfalls

- **Jikan 504s when the MAL backend is down.** One or two retries with backoff, then pivot to Danbooru (fan art) + AniList (official art). Don't burn the session retrying.
- **execute_code sandbox does NOT inherit terminal env vars.** `os.environ["NOTION_API_KEY"]` fails there even when the terminal has it. Read keys from the profile dotenv inside the script: `~/.hermes/profiles/<profile>/.env`.
- **Notion image blocks are external embeds, not uploads.** Notion links the source URL — if the CDN link dies, the tile breaks. Tell the user this trade-off.
- **Notion block nesting: max 2 levels per API call.** `column_list → column → image` is exactly 2 — fine. Deeper needs separate PATCH calls.
- **Notion API version header is required** — use `Notion-Version: 2025-09-03` (databases/data-sources split; see notion-api-basics).
