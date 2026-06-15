---
name: ai-trading-research
description: "AI-assisted trading research agent — builds agents that research markets, generate trade signals, and track P&L, while the human makes all execution decisions. Covers architecture, data sources, cron scheduling, and the human-in-the-loop pattern."
version: 1.0.0
---

# AI Trading Research Agent

## When to Use

- User wants an AI agent to do market research and present trade ideas — but user decides what to actually trade
- Building cron-driven market briefs, watchlist scanners, or trade journaling systems
- Evaluating free data APIs (Finnhub, Alpha Vantage, Alpaca) for trading agent use
- Designing the human-in-the-loop pattern: agent proposes, human disposes

## Core Architecture

```
YOU (decide entry/exit/position size)
  ↑
AGENT (research + signals + tracking)
  ├── Cron: Pre-market scan (30 min before open)
  ├── Cron: Intraday alerts (price levels, news)
  ├── Cron: End-of-day journal + P&L
  └── On-demand: "What do you think about X?"
```

### The Five Pillars

1. **Pre-market research** — news scan, economic calendar, earnings, sentiment
2. **Screening** — filter watchlist by technical criteria (MA, volume, RSI, etc.)
3. **Signal generation** — specific trade ideas with entry, stop, target, and reasoning
4. **Trade journaling** — log every idea, entry/exit, P&L, and reasoning
5. **Post-trade analysis** — review what worked, what didn't, adjust

## Human-in-the-Loop Rules (Hard Constraints)

- **Agent never places trades.** Always present ideas as proposals.
- Always include: ticker, direction (long/short), entry level, stop loss, target, and 1-sentence reasoning.
- User must explicitly confirm before any trade is recorded as "entered."
- Track closed trades with actual P&L vs projected P&L.
- Agent's track record is always visible — no survivorship bias.

## Data Sources (Free Tier)

See `references/data-sources.md` for detailed API comparison, rate limits, and setup.

Quick reference:
- **Finnhub** (60 calls/min free) — real-time quotes, news, earnings, economic calendar. Best all-rounder.
- **Alpaca** (paper trading free) — paper trading API + market data. Commission-free. Use paper keys for development.
- **Alpha Vantage** (25 calls/day free) — historical data, technical indicators. Good for backtesting.
- **Yahoo Finance** (unofficial) — backup for quotes and basic data.

## Cron Pattern for Market Briefs

Three standard schedules for a US equities-focused trading agent:

| Job | Time | Purpose |
|-----|------|---------|
| Morning brief | 9:15 AM ET (pre-market) | News, watchlist scan, levels, ideas |
| Intraday check | 12:00 PM ET | Price alerts, breaking news, position updates |
| End-of-day | 4:30 PM ET | Journal entries, P&L summary, tomorrow's watch |

For crypto (24/7): run every 4-6 hours instead of market-hours-based.

## Bait vs Real (What to Ignore on X)

**Red flags (probably bait):**
- "I gave AI $150 and it made $XX,XXx" — no risk management shown, survivorship bias
- "Fully autonomous trader" — nobody serious runs fully autonomous without kill switches
- "Just connect ChatGPT to your broker" — that's gambling, not a strategy
- No mention of position sizing, stop losses, or track record over 50+ trades

**Green flags (probably real):**
- Starts with paper trading, shows actual track record
- Has explicit risk rules (max position size, stop losses, etc.)
- Shows the full workflow: data → analysis → decision → journal
- Acknowledges the human makes final decisions

## Integration with Multi-Agent Discord

If the user runs a multi-agent Discord setup (reference: `project-workspace` skill), the trading researcher fits as:
- A dedicated profile (e.g., `trader` profile with its own Discord bot)
- Home channel like `#trading-ideas` or `#market-briefs`
- Cron jobs deliver scheduled briefs to the channel
- User replies in-thread to confirm/decline trade ideas
- Writer agent can format trade reviews; Analyst agent can compute stats

## Pitfalls

- **Don't over-automate early.** Start with morning brief cron only, add others after 2 weeks of use.
- **Free API limits are real.** Finnhub allows 60 calls/min — if scanning 50+ tickers, batch or sequence calls.
- **Paper trade first.** Even if the user plans real trades, run the agent on paper for 30+ trades to validate the workflow.
- **Journal or die.** The agent is useless without tracking which ideas played out. Make the journal cron non-negotiable.
- **Timezone matters.** Cron times should be in ET for US markets, UTC for crypto. Label all cron schedules with timezone.
