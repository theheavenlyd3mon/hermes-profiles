import sys
from pathlib import Path

# Ensure repo root is importable so `from agent import ...` (and similar
# root-relative imports) resolve under ANY pytest invocation:
#   pytest .        (rootdir = repo root)
#   pytest tests/   (rootdir = tests/  -> would otherwise break imports)
#   pytest -q       (bare)
sys.path.insert(0, str(Path(__file__).parent))
