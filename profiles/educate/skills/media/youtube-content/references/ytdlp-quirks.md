# yt-dlp Subtitle Extraction Quirks

## The `--write-auto-sub` problem (PO Token)

`yt-dlp` can list available subtitles with `--list-subs` but may fail to download them with `--write-auto-sub`. As of yt-dlp 2025.x, the root cause is often a **missing PO (Proof of Origin) token**, not a language mismatch:

```bash
# This WORKS — shows auto-captions are available:
python3 -m yt_dlp --list-subs --skip-download "URL"
# Output: en English vtt, srt, ttml, srv3, srv2, srv1, json3

# This FAILS — misleading error:
python3 -m yt_dlp --write-auto-sub --sub-lang en --skip-download -o "/tmp/%(id)s" "URL"
# stderr shows: "There are missing subtitles languages because a PO token was not provided"
# Then: "There are no subtitles for requested languages" (misleading — real cause is PO token)
```

### Workaround: Use android/ios player client

The `android` and `ios` player clients don't require a PO token for subtitle discovery:

```bash
# This finds subtitle tracks (android client bypasses PO token):
python3 -m yt_dlp --extractor-args "youtube:player_client=android" --list-subs --skip-download "URL"

# Attempt download with android client:
python3 -m yt_dlp --extractor-args "youtube:player_client=android" \
  --write-auto-sub --sub-lang en --sub-format vtt \
  --skip-download -o "/tmp/%(id)s" "URL"
```

**Note:** The android client identifies subtitle tracks successfully, but the actual download may still hit 429 if the IP is rate-limited. This is a separate issue from the PO token.

### Workaround: Install curl_cffi for impersonation

```bash
pip3 install curl_cffi
# Then use --impersonate with yt-dlp:
python3 -m yt_dlp --impersonate "chrome" --extractor-args "youtube:player_client=android" \
  --write-auto-sub --sub-lang en --skip-download -o "/tmp/%(id)s" "URL"
```

This helps with some blocks but doesn't bypass IP-level 429s.

### Workaround: Extract caption URL from JSON dump

```bash
python3 -m yt_dlp --dump-json --skip-download "URL" 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
auto = data.get('automatic_captions', {})
if 'en' in auto:
    for t in auto['en']:
        print(f'{t[\"ext\"]}: {t[\"url\"]}')
elif auto:
    lang = list(auto.keys())[0]
    for t in auto[lang]:
        print(f'{lang} {t[\"ext\"]}: {t[\"url\"]}')
"
```

Then fetch the URL directly with curl (may still be rate-limited).

## Workaround: Page source extraction

Extract caption track URLs from the video page HTML:

```python
import subprocess, json, re
r = subprocess.run(['curl', '-s', '-L', '--max-time', '30',
    '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    f'https://www.youtube.com/watch?v={video_id}'],
    capture_output=True, text=True, timeout=45)

match = re.search(r'"captionTracks":\[(.*?)\]', r.stdout)
if match:
    tracks = json.loads('[' + match.group(1) + ']')
    for t in tracks:
        print(f'{t["languageCode"]}: {t["baseUrl"][:100]}')
```

**Important:** Caption URLs are session-bound. You must fetch them using the same HTTP session (cookies) that loaded the page. Using a separate curl call may return a Google "Sorry..." error page. Use `urllib` with `http.cookiejar.MozillaCookieJar` to maintain the session.

## When to use yt-dlp vs youtube-transcript-api

| Scenario | Use |
|---|---|
| Single video, fresh IP | `youtube-transcript-api` (cleaner output) |
| Rate-limited, need auto-captions | Try yt-dlp (different request pattern) |
| Rate-limited, both blocked | Wait 15-30 min or use proxy |
| Need manual subtitles (not auto) | `youtube-transcript-api` or yt-dlp |
| Playlist with 50+ videos | `fetch_playlist.py` with 5s delays |
