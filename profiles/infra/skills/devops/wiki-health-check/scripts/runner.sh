#!/usr/bin/env python3
"""
wiki-lint-runner: Wrapper to run the wiki-lint.py script with consistent options.
"""

import subprocess, sys, os
from pathlib import Path

WIKI_PATH = os.environ.get('WIKI_PATH', os.path.expanduser('~/wiki'))

script_path = Path(__file__).parent / 'scripts' / 'wiki-lint.py'
if not script_path.exists():
    print(f"ERROR: wiki-lint.py not found at {script_path}", file=sys.stderr)
    sys.exit(1)

result = subprocess.run([sys.executable, str(script_path), WIKI_PATH], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)