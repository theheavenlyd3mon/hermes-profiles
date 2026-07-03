# YouTube Rate Limiting & IP Blocks

## What happens

YouTube aggressively rate-limits transcript/subtitle API requests. After ~3-5 rapid requests from the same IP, you'll see:

- `youtube-transcript-api`: `IpBlocked` exception with a long error message
- `curl` to caption URLs: HTTP 429 (Too Many Requests) or Google "Sorry..." HTML error page
- `yt-dlp --write-auto-sub`: "no subtitles for requested languages" (even when `--list-subs` shows them)

The block is **temporary** — typically clears in 15-30 minutes. It applies to the entire IP, not per-tool.

## Why batch processing fails

When processing a playlist of 30+ videos, the first few requests succeed, then YouTube blocks the IP. All subsequent requests (from any tool) fail until the block clears. This is why:

1. The subagent timed out trying to process 84 videos
2. Switching from `youtube-transcript-api` to `curl` to `yt-dlp` didn't help — same IP, same block
3. Adding cookies didn't bypass it — it's an IP-level block, not an auth issue

## Mitigations

### 1. Add delays between requests (prevention)
- Minimum 8-10 seconds between requests (5s is too aggressive — causes 429s on playlists of 20+ videos)
- 10-15s for larger batches (50+ videos)
- The `fetch_playlist.py` script defaults to 3-second delays — consider patching to 8s

### 2. Wait it out (recovery)
- If blocked, wait 15-30 minutes before retrying
- Don't loop retrying immediately — it extends the block

### 3. Use a proxy (bypass)
- `youtube-transcript-api` v1.x supports `GenericProxyConfig`:
  ```python
  from youtube_transcript_api import YouTubeTranscriptApi
  from youtube_transcript_api.proxies import GenericProxyConfig
  api = YouTubeTranscriptApi(proxy_config=GenericProxyConfig(
      http_url="http://proxy:port",
      https_url="http://proxy:port"
  ))
  ```
- Residential proxies work best; datacenter proxies may already be blocked

### 4. Use a VPN (bypass)
- Connect to a different IP before retrying
- Works immediately but requires user action

### 5. Browser cookies (limited help)
- `browser_cookie3` can extract Chrome/Safari cookies
- Helps with authenticated requests but doesn't bypass IP blocks
- On macOS with Hermes: cookies are in the actual user home, not the profile home:
  ```python
  import browser_cookie3
  cj = browser_cookie3.chrome(domain_name='.youtube.com')
  ```
- Requires Chrome/Safari to have an active YouTube session

## Anti-pattern

```
❌ Get IpBlocked → try curl → try yt-dlp → try different user-agent → try cookies → loop
✅ Get IpBlocked → inform user → suggest wait/VPN/proxy → move on
```

Don't waste time trying alternative tools against the same blocked IP. The block is IP-level.
