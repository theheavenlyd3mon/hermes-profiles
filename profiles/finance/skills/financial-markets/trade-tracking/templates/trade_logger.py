#!/usr/bin/env python3
"""
Trade Logger - Logs trades to Notion or Obsidian
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from dataclasses import dataclass, asdict

# Simple Trade class for logging (no circular import)
@dataclass
class Trade:
    """Represents a single trade for logging purposes."""
    symbol: str
    side: str
    entry_price: float
    quantity: float
    exit_price: Optional[float] = None
    entry_time: Optional[str] = None
    exit_time: Optional[str] = None
    note: Optional[str] = None
    
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

class TradeLogger:
    """Logs trades to various platforms."""
    
    def __init__(self, config_file="trade_config.json"):
        self.config = self._load_config(config_file)
        self.platform = self.config.get("default_platform", "obsidian")
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"default_platform": "obsidian", "notion": {"enabled": False}, "obsidian": {"enabled": False}}
    
    def log_trade(self, trade: Trade, platform: Optional[str] = None) -> bool:
        """Log a trade to the specified platform."""
        platform = platform or self.platform
        
        if platform == "notion" and self.config["notion"]["enabled"]:
            return self._log_to_notion(trade)
        elif platform == "obsidian" and self.config["obsidian"]["enabled"]:
            return self._log_to_obsidian(trade)
        else:
            print(f"Platform {platform} not enabled or configured")
            return False
    
    def _log_to_obsidian(self, trade: Trade) -> bool:
        """Log trade to Obsidian vault."""
        obsidian_config = self.config["obsidian"]
        vault_path = obsidian_config.get("vault_path", "")
        
        if not vault_path:
            print("Obsidian vault_path not configured")
            return False
        
        # Create trade note
        profitable = "PROFITABLE" if trade.is_profitable() else "NOT PROFITABLE"
        template = obsidian_config.get("template", "")
        
        note_content = template.replace("{{symbol}}", trade.symbol)
        note_content = note_content.replace("{{status}}", profitable)
        note_content = note_content.replace("{{entry_price}}", f"${trade.entry_price:.2f}")
        note_content = note_content.replace("{{entry_time}}", trade.entry_time or "N/A")
        note_content = note_content.replace("{{exit_price}}", f"${trade.exit_price:.2f}" if trade.exit_price else "Open")
        note_content = note_content.replace("{{exit_time}}", trade.exit_time or "Open")
        note_content = note_content.replace("{{quantity}}", str(trade.quantity))
        note_content = note_content.replace("{{pnl}}", f"${trade.pnl():.2f}")
        note_content = note_content.replace("{{profitable}}", profitable)
        note_content = note_content.replace("{{note}}", trade.note or "")
        
        # Create filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{trade.symbol}_{date_str}.md"
        folder_path = os.path.join(vault_path, obsidian_config.get("notes_folder", "Trade Tracking"))
        filepath = os.path.join(folder_path, filename)
        
        # Create folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)
        
        # Write note
        try:
            with open(filepath, 'w') as f:
                f.write(note_content)
            print(f"Logged {trade.symbol} to Obsidian: {filepath}")
            return True
        except Exception as e:
            print(f"Error logging to Obsidian: {e}")
            return False
    
    def _log_to_notion(self, trade: Trade) -> bool:
        """Log trade to Notion."""
        notion_config = self.config["notion"]
        api_key = os.getenv("NOTION_API_KEY")
        
        if not api_key:
            print("NOTION_API_KEY not set")
            return False
        
        # Determine if we're logging to database or page
        if notion_config.get("database_id"):
            return self._log_to_notion_database(trade, notion_config, api_key)
        elif notion_config.get("page_id"):
            return self._log_to_notion_page(trade, notion_config, api_key)
        else:
            print("No Notion database_id or page_id configured")
            return False
    
    def _log_to_notion_database(self, trade: Trade, config: Dict, api_key: str) -> bool:
        """Log trade to Notion database."""
        database_id = config["database_id"]
        props = config.get("properties", {})
        
        # Prepare trade data
        trade_data = {
            "symbol": trade.symbol,
            "side": trade.side,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "quantity": trade.quantity,
            "pnl": trade.pnl(),
            "profitable": trade.is_profitable(),
            "entry_time": trade.entry_time,
            "exit_time": trade.exit_time or datetime.now().isoformat()
        }
        
        # Build properties
        properties = {}
        for key, notion_prop in props.items():
            if key in trade_data:
                value = trade_data[key]
                if key in ["entry_price", "exit_price", "quantity", "pnl"]:
                    properties[notion_prop] = {"number": value}
                elif key == "profitable":
                    properties[notion_prop] = {"checkbox": value}
                elif key in ["entry_time", "exit_time"]:
                    properties[notion_prop] = {"date": {"start": value}}
                else:
                    properties[notion_prop] = {"title": [{"text": {"content": str(value)}}]}
        
        # Make API call
        url = "https://api.notion.com/v1/pages"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json"
        }
        data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                print(f"Logged {trade.symbol} to Notion database")
                return True
            else:
                print(f"Notion API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error logging to Notion: {e}")
            return False
    
    def setup_obsidian_folder(self, folder_name: str = "Trade Tracking") -> bool:
        """Create Obsidian folder structure."""
        obsidian_config = self.config["obsidian"]
        vault_path = obsidian_config.get("vault_path", "")
        
        if not vault_path:
            print("Obsidian vault_path not configured")
            return False
        
        folder_path = os.path.join(vault_path, folder_name)
        try:
            os.makedirs(folder_path, exist_ok=True)
            
            # Create index note
            index_content = f"""# Trade Tracking

