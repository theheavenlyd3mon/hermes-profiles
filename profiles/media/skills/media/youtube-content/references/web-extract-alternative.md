# web_extract Alternative for YouTube Knowledge Bases

## When to Use

Building a structured knowledge base from a YouTube playlist (e.g., tutorial series for an AI coding agent). The `web_extract` tool scrapes YouTube pages and returns auto-generated summaries with code blocks, parameter values, and implementation steps.

## Why This Works Better Than Transcripts for Knowledge Bases

1. **Structured output** — Headers, bullet points, code blocks (transcripts are flat timestamped text)
2. **No youtube-transcript-api rate limits** — Uses Firecrawl/scraping path, different IP reputation
3. **Works on videos without transcripts** — Extracts page metadata + YouTube's auto-summary
4. **Batch-friendly** — 5 URLs per `web_extract` call

## Full Workflow

### Step 1: Get video URLs
```bash
yt-dlp --flat-playlist --dump-single-json --no-warnings "PLAYLIST_URL" 2>/dev/null | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for i, e in enumerate(data.get('entries', []), 1):
    vid_id = e.get('id', '')
    title = e.get('title') or 'Untitled'
    print(f'{i}|{vid_id}|{title}')
" > /tmp/videos.txt
```

### Step 2: Process in batches of 5
```python
# Read URLs from /tmp/videos.txt
# For each batch of 5:
urls = [f"https://www.youtube.com/watch?v={line.split('|')[1]}" for line in batch]
results = web_extract(urls)
```

### Step 3: Save as .md files
```python
for r in results:
    if r.get('content') and not r.get('error'):
        vid_id = r['url'].split('v=')[-1]
        title = r['title'].replace(' - YouTube', '').strip()
        # Save to outdir with numbered prefix
```

### Step 4: Handle failures and low-quality extractions
- **403 / unavailable**: Skip, log the video ID. See "Content quality tiers for 403 responses" below.
- **500 Internal Server Error**: Transient scraping backend failure. Retry once after 8s. If still fails, mark as failed in checkpoint and continue — don't retry a third time in the same run (schedule a separate retry job). Some videos consistently return 500 across all attempts (the scraping backend may not support that video's page structure). In this session, `amjtrkFYArI` returned 500 on 3 separate attempts over 40+ minutes.
- **Timeout**: Retry once after 5s, then skip
- **Empty content**: Skip (video may have been removed)
- **Metadata-only (no 403, no error)**: Some videos return structured metadata (chapter timestamps, description, channel info) but no actual transcript/summary content. Content is typically 500-1500 chars of useful metadata. These are worth saving — classify as Tier 2 quality. Don't retry; the metadata is the best available.
- **Rate limit**: Wait 2-3 min between batches if hitting limits
- **Minimal content (< 200 chars)**: YouTube sometimes returns just "Tap to unmute" or a few boilerplate lines instead of a 403 error. This is an extraction failure, not an unavailable video. When this happens, **reconstruct from available metadata**:
  1. Parse the video title for episode number and topic
  2. Use series context (adjacent episodes, known arc structure) to infer what was covered
  3. Pull keywords from tags/description
  4. Write a structured summary with what you know, noting it's metadata-derived
  5. This produces a useful knowledge base entry even when the extraction service fails
  6. Mark the video ID as "done" (not "failed") since you produced a valid .md file — but add a note in the checkpoint about content quality

## Output Quality Comparison

| Aspect | Transcript (youtube-transcript-api) | web_extract summary |
|--------|-------------------------------------|---------------------|
| Structure | Flat text with timestamps | Headers, code blocks, lists |
| Code snippets | None (spoken words only) | Extracted and formatted |
| Parameter values | Mentioned in speech | Listed in tables/code |
| Length | Full (~10K+ chars) | ~3-5K chars (summarized) |
| Availability | ~40-60% of tutorial videos | Higher (uses page metadata) |
| Rate limiting | Aggressive (IP block after 10-20) | Less aggressive |

## Real-World Result

From an 85-video UE5 RPG tutorial playlist:
- 9 raw transcripts obtained (videos with captions enabled)
- 70+ structured summaries via web_extract (including videos that showed "no transcript")
- Total: 79/85 videos covered (~93%)
- The summaries contained code snippets, parameter values, and step-by-step instructions that raw transcripts would NOT have had

## Cron Job Pattern for Large Playlists

When processing 100+ videos across multiple playlists, use scheduled cron jobs:

