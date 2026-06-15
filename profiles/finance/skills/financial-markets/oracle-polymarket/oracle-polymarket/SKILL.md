---
name: oracle-polymarket
description: Polymarket prediction market integration — read markets, orderbooks, publish simulated trades. Direct API reads + AI-Trader for simulated execution.
version: 1.0.0
platforms: [macos, linux]
triggers: [polymarket, prediction market, orderbook, market odds, probability market]
metadata:
  hermes:
    tags: [finance, polymarket, prediction-markets, orderbook]
---

# Polymarket — Prediction Market Integration

## Architecture
- **Read** market data directly from Polymarket APIs (no auth needed)
- **Publish** simulated trades via AI-Trader (requires AI_TRADER_TOKEN)
- Do NOT route market-discovery traffic through AI-Trader

## Public APIs

### Gamma Markets API — Discover Markets
```bash
# By slug
curl -s "https://gamma-api.polymarket.com/markets?slug=will-btc-be-above-120k-on-june-30" | jq .

# By conditionId
curl -s "https://gamma-api.polymarket.com/markets?conditionId=0x1234..." | jq .

# Search
curl -s "https://gamma-api.polymarket.com/markets?limit=20&active=true" | jq .
```

Key fields: `question`, `slug`, `outcomes`, `clobTokenIds`

### CLOB Orderbook API — Get Prices
```bash
curl -s "https://clob.polymarket.com/book?token_id=123456789" | jq .
```
Use best bid/ask to derive mid price.

## Resolving a Market
1. Query Gamma API with slug or search terms
2. Extract `outcomes[i]` and `clobTokenIds[i]` (paired)
3. Choose concrete outcome (e.g., "Yes")
4. Query CLOB orderbook with corresponding `token_id`
5. Read best bid/ask → mid price = current market probability

## Publish Simulated Trade (via AI-Trader)
```bash
curl -X POST https://ai4trade.ai/api/signals/realtime \
  -H "Authorization: Bearer $AI_TRADER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "market": "polymarket",
    "action": "buy",
    "symbol": "will-btc-be-above-120k-on-june-30",
    "outcome": "Yes",
    "token_id": "123456789",
    "price": 0,
    "quantity": 20,
    "executed_at": "now"
  }'
```

Actions: `buy` or `sell` only (no short/cover for polymarket)
`price`: 0 for market orders

## Pitfalls
- Gamma API is for discovery, CLOB is for prices — use both
- `clobTokenIds[i]` maps to `outcomes[i]` — don't mix up pairs
- Polymarket prices = implied probabilities (0.65 = 65% chance)
- Market liquidity varies — check orderbook depth before large positions
