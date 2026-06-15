---
name: oracle-market-intel
description: Read-only financial market intelligence via AI-Trader's Market Intel API — macro signals, ETF flows, stock analysis, grouped news. No auth required for reads.
version: 1.0.0
platforms: [macos, linux]
triggers: [market intel, macro signals, etf flows, stock analysis, financial news, market overview]
metadata:
  hermes:
    tags: [finance, market-data, macro, etf, stocks, news]
---

# Market Intel — AI-Trader Read-Only API

Base URL: `https://ai4trade.ai/api`

All endpoints are read-only. No auth required for reads. Requests do NOT trigger live news collection.

## Endpoints

### Overview (start here)
```
GET /api/market-intel/overview
```
Returns: `available`, `last_updated_at`, `news_status`, `headline_count`, `active_categories`, `top_source`, `latest_headline`, `categories`

### Macro Signals
```
GET /api/market-intel/macro-signals
```
Returns: `available`, `verdict`, `bullish_count`, `total_count`, `signals`, `meta`, `created_at`

### ETF Flows
```
GET /api/market-intel/etf-flows
```
Returns: `available`, `summary`, `etfs`, `created_at`, `is_estimated`

### Stock Analysis
```
GET /api/market-intel/stocks/featured          # server-generated snapshots
GET /api/market-intel/stocks/{symbol}/latest   # includes optional adanos_sentiment
GET /api/market-intel/stocks/{symbol}/history  # recent historical snapshots
```

### Grouped Financial News
```
GET /api/market-intel/news?category=equities|macro|crypto|commodities&limit=N
```
Returns grouped news by category with: `title`, `url`, `source`, `summary`, `time_published`, `overall_sentiment_label`

## Usage Pattern
1. Start with `/api/market-intel/overview`
2. If `available` is false, proceed without market-intel context
3. For details, call category-specific endpoints
4. Prefer category reads when domain is known

## curl Examples
```bash
# Overview
curl -s https://ai4trade.ai/api/market-intel/overview | jq .

# Macro signals
curl -s https://ai4trade.ai/api/market-intel/macro-signals | jq .

# BTC ETF flows
curl -s https://ai4trade.ai/api/market-intel/etf-flows | jq .

# NVDA analysis
curl -s https://ai4trade.ai/api/market-intel/stocks/NVDA/latest | jq .

# Crypto news (top 5)
curl -s "https://ai4trade.ai/api/market-intel/news?category=crypto&limit=5" | jq .
```

## Response Structure (news)
```json
{
  "categories": [
    {
      "category": "macro",
      "label": "Macro",
      "available": true,
      "created_at": "2026-03-21T03:10:00Z",
      "summary": {
        "item_count": 5,
        "activity_level": "active",
        "top_headline": "Fed comments shift rate expectations"
      },
      "items": [
        {
          "title": "Fed comments shift rate expectations",
          "url": "https://example.com/article",
          "source": "Reuters",
          "summary": "Short event summary...",
          "time_published": "2026-03-21T02:55:00Z",
          "overall_sentiment_label": "Neutral"
        }
      ]
    }
  ]
}
```

## Pitfalls
- **KNOWN ISSUE (2026-05-29): API data frozen since May 12, 2026.** All endpoints return cached snapshots from that date — backend pipeline appears dead. Always check `last_updated_at` in `/overview` before using any data. If >24h stale, skip entirely and rely on web_search.
- Data is refreshed by backend jobs, not live — check `last_updated_at` for staleness
- Adanos sentiment is optional alternative-data context — never the sole reason to trade
- `etf-flows` are estimated, not confirmed fund flows
