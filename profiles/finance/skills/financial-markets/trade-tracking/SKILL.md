---
name: trade-tracking
description: "Track trade profitability with automatic logging to Obsidian or Notion. Simple CLI for adding/closing trades, auto-generates notes with PnL and win rate metrics."
version: 1.0.0
platforms: [macos, linux]
triggers: [trade tracking, trade logging, profitability tracking, PnL tracking, trade journal, obsidian trades, notion trades]
metadata:
  hermes:
    tags: [trading, finance, obsidian, notion, logging, performance]
---

# Trade Tracking

Simple system to track whether trades are profitable or not, with automatic logging to Obsidian or Notion.

## When to Use

- User wants to track trade outcomes (profitable/unprofitable)
- User wants automatic logging to their note-taking system
- User wants simple PnL tracking, not complex portfolio analytics
- Integration with AI-Trader or other signal sources

## Architecture

```
trade_tracker.py      # Main CLI and Trade class
trade_logger.py       # Platform-specific logging (Obsidian/Notion)
trade_config.json     # Configuration
ai_trader_integration.py  # Example integration
```

## Quick Start

### 1. Track Trades

```bash
# Add a trade
python3 trade_tracker.py add AAPL buy 150.50 10

# Close a trade (auto-logs to configured platform)
python3 trade_tracker.py close AAPL 155.25

# Check profitability
python3 trade_tracker.py check
# Output: Overall: PROFITABLE ($47.50)
```

### 2. Setup Logging

#### Obsidian (Default)
```bash
python3 trade_tracker.py setup obsidian
```

#### Notion
```bash
python3 trade_tracker.py setup notion [page_id]
```

## Key Design Decisions

### 1. Simple Over Complex
- Just track entry/exit prices and quantity
- Calculate PnL and profitability (yes/no)
- Win rate and total PnL summary
- No Sharpe ratio, drawdown, or complex metrics (user explicitly wanted simple)

### 2. Automatic Logging
- Trades auto-log when closed (not manual)
- Creates Obsidian notes or Notion pages automatically
- Template-based for consistency

### 3. Modular Design
- Separate tracker (data) from logger (output)
- Config-driven platform selection
- Easy to add new logging platforms

## Configuration

### trade_config.json

```json
{
  "default_platform": "obsidian",
  "obsidian": {
    "enabled": true,
    "vault_path": "/path/to/vault",
    "notes_folder": "Trade Tracking",
    "template": "# Trade: {{symbol}}\n\n**Status:** {{status}}\n..."
  },
  "notion": {
    "enabled": true,
    "database_id": "",
    "page_id": ""
  }
}
```

## Quick Reference

### Commands
```bash
# Add trade
python trade_tracker.py add SYMBOL SIDE PRICE QUANTITY
python trade_tracker.py add AAPL buy 150.50 10

# Close trade (auto-logs)
python trade_tracker.py close SYMBOL EXIT_PRICE
python trade_tracker.py close AAPL 155.25

# Check profitability
python trade_tracker.py check              # Overall
python trade_tracker.py check AAPL         # Specific symbol

# Summary
python trade_tracker.py summary

# Setup
python trade_tracker.py setup obsidian [folder]
python trade_tracker.py setup notion [page_id]

# Test
python scripts/test_setup.py
```

### Expected Output
```
# Add
Added buy 10.0 AAPL @ $150.50

# Close
Logged AAPL to Obsidian: /path/to/AAPL_2026-05-21.md
Closed AAPL @ $155.25

# Check
Overall: PROFITABLE ($47.50)

# Summary
Trade Summary:
  Total Calls: 1
  Profitable: 1
  Total PnL: $47.50
  Win Rate: 100.0%
  Overall: PROFITABLE
```

## Pitfalls

1. **Circular imports**: trade_logger.py defines its own Trade class to avoid importing from trade_tracker.py. Don't try to share the class - it creates circular dependencies.

2. **Missing entry_time**: Trade class must have `entry_time` field, and `add_call()` must set it to `datetime.now().isoformat()`. Logger expects this field.

3. **exit_time vs closed_at**: Both fields exist but serve different purposes. `closed_at` is for internal tracking, `exit_time` is for logging. Set both in `close_call()`.

4. **Platform not configured**: If default platform has no database_id/page_id (Notion) or vault_path (Obsidian), logging fails silently with warning. Always run `setup` first.

5. **Practice trade integration**: When providing practice trade recommendations from oracle-analyst, always include exact `python3 trade_tracker.py add` commands. Users need the specific command to log trades, not just the recommendation. See `references/practice-trade-integration.md` for workflow details.

## Obsidian Note Template

```markdown
# Trade: {{symbol}}

**Status:** {{status}}
**Entry:** {{entry_price}} @ {{entry_time}}
**Exit:** {{exit_price}} @ {{exit_time}}
**Quantity:** {{quantity}}
**PnL:** {{pnl}}
**Profitable:** {{profitable}}

## Notes
{{note}}
```

## Philosophy

**Simple > comprehensive.** The user typically wants one answer: "am I profitable?" Keep it minimal. Do NOT propose QuantConnect, portfolio optimization libraries, or multi-broker integrations unless asked. Default to the simplest thing that answers "profitable or not."

## AI-Trader Gap

AI-Trader (ai4trade.ai) does NOT track realized PnL, closed trade history, or win rate. See `references/ai-trader-gap.md` for API evidence and workaround strategy. Use this tracker as the external PnL layer for AI-Trader signals.

## Integration Examples

### AI-Trader Integration

```python
from trade_tracker import TradeTracker

tracker = TradeTracker()

# Log AI-Trader signal
tracker.add_call(
    symbol="BTC",
    side="buy",
    entry_price=65000.00,
    quantity=0.1
)

# Close when ready (auto-logs to Obsidian)
tracker.close_call("BTC", 67000.00)

# Check profitability
print(tracker.check_profitability())
```

### Custom Integration

```python
from trade_tracker import TradeTracker

tracker = TradeTracker()

# Add trade from any source
tracker.add_call(
    symbol="NVDA",
    side="buy",
    entry_price=800.00,
    quantity=5
)

# Close at exit price
tracker.close_call("NVDA", 850.00)

# Get summary
summary = tracker.get_summary()
print(f"Win rate: {summary['win_rate']}%")
print(f"Total PnL: ${summary['total_pnl']}")
```

## Files

### Templates (copy and modify)
- `templates/trade_tracker.py` - Main tracking system with CLI
- `templates/trade_logger.py` - Logging to Obsidian/Notion
- `templates/trade_config.json` - Configuration

### References
- `references/implementation-notes.md` - Pitfalls, lessons learned, and technical details

### Scripts
- `scripts/test_setup.py` - Verify installation and configuration

## Quick Setup

1. Copy templates to your project:
   ```bash
   cp templates/trade_tracker.py .
   cp templates/trade_logger.py .
   cp templates/trade_config.json .
   ```

2. Configure for your platform:
   ```bash
   # Edit trade_config.json with your vault path or Notion details
   ```

3. Run setup:
   ```bash
   python trade_tracker.py setup obsidian
   # or
   python trade_tracker.py setup notion [page_id]
   ```

4. Verify installation:
   ```bash
   python scripts/test_setup.py
   ```

## Future Extensions

- Web dashboard for visualization
- Risk metrics (Sharpe, max drawdown)
- Benchmark comparison (SPY, BTC)
- Multi-portfolio support
- Real-time price integration
