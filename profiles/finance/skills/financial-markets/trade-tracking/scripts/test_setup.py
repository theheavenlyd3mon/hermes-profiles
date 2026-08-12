#!/usr/bin/env python3
"""
Test script for trade tracking system.
Verifies setup and basic functionality.
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration file."""
    print("1. Testing configuration...")
    try:
        with open("trade_config.json", 'r') as f:
            config = json.load(f)
        
        platform = config.get("default_platform")
        print(f"   Default platform: {platform}")
        
        if platform == "obsidian":
            vault_path = config["obsidian"]["vault_path"]
            folder = config["obsidian"]["notes_folder"]
            print(f"   Obsidian vault: {vault_path}")
            print(f"   Notes folder: {folder}")
            
            # Check if folder exists
            folder_path = os.path.join(vault_path, folder)
            if os.path.exists(folder_path):
                print(f"   ✓ Folder exists: {folder_path}")
            else:
                print(f"   ✗ Folder missing: {folder_path}")
                print(f"     Run: python trade_tracker.py setup obsidian")
        
        elif platform == "notion":
            db_id = config["notion"]["database_id"]
            page_id = config["notion"]["page_id"]
            print(f"   Notion database_id: {db_id or 'Not set'}")
            print(f"   Notion page_id: {page_id or 'Not set'}")
            
            if not db_id and not page_id:
                print("   ✗ No Notion target configured")
                print("     Run: python trade_tracker.py setup notion [page_id]")
        
        return True
    except Exception as e:
        print(f"   ✗ Config error: {e}")
        return False

def test_logger():
    """Test logger import."""
    print("\n2. Testing logger...")
    try:
        from trade_logger import TradeLogger, Trade
        print("   ✓ Logger imported successfully")
        
        logger = TradeLogger()
        print(f"   ✓ Logger initialized (platform: {logger.platform})")
        
        return True
    except Exception as e:
        print(f"   ✗ Logger error: {e}")
        return False

def test_tracker():
    """Test tracker import and basic operations."""
    print("\n3. Testing tracker...")
    try:
        from trade_tracker import TradeTracker, Trade
        print("   ✓ Tracker imported successfully")
        
        # Test with temporary file
        test_file = "test_trades.json"
        tracker = TradeTracker(data_file=test_file)
        print("   ✓ Tracker initialized")
        
        # Test add
        trade_id = tracker.add_call("TEST", "buy", 100.0, 1)
        print(f"   ✓ Added trade: {trade_id}")
        
        # Test close
        success = tracker.close_call("TEST", 105.0)
        print(f"   ✓ Closed trade: {success}")
        
        # Test check
        result = tracker.check_profitability()
        print(f"   ✓ Profitability: {result}")
        
        # Cleanup
        os.remove(test_file)
        
        return True
    except Exception as e:
        print(f"   ✗ Tracker error: {e}")
        return False

def test_logging():
    """Test actual logging to configured platform."""
    print("\n4. Testing logging...")
    try:
        from trade_tracker import TradeTracker
        
        tracker = TradeTracker()
        
        if not tracker.logger:
            print("   ✗ Logger not initialized")
            return False
        
        # Add and close a test trade
        trade_id = tracker.add_call("TEST_LOG", "buy", 50.0, 1)
        success = tracker.close_call("TEST_LOG", 55.0)
        
        if success:
            print("   ✓ Trade logged successfully")
            
            # Check if note was created (for Obsidian)
            config = tracker.logger.config
            if config.get("default_platform") == "obsidian":
                vault_path = config["obsidian"]["vault_path"]
                folder = config["obsidian"]["notes_folder"]
                note_path = os.path.join(vault_path, folder, "TEST_LOG_" + datetime.now().strftime("%Y-%m-%d") + ".md")
                
                if os.path.exists(note_path):
                    print(f"   ✓ Obsidian note created: {note_path}")
                    # Cleanup
                    os.remove(note_path)
                else:
                    print(f"   ✗ Obsidian note not found: {note_path}")
            
            return True
        else:
            print("   ✗ Failed to close trade")
            return False
            
    except Exception as e:
        print(f"   ✗ Logging error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Trade Tracking System - Setup Verification")
    print("=" * 60)
    
    results = []
    results.append(("Config", test_config()))
    results.append(("Logger", test_logger()))
    results.append(("Tracker", test_tracker()))
    results.append(("Logging", test_logging()))
    
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Add a trade: python trade_tracker.py add AAPL buy 150.50 10")
        print("2. Close it: python trade_tracker.py close AAPL 155.25")
        print("3. Check: python trade_tracker.py check")
    else:
        print("Some tests failed. Check errors above.")
        print("\nCommon fixes:")
        print("- Run: python trade_tracker.py setup obsidian")
        print("- Check trade_config.json has correct vault_path")
        print("- Ensure NOTION_API_KEY is set (for Notion)")
    print("=" * 60)

if __name__ == "__main__":
    main()