This folder contains trade tracking notes.

## Structure
- Each trade gets its own note: `SYMBOL_DATE.md`
- Notes are automatically created when trades are closed
- Use Obsidian search to find trades by symbol or date

## Usage
Trades are automatically logged here when closed in the trade tracker.
"""
            index_path = os.path.join(folder_path, "index.md")
            with open(index_path, 'w') as f:
                f.write(index_content)
            
            # Update config
            self.config["obsidian"]["notes_folder"] = folder_name
            with open("trade_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"Created Obsidian folder: {folder_path}")
            return True
        except Exception as e:
            print(f"Error creating Obsidian folder: {e}")
            return False

if __name__ == "__main__":
    import sys
    
    logger = TradeLogger()
    
    if len(sys.argv) < 2:
        print("Trade Logger")
        print("Usage:")
        print("  python trade_logger.py setup notion [page_id]  # Setup Notion database")
        print("  python trade_logger.py setup obsidian [folder]  # Setup Obsidian folder")
        print("  python trade_logger.py test                     # Test logging")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "setup":
        if len(sys.argv) < 3:
            print("Usage: setup notion [page_id] | setup obsidian [folder]")
            sys.exit(1)
        
        platform = sys.argv[2]
        if platform == "notion":
            page_id = sys.argv[3] if len(sys.argv) > 3 else input("Enter Notion parent page ID: ")
            logger.setup_notion_database(page_id)
        elif platform == "obsidian":
            folder = sys.argv[3] if len(sys.argv) > 3 else "Trade Tracking"
            logger.setup_obsidian_folder(folder)
    
    elif cmd == "test":
        # Create a test trade
        test_trade = Trade(
            symbol="TEST",
            side="buy",
            entry_price=100.0,
            quantity=1,
            exit_price=105.0,
            entry_time=datetime.now().isoformat(),
            exit_time=datetime.now().isoformat()
        )
        
        print(f"Test trade: {test_trade.symbol} PnL: ${test_trade.pnl():.2f}")
        logger.log_trade(test_trade)
    
    else:
        print(f"Unknown command: {cmd}")
