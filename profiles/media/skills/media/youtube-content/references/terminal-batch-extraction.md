# Terminal-Based Batch Extraction Pattern

When `web_extract` or `youtube-transcript-api` fail or produce low-quality output, fall back to terminal-based extraction using `yt-dlp` + `execute_code`.

## The Problem This Solves

- `web_extract` returns YouTube descriptions (1-3KB) instead of actual tutorial content
- `youtube-transcript-api` gets rate-limited on large playlists
- Cron jobs write to sandbox that doesn't persist to real filesystem

## Pattern: yt-dlp URL list + web_extract in execute_code

### Step 1: Build URL Lists

```python
from hermes_tools import terminal

# Write parser script to disk FIRST (avoids quoting hell)
parser = '''
import json, sys, os

for jf in sys.argv[1:]:
    name = os.path.basename(jf).replace("_raw.json", "")
    outf = f"/tmp/{name}_urls.txt"
    try:
        data = json.load(open(jf, encoding="utf-8"))
        entries = data.get("entries", [])
        with open(outf, "w") as f:
            for e in entries:
                vid = e.get("id", "")
                title = e.get("title", "Untitled").replace("\\n", " ")
                f.write(f"{vid}|{title}\\n")
        print(f"{name}: {len(entries)} entries")
    except Exception as ex:
        print(f"{name}: ERROR {ex}")
'''
terminal(f"cat > /tmp/parse_urls.py << 'EOF'\n{parser}\nEOF")

# For each playlist: dump JSON to file (NOT terminal capture), then parse
for name, url in playlist_urls.items():
    terminal(f'yt-dlp --flat-playlist --dump-single-json --no-warnings "{url}" > /tmp/{name}_raw.json', timeout=180)

terminal("python3 /tmp/parse_urls.py /tmp/*_raw.json")
```

### Step 2: Process with web_extract (batches of 5, 10s delays)

```python
import re, time
from hermes_tools import web_extract, terminal

PLAYLIST = "Playlist_Name"
URL_FILE = f"/tmp/{PLAYLIST}_urls.txt"
OUT_DIR = f"~/Documents/YouTube-Transcripts/{PLAYLIST}"

terminal(f"mkdir -p {OUT_DIR}")

# Check existing files (skip duplicates)
existing = terminal(f"ls {OUT_DIR}/*.md 2>/dev/null | xargs -I{{}} basename {{}}")["output"]

def sanitize(title):
    s = re.sub(r'[^\w\s-]', '', title)[:100].strip()
    return re.sub(r'[\s]+', '_', s)

def save_summary(title, video_id, content):
    fname = sanitize(title) + ".md"
    if fname in existing:
        return  # skip
    path = f"{OUT_DIR}/{fname}"
    md = f"---\ntitle: \"{title}\"\nsource: https://www.youtube.com/watch?v={video_id}\nvideo_id: {video_id}\ntype: youtube-summary\ntags: [ue5, tutorial]\n---\n\n{content}"
    terminal(f"cat > '{path}' << 'TRANSCRIPT_EOF'\n{md}\nTRANSCRIPT_EOF")

# Read URLs
videos = []
for line in open(URL_FILE):
    parts = line.strip().split("|", 1)
    if len(parts) == 2 and parts[0]:
        videos.append((parts[0], parts[1]))

# Process in batches of 5
failed = []
for i in range(0, len(videos), 5):
    batch = videos[i:i+5]
    urls = [f"https://www.youtube.com/watch?v={vid}" for vid, _ in batch]
    results = web_extract(urls)
    for (vid, title), r in zip(batch, results.get("results", [])):
        content = r.get("content", "")
        if not content or r.get("error") or len(content) < 200:
            failed.append((vid, title))
        else:
            save_summary(title, vid, content)
    if i + 5 < len(videos):
        time.sleep(10)

print(f"Done: {len(videos) - len(failed)}/{len(videos)} succeeded")
```

### Step 3: Verify

```python
from hermes_tools import terminal

total = terminal(f"ls {OUT_DIR}/*.md | wc -l")["output"].strip()
good = terminal(f"find {OUT_DIR} -name '*.md' -size +200c | wc -l")["output"].strip()
print(f"Files: {total} total, {good} with content")
```

## Key Lessons

- **ALWAYS use `terminal()` for file writes** in execute_code context — never `write_file` (sandbox mismatch)
- **Pipe yt-dlp JSON to files** — don't capture large JSON in terminal() (corrupts at 40+ videos)
- **Write helper scripts to disk first** — avoids Python/shell quoting hell
- **10s delay between batches** — prevents rate limiting
- **Skip existing files** — idempotent re-runs
- **Verify with byte count, not line count** — `wc -l` lies for files without trailing newlines

## When to Use This Pattern

- User has a custom extraction script (not using the skill's built-in scripts)
- `web_extract` produces better structured summaries than raw transcripts for the content type
- Knowledge base / tutorial reference (not verbatim transcript)
- Large playlists (50+ videos) where cron jobs would be fragile
