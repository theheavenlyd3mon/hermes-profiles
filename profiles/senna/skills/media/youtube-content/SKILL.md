---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube Content

**Batch extraction patterns:** See `references/batch-extraction-reliability.md` for cron mode fallback, web_extract reliability handling, checkpoint management, and file naming conventions for batch playlist extraction. Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
pip3 install youtube-transcript-api   # primary tool
pip3 install pytubefix                # for playlist URL extraction
# yt-dlp also works as a fallback for subtitle extraction (often pre-installed)
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

### Batch Playlist Script

```bash
# Fetch all transcripts from a playlist (with 5s delays by default)
python3 SKILL_DIR/scripts/fetch_playlist.py "https://youtube.com/playlist?list=PLAYLIST_ID" [OUTPUT_PATH] [DELAY_SECONDS]

# Example: custom output path with 10-second delays
python3 SKILL_DIR/scripts/fetch_playlist.py "https://youtube.com/playlist?list=PLxxx" ~/my-transcripts.md 10
```

Features:
- **Checkpoint/resume**: saves progress after each video. If interrupted, re-run and it skips already-done videos.
- **Retry with backoff**: on rate limit (429/IpBlocked), retries with exponential backoff (5s → 10s → 20s → ... up to 5min).
- **Auto-fallback**: if `youtube-transcript-api` gets rate-limited, automatically switches to `yt-dlp` with android client for remaining videos.
- **Incremental output**: markdown file is rewritten after each video — partial results are always available.
- Cleans up checkpoint file on successful completion.

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Batch Extraction Pipeline (merged from `youtube-batch-extraction`)

For extracting content from multiple YouTube playlists or large numbers of videos (10+), use the unified batch pipeline:

