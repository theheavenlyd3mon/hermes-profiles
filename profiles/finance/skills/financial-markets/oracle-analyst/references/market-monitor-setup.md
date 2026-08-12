# Oracle Market Monitor — Hybrid Script + Agent Setup

## Architecture

Oracle's market monitoring uses a two-tier hybrid pattern for token efficiency:

```
┌─────────────────────────────────┐     ┌──────────────────────────────┐
│  TIER 1: market-monitor.py      │────▶│  TIER 2: oracle-alert-analyst│
│  no_agent=true, 0 tokens        │     │  oracle profile + skill      │
│  Runs every 1h                  │     │  Runs every 1h               │
│  Fetches prices, checks         │     │  Reads script output via     │
│  thresholds, prints only if     │     │  context_from. [SILENT] if   │
│  notable event detected         │     │  empty. Deep analysis if not. │
└─────────────────────────────────┘     └──────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `~/.hermes/oracle/watchlist.json` | Tickers, crypto pairs, thresholds |
| `~/.hermes/oracle/state.json` | Current prices (overwritten each run) |
| `~/.hermes/oracle/alerts.log` | Append-only log of notable events |
| `~/.hermes/oracle/daily/YYYY-MM-DD.json` | Daily price snapshots |
| `~/.hermes/oracle/scripts/market-monitor.py` | The monitoring script |
| `~/.hermes/profiles/oracle/scripts/market-monitor.py` | **Real file copy** (NOT symlink — see Pitfall #6) |

## Cron Jobs

| Job ID | Name | Type | Schedule | Profile |
|--------|------|------|----------|---------|
| `bc03fdc9b207` | oracle-market-scan | script (no_agent) | every 1h | oracle |
| `b77fbea0062b` | oracle-alert-analyst | agent | every 1h | oracle |

The agent job uses `context_from: [bc03fdc9b207]` to chain from the script.

## Data Sources

| Asset | Source | API |
|-------|--------|-----|
| Stocks (SPY/QQQ/NVDA/AAPL/TSLA) | Yahoo Finance | `query1.finance.yahoo.com/v8/finance/chart/` |
| Crypto (BTC/ETH/SOL) | CoinGecko | `api.coingecko.com/api/v3/simple/price` |
| Fear & Greed | Alternative.me | `api.alternative.me/fng/` |

All are free, no API keys required.

## Thresholds (in watchlist.json)

- Stocks: 2-5% move triggers alert (SPY/QQQ most sensitive at 2%, TSLA least at 5%)
- Crypto: 5-8% move triggers alert (BTC most sensitive at 5%, SOL least at 8%)
- Fear & Greed: Extreme Fear (<20) or Extreme Greed (>80)
- Volume spike: 2x average daily volume

## Pitfalls

1. **Path.home() in scripts** — resolves to profile sandbox, not real home. Use absolute paths. See `hermes-agent` skill `references/cron-automation-patterns.md` for details.
2. **Script resolution** — cron `script:` resolves from `~/.hermes/profiles/<profile>/scripts/`. **Copy the actual file there** — do NOT use symlinks to external paths, as the cron safety check resolves symlinks and blocks any that point outside the scripts directory (error: "Blocked: script path resolves outside the scripts directory"). The script can still read/write data files elsewhere via absolute paths (e.g., `~/.hermes/oracle/`).
3. **First run** — no previous state means "since last check" comparisons are skipped. Alerts only fire on the second run onward.
4. **Yahoo Finance rate limits** — unofficial API, no guaranteed SLA. If it breaks, fall back to yfinance pip package.
5. **CoinGecko free tier** — rate limited to ~10-30 req/min. One batch request per run is fine.
6. **Symlinks blocked by cron safety check** — the cron runner resolves symbolic links and blocks any script whose real path falls outside `~/.hermes/profiles/<profile>/scripts/`. The symlink-based setup described in earlier versions of this doc produced: "Blocked: script path resolves outside the scripts directory". **Fix:** remove the symlink and copy the actual file (`cp` not `ln -s`). The script at `~/.hermes/oracle/scripts/market-monitor.py` uses absolute paths for all data files so it works from any location. If the original is updated, re-copy.

## Customization

Edit `~/.hermes/oracle/watchlist.json` to:
- Add/remove tickers or crypto pairs
- Adjust thresholds per asset
- Change volume spike multiplier
- Adjust Fear & Greed extremes

The script auto-discovers entries from the watchlist — no code changes needed.

## Existing Oracle Cron Jobs

Oracle still has three original full-agent jobs that predate this setup:

| Job | Schedule | Notes |
|-----|----------|-------|
| oracle-morning-brief | Mon-Fri 9am | Full brief with trade ideas. Could be lighter (read state file). |
| oracle-crypto-pulse | every 4h | Now redundant — hourly scan covers crypto. Candidate to pause. |
| oracle-eod-journal | Mon-Fri 4:30pm | Reviews daily performance. Could read daily/ snapshots. |

Consider pausing `oracle-crypto-pulse` since the hourly scan covers the same ground.
