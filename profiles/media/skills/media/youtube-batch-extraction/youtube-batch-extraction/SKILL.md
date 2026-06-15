---
name: youtube-batch-extraction
description: "Batch extraction pipeline for multiple YouTube playlists — URL discovery, rate-limited web_extract, checkpoint/resume, cron scheduling, retry logic."
triggers:
  - "extract multiple YouTube playlists"
  - "batch YouTube transcript extraction"
  - "large YouTube playlist extraction"
  - "YouTube playlist pipeline"
tags: [youtube, extraction, batch, pipeline, transcripts, web-extract, cron]
---

# YouTube Batch Extraction Pipeline

## When to Use
User wants to extract content from multiple YouTube playlists or a large number of videos (10+). This covers the full pipeline: URL discovery, rate-limited extraction, checkpoint/resume, cron scheduling, and retry logic.

## Overview
Two extraction methods, chosen by need:
1. **yt-dlp transcripts** — fast (3-5s/video), only works if creator enabled captions
2. **web_extract summaries** — slower (10-15s/video), works on all videos, produces richer structured content

For game dev tutorials, web_extract is preferred — it produces step-by-step implementation details, code snippets, and parameter values rather than raw timestamped text.

**Preferred: Unified pipeline** (`scripts/batch_unified.py`) — tries transcript API first, falls back to page-scraped summary. Handles both paths automatically. Use this for new batch work.

## Prerequisites

```bash
brew install yt-dlp   # required for URL discovery and subtitle extraction
```

yt-dlp is NOT installed by default on macOS. The `execute_code` sandbox uses system Python (3.9) which doesn't have yt-dlp in PATH. Install via Homebrew — pip's `--user` flag is unsupported on modern macOS without a venv.

## Unified Pipeline (transcript-first, summary-fallback)

