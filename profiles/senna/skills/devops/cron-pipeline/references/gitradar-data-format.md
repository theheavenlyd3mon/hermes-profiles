# GitRadar recommendations.json Format

Last verified: 2026-06-25

## File Location

Actual path (not the cron-resolved path):
```
~/.hermes/profiles/senna/home/gitradar/data/recommendations.json
```

**Note:** Cron sessions resolve `~/gitradar/` to the profile home (`~/.hermes/profiles/senna/home/gitradar/`), NOT `~/gitradar/`. See the profile HOME path mismatch pitfall in SKILL.md.

## Structure

```json
{
  "collected_at": "2026-05-18T16:50:31.185123Z",
  "total_repos": 229,
  "repos": [
    {
      "full_name": "owner/repo",
      "description": "...",
      "stars": 3327,
      "forks": 706,
      "language": "Python",
      "topics": ["topic1", "topic2"],
      "created_at": "2026-05-13T23:40:15Z",
      "pushed_at": "2026-05-14T00:11:48Z",
      "open_issues": 0,
      "license": "MIT",
      "html_url": "https://github.com/owner/repo",
      "source": "api",
      "score": 73.61,
      "label": "EXTRACT"
    }
  ]
}
```

## Labels (categories)

| Label | Meaning |
|-------|---------|
| ADOPT | Ready to use directly |
| EXTRACT | Useful patterns/components to extract |
| FORK/PRODUCT | Potential fork or product idea |
| INSPIRATION | Ideas and inspiration |
| PLUGIN/SKILL | Could become a Hermes plugin or skill |

## Parsing with jq

```bash
# Category breakdown
jq '[.repos[].label] | group_by(.) | map({label: .[0], count: length})' recommendations.json

# Top N by category
jq '[.repos[] | select(.label == "ADOPT")] | sort_by(-.score) | .[0:8]' recommendations.json

# Summary fields per repo
jq '.repos[] | {name: .full_name, score, stars, language, desc: (.description // "" | .[0:140])}' recommendations.json
```

## Cache File (`data/cache.json`)

As of 2026-06-08, the cache stores timestamps for TTL-based expiry (14 days):
```json
{"seen": {"owner/repo": "2026-06-08", "other/repo": "2026-06-01"}}
```
Old format was a flat list `{"seen": ["repo1", "repo2"]}` — auto-migrated on first load.
Entries older than `CACHE_TTL_DAYS` (14) are pruned on load. This prevents cache
saturation where all search results are already cached, causing empty pipeline output.

## Typical File Size

~200KB for 229 repos. Safe to parse with jq (streaming parser). Avoid loading the full file into Python memory when jq can filter first.

## Retrieving Results When the User Asks

The GitRadar cron job (`aafd34198ffb`) delivers to **Discord #research-lab** (`1508955977255223406`) on Mon/Thu at 9am.

**Preferred retrieval order (fastest first):**

1. **Discord messages** — `discord(action='fetch_messages', channel_id='1508955977255223406', limit=5)` gets the most recent delivery. The report is split across 2 messages (page 1/2 and 2/2). Fastest path — no file I/O, returns pre-summarized prose.
2. **JSON data file** — `recommendations.json` at the profile home path (see File Location above). Full structured data with scores, labels, and raw metadata. Parse with jq or Python. The `full_name` key is `owner/repo`.
3. **Re-run cron job** — `cronjob(action='run', job_id='aafd34198ffb')` if both above are stale/missing. Avoid if the job already ran today — it regenerates the cache, taking ~5-10 minutes.

**When to use each:**
- User asks "what did GitRadar find" = Discord messages (pre-digested, conversational)
- User asks "show me the raw scores for ADOPT repos" = JSON data file
- User asks "run it again" or results are from last week = re-run cron job

## Presenting Per-Machine Recommendations

When the user has multiple machines (Mac Hermes + Windows Hermes), filter recommendations by what each machine can actually use:

| Filter | Mac Hermes | Windows Hermes |
|--------|-----------|----------------|
| Profiles | Orchestrator, research, creative, code, security, financial | blender-coder, ue5-coder, threejs-coder, designer |
| GPU | None (M-series, no heavy inference) | your GPU (ComfyUI, Krea 2, llama.cpp) |
| Specialties | Agent infra, MCP servers, skills, orchestration | UE5, Blender, 3D web, ComfyUI workflows |

**Windows-first picks:** ComfyUI tools (`ComfyUI-Agent-Kit`, `ComfyUI-ConditioningKrea2Rebalance`), image gen inference code (`krea-2`), UE5-related (`unreal-agent-harness`), Three.js/web UI polish (`liquid-glass`), canvas/design tools (`AI-Canvas`), video storyboard (`codex-storyboard`).

**Mac-first picks:** MCP infrastructure (`conduit`, `patchright-browser`), orchestration patterns (`OpenFugu`), agent sandboxes (`tupper`), agent research (`Qwen-AgentWorld`), token optimization (`honey-for-devs`), security intel (`darknet-mcp-server`), self-hosted AI workspace (`disp8ch`).

**Spam filter:** Game trainers from `ma7mod7`, `we9lii`, `Danu-Nur` accounts are duplicates with copy-paste descriptions across multiple game titles (Paralives, Resident Evil, 007). Dedup by `full_name` before presenting. These publish near-identical repos with only the game name changed. Score them at 80-91 but flag as noise — don't recommend without user interest in game trainers.
