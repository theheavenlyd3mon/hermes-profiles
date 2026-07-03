# Cron Reliability Pitfalls for YouTube Batch Processing

## One-Shot Cron Job Auto-Cleanup

**Problem:** One-shot cron jobs (`repeat: once`) get auto-removed when their scheduled time passes, even if they never actually ran.

**What happened:**
- 11 cron jobs were scheduled for 11:15 AM - 2:00 PM
- By 3:21 PM, all had disappeared from `cronjob list`
- No output files were created — jobs never executed
- The scheduler cleaned them up without running them

**Detection:**
- `cronjob list` shows fewer jobs than expected
- Output directories are empty despite scheduled jobs
- `last_run_at: null` and `next_run_at: null` on remaining jobs

**Prevention:**
1. Schedule jobs for times that are still in the future
2. Monitor the first batch to confirm execution
3. Space jobs 15-20 minutes apart
4. Verify execution by checking filesystem, not cron list
5. If jobs disappear without running, rebuild immediately with future-dated schedules

**Root cause:** The cron scheduler's one-shot cleanup logic removes jobs whose `next_run_at` is in the past, regardless of whether the job actually executed.

## write_file vs terminal for File Writes (Context-Dependent)

**The reliable tool depends on session type.** This is the opposite of what you might expect:

### Discord Sessions: `terminal` is reliable, `write_file` may sandbox
- `write_file` may write to a sandbox filesystem that doesn't persist to the terminal's actual filesystem
- Use `terminal` with `python3 -c "open(path,'w').write(content)"` or heredoc syntax instead
- Verify with `terminal` after writing

### Cron Sessions (no user present): `write_file` is reliable, `terminal` heredocs fail
- `terminal` heredocs (`cat > file << 'EOF'`) have TWO failure modes in cron context:
  1. **Silent failure**: Returns "DONE" (from trailing `echo`) but files don't exist on disk
  2. **Active error**: Returns error like "Foreground command uses '&' backgrounding" when markdown content contains shell-special characters (`*`, `&`, `(`, `)`) — even with a quoted heredoc delimiter
- `write_file` reliably persists in cron context
- This was verified in a 20-video batch extraction where heredoc-written files were missing/unwritten but write_file-written files were present
- **Rule: Always use `write_file` for batch file creation in cron sessions.** Don't attempt terminal heredocs with markdown content — the failure modes are unpredictable.

### Always Verify
- Check file persistence with `terminal` (`ls`, `wc -c`) after writing, regardless of which tool you used
- Losing hours of extraction work to a silent write failure is a painful lesson

## Rate Limiting Returns Misleading "No Transcript"

**Problem:** `youtube-transcript-api` silently returns empty results when your IP is throttled — it looks identical to a video that genuinely has no transcripts.

**Detection:**
- Long streak of "no transcript" after prior rapid requests
- Videos that worked in a prior run suddenly show "no transcript" on retry
- No error messages or 429 status codes

**Prevention:**
1. If you see 10+ consecutive "no transcript" results, assume rate limiting
2. Wait 15-30 minutes before retrying
3. Check if the same videos had transcripts in a prior run
4. Use `yt-dlp --extractor-args "youtube:player_client=android" --list-subs` to verify

**Root cause:** The API returns empty results instead of rate limit errors, making it impossible to distinguish between "no transcript available" and "IP blocked".

## Sibling Subagent Checkpoint Conflicts

**Problem:** When multiple cron jobs process different batches of the same playlist concurrently (e.g., job A processes videos 41-60 and job B processes videos 61-80), they both write to the same `.checkpoint.json` file. The `write_file` tool warns: *"was modified by sibling subagent but this agent never read it"* — one job's checkpoint overwrites the other's.

**What happened:**
- Two cron jobs ran ~10 seconds apart, each processing 20 videos from the same playlist
- Both wrote to `~/Documents/YouTube-Transcripts/UE5_RPG_Framework/.checkpoint.json`
- Job A's checkpoint (videos 41-60) overwrote Job B's checkpoint (videos 61-80)
- The warning appeared but didn't block the write — data was silently lost

**Detection:**
- `write_file` returns a `_warning` about sibling subagent modification
- Checkpoint file shows only one batch's data instead of cumulative progress

**Prevention:**
1. **Use batch-scoped checkpoint keys** — Instead of overwriting the whole file, read first, then merge:
   ```json
   {
     "batches": {
       "41-60": {"last_processed": 60, "saved": 20, "failed": []},
       "61-80": {"last_processed": 80, "saved": 20, "failed": []}
     }
   }
   ```
2. **Read before write** — Always `read_file` the checkpoint before writing, then merge your batch's data with existing data
3. **Use per-batch checkpoint files** — Each cron job writes to `.checkpoint-41-60.json` instead of a shared file; a final merge job combines them
4. **Sequential, not concurrent** — Space cron jobs far enough apart that one finishes before the next starts (20+ min apart)

**Best practice:** Read the existing checkpoint, merge your batch's results into it, then write the merged result. This prevents one batch from clobbering another's progress.
