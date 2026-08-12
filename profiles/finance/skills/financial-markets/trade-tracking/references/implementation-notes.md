# Trade Tracking: Implementation Notes

## Circular Import Problem

**Problem**: trade_tracker.py and trade_logger.py both need a Trade class. If trade_logger imports Trade from trade_tracker, and trade_tracker imports TradeLogger from trade_logger, you get a circular import.

**Solution**: Each module defines its own Trade class. trade_logger.py has a simplified version with just the fields needed for logging. trade_tracker.py has the full version with is_closed(), closed_at, etc.

**Lesson**: Don't try to share data classes between modules that import each other. Duplicate the class definition if needed.

## Missing entry_time Field

**Problem**: Logger template expects {{entry_time}} but Trade class in trade_tracker.py didn't have this field initially.

**Solution**: 
1. Add `entry_time: Optional[str] = None` to Trade dataclass
2. Set `entry_time=datetime.now().isoformat()` in add_call()
3. Set `exit_time=datetime.now().isoformat()` in close_call()

**Lesson**: When using template-based logging, ensure all template variables exist in the data class and are populated at the right time.

## exit_time vs closed_at

**Problem**: Two similar fields serve different purposes:
- `closed_at`: Internal tracking, set in close_call()
- `exit_time`: For logging/export, also set in close_call()

**Solution**: Set both fields to the same value in close_call(). This maintains backward compatibility while supporting the logger.

**Lesson**: When adding new fields for logging/export, don't rename existing fields. Add new ones and keep both.

## Platform Configuration

**Problem**: If default_platform is "notion" but no database_id or page_id is configured, logging fails silently.

**Solution**: 
1. Set default_platform to "obsidian" initially (easier to setup)
2. Run `setup obsidian` or `setup notion [page_id]` before first use
3. Logger prints warning if platform not configured

**Lesson**: Always provide a setup command that creates necessary structure (folders, databases) before first use.

## Obsidian Note Template

The template in trade_config.json uses {{variable}} syntax:
- {{symbol}}, {{side}}, {{entry_price}}, {{exit_price}}, {{quantity}}
- {{entry_time}}, {{exit_time}}
- {{pnl}}, {{profitable}}, {{status}}
- {{note}}

All variables must be replaced in _log_to_obsidian(). Missing variables cause incomplete notes.

## Notion API Version

Use `Notion-Version: 2025-09-03` (latest as of May 2026). Earlier versions may not support all features.

## requests Library Warning

Python 3.9 + requests 2.32.x shows urllib3 OpenSSL warning. This is cosmetic and doesn't affect functionality. Can be suppressed with:
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
```

## File Structure

```
project/
├── trade_tracker.py      # Main tracker (CLI + Trade class)
├── trade_logger.py       # Logger (Obsidian/Notion)
├── trade_config.json     # Configuration
├── trades.json           # Data storage (auto-created)
└── Trade Tracking/       # Obsidian notes (auto-created)
    ├── index.md
    ├── AAPL_2026-05-21.md
    └── TSLA_2026-05-21.md
```

## Integration Pattern

For integrating with external trading systems (AI-Trader, etc.):

```python
from trade_tracker import TradeTracker

tracker = TradeTracker()

# 1. Log signal
tracker.add_call(symbol, side, entry_price, quantity)

# 2. Close when ready (auto-logs to Obsidian)
tracker.close_call(symbol, exit_price)

# 3. Check profitability
print(tracker.check_profitability())
```

The key insight: close_call() automatically triggers logging. No manual step needed.
