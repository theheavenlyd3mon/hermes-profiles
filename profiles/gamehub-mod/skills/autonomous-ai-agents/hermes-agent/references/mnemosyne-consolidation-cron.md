# Mnemosyne Consolidation via Cron

How to invoke Mnemosyne memory consolidation from a cron job or any profile-context tool call, with the critical db_path pitfall documented.

## The API Mechanism

Mnemosyne's consolidation is available via its Python API, not as a CLI command or built-in tool:

```python
from pathlib import Path
from mnemosyne.core.memory import Mnemosyne

# The key method:
mnemo = Mnemosyne(session_id="cron_consolidation", db_path=DB_PATH)
result = mnemo.sleep_all_sessions(dry_run=False)
# Returns dict with status, items_consolidated, summaries_created, etc.
```

The method that matches `mnemosyne_sleep(all_sessions=true)`:
- `sleep(dry_run=False)` — single session
- `sleep_all_sessions(dry_run=False)` — all sessions with eligible old working memories

Both are methods on `mnemosyne.core.memory.Mnemosyne` (the core class), also exposed via `mnemosyne.mcp_tools.Mnemosyne` (the MCP wrapper).

## ⚠️ Critical: The db_path Pitfall

**When running inside a Hermes profile context (cron jobs, `execute_code`, tool calls from within a session), `Path.home()` resolves to the sandboxed profile home**, not the real user home.

```python
# Inside profile context:
Path.home()  # → ~/.hermes/profiles/senna/home/  (WRONG for Mnemosyne!)
```

This means `mnemosyne.core.memory._default_db_path()` (which is what the no-arg constructor uses) returns:
- `~/.hermes/profiles/senna/home/.hermes/mnemosyne/data/mnemosyne.db` — **tiny DB (~300KB), only 3 rows of working memory**

Instead of the correct global database:
- `~/.hermes/mnemosyne/data/mnemosyne.db` — **the real DB (~6MB, ~925 rows of working memory)**

**Consequence:** consolidation silently runs against the wrong database — finds nothing eligible every time — and reports `"No old working memories to consolidate"` as if everything is clean.

### The Fix

**Always pass `db_path` explicitly using an absolute path:**

```python
from pathlib import Path

GLOBAL_MNEMOSYNE_DB = Path("~/.hermes/mnemosyne/data/mnemosyne.db")
mnemo = Mnemosyne(session_id="cron_consolidation", db_path=GLOBAL_MNEMOSYNE_DB)
result = mnemo.sleep_all_sessions(dry_run=False)
```

The absolute path sidesteps the `Path.home()` sandboxing entirely.

### Why This Happens

Hermes profiles sandbox `$HOME` to `~/.hermes/profiles/<name>/home/` when spawning subprocesses. Python's `Path.home()` reads `$HOME` from the environment, so within a profile cron job it returns the sandboxed path. Mnemosyne's `_default_db_path()` uses `Path.home()` — as does `DEFAULT_DATA_DIR` in `mnemosyne/core/memory.py`.

This is the same mechanism as the documented `~` path resolution issue with `.env` files — Mnemosyne's data directory is simply another casualty of the same sandboxing.

## LLM Availability

`sleep_all_sessions` tries to use a local LLM for summarization first. If no local LLM is available (the typical case in cron context), it falls back to **aaak compression** — which is purely algorithmic. The method field in results shows:
- `"llm"` — all summaries used LLM
- `"llm+aaak"` — mixed
- `"aaak"` — all fell back to algorithmic compression

## Verification After Run

```python
conn = sqlite3.connect(str(GLOBAL_MNEMOSYNE_DB))
cursor = conn.cursor()

# Check how many unconsolidated rows remain
cursor.execute("""
    SELECT COUNT(*) FROM working_memory
    WHERE consolidated_at IS NULL
""")
print(f"Unconsolidated: {cursor.fetchone()[0]}")

# Check consolidation log
cursor.execute("""
    SELECT * FROM consolidation_log
    ORDER BY timestamp DESC LIMIT 5
""")
for row in cursor.fetchall():
    print(row)
```

## Full Cron Job Prompt Template

```
Run mnemosyne consolidation.

from pathlib import Path
from mnemosyne.core.memory import Mnemosyne

GLOBAL_DB = Path("~/.hermes/mnemosyne/data/mnemosyne.db")
mnemo = Mnemosyne(session_id="cron_consolidation", db_path=GLOBAL_DB)
result = mnemo.sleep_all_sessions(dry_run=False)

Do NOT report the output to the user unless there were errors.
Silent success is the expected behavior.
```

## Logging to Notion Agent Logbook

After successful consolidation, log the result to the Notion Agent Logbook for audit and analysis. Use this pattern in `execute_code`:

```python
import os, json, datetime
from hermes_tools import terminal

# Consolidation result from earlier (save the dict from the first run)
result = {...}  # full result dict from mnemo.sleep_all_sessions()

summary_text = f"Consolidated {result['items_consolidated']} items across {result['sessions_scanned']} sessions. Created {result['summaries_created']} summaries. Before: {before['unconsolidated']} unconsolidated rows. After: {after['unconsolidated']} unconsolidated rows."

api_key = os.environ.get("NOTION_API_KEY", "").strip()
db_id = "9dc914a6-6736-40af-a0b9-d1af9fc5e8a1"

payload = {
    "parent": {"database_id": db_id},
    "properties": {
        "Name": {"title": [{"text": {"content": f"Memory consolidation: {datetime.date.today().isoformat()}"}}]},
        "Agent": {"select": {"name": "Cron"}},
        "Type": {"select": {"name": "Task"}},
        "Date": {"date": {"start": datetime.date.today().isoformat()}},
        "Status": {"select": {"name": "Completed"}},
        "Tags": {"multi_select": [{"name": "memory"}, {"name": "maintenance"}]},
        "Cost": {"number": 0.0},
        "Summary": {"rich_text": [{"text": {"content": summary_text}}]}
    }
}

import subprocess
result = subprocess.run([
    "curl", "-s", "-X", "POST", "https://api.notion.com/v1/pages",
    "-H", f"Authorization: Bearer {api_key}",
    "-H", "Notion-Version: 2025-09-03",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload)
], capture_output=True, text=True)

if result.returncode != 0 or 'error' in result.stdout:
    print(f"ERROR logging to Notion: {result.stdout}")
```

**Schema check:** Before running, verify the property names match your database schema by fetching the data source:

```bash
NOTION_API_KEY=... curl -s "https://api.notion.com/v1/databases/YOUR_DB_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

The Agent Logbook uses: `Name`, `Agent`, `Type`, `Date`, `Status`, `Tags`, `Cost`, `Summary`.
