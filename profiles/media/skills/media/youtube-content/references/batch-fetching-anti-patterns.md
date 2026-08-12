# Batch Transcript Fetching Anti-Patterns

## The Overwrite Anti-Pattern

**What happened (June 2026):** A custom `batch_transcripts.py` was written to process 84 videos from a playlist. The script:
1. Iterated through ALL videos on each run
2. Wrote the output markdown file from scratch at the END of each run
3. Had no checkpoint — if a run hit rate limits partway through, the next run started from scratch
4. First run got 21/84 OK, second run got 0/84 (rate limited), and **overwrote the 21 successes**

**The fix:** The skill's `scripts/fetch_playlist.py` already solves this:
- Checkpoint file (`/tmp/yt_transcript_checkpoint.json`) saves state after EACH video
- Output file is rewritten incrementally (after each successful fetch)
- Failed videos are retried on next run, successful ones are skipped
- Rate-limit backoff with exponential delay
- Auto-fallback to yt-dlp android client

**Rule:** Always use `fetch_playlist.py` for batch work. If it's missing a feature, add it — don't write a parallel script.

## Cron Job Setup Pattern

```bash
# Correct: use the skill's built-in script
python3 ~/.hermes/profiles/senna/skills/media/youtube-content/scripts/fetch_playlist.py \
  "https://youtube.com/playlist?list=PLAYLIST_ID" \
  ~/playlist-transcripts.md \
  5  # 5-second delay between videos
```

```bash
# Wrong: custom script that overwrites on each run
python3 ~/my_batch_script.py  # DO NOT DO THIS
```

## The Non-Terminal Status Loop (June 2026)

**What happened:** A custom `fetch_playlist_transcripts.py` script saved videos with status `NO_SUB` when yt-dlp didn't produce a subtitle file. The script's "pending" filter only skipped `("OK", "FAILED")`, so `NO_SUB` videos were retried every run — but kept producing `NO_SUB` because the underlying issue (YouTube blocking or no auto-captions) persisted. Result: the cron job reported "0/85 OK, 8 attempted, 77 remaining" on every single run for days, never progressing past the same 8 videos.

**Root causes:**
1. `NO_SUB` was not in the terminal status filter, so it was retried indefinitely
2. `BACKOFF_BASE=20` with `MAX_RETRIES=3` meant 140 seconds per rate-limited video — the cron job timed out before processing all 8
3. The checkpoint file at `/tmp/yt_transcript_checkpoint.json` persisted the stale entries across runs

**The fix:**
1. Delete the stale checkpoint: `rm /tmp/yt_transcript_checkpoint.json`
2. Reduce backoff: `BACKOFF_BASE=5` (max 35s per video instead of 140s)
3. Treat `NO_SUB` as terminal — a video without subtitles won't get them on retry

**Detection:** If a cron job shows the same "N attempted, M remaining" numbers across 3+ runs with 0 progress, suspect a non-terminal status loop. Check the checkpoint file's status distribution.

## Rate Limit Recovery Timeline

From real-world observation (June 2026, residential IP):
- First batch of ~20-30 requests: usually succeeds
- After ~80-100 rapid requests: IP blocked
- Recovery time: 1-6 hours typically, sometimes up to 24h
- The `fetch_playlist.py` script's 5-second default delay helps avoid hitting the limit in the first place
- Switching to VPN briefly can provide a fresh IP for an immediate batch
