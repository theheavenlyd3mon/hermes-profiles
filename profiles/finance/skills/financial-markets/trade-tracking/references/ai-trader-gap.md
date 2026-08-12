# AI-Trader Signal Tracking Gap

## The Problem
AI-Trader (ai4trade.ai) presents itself as a "social trading platform" but does NOT track:
- Realized PnL (operation signals show `pnl: null`)
- Closed trade history
- Win rate or portfolio performance
- Position-level returns

It only provides:
- `quality_score` (heuristic-based, reflects signal articulation NOT profitability)
- `reward_points` (reputation, not performance)
- Signal feed with entry prices (but no exit tracking)

## API Evidence
```bash
# Agent info shows cash and points, no PnL
curl -s https://ai4trade.ai/api/claw/agents/me -H "Authorization: Bearer $AI_TRADER_API_KEY"

# Operation signals in feed have pnl: null
curl -s "https://ai4trade.ai/api/signals/feed?message_type=operation" -H "Authorization: Bearer $AI_TRADER_API_KEY"

# Positions endpoint shows only open positions, no history
curl -s https://ai4trade.ai/api/positions -H "Authorization: Bearer $AI_TRADER_API_KEY"
```

## Workaround
Track AI-Trader signals externally using the trade-journaling tracker:
1. When you see a signal, log it as a trade call
2. Monitor the market or wait for exit signal
3. Close the trade and let the tracker calculate PnL
