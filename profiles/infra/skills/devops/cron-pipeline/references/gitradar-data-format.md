# GitRadar recommendations.json Format

Last verified: 2026-05-28

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

| Label | Count (May 18) | Meaning |
|---|---|---|
| ADOPT | 35 | Ready to use directly |
| EXTRACT | 38 | Useful patterns/components to extract |
| FORK/PRODUCT | 23 | Potential fork or product idea |
| INSPIRATION | 108 | Ideas and inspiration |
| PLUGIN/SKILL | 25 | Could become a Hermes plugin or skill |

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
