# Pipeline Empty Output: Diagnostic Checklist

When a multi-stage data pipeline (discover → filter → score → output) produces zero results, work backwards from the output through each stage.

## Diagnostic Order

1. **Auth & API** — Is the token valid? Are rate limits hit? (`gh auth status`, `gh api rate_limit`)
2. **Raw API test** — Call the same endpoint manually with the same params. If it returns data, the issue is downstream.
3. **Stage isolation** — Import and run each pipeline function independently:
   ```python
   # Test auth
   token = gh_auth_token()
   # Test a single search
   items, total = github_search(query, sort, order, 100, 1)
   # Check rate limiter
   is_rate_limited()
   ```
4. **Cache saturation** — If the API returns results but the pipeline filters them all out, check the dedup cache. Count how many API results are already in `seen`:
   ```python
   seen = load_cache()
   new = sum(1 for i in items if i.get('full_name', '') not in seen)
   ```
   If `new == 0`, the cache is saturated.

## Root Cause: Cache Saturation

**Symptom:** Pipeline output is empty, API works fine, auth is valid, no rate limits.

**Pattern:** A deduplication/seen-cache that never expires accumulates entries until every result from the search queries is already cached. Common when:
- Search queries are broad (high star thresholds, popular topics)
- Cache has no TTL — entries live forever
- Pipeline runs frequently (daily cron on a 7-day recency window means the same high-star repos appear in every run)

**Fix options:**
1. Clear the cache to let the pipeline re-discover fresh (immediate, but problem recurs)
2. Add TTL to cache entries (expire after N days) — **recommended, permanent fix**
3. Rotate cache on a schedule (e.g., weekly prune)

**Key insight:** A cache without TTL is a monotonic set — it can only grow. Over time, the signal-to-noise ratio of "new vs cached" approaches zero, even though the upstream data source is healthy.

### TTL Migration Pattern (proven fix)

Migrate from a flat list `{"seen": ["repo1", "repo2"]}` to a timestamped dict
`{"seen": {"repo1": "2026-06-08", "repo2": "2026-06-01"}}`:

```python
CACHE_TTL_DAYS = 14

def load_cache():
    """Returns (seen_names_set, timestamps_dict)."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=CACHE_TTL_DAYS)).strftime("%Y-%m-%d")
    with open(CACHE_FILE) as f:
        data = json.load(f)
    raw = data.get("seen", {})
    timestamps = {}
    if isinstance(raw, list):  # migrate old format
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        for name in raw:
            if isinstance(name, str) and name:
                timestamps[name] = today
    elif isinstance(raw, dict):  # new format — filter expired
        for name, ts in raw.items():
            if isinstance(ts, str) and ts >= cutoff:
                timestamps[name] = ts
    return set(timestamps.keys()), timestamps

def save_cache(seen, timestamps=None):
    """Save with timestamps. New entries get today's date."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    merged = dict(timestamps or {})
    for name in seen:
        if name not in merged:
            merged[name] = today
    with open(CACHE_FILE, "w") as f:
        json.dump({"seen": merged}, f)
```

**Migration notes:**
- Old list entries get today's date on first load (they'll expire in TTL days)
- `load_cache()` now returns a tuple — update all call sites: `seen, timestamps = load_cache()`
- Pass `timestamps` through `collect()` → `save_cache(seen, timestamps)` so existing entries keep their original dates

## GitRadar-Specific Architecture

```
gitradar-discover.py → data/discoveries.json → gitradar-score.py → data/recommendations.json
                           ↑
                    data/cache.json (seen repos, no TTL)
                    data/thresholds.json (self-tuning)
                    data/metrics.json (run history)
```

- `discover.py` queries GitHub Search API (9 query templates) + scrapes GitHub Trending
- Deduplicates against `cache.json` before outputting
- `score.py` reads discoveries, scores against `config/stack.json` preferences, outputs recommendations
- Self-tuning adjusts `star_threshold` based on noise/signal metrics, but can't help when collection itself returns zero
