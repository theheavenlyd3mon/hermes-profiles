# Trading Agent Data Sources (Free Tier)

## Finnhub (Recommended Primary)
- **URL:** https://finnhub.io
- **Free tier:** 60 API calls/minute
- **Covers:**
  - Real-time stock quotes (`/api/v1/quote`)
  - Company news (`/api/v1/company-news`)
  - Economic calendar (`/api/v1/calendar/economic`)
  - Earnings calendar (`/api/v1/calendar/earnings`)
  - Basic financials (`/api/v1/stock/metric`)
  - Market news (`/api/v1/news`)
- **Setup:** Register → get API key → `FINNHUB_API_KEY=xxx`
- **Best for:** Real-time quotes, news scanning, earnings dates

## Alpaca (Paper Trading + Market Data)
- **URL:** https://alpaca.markets
- **Free tier:** Paper trading unlimited, market data included
- **Covers:**
  - Paper trading (buy/sell with fake money)
  - Real-time and historical bars (`/v2/stocks/{symbol}/bars`)
  - Account/position tracking
  - News (beta, `/v1beta1/news`)
- **Setup:** Register → generate paper API keys → set env vars:
  ```
  APCA_API_KEY_ID=your_paper_key_id
  APCA_API_SECRET_KEY=your_paper_secret_key
  APCA_BASE_URL=https://paper-api.alpaca.markets
  ```
- **Best for:** Paper trading, testing strategies without risk, order simulation

## Alpha Vantage (Historical Data + Indicators)
- **URL:** https://www.alphavantage.co
- **Free tier:** 25 API calls/day (use sparingly)
- **Covers:**
  - Historical daily/weekly/monthly prices
  - Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
  - Forex and crypto data
  - Sector performance
- **Best for:** Backtesting, technical indicator computation, historical analysis
- **Tip:** Cache results locally — don't re-fetch the same data

## Yahoo Finance (Unofficial Backup)
- **Library:** `yfinance` Python package
- **Free:** No API key needed
- **Covers:** Quotes, historical data, basic fundamentals
- **Best for:** Quick lookups, backup when other APIs hit limits
- **Caution:** Unofficial, can break without notice

## Choosing What to Use

| Need | Primary | Backup |
|------|---------|--------|
| Real-time quotes | Finnhub | yfinance |
| News scanning | Finnhub | Alpaca news |
| Historical prices | Alpha Vantage | yfinance |
| Technical indicators | Alpha Vantage | Compute from price data |
| Paper trading | Alpaca | — |
| Economic calendar | Finnhub | — |
| Earnings dates | Finnhub | — |

## Rate Limit Management

- Finnhub: 60/min — safe for scanning ~50 tickers in a batch with 1-second spacing
- Alpha Vantage: 25/day — cache aggressively, use only for historical/indicator data
- Alpaca: generous for paper trading, but respect 200/min for market data
- yfinance: no hard limit but be reasonable (add `time.sleep(0.5)` between calls)
