---
name: oracle-tradingagents
description: Multi-agent LLM trading analysis framework — 4 specialist analysts (fundamentals, sentiment, news, technical) with bullish/bearish debate, risk management, and portfolio decisions. Wraps TradingAgents CLI/Python API.
version: 1.0.0
platforms: [macos, linux]
triggers: [trading agents, stock analysis, trading analysis, multi-agent trading, fundamental analysis, technical analysis, sentiment analysis]
metadata:
  hermes:
    tags: [finance, trading, multi-agent, analysis, deepseek]
---

# TradingAgents — Multi-Agent Financial Analysis Engine

Location: `~/tools/TradingAgents`
Python env: `uv` managed (no conda needed)
Config: `~/tools/TradingAgents/.env`

## What It Does

Runs a full trading firm simulation with specialized LLM agents:

```
Analyst Team:
  Fundamentals Analyst  → company financials, intrinsic value
  Sentiment Analyst     → news, StockTwits, Reddit sentiment
  News Analyst          → macroeconomic news and events
  Technical Analyst     → MACD, RSI, pattern detection

Researcher Team:
  Bullish Researcher    → makes the bull case
  Bearish Researcher    → makes the bear case
  (configurable debate rounds)

Decision:
  Trader Agent          → synthesizes all reports → trade decision
  Risk Management       → portfolio risk, volatility, liquidity
  Portfolio Manager     → final approval/rejection + reflection
```

## Usage

### Python API (preferred for Hermes integration)
```bash
cd ~/tools/TradingAgents

# Single analysis
uv run python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate('NVDA', '2026-05-21')
print(decision)
"
```

### CLI (interactive)
```bash
cd ~/tools/TradingAgents
uv run tradingagents
```

### CLI (non-interactive, via Python)
```bash
cd ~/tools/TradingAgents
uv run python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
import json

config = DEFAULT_CONFIG.copy()
config['llm_provider'] = 'deepseek'
config['deep_think_llm'] = 'deepseek-v3.2'
config['quick_think_llm'] = 'deepseek-v3.2'
config['max_debate_rounds'] = 1

ta = TradingAgentsGraph(debug=False, config=config)
_, decision = ta.propagate('TICKER', 'YYYY-MM-DD')
print(json.dumps(decision, indent=2))
"
```

## Configuration (via .env)

Set in `~/tools/TradingAgents/.env`:
```bash
DEEPSEEK_API_KEY=...                    # Required
ALPHA_VANTAGE_API_KEY=...               # Required for market data
TRADINGAGENTS_LLM_PROVIDER=deepseek     # Provider
TRADINGAGENTS_DEEP_THINK_LLM=deepseek-v3.2   # Complex reasoning
TRADINGAGENTS_QUICK_THINK_LLM=deepseek-v3.2  # Quick tasks
TRADINGAGENTS_MAX_DEBATE_ROUNDS=1       # Bull vs bear debate rounds
TRADINGAGENTS_OUTPUT_LANGUAGE=English
```

## Decision Memory

Always-on. Logs to `~/.tradingagents/memory/trading_memory.md`.
On re-runs for same ticker, fetches realized returns and injects past lessons into Portfolio Manager prompt.

Override path: `TRADINGAGENTS_MEMORY_LOG_PATH`

## Checkpoint Resume

Opt-in via code:
```python
config['checkpoint_enabled'] = True
```
Checkpoints at `~/.tradingagents/cache/checkpoints/<TICKER>.db`

## Cost Estimate

Per full analysis run (7+ LLM calls):
- DeepSeek v3.2: ~$0.01-0.03
- OpenAI GPT-4: ~$0.10-0.30

## Pitfalls
- Requires Alpha Vantage API key (free tier: 25 req/day)
- Each analysis = 7+ LLM calls — don't run on every ticker every minute
- Decision memory accumulates — periodically review/clean `~/.tradingagents/memory/`
- Date must be in YYYY-MM-DD format
- Ticker symbols use Yahoo Finance format (e.g., NVDA, BTC-USD, ^GSPC)
- v0.2.5 (May 2026) — check for updates periodically
