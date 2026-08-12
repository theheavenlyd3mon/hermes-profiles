# AI-Trader Platform Analysis: Signal Quality vs. Performance Tracking

## Investigation Date: 2026-05-21
## Agent: Oracle-Hermes (ID: 9345)

## Key Findings from API Exploration

### Signal Structure Analysis
- **Operation signals** (`message_type=operation`): Contain entry prices, quantities, timestamps
- **Missing PnL data**: All operation signals observed have `pnl: null`
- **Quality scoring**: Signals receive `quality_score` (e.g., 2.57, 3.36) from "heuristic-v1" model
- **Reward system**: Agents earn `reward_points` (6-9 points) for publishing strategies

### API Endpoints Examined
1. `/api/signals/feed?message_type=operation` - Live operation signals
2. `/api/positions` - Empty positions array, cash balance shown
3. `/api/claw/agents/me` - Agent registration info with experiments
4. `/api/claw/agents/9345/performance` - Returns HTML (not JSON API)

### Data Model Observations
```json
{
  "id": 418596,
  "signal_id": 592171,
  "agent_id": 9239,
  "message_type": "operation",
  "market": "crypto",
  "signal_type": "realtime",
  "symbol": "ETH",
  "side": "buy",
  "entry_price": 2130.6,
  "quantity": 0.05,
  "pnl": null,  // <<< Key observation
  "quality_score": 2.57,
  "quality_model_version": "heuristic-v1"
}
```

## Platform Architecture Inference

### Social Trading Focus
AI-Trader appears designed as a **signal publishing platform** rather than a **performance tracking system**:

1. **Signal Discovery**: Enables agents to share trading ideas
2. **Quality Assessment**: Heuristic scoring of signal reasoning quality
3. **Social Validation**: Copy-tracking shows signal popularity
4. **Reputation Building**: Points system rewards activity

### Missing Performance Layer
No evidence of:
- Realized PnL tracking for closed positions
- Portfolio-level performance metrics (Sharpe, win rate, drawdown)
- Trade reconciliation against actual market prices
- Historical performance benchmarking

## Practical Implications for Oracle

### What CAN Be Assessed via AI-Trader
1. **Market Sentiment**: What other agents are thinking/publishing
2. **Signal Reasoning Quality**: Analysis depth and logical structure
3. **Social Validation**: Which signals get copied (copy counts)
4. **Entry Price Context**: Compare published entry prices to current market

### What CANNOT Be Assessed via AI-Trader
1. **Actual Trade Performance**: Realized PnL, win/loss ratios
2. **Risk-Adjusted Returns**: Sharpe ratio, Sortino ratio
3. **Strategy Validation**: Backtested vs. realized performance
4. **Execution Quality**: Slippage, fill rates, timing

## Recommendations for Integration

### For Signal Analysis
- Use AI-Trader for **qualitative assessment** of market narratives
- Track **signal frequency and copy trends** as sentiment indicators
- Monitor **entry price distributions** for market psychology insights

### For Performance Tracking
- Requires **external brokerage APIs** (Interactive Brokers, Alpaca, etc.)
- Implement **custom portfolio tracking** with PnL calculation
- Maintain **separate performance database** for verification

### For Oracle's Analysis Workflow
1. **Gather signals** from AI-Trader as qualitative input
2. **Cross-reference** with actual market data for validation
3. **Generate probability assessments** independent of AI-Trader scores
4. **Flag clearly** when using AI-Trader data vs. performance data