**Scripts** (in this skill's `scripts/` directory):
- `batch_unified.py` — transcript-first, summary-fallback pipeline with checkpoint/resume
- `batch_transcripts.py` — transcript-only batch processor

**Key references:**
- `references/obsidian-vault-preparation.md` — convert extracted content into an Obsidian vault with wikilinks and MOC files
- `references/ue5-knowledge-base-sources.md` — curated UE5 tutorial playlist sources
- `references/post-extraction-organization.md` — dedup, non-edu triage, naming normalization

**Quick start:**
```bash
python3 SKILL_DIR/scripts/batch_unified.py \
  /tmp/PLAYLIST_NAME_urls.txt \
  --outdir ~/Documents/YouTube-Transcripts/PLAYLIST_NAME \
  --name PLAYLIST_NAME --delay 15 --summary-delay 8
```

See the original `youtube-batch-extraction` skill's SKILL.md content (now archived) for the full pipeline documentation including URL discovery, cron scheduling, and retry logic.

To process a YouTube playlist:

```python
# Step 1: Get all video URLs using pytubefix
from pytubefix import Playlist
playlist = Playlist("https://youtube.com/playlist?list=PLAYLIST_ID")
video_urls = list(playlist.video_urls)
```

```bash
pip3 install pytubefix   # if not installed
```

**Critical: YouTube rate-limits aggressively.** After ~3-5 rapid requests, your IP gets temporarily blocked (429 or `IpBlocked` error). Default to conservative delays (5s+) — being slow is always better than getting blocked mid-batch. For batch processing:

1. **Add delays** — minimum 8-10 seconds between requests (5s is too aggressive — causes 429s on playlists of 20+ videos). 10-15s for medium batches (20-50 videos). **30s+ for large batches (50+ videos)** — YouTube's rate limiter is cumulative; even 8s delays will trigger IP blocks on 80+ video playlists (confirmed: blocked after ~10 videos at 8s delays). When in doubt, go slower.
2. **Prefer cron over background** — `terminal(background=true)` gets killed by session timeouts. Use `cronjob(action='create', script='fetch_playlist.py', schedule='every 30m')` instead. Each run processes a batch, checkpoints progress, and exits. The cron keeps retrying until done.
3. **Write results incrementally** — save each transcript to disk as it's fetched, not all at the end (so partial progress survives interruptions)
4. **Use `PYTHONUNBUFFERED=1`** — otherwise background process output is buffered and invisible
5. **If rate-limited**, wait 15-30 minutes before retrying. The block is temporary.

```bash
# Background batch with progress
PYTHONUNBUFFERED=1 python3 /path/to/batch_script.py 2>&1
```

## Fallback: yt-dlp for Subtitles

When `youtube-transcript-api` is rate-limited, `yt-dlp` can sometimes still fetch subtitles (it uses different request patterns). However, there's a known quirk:

```bash
# This LIST subtitles (works):
python3 -m yt_dlp --list-subs --skip-download "URL"

# But this MAY FAIL silently ("no subtitles for requested languages"):
python3 -m yt_dlp --write-auto-sub --sub-lang en --skip-download "URL"

# Workaround: dump JSON and extract caption URL directly
python3 -m yt_dlp --dump-json --skip-download "URL" | python3 -c "
import sys, json
data = json.load(sys.stdin)
auto = data.get('automatic_captions', {})
for lang, tracks in auto.items():
    for t in tracks:
        print(f'{lang}: {t[\"ext\"]} - {t[\"url\"][:100]}')
"
```

## Fallback: Direct Caption URL Extraction

YouTube embeds caption track URLs in the video page source. Extract with curl + regex:

```python
import subprocess, json, re, html

def get_transcript_from_page(video_id):
    # Step 1: Fetch page
    r = subprocess.run([
        'curl', '-s', '-L', '--max-time', '30',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        f'https://www.youtube.com/watch?v={video_id}'
    ], capture_output=True, text=True, timeout=45)

    # Step 2: Extract caption URL from page source
    match = re.search(r'"captionTracks":\[(.*?)\]', r.stdout)
    if not match:
        return None  # No captions available
    tracks = json.loads('[' + match.group(1) + ']')

    # Step 3: Get caption URL (prefer English)
    caption_url = None
    for t in tracks:
        if t.get('languageCode', '').startswith('en'):
            caption_url = t['baseUrl']
            break
    if not caption_url and tracks:
        caption_url = tracks[0]['baseUrl']
    return caption_url

# Step 4: Fetch and parse (must use SAME session/cookies for caption URL)
# NOTE: Caption URLs are session-bound — fetching with a different curl
# session may return Google "Sorry" error page. Use urllib with cookie jar:
import http.cookiejar, urllib.request
jar = http.cookiejar.MozillaCookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [('User-Agent', 'Mozilla/5.0 ...')]

# Fetch page first (establishes cookies), THEN fetch caption URL
resp = opener.open(page_url)
resp2 = opener.open(caption_url)
xml = resp2.read().decode()

# Parse XML
for m in re.finditer(r'<text start="([\d.]+)"[^>]*>(.*?)</text>', xml):
    text = html.unescape(re.sub(r'<[^>]+>', '', m.group(2)))
```

**This method also gets rate-limited.** Same IP, same limits. The urllib cookie-jar approach helps with session-bound caption URLs but doesn't bypass IP blocks.

## Alternative: web_extract for Structured Summaries

When building a **knowledge base** (e.g., tutorial series for an AI coding agent), `web_extract` on YouTube video pages often produces **better output than raw transcripts**. YouTube's auto-generated chapter summaries include structured code snippets, parameter values, and implementation steps — far more useful than timestamped text.

**Advantages over transcripts:**
- Produces structured markdown with headers, code blocks, and bullet points
- No youtube-transcript-api rate limiting (uses a different scraping path)
- Works even when transcripts are disabled (extracts page metadata + auto-summary)
- Batch of 5 URLs per `web_extract` call

**Workflow for playlist → knowledge base:**
```bash
# 1. Get all video URLs (fast with --flat-playlist)
yt-dlp --flat-playlist --dump-single-json --no-warnings "PLAYLIST_URL" | \
  python3 -c "import json,sys; [print(e.get('id','')) for e in json.load(sys.stdin).get('entries',[])]"
```
Then call `web_extract` in batches of 5 URLs, save each result as a .md file.

**Limitations:**
- Some videos return 403 on the video stream — but the page metadata still comes through. YouTube pages return structured data (title, description, chapter markers, creator info, related videos, hashtags) even when the video itself is inaccessible. This metadata is often sufficient for creating useful tutorial summaries. After completing all batches, retry 403 videos once — many succeed on second attempt (transient scraping failures).
- Rate-limited after ~15-20 rapid batch calls — add 8s delay between batches (matches the main rate-limiting guidance)
- Output is LLM-summarized by the extraction service, not verbatim transcript
- Max ~5000 chars per page (truncated for long videos)
- `write_file` is preferred over `terminal(python3 -c)` for markdown content with special characters (parentheses, backticks, code blocks). Bash interprets these in `python3 -c` strings, causing partial writes or syntax errors. Use `write_file` for all markdown file creation; verify with `terminal(ls/wc)` after.

**When to use this vs transcripts:**
- Knowledge base for AI agent → `web_extract` (structured, code-heavy)
- Verbatim quotes with timestamps → transcripts (youtube-transcript-api)
- User wants to read the full conversation → transcripts
- Game dev tutorials for an AI coding agent → `web_extract` (extracts Blueprint nodes, parameter values, implementation steps)

**⚠️ USER PREFERENCE: Raw transcripts are the DEFAULT.** This user explicitly rejected summaries ("i dont want the summaries unless they go in depth step by step"). `web_extract` produces condensed summaries — use it ONLY when:
- The user explicitly asks for summaries
- Transcripts are unavailable (no captions on the video)
- The user says "just get whatever you can"

If the user says "get the transcripts" or "fetch the content" — that means raw transcripts with timestamps, NOT web_extract summaries. When in doubt, try youtube-transcript-api first; fall back to web_extract only after confirming no captions exist.

**Workflow for large playlists (100+ videos):**
1. Scan playlists: `yt-dlp --flat-playlist --dump-single-json` → save video IDs + titles to `/tmp/PLAYLIST_NAME_urls.txt`
2. Schedule cron jobs spaced 20 min apart, each processing 20 videos
3. Each cron job reads from the temp file, calls `web_extract` in batches of 5 with 8s delays
4. Saves results to `~/Documents/YouTube-Transcripts/PLAYLIST_NAME/` with YAML frontmatter
5. Checkpoint file (`.checkpoint.json`) in each output dir prevents re-processing

See `references/web-extract-alternative.md` for a full worked example and cron job prompt template. See `references/cron-reliability-pitfalls.md` for critical pitfalls when using cron jobs for batch YouTube extraction — one-shot job auto-cleanup, write_file sandbox mismatch, and rate-limiting detection. See `references/terminal-batch-extraction.md` for the execute_code-based batch pattern using yt-dlp URL lists + web_extract in batches (preferred when cron jobs are fragile or the user has a custom extraction workflow).

## Output File Format

### YAML Frontmatter Template
Each knowledge base .md file should use this frontmatter:
```yaml
---
title: "Original Video Title"
source: "https://www.youtube.com/watch?v=VIDEO_ID"
video_id: "VIDEO_ID"
type: youtube-summary
series: "Series Name"
episode: 0
tags: [topic1, topic2, topic3]
---
```
Tags should reflect the series domain (e.g., `[ue5, tutorial, blueprint, gamedev]` for UE5 tutorials).

### File Naming Convention
For ordered tutorial series, prefix filenames with the episode number:
```
NN_Topic_Name.md
```
Examples:
- `01_Introduction.md`
- `79_Character_Mesh.md`
- `83_The_Final_Episode.md`

Sanitization: underscores (not hyphens) for Obsidian compatibility, Title Case, strip special characters (`#`, `!`, `&`, `,`), keep episode number prefix for sort order.

### Obsidian Vault Formatting

When building a knowledge base for Obsidian:

1. **Consistent frontmatter** — every file needs `title`, `source`, `video_id`, `type`, `series`, `episode`, `tags`
2. **Wikilinks** — add `## Related` section at bottom with `← Previous: [[file]]`, `→ Next: [[file]]`, `📚 Series: [[_MOC_Series]]`
3. **MOC files** — one `_MOC_FolderName.md` per folder linking to all files in that series. The underscore prefix sorts it to the top in Obsidian's file explorer. MOC files don't need `source` or `video_id` — they're index files, not content.
4. **No `#` in filenames** — Obsidian interprets `#` as tag syntax. Rename files before importing.
5. **Tags as arrays** — `tags: [ue5, rpg, combat]` not `tags: "ue5, rpg, combat"`
6. **Cross-folder references** — Step-by-Step guides should link back to their source transcripts with `📄 Full Transcript: [[filename]]`

The series wikilink (`📚 Series`) should point to the MOC file, NOT the first episode. The MOC is the canonical entry point for browsing a series.

For the full batch workflow (frontmatter standardization script, wikilink generation, MOC creation, verification), see the `youtube-batch-extraction` skill's `references/obsidian-vault-preparation.md`.

### Checkpoint Format
Track both successful and failed videos to enable targeted retries:
```json
{
  "done": {"VIDEO_ID_1": "transcript", "VIDEO_ID_2": "summary"},
  "failed": ["VIDEO_ID_3"]
}
```
The dict format (video_id → content type) lets you know which files are real transcripts vs summaries for future re-processing. Legacy format used a plain list — always handle migration on load:
```python
done = data.get("done", {})
if isinstance(done, list):
    done = {vid: "transcript" for vid in done}
```

## Pitfalls

- **Rate Limits**: YouTube rate-limits transcript requests. After ~3-5 rapid requests, you may get 429 errors. After rapid-fire attempts, you may get IP-blocked for 30-60 min (all requests return "no transcript" or 403). The helper scripts include retry logic with backoff. For playlists, add delays between fetches (5-10s minimum, 10-15s recommended for 50+ video playlists, 30s+ for 80+ videos). After an IP block, wait 30+ min before retrying (can last up to 60 min — test with a single video before restarting a batch).
- **write_file sandbox mismatch**: The `write_file` tool may write to a sandbox filesystem that doesn't match the terminal's filesystem. Files written via `write_file` won't always be visible to `terminal` commands (ls, find, etc.). **Always verify file persistence with a terminal check** after using write_file for important saves. For mission-critical writes, use `terminal` with python -c or cp instead.
- **hermes_tools not importable from subprocess**: The `hermes_tools` module (web_extract, web_search, etc.) is agent-internal only. Any Python script run via `terminal` or as a background process CANNOT import it. Scripts that need web_extract must be run as agent-driven cron jobs, not background processes.
- **Cron job scheduling**: One-shot cron jobs scheduled for times that have already passed get auto-cleaned silently (no error, just disappear). Always schedule at least 15 min in the future. Space jobs 30 min apart to avoid overlap — each job needs time to complete before the next starts.
- **Cron jobs for transcript fetching should invoke `fetch_playlist.py`**, not a custom script. The checkpoint file (`OUTPUT_PATH.checkpoint.json`) survives across cron runs, so each run picks up where the last left off. Set schedule to `every 30m` or `every 1h` depending on rate limit severity.
- **Checkpoint non-terminal status loops (common bug in custom scripts):** If your checkpoint skip logic only filters `("OK", "FAILED")` but you save other statuses like `NO_SUB`, `TIMEOUT`, or `ERROR`, those videos get retried every run forever — but they keep failing with the same status. The skill's `fetch_playlist.py` correctly includes `TOO_SHORT` in the terminal filter. If writing your own: either (a) treat all non-OK statuses as terminal so you move on to fresh videos, or (b) explicitly include every possible failure status in your skip filter. The symptom is a cron job stuck at "0/N OK" across every run despite the API working fine for other videos.
- **Backoff settings for cron context:** `BACKOFF_BASE=20` with `MAX_RETRIES=3` means 20+40+80 = 140 seconds per rate-limited video. With 8 videos per batch, a single rate-limited batch can take 18+ minutes, exceeding typical cron timeout windows. The skill's `fetch_playlist.py` uses `BASE_DELAY=5` with `BACKOFF_MULT=2` and `MAX_BACKOFF=300` — more reasonable. For cron scripts, keep per-video retry budget under 60s total.
- **Stale checkpoint recovery:** When a checkpoint has all entries stuck in a non-terminal failure state (e.g., all `NO_SUB`), the fix is to delete the checkpoint file and let the script re-process from scratch. Don't just restart the cron — the stale entries persist. Checkpoint path for `fetch_playlist.py`: `OUTPUT_PATH.checkpoint.json`. For custom scripts: check `/tmp/yt_transcript_checkpoint*.json`.
- **Post-extraction verification: count content, not just files.** After a batch extraction, don't just count files — check content quality. Pattern:
  ```python
  # Count total files
  total = terminal("ls dir/*.md | wc -l")["output"].strip()
  # Count files with real content (>200 bytes)
  good = terminal("find dir -name '*.md' -size +200c | wc -l")["output"].strip()
  # Count stubs (<=200 bytes)
  stubs = int(total) - int(good)
  # Check for duplicates from multiple runs (files exceeding expected count)
  ```
  Also classify by content type: `grep -rl '[**0-9]' dir/*.md` finds real transcripts (with timestamps), while the rest are description-only summaries. This distinction matters when deciding what to process further.
- **`stat -f '%z'` fails with `#` in filenames.** On macOS, `stat -f '%z' 'file with #.md'` returns 0 or errors because `#` is interpreted as a shell comment. `wc -c < 'file'` has the same issue. **Use `os.path.getsize()` in Python** — it handles all special characters natively. This matters when comparing file sizes during deduplication.
- **Most playlist files are non-educational descriptions.** After extraction, many files will be YouTube descriptions only (50-200 words, links, chapter timestamps) with no actual tutorial content. Typical breakdown: 10-30% real transcripts/summaries with steps, 70-90% description-only. Use word count + step markers to triage: files with `< 200 words` and no `## Step` / `### 1` / `1. **` patterns are description-only. Move these to a `_non_educational/` folder (NOT `_duplicates/` — that's for same-content copies). Preserve subfolder structure so the user can see where each came from. The user reviews `_non_educational/` and decides what to keep or delete. See `references/research-pipeline.md` for the full pipeline for finding NEW videos by topic gap analysis, version verification, priority-based extraction, and user review workflow. See `references/post-extraction-organization.md` for the full triage workflow and script patterns.
- **`wc -l` reports 0 for files without trailing newlines.** Heredocs (`cat > file << 'EOF'`) strip the trailing newline. `wc -l` counts newline characters, so a file with content but no final `\n` reports 0 lines. Use `wc -c` (byte count) or `grep -c ''` instead when verifying file content. Or add an explicit `echo >> file` after the heredoc to ensure a trailing newline.
- **Rate limiting is the #1 blocker for batch work.** Don't promise the user you'll process 50+ videos in one go. Be upfront about delays. The script handles this automatically with backoff and yt-dlp fallback.
- **Rate-limited requests return "no transcript" instead of an error.** `youtube-transcript-api` can silently return empty results when your IP is throttled — it looks identical to a video that genuinely has no transcripts. If you see a long streak of "no transcript" after prior rapid requests, assume rate limiting, not missing transcripts. Wait 15-30 min and retry. The tell: videos that worked in a prior run suddenly show "no transcript" on retry.
- **`youtube-transcript-api` v1.x constructor changed.** The `YouTubeTranscriptApi()` constructor no longer takes a list directly — use `api.fetch(video_id)` instead of `YouTubeTranscriptApi.list_transcripts(video_id)`. The `fetch()` method returns a list of `FetchedTranscriptSnippet` objects with `.text`, `.start`, `.duration` attributes.
- **None titles in playlist entries.** Some YouTube playlist entries have `None` as their title. Always guard: `title = v['title'] or 'Untitled'` before indexing or printing. Crashes on `v['title'][:80]` with `TypeError: 'NoneType' object is not subscriptable`. When processing from a text file (e.g., `video_id|title` format), skip lines where the title field is literally "None" — these are typically removed/private videos that will fail extraction. Don't assign "Untitled" and attempt extraction; just skip and log the video ID as skipped in the checkpoint.
- **Double yt-dlp call is a common custom-script bug.** If your script calls yt-dlp twice — once with `--flat-playlist` for entries, once without for the playlist title — the second call fetches full metadata for ALL videos and hangs on large playlists. The title is already in the first `--flat-playlist` response (`data.get('title', '')`). One call is enough.
- **`hermes_tools` cannot be imported from subprocess.** If you try to create a standalone Python script that does `from hermes_tools import web_extract`, it will fail with `No module named 'hermes_tools'`. The `web_extract` function is agent-internal — it can only be called directly from the agent's tool-calling interface, not from a background script. For batch web_extract processing, use cron jobs with agent prompts (not `no_agent` scripts) that call `web_extract` directly.
- **`write_file` vs `terminal` for file writes — context-dependent.** The reliable tool depends on session type:
  - **Discord sessions:** `write_file` may write to a sandbox that doesn't match the terminal filesystem. Use `terminal` with `python3 -c "open(path,'w').write(content)"` or heredoc syntax instead. Verify with `terminal` after writing.
  - **Cron sessions (no user present):** `terminal` heredocs (`cat > file << 'EOF'`) have TWO failure modes: (1) silent failure — returns "DONE" but files don't exist on disk; (2) active error — returns "Foreground command uses '& backgrounding'" when markdown content contains shell-special characters (`*`, `&`, `(`, `)`), even with a quoted heredoc delimiter. Use `write_file` instead — it reliably persists in cron context. This is the opposite of Discord behavior. **Rule: Always use `write_file` for batch file creation in cron sessions.**
  - **Always verify** file persistence with a terminal `ls` or `wc -c` check after writing, regardless of which tool you used.
  - This is especially critical for knowledge base files — losing hours of extraction work to a silent write failure is a painful lesson.
- **One-shot cron jobs auto-cleanup without executing.** One-shot cron jobs (`repeat: once`) get auto-removed when their scheduled time passes, even if they never actually ran. In this session, 11 scheduled jobs were created for 11:15 AM-2:00 PM, but by 3:21 PM all had disappeared without producing any output files. The jobs were cleaned up by the scheduler but never executed. **Critical workaround:** Always verify cron job execution by checking the filesystem for expected output files, not just by checking if the job exists in the cron list. If jobs disappear without running, rebuild them with future-dated schedules immediately. Consider spacing jobs 15-20 minutes apart and monitoring the first batch to confirm execution before trusting the rest.
- **Rate-limited requests return misleading "no transcript" instead of errors.** `youtube-transcript-api` silently returns empty results when your IP is throttled — it looks identical to a video that genuinely has no transcripts. If you see a long streak of "no transcript" after prior rapid requests, assume rate limiting, not missing transcripts. The tell: videos that worked in a prior run suddenly show "no transcript" on retry. Wait 15-30 min and retry.
- **Metadata-only extraction on retry.** Sometimes `web_extract` times out on first attempt, succeeds on retry, but returns only page metadata (title, description, tags) without actual tutorial content. The YouTube page may have minimal description and no transcript. Signs: content <200 chars, no code snippets, no implementation steps. **Workaround:** (1) Try browser navigation to expand the description or find a transcript button. (2) If still no content, create a metadata-only summary with a `## Note` section explaining "Full tutorial content was not available for extraction (YouTube transcript not enabled, minimal description)." Include whatever context you can infer from the title, series position, and related videos. Mark these in the checkpoint with a `notes` field so future retry runs can target them specifically. Don't skip the video entirely — a metadata stub is better than nothing and can be enriched later.
- **`execute_code` is blocked in cron mode.** When running as a scheduled cron job (no user present), `execute_code` is denied with "BLOCKED: cron jobs run without a user present." You cannot use `execute_code` to script batch loops, conditionals, or batched file writes in cron context. Workaround: use direct tool calls — call `web_extract` with up to 5 URLs per batch, then call `write_file` for each result, sequentially. Plan for ~4x more tool calls than you'd need with `execute_code`. If the batch is large (20+ videos), consider splitting across multiple cron jobs (each processing 10-15 videos) rather than trying to fit everything into one cron run.
- **Retry once before marking failed.** `web_extract` can fail with 500 or 403 on a video that succeeds on the next attempt (transient scraping failures). After completing all batches, retry failed videos once. Only persist failures to the checkpoint after the retry pass. Videos that fail twice are genuinely unavailable (private, removed) — don't retry further. **403 errors specifically are often transient** — in a 20-video batch, 5 returned 403 on first attempt, all 5 succeeded on immediate retry without any cooldown.
- **Cron job pattern for web_extract batches.** When processing many videos with web_extract, schedule cron jobs spaced 20 min apart, each processing 20 videos in batches of 5 with 8s delays. Use `cronjob(action='create')` with a self-contained prompt that instructs the agent to read URLs from a temp file, call web_extract in batches, and save results. Checkpoint files in each output directory prevent re-processing. Example schedule: 11:15, 11:35, 11:55, 12:15, 12:35 (5 jobs × 20 videos = 100 videos).
- **Don't present options when the user wants results.** If the fetcher breaks, fix it and deliver — don't lay out 4 options and ask which direction. The user said "we need those scripts" meaning "stop talking and ship it."
- **Cron jobs and transcript batches conflict.** If you have cron jobs running `web_extract` summaries AND a transcript batch fetching raw captions to the same directory, they'll create files with different names and different content types. The summaries use short filenames (`060-title.md`, 1-2KB) while transcripts use full titles (`Playlist_Name_-_#60_Title.md`, 20-60KB). This confuses the user. **Rule:** Never run both approaches to the same output directory simultaneously. Pick one method per playlist directory. If switching from summaries to transcripts, delete the old summary files first (filter by size: <5KB = summary, >5KB = transcript).
- **yt-dlp PO token (2025+):**
- **Background Python output is invisible by default.** When running Python via `terminal(background=true)`, stderr/stdout are buffered (not a TTY). You MUST set `PYTHONUNBUFFERED=1` AND pass `-u` to Python: `PYTHONUNBUFFERED=1 python3 -u script.py 2>&1`. Without both, the process runs but produces zero visible output — you'll poll forever seeing nothing. Even with both, output capture in background mode can be unreliable — if you see no output after 30s+, the script may still be running correctly. Verify by checking output files on disk.
- **`yt-dlp --dump-single-json` without `--flat-playlist` hangs on large playlists.** When fetching playlist metadata, ALWAYS use `--flat-playlist`. Without it, yt-dlp fetches full metadata for every video — on 80+ video playlists this hangs for minutes. The correct pattern: `yt-dlp --flat-playlist --dump-single-json --no-warnings PLAYLIST_URL` returns title + entries in seconds. A second call without `--flat-playlist` (to get the playlist title) is a common bug — the title is already in the first response.
- **yt-dlp large JSON output corrupts when captured by `terminal()`.** When `execute_code` calls `terminal()` to run yt-dlp with `--dump-single-json`, large playlists (40+ videos) produce JSON that is too large or contains control characters, causing `json.JSONDecodeError` on parse. **Fix:** Pipe yt-dlp output directly to a file instead of capturing in terminal(), then parse from the file in a separate call. Pattern:
  ```python
  # BAD: captures in terminal, JSON parse fails on large output
  r = terminal('yt-dlp --flat-playlist --dump-single-json URL')
  data = json.loads(r["output"])  # JSONDecodeError

  # GOOD: pipe to file, parse from disk
  terminal('yt-dlp --flat-playlist --dump-single-json URL > /tmp/name.json')
  # Then parse with a helper script written to disk first
  terminal("python3 /tmp/parse_helper.py /tmp/name.json /tmp/name_urls.txt")
  ```
  Write the parser script to disk first (cat heredoc), then invoke it. Avoids quoting hell with inline Python in shell commands.
- **`yt-dlp` android client finds auto-captions the API misses.** When `youtube-transcript-api` says "no transcript" but you suspect captions exist, try: `yt-dlp --extractor-args "youtube:player_client=android" --list-subs --skip-download "URL"`. The android client bypasses PO token requirements and often finds auto-captions. However, downloading them may still hit 429.
- **yt-dlp PO token (2025+):** Newer yt-dlp versions require a PO token for auto-caption access via the default web client. Use `--extractor-args "youtube:player_client=android"` to bypass. See `references/ytdlp-quirks.md` for details.
- **Post-extraction organization is a separate phase.** After extraction completes, you have raw files — not a usable knowledge base. The organization pipeline (dedup → non-edu triage → naming normalization → Obsidian formatting) is a distinct workflow that takes 20-30 min for 200+ files. Don't skip it. See `references/post-extraction-organization.md` for the full pipeline.
- **`_non_educational/` and `_duplicates/` are different.** Duplicates = same content, different names (from multiple extraction runs). Non-educational = unique files that lack how-to content (YouTube descriptions, chapter lists, promos). They go in separate folders at the vault root. The user reviews `_non_educational/` and decides what to keep; `_duplicates/` can be deleted when the user is confident.
- **Subagent and execute_code file writes don't persist to real filesystem.** Two distinct failure modes:
  - **Subagent delegation (delegate_task):** terminal() writes from the subagent go to a sandbox that doesn't match the real filesystem. Files appear to be created (terminal returns success) but don't exist when checked from the main session. write_file from subagents is inconsistent — sometimes persists, sometimes doesn't. **Fix:** Use write_file directly from the main session, not via delegation. If you must delegate, have the subagent use write_file (not terminal) and verify persistence with a terminal(ls) check afterward.
  - **execute_code sandbox:** terminal() calls from within execute_code also run in a sandbox. write_file imported from hermes_tools within execute_code writes to the sandbox, not the real filesystem. **Fix:** For writes that must persist, use the top-level write_file tool directly (outside execute_code), or use terminal() to run cp from a temp file created by the write_file tool.
  - This is the biggest time-waster in batch extraction workflows — an entire batch can succeed in a subagent or execute_code but produce zero files on disk. Always verify with terminal(ls -la path) after writes.
- **`ls -t` output includes file sizes when piped.** When `ls -t` output is piped to another command (e.g., `ls -t dir/*.md | head -5 | xargs cat`), some systems include file size annotations in the output, breaking downstream commands. Use `ls -1` for clean filename-only output, or `find ... -exec` for reliable file iteration.
- **`youtube-transcript-api` v1.x** supports `proxy_config` and `http_client` params in the constructor — useful if you have a proxy available:
  ```python
  from youtube_transcript_api import YouTubeTranscriptApi
  from youtube_transcript_api.proxies import GenericProxyConfig
  api = YouTubeTranscriptApi(proxy_config=GenericProxyConfig(
      http_url="http://proxy:port",
      https_url="http://proxy:port"
  ))
  ```
- **curl-based "Video unavailable" detection has false positives.** The string "Video unavailable" appears in YouTube's page template for ALL videos, not just unavailable ones. Checking for this string in raw HTML will incorrectly mark every video as unavailable. Correct detection: check for `"playabilityStatus":"ERROR"` in the JSON data, or verify the video ID appears in the page (`f'"videoId":"{video_id}"' in html`). Better yet, just extract the title/description — if they're present, the video is available.
- **`list[dict] | None` type annotation fails on Python 3.9.** PEP 604 union types (`X | Y`) require Python 3.10+. On macOS system Python (3.9) or older environments, this crashes with `TypeError: unsupported operand type(s) for |`. Use `Optional[list[dict]]` from `typing` instead, or `from __future__ import annotations` to defer evaluation.
- **Cron job script path requirement.** Scripts for `cronjob(no_agent=true, script=...)` must be placed in `~/.hermes/scripts/` and referenced by filename only (e.g., `script='my_script.sh'`), not absolute paths. The cron system resolves paths relative to that directory. Absolute paths are rejected.
- **Script path resolution**: The helper script lives at the skill's `scripts/fetch_transcript.py`. Use the absolute path from `skill_dir`, not `SKILL_DIR` in shell commands (the variable doesn't expand in all contexts).
- **pytubefix** is the maintained fork of pytube. Use `from pytubefix import Playlist` not `from pytube`.

## Error Handling

- **IP Blocked / 429**: YouTube has rate-limited your IP. Wait 15-30 minutes. For batch jobs, add longer delays between requests (5+ seconds). Suggest VPN/proxy if user needs results now.
- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `pip3 install youtube-transcript-api` and retry.
- **yt-dlp `--write-auto-sub` fails but `--list-subs` shows captions**: Known quirk. Use `--dump-json` to extract caption URL directly, or fall back to page-source extraction.