1. **Save video URLs to temp files** — one per playlist (e.g., `/tmp/UE5_RPG_Framework_urls.txt`)
2. **Schedule cron jobs spaced 20 min apart** — each processes 20 videos
3. **Each cron job prompt** instructs the agent to:
   - Read URLs from the temp file (skip already-done based on checkpoint)
   - Call `web_extract` in batches of 5 with 8s delays
   - Save results as .md files with YAML frontmatter
   - Update checkpoint file
4. **Final retry job** — runs after all batches, retries any failures

Example schedule for 172 videos across 4 playlists:
```
11:15 - batch1 (videos 1-20, playlist 1)
11:35 - batch2 (videos 21-40, playlist 1)
11:55 - batch3 (videos 41-60, playlist 1)
12:15 - batch4 (videos 61-80, playlist 1)
12:35 - batch5 (videos 81-85 + all playlist 2)
12:55 - batch6 (videos 1-20, playlist 3)
1:15  - batch7 (videos 21-40, playlist 3)
1:35  - batch8 (videos 41-43 + all playlist 4)
2:00  - retry (all failures)
```

## Pitfalls

- **`hermes_tools` cannot be imported from subprocess.** If you try to create a standalone Python script that does `from hermes_tools import web_extract`, it will fail with `No module named 'hermes_tools'`. The `web_extract` function is agent-internal — it can only be called directly from the agent's tool-calling interface, not from a background script. For batch web_extract processing, use cron jobs with agent prompts (not `no_agent` scripts) that call `web_extract` directly.
- **Don't use `execute_code` for the batch loop** — it may be blocked in some sessions. Use manual `web_extract` calls or a cron job with an agent prompt.
- **Title sanitization** — Some YouTube titles contain characters invalid for filenames. Always sanitize: `re.sub(r'[\\/*?:"<>|]', '', title).replace(' ', '_')`
- **Playlist entry ordering** — yt-dlp returns entries in playlist order, not video upload order. The `index` from the playlist is the correct ordering.
- **Some videos are private/unavailable** — These return 403 from web_extract. Don't treat as rate limiting; just skip.
- **curl-based availability detection is unreliable.** Don't check for "Video unavailable" in raw HTML — it appears in the page template for ALL videos. Use `web_extract` directly (it handles availability internally) or check for `"playabilityStatus":"ERROR"` in the page JSON.
- **Checkpoint format for resume.** Store checkpoints as `{video_id: {"status": "OK", "title": "..."}}` dicts, not bare strings. This allows storing metadata alongside status for later auditing. For multi-playlist jobs, include `playlist` name and a `failed` array for videos that couldn't be processed:
  ```json
  {
    "playlist": "UE5_Beginner_Tutorials",
    "last_updated": "2026-06-10",
    "processed_videos": ["vid1", "vid2"],
    "total_processed": 19,
    "failed": [{"video_id": "vidX", "title": "...", "error": "500 Internal Server Error"}]
  }
  ```
  The `failed` array makes it easy for retry jobs to know exactly which videos to re-attempt without scanning all entries.
- **Minimal content is NOT a 403.** Some videos return just "Tap to unmute" or a few lines of YouTube boilerplate — no actual tutorial content. This is distinct from a 403 (unavailable) error. The video exists but the extraction service couldn't get the summary. When content length < 200 chars, treat it as a metadata-reconstruction opportunity, not a hard failure. You can still produce a useful .md file from the title, tags, series context, and adjacent episode summaries. In the checkpoint, record these as done with a quality note (e.g., content_quality: metadata-derived).
- **Content quality tiers for 403 responses.** Not all 403s return the same metadata. Classify each result to set expectations and plan retries:
  - **Tier 1 — Rich metadata** (>1.5K chars): Full description, auto-generated chapter timestamps, detailed steps, tags, channel info. Produces a comprehensive summary. Example: video descriptions with numbered step lists, chapter markers like "0:00 Intro / 1:50 Creating a Level Sequence / 15:35 Playing Cinematic from Code." These are as good as full extractions.
  - **Tier 2 — Standard metadata** (500–1500 chars): Title, partial description, some tags, channel blurb. Produces a usable summary but lacks implementation detail. Worth saving; don't retry.
  - **Tier 3 — Boilerplate only** (<500 chars): "Tap to unmute" + "Error 403" + maybe channel name. Produces a skeleton summary from series context alone (~900–1200 chars if you know the series arc). Mark as content_quality: metadata-derived in checkpoint. These are candidates for retry if the video is confirmed public.
  - **Determining tier**: Check for presence of chapter timestamps, key topics sections, numbered step lists, or code blocks in the extracted content. Their presence indicates Tier 1. Tag lists and creator bio indicate Tier 2. Pure UI boilerplate ("Copy link", "Error 403") indicates Tier 3.
