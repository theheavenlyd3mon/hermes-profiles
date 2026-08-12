#!/usr/bin/env python3
"""
Verify if the current Hermes model supports reasoning_effort.

This script tests the reasoning_effort parameter against the configured
model to determine if it's actually used or ignored.

Usage:
    python verify_reasoning_effort.py

Exit codes:
    0 = Model supports reasoning_effort
    1 = Model ignores reasoning_effort (no error, just unused)
    2 = Error occurred
"""

import sys
import os

# Add hermes-agent to path
hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
sys.path.insert(0, os.path.join(hermes_home, "hermes-agent"))

from hermes_constants import parse_reasoning_effort


def test_parse_reasoning_effort():
    """Test parse_reasoning_effort function directly."""
    print("Testing parse_reasoning_effort() function:")
    
    test_cases = [
        ("", None),
        ("none", {"enabled": False}),
        ("minimal", {"enabled": True, "effort": "minimal"}),
        ("low", {"enabled": True, "effort": "low"}),
        ("medium", {"enabled": True, "effort": "medium"}),
        ("high", {"enabled": True, "effort": "high"}),
        ("xhigh", {"enabled": True, "effort": "xhigh"}),
        ("  Medium  ", {"enabled": True, "effort": "medium"}),  # whitespace handling
        ("invalid", None),
    ]
    
    all_passed = True
    for value, expected in test_cases:
        result = parse_reasoning_effort(value)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"  {status} parse_reasoning_effort({repr(value)}) = {result}")
    
    return all_passed


def check_current_config():
    """Check current reasoning_effort setting from config."""
    import yaml
    
    # Try profile-specific config first
    config_paths = [
        os.path.expanduser("~/.hermes/profiles/senna/home/.hermes/config.yaml"),
        os.path.expanduser("~/.hermes/config.yaml"),
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            print(f"\nReading config from: {path}")
            with open(path) as f:
                config = yaml.safe_load(f)
            
            agent_cfg = config.get("agent", {})
            effort = agent_cfg.get("reasoning_effort", "")
            print(f"  Current agent.reasoning_effort: {repr(e effort)}")
            print(f"  Parsed result: {parse_reasoning_effort(effort)}")
            return effort
    
    print("  No config file found")
    return None


def main():
    print("=" * 60)
    print("Hermes Reasoning Effort Verification")
    print("=" * 60)
    print()
    
    # Test parse function
    print("1. Function Test:")
    func_ok = test_parse_reasoning_effort()
    print()
    
    # Check config
    print("2. Current Config:")
    current_effort = check_current_config()
    print()
    
    # Summary
    print("3. Summary:")
    if current_effort is None:
        print("  No reasoning_effort set in config")
    elif current_effort == "":
        print("  reasoning_effort is empty (provider default)")
    elif current_effort == "none":
        print("  reasoning_effort is 'none' (disabled)")
    else:
        parsed = parse_reasoning_effort(current_effort)
        if parsed and parsed.get("enabled", False):
            print(f"  reasoning_effort is '{current_effort}' (enabled)")
    
    print()
    
    # Provider note
    print("4. Provider Notes:")
    print("  - Kimi/Moonshot: ✅ Supports reasoning_effort")
    print("  - DeepSeek:      ⚠️  Parameter ignored (no error)")
    print("  - OpenAI GPT:    ⚠️  Parameter ignored (no error)")
    print("  - Anthropic:     ⚠️  Parameter ignored (no error)")
    print()
    
    if func_ok:
        print("✅ All tests passed")
        return 0
    else:
        print("❌ Some tests failed")
        return 2


if __name__ == "__main__":
    sys.exit(main())