The preferred approach for batch processing: try `youtube-transcript-api` for raw transcripts first, fall back to page-scraped summaries for videos without captions. Use `scripts/batch_unified.py` (in this skill's scripts/ directory):

```bash
# Single playlist (use ABSOLUTE paths — ~ expands to sandbox home in cron/agent context)
python3 ~/.hermes/profiles/senna/skills/media/youtube-batch-extraction/scripts/batch_unified.py \
  /tmp/PLAYLIST_NAME_urls.txt \
  --outdir ~/documents/transcripts/PLAYLIST_NAME \
  --name PLAYLIST_NAME \
  --delay 15 --summary-delay 8

# Process a subset (lines 41-43 from a 1-indexed file → --start 40 --limit 3)
python3 .../batch_unified.py /tmp/urls.txt --start 40 --limit 3 --outdir /absolute/path --name NAME

# All playlists at once
python3 SKILL_DIR/scripts/batch_unified.py --all --delay 15 --summary-delay 5
```

**Critical `--outdir` behavior:** The script ALWAYS creates a nested directory: `outdir/PLAYLIST_NAME/`. It does NOT write directly to `outdir`. After the script completes, files are at `outdir/PLAYLIST_NAME/*.md` and the checkpoint is at `outdir/PLAYLIST_NAME/.checkpoint.json`. You must move/copy them to the intended final location.

**Critical `--start` indexing:** `--start` is 0-based (first line = 0). URL files are 1-indexed (line 1 = first video). To process lines 41-43: use `--start 40 --limit 3`. Using `--start 41` skips the first video and processes lines 42-44.

**Delay settings:**
- `--delay 15` — seconds between transcript API calls (15s minimum to avoid IP bans on 50+ video playlists; 30s for 80+ videos)
- `--summary-delay 5` — seconds between page-scrape summaries (safer, no API ban risk)

**Checkpoint format:** Dict with `video_id -> "transcript"|"summary"`. Handles migration from old list format automatically.

**Output:** Transcripts are 20-60KB with timestamps. Summaries are 1-2KB with title, channel, duration, description, and chapters extracted from page source.

## Pipeline Steps

### Step 0: Check Existing Output (ALWAYS FIRST)
Before running ANY pipeline step, check whether prior runs already completed the work:
```python
from hermes_tools import terminal

for name in playlists:
    outdir = f"~/documents/transcripts/{name}"
    total = terminal(f"ls '{outdir}'/*.md 2>/dev/null | wc -l")["output"].strip()
    good = terminal(f"find '{outdir}' -name '*.md' -size +200c | wc -l")["output"].strip()
    stubs = terminal(f"find '{outdir}' -name '*.md' ! -size +200c | wc -l")["output"].strip()
    print(f"{name}: {total} files, {good} good (>200b), {stubs} stubs")
```
If `good` count meets or exceeds expected video count, that playlist is DONE — skip it. Don't rebuild URL lists, don't install tools, don't re-process. Only work on playlists with missing or stub files.

### Step 1: Discover URLs
```bash
YTDLP="~/.hermes/hermes-agent/venv/bin/yt-dlp"
"$YTDLP" --flat-playlist --dump-single-json --no-warnings "PLAYLIST_URL" | \
  python3 -c "
import json,sys
d=json.load(sys.stdin)
for e in d.get('entries',[]):
    vid=e.get('id') or e.get('url','').split('v=')[-1].split('&')[0]
    print(f'{vid}|{e.get(\"title\",\"Untitled\")}')
" > /tmp/PLAYLIST_NAME_urls.txt
```
Save to `/tmp/PLAYLIST_NAME_urls.txt` — one `video_id|title` per line. Use `--flat-playlist` to avoid fetching full metadata (very slow on 50+ video playlists).

### Step 2: Extract via web_extract (agent-driven)
- Call `web_extract` in batches of 5 URLs max (API limit)
- 8-10 second delay between batches
- Save each summary as `.md` with YAML frontmatter:
```yaml
---
title: "Video Title"
source: "https://www.youtube.com/watch?v=VIDEO_ID"
video_id: "VIDEO_ID"
type: "youtube-summary"
tags: [ue5, tutorial, topic, gamedev]
---
```
- Write files via Python script in terminal with explicit absolute paths (most reliable method across all session types); see Pitfalls section for write_file and heredoc gotchas
- Output dir: `~/Documents/YouTube-Transcripts/PLAYLIST_NAME/`

### Step 3: Checkpoint tracking
Save `~/Documents/YouTube-Transcripts/PLAYLIST_NAME/.checkpoint.json`.

**Current format (dict)** — tracks content type:
```json
{"done": {"vid1": "transcript", "vid2": "summary"}, "failed": ["vid3"]}
```

**Legacy format (list)** — just video IDs:
```json
{"done": ["vid1", "vid2"], "failed": ["vid3"]}
```

Always handle migration on load:
```python
done = data.get("done", {})
if isinstance(done, list):
    done = {vid: "transcript" for vid in done}
    data["done"] = done
```

The dict format lets you know which files are real transcripts (>5KB) vs summaries (<2KB) for future re-processing.

### Step 4: Cron scheduling for large batches
- One agent-driven cron job per 20-video batch
- **30 minutes between jobs** (generous spacing prevents overlap)
- Each job reads `/tmp/PLAYLIST_NAME_urls.txt`, skips already-done videos
- Retry job scheduled 30 min after last batch
- Schedule at least 15 min in the future (past times get auto-cleaned silently)

### Step 5: Retry failed videos
- Check `.checkpoint.json` for "failed" list
- Retry with 10s delay between attempts
- Some videos fail on first pass due to transient YouTube errors

## Output Format
```markdown
---
title: "Video Title"
source: "https://www.youtube.com/watch?v=VIDEO_ID"
video_id: "VIDEO_ID"
type: "youtube-summary"
tags: [ue5, tutorial, topic, gamedev]
---

# Video Title

**URL:** ...
**Creator:** ...
**Length:** ...

## Overview
[2-3 sentence summary]

## Key Implementation Details
[Structured content with code snippets, node names, parameter values]

## Timestamps
| Time | Topic |
|------|-------|
| 0:00 | ... |
```

## Pitfalls

- **File writing reliability (critical)**: Neither `write_file` nor terminal heredocs are fully reliable for writing markdown summaries:
  - `write_file` may report success (bytes_written, resolved_path) but files don't actually persist to the real filesystem. In sandboxed/cron environments, it may write to a virtual overlay that doesn't match the real path.
  - Terminal heredocs (`cat > file << 'EOF'`) fail when markdown content contains shell-interpreted characters (`&`, backticks, `$`, `*` in certain contexts). Error: "Foreground command uses '&' backgrounding."
  - Terminal `~` resolves to the sandbox home (e.g., `~/.hermes/profiles/senna/home/...`) while `write_file` resolves to the real home (`~/...`). Files split across both locations.
  - **Reliable method**: Use Python via terminal with explicit absolute paths:
    ```python
    python3 -c "
    import os
    dest = '~/documents/transcripts/PLAYLIST_NAME'
    for name, content in files.items():
        with open(os.path.join(dest, name), 'w') as f:
            f.write(content)
    "
    ```
  - Always verify with `terminal` ls/find after writing, regardless of method used.
- **hermes_tools not importable**: `web_extract` etc. are agent-internal. Background scripts CANNOT use them. Must use agent-driven cron jobs.
- **Cron auto-cleanup**: One-shot jobs scheduled in the past disappear silently. Schedule 15+ min in the future.
- **Non-English extraction results**: web_extract sometimes returns summaries in the video's spoken language rather than English (e.g., Chinese for a Chinese-dubbed tutorial). When this happens, translate and rewrite the summary in the target language when saving the .md file — don't save non-English content to an English knowledge base.
- **Rate limiting**: After rapid-fire YouTube requests, you may get IP-blocked for 15-30 min. Use 8-10s delays. After a block, wait 30+ min.
- **403 errors are often transient — retry immediately.** When `web_extract` returns 403 Forbidden on YouTube URLs, retry the same URLs in the next batch cycle. In a 20-video batch processed in 4 groups of 5, 5 videos initially returned 403 — all 5 succeeded on immediate retry (no 30-min cooldown needed). This is distinct from IP-level rate blocking. The 403 appears to be YouTube's per-request scraping defense, not an IP ban. Pattern: collect failures during batch processing → retry all failures in a single final batch → only mark truly failed after retry.
- **Sibling subagent file conflicts (harmless).** When multiple Hermes sessions or subagents write to the same output directory concurrently, `write_file` may return warnings like "was modified by sibling subagent... but this agent never read it." This is a safety check, not an error — the writes still succeed. The warning appears when two agents write the same filename within a short window. If processing a playlist with multiple concurrent cron jobs, expect these warnings. They don't affect file content or integrity. No action needed.
- **`wc -l` returns 0 for heredoc-written files.** The `cat > file << 'EOF'` heredoc pattern strips trailing newlines. `wc -l` counts newline characters, so a file with content but no final `\n` reports 0 lines. This caused a false "0 URLs" report when the files actually had 43 and 85 entries. **Fix:** Use `wc -c` (byte count) or `ls -la` to verify file size, or `python3 -c "print(len(open(f).readlines()))"` which counts lines regardless of trailing newline.
- **`execute_code` quoting hell with shell-in-Python.** When `execute_code` scripts need to run shell commands with complex quoting (nested single/double/escaped quotes), the string escaping becomes fragile and breaks. **Fix:** Write the helper script to disk first via `terminal()` with a heredoc, then call it by path:
  ```python
  terminal(f"cat > /tmp/helper.py << 'EOF'\n{script_content}\nEOF")
  terminal(f"python3 /tmp/helper.py '{arg1}' '{arg2}'")
  ```
  This avoids all quoting issues since the script content is in a quoted heredoc and arguments are passed separately.
- **`yt-dlp --flat-playlist`: Always use for playlist metadata.** Without it, yt-dlp fetches full video info for ALL videos (extremely slow on large playlists).
- **Python type annotations**: Use `from __future__ import annotations` for `|` syntax on Python <3.10. Always handle None titles from yt-dlp — skip lines where title is "None" or empty when reading URL files.
- **Cron/transcript conflict**: If cron jobs are running `web_extract` summaries to the same directory where you're fetching raw transcripts, they'll create files with different names and sizes. Summaries use short filenames (`060-title.md`, 1-2KB) while transcripts use full titles (`Playlist_Name_-_#60_Title.md`, 20-60KB). **Rule:** Never run both approaches to the same output directory simultaneously. If switching from summaries to transcripts, delete old summary files first (filter by size: <5KB = summary, >5KB = transcript). Check for re-created summaries periodically during long transcript batches.
- **Most videos in a playlist may lack captions.** Don't assume all videos have transcripts. In a typical tutorial playlist, only 10-30% may have captions enabled. The unified pipeline handles this gracefully — transcript API returns `None`, summary fallback kicks in. Report the final breakdown (📝 X transcripts, 📋 Y summaries, ❌ Z failed) so the user knows the coverage.
- **Don't present options when you can execute.** If the pipeline breaks, fix it and deliver. Don't lay out 4 options and ask which direction. The user said "run it" meaning "stop talking and deliver results."
- **YouTube page-source summary extraction**: When `youtube-transcript-api` and `web_extract` both fail or are rate-limited, you can still extract useful metadata directly from the YouTube page via curl + regex. The `batch_unified.py` script's `fetch_summary_via_curl()` function does this — extracts title, channel, duration, description, and chapters from the page HTML. This never gets rate-limited (same as loading a webpage) but produces less structured content than `web_extract`.
- **Cron job spacing**: 30 min between jobs. Each batch of 20 takes ~5-10 min. Tighter spacing causes overlap failures.
- **Post-batch file relocation required**: Because `--outdir` always nests (`outdir/PLAYLIST_NAME/`), files end up in a subdirectory. After the script completes: (1) copy/move `*.md` and `.checkpoint.json` from the nested dir to the intended output dir, (2) verify with `ls -la` on the target, (3) clean up the nested dir. Do this immediately after each batch run — don't leave files in the wrong location.
- **YouTube IP block = expected fallback, not an error**: After processing a batch of transcripts (typically 3-5 videos), YouTube will IP-block the transcript API. The `batch_unified.py` script automatically falls back to page-scraped summaries for remaining videos. This is normal — report the breakdown (📝 N transcripts, 📋 M summaries) and note that transcripts can be retried after 30+ min cooldown. Don't retry transcripts in the same session.
- **Merge with previous-run transcripts**: When a directory already contains transcript files from prior runs (>2KB, with timestamps) and a new batch produces summaries (<2KB, description+chapters only) for the same videos, KEEP the transcripts. They contain more detailed content. After a batch run: (1) detect duplicates by video_id in frontmatter, (2) keep the largest file, (3) move smaller duplicates to `_duplicates/`, (4) update checkpoint to reflect actual content types.

## Post-Extraction Organization

After extraction completes, the output directory typically needs cleanup: duplicate files from multiple runs, inconsistent naming, and a mix of educational vs non-educational content. See `references/post-extraction-organization.md` for the full workflow covering:

- **Content quality triage**: Classify files as educational (steps, >200 words, structured) vs non-educational (YouTube descriptions, chapter lists, links-only). Script pattern included.
- **Folder deduplication**: When the same series exists across multiple directories, compare file sizes, keep the largest version, move dupes to `_duplicates/`.
- **File naming normalization**: Consistent `NN_Topic_Name.md` format, strip special chars, remove long prefixes. Use `os.rename()` (not shell) for files with `#`, `!`, `,` in names.
- **`_duplicates/` protection**: Never run broad `find -delete` or `xargs rm` against the extraction root — scope cleanup commands to specific directories or use Python with explicit path checks.

## Obsidian Vault Preparation

After organization, convert the directory into an Obsidian vault. See `references/obsidian-vault-preparation.md` for the full workflow covering:

- **Frontmatter standardization**: Consistent YAML with title, source, video_id, type, series, episode, tags. Folder→series mapping for batch processing.
- **Wikilink generation**: `## Related` section with `← Previous`, `→ Next`, `📚 Series: [[_MOC_Folder]]` links. Cross-folder references for Step-by-Step guides → source transcripts.
- **MOC index files**: One `_MOC_FolderName.md` per folder linking to all files. Entry point for browsing the vault.
- **Verification**: 100% frontmatter, 99%+ wikilinks, all folders have MOC.