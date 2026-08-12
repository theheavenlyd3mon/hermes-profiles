# Batch YouTube Extraction — Reliability Patterns

## Cron Mode Fallback

When `execute_code` is blocked by `cron_mode: approve` (cron jobs without user present), fall back to direct tool calls:

1. Use `web_extract` directly in batches of 5 URLs (the API max)
2. Save each batch's results immediately with `write_file` — don't accumulate
3. Use `terminal` for directory creation (`mkdir -p`) and checkpoint updates
4. Sequential batches, no parallelism needed (web_extract handles 5 URLs per call)

## web_extract Reliability on YouTube URLs

### Known Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| 504 timeout (Firecrawl) | Upstream timeout on YouTube page load | Retry immediately — usually succeeds on 2nd attempt |
| Title present, content empty | YouTube returned metadata only (no transcript/summary) | Mark as insufficient, skip — don't retry |
| Content < 200 chars | Only channel info or error page captured | Treat as failed — insufficient for a useful summary |
| Content is just channel description | Video page loaded but transcript unavailable | Skip — some videos don't have extractable content |

### Retry Strategy

- **Timeout errors:** Immediate retry (no delay needed). Success rate ~90% on retry.
- **Insufficient content:** Don't retry — the video genuinely lacks extractable content.
- **Batch partial failure:** Save successful results immediately, retry failed URLs in a new call.

### Content Quality Filtering

```
Good content indicators:
- Has structured sections (## headers)
- Contains specific technical content (node names, settings, values)
- Length > 500 chars = excellent summary
- Length 200-500 chars = usable but thin
- Length < 200 chars = insufficient, skip

Bad content indicators:
- Only channel description / about page
- Just video title repeated
- Error messages or "unavailable" text
- No actual tutorial/summary content
```

## Checkpoint Management

### Pattern

```json
{
  "done": ["video_id_1", "video_id_2"],
  "failed": ["video_id_3"],
  "failed_reasons": {
    "video_id_3": "Insufficient content - only metadata returned"
  },
  "last_processed": 5,
  "notes": "Brief summary of this batch"
}
```

### Pitfalls

- **Read before write:** When running alongside other agents (parallel cron jobs, sibling subagents), ALWAYS read the existing checkpoint before writing. The `write_file` tool will warn about sibling modifications — heed the warning.
- **Track failures with reasons:** Don't just track successes. Failed IDs with reasons prevent wasting time on retries of genuinely unavailable content.
- **last_processed counter:** Enables resumability. Next run reads this and continues from where it left off.

## File Naming for Batch Extraction

### Recommended Convention

```
{playlist-prefix}-{episode-number}-{short-slug}.md
```

Examples:
- `ue5-rpg-82-bug-fixing.md`
- `ue5-starter-06-lighting.md`

### YAML Frontmatter Template

```yaml
---
title: "Full Video Title"
source: https://www.youtube.com/watch?v=VIDEO_ID
video_id: VIDEO_ID
type: youtube-summary
tags: [ue5, tutorial, blueprint, gamedev]  # adjust per video
---
```

### Pitfalls

- **Sanitize titles for filesystem:** Remove/replace: `:`, `/`, `\`, `?`, `*`, `<`, `>`, `|`, `"`, `(`, `)`
- **Consistent naming within a playlist:** All files in a playlist directory should follow the same prefix pattern
- **Don't use full titles as filenames** — they're too long and break on various filesystems. Use short descriptive slugs.
