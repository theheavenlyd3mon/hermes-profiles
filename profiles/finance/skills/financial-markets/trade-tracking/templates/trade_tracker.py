#!/usr/bin/env python3
"""
Simple Trade Profitability Tracker
Just tracks whether calls are profitable or not.
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from trade_logger import TradeLogger
    logger_available = True
except ImportError:
    logger_available = False
    print("Warning: trade_logger.py not found. Logging disabled.")

@dataclass
class Trade:
    """Represents a single trade call."""
    symbol: str
    side: str  # "buy" or "sell"
    entry_price: float
    quantity: float
    exit_price: Optional[float] = None
    entry_time: Optional[str] = None
    exit_time: Optional[str] = None
    closed_at: Optional[str] = None
    
    def pnl(self) -> float:
        """Calculate profit/loss."""
        if self.exit_price is None:
            return 0.0
        if self.side == "buy":
            return (self.exit_price - self.entry_price) * self.quantity
        else:  # sell (short)
            return (self.entry_price - self.exit_price) * self.quantity
    
    def is_profitable(self) -> bool:
        """Check if trade is profitable."""
        return self.pnl() > 0
    
    def is_closed(self) -> bool:
        return self.exit_price is not None

class TradeTracker:
    """Simple tracker for trade profitability."""
    
    def __init__(self, data_file="trades.json"):
        self.data_file = data_file
        self.trades = self._load_trades()
        self.logger = None
        if logger_available:
            try:
                self.logger = TradeLogger()
            except Exception as e:
                print(f"Could not initialize logger: {e}")
    
    def setup_logging(self, platform: str = None, **kwargs):
        """Setup logging integration."""
        if not logger_available:
            print("Logger not available")
            return False
        
        if not self.logger:
            self.logger = TradeLogger()
        
        if platform == "notion" or (platform is None and self.logger.platform == "notion"):
            if "page_id" in kwargs:
                self.logger.setup_notion_database(kwargs["page_id"])
                return True
            else:
                print("Notion setup requires page_id parameter")
                return False
        
        elif platform == "obsidian" or (platform is None and self.logger.platform == "obsidian"):
            folder = kwargs.get("folder", "Trade Tracking")
            self.logger.setup_obsidian_folder(folder)
            return True
        
        return False
    
    def _load_trades(self) -> List[Trade]:
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                return [Trade(**t) for t in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save(self):
        with open(self.data_file, 'w') as f:
            json.dump([asdict(t) for t in self.trades], f, indent=2)
    
    def add_call(self, symbol: str, side: str, entry_price: float, quantity: float) -> str:
        """Add a new trade call. Returns trade ID."""
        trade_id = f"{symbol}_{len(self.trades)+1}"
        trade = Trade(
            symbol=symbol,
            side=side.lower(),
            entry_price=entry_price,
            quantity=quantity,
            entry_time=datetime.now().isoformat()
        )
        self.trades.append(trade)
        self._save()
        return trade_id
    
    def close_call(self, symbol: str, exit_price: float, trade_num: Optional[int] = None) -> bool:
        """Close a trade call. Returns success status."""
        trade_closed = False
        
        # Find the open trade
        if trade_num:
            # Close specific trade number
            idx = trade_num - 1
            if 0 <= idx < len(self.trades) and not self.trades[idx].is_closed():
                self.trades[idx].exit_price = exit_price
                self.trades[idx].closed_at = datetime.now().isoformat()
                self.trades[idx].exit_time = datetime.now().isoformat()
                self._save()
                trade_closed = True
                closed_trade = self.trades[idx]
        else:
            # Close most recent open trade for this symbol
            for trade in reversed(self.trades):
                if trade.symbol.upper() == symbol.upper() and not trade.is_closed():
                    trade.exit_price = exit_price
                    trade.closed_at = datetime.now().isoformat()
                    trade.exit_time = datetime.now().isoformat()
                    self._save()
                    trade_closed = True
                    closed_trade = trade
                    break
        
        # Log the trade if logger is available and trade was closed
        if trade_closed and self.logger:
            try:
                self.logger.log_trade(closed_trade)
            except Exception as e:
                print(f"Warning: Could not log trade: {e}")
        
        return trade_closed
    
    def get_summary(self) -> dict:
        """Get simple summary of profitability."""
        closed = [t for t in self.trades if t.is_closed()]
        open_trades = [t for t in self.trades if not t.is_closed()]
        
        profitable = [t for t in closed if t.is_profitable()]
        unprofitable = [t for t in closed if not t.is_profitable()]
        
        total_pnl = sum(t.pnl() for t in closed)
        win_rate = len(profitable) / len(closed) * 100 if closed else 0
        
        return {
            "total_calls": len(self.trades),
            "open_calls": len(open_trades),
            "closed_calls": len(closed),
            "profitable_calls": len(profitable),
            "unprofitable_calls": len(unprofitable),
            "total_pnl": round(total_pnl, 2),
            "win_rate": round(win_rate, 2),
            "overall_profitable": total_pnl > 0
        }
    
    def check_profitability(self, symbol: Optional[str] = None) -> str:
        """Simple check: are we profitable?"""
        if symbol:
            # Check specific symbol
            symbol_trades = [t for t in self.trades if t.symbol.upper() == symbol.upper() and t.is_closed()]
            if not symbol_trades:
                return f"No closed trades for {symbol}"
            total_pnl = sum(t.pnl() for t in symbol_trades)
            return f"{symbol}: {'PROFITABLE' if total_pnl > 0 else 'NOT PROFITABLE'} (${total_pnl:.2f})"
        else:
            # Check overall
            summary = self.get_summary()
            if summary['closed_calls'] == 0:
                return "No closed trades to evaluate"
            return f"Overall: {'PROFITABLE' if summary['overall_profitable'] else 'NOT PROFITABLE'} (${summary['total_pnl']:.2f})"

# Quick CLI interface
if __name__ == "__main__":
    import sys
    
    tracker = TradeTracker()
    
    if len(sys.argv) < 2:
        print("Simple Trade Tracker")
        print("Usage:")
        print("  python trade_tracker.py add AAPL buy 150.50 10    # Add trade")
        print("  python trade_tracker.py close AAPL 155.25        # Close trade")
        print("  python trade_tracker.py check                    # Check overall profitability")
        print("  python trade_tracker.py check AAPL               # Check specific symbol")
        print("  python trade_tracker.py summary                  # Show summary")
        print("  python trade_tracker.py setup notion [page_id]   # Setup Notion logging")
        print("  python trade_tracker.py setup obsidian [folder]  # Setup Obsidian logging")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        if len(sys.argv) != 6:
            print("Usage: add SYMBOL SIDE PRICE QUANTITY")
            print("Example: add AAPL buy 150.50 10")
            sys.exit(1)
        symbol, side, price, qty = sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
        trade_id = tracker.add_call(symbol, side, price, qty)
        print(f"Added {side} {qty} {symbol} @ ${price:.2f}")
        
    elif cmd == "close":
        if len(sys.argv) < 4:
            print("Usage: close SYMBOL EXIT_PRICE [TRADE_NUM]")
            print("Example: close AAPL 155.25")
            sys.exit(1)
        symbol = sys.argv[2]
        exit_price = float(sys.argv[3])
        trade_num = int(sys.argv[4]) if len(sys.argv) > 4 else None
        success = tracker.close_call(symbol, exit_price, trade_num)
        if success:
            print(f"Closed {symbol} @ ${exit_price:.2f}")
        else:
            print(f"Could not find open trade for {symbol}")
            
    elif cmd == "check":
        symbol = sys.argv[2] if len(sys.argv) > 2 else None
        print(tracker.check_profitability(symbol))
        
    elif cmd == "summary":
        summary = tracker.get_summary()
        print("Trade Summary:")
        print(f"  Total Calls: {summary['total_calls']}")
        print(f"  Open Calls: {summary['open_calls']}")
        print(f"  Closed Calls: {summary['closed_calls']}")
        print(f"  Profitable: {summary['profitable_calls']}")
        print(f"  Unprofitable: {summary['unprofitable_calls']}")
        print(f"  Total PnL: ${summary['total_pnl']:.2f}")
        print(f"  Win Rate: {summary['win_rate']:.1f}%")
        print(f"  Overall: {'PROFITABLE' if summary['overall_profitable'] else 'NOT PROFITABLE'}")
        
    elif cmd == "setup":
        if len(sys.argv) < 3:
            print("Usage: setup notion [page_id] | setup obsidian [folder]")
            sys.exit(1)
        
        platform = sys.argv[2]
        if platform == "notion":
            page_id = sys.argv[3] if len(sys.argv) > 3 else input("Enter Notion parent page ID: ").strip()
            if page_id:
                tracker.setup_logging(platform="notion", page_id=page_id)
            else:
                print("Notion setup requires page_id")
        elif platform == "obsidian":
            folder = sys.argv[3] if len(sys.argv) > 3 else "Trade Tracking"
            tracker.setup_logging(platform="obsidian", folder=folder)
        else:
            print(f"Unknown platform: {platform}")
            print("Use: notion, obsidian")
    
    else:
        print(f"Unknown command: {cmd}")
        print("Use: add, close, check, summary, setup")
