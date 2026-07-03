# Fabric Interaction from Cron Context

How to interact with the Icarus fabric system when running as a cron job or in contexts where Hermes plugin tools aren't directly callable.

## Problem

The Icarus plugin provides tools like `fabric_report`, `fabric_curate`, `fabric_search`, and `fabric_recall`. These are registered as Hermes plugin tools (see `plugin.yaml`), but:

- `hermes tools` doesn't list them
- They're not callable via CLI (`hermes icarus` doesn't exist)
- They're only available during interactive LLM sessions where the plugin is loaded

## Solution: Direct Python Import

The icarus state module can be imported directly in `execute_code`:

```python
import sys
import os

# Add the plugins directory to the path
plugins_dir = "/Users/noctis/.hermes/profiles/senna/plugins"
sys.path.insert(0, plugins_dir)

# Set the FABRIC_DIR environment variable
os.environ["FABRIC_DIR"] = "/Users/noctis/Hermes Vault/Hermes/icarus"

from icarus import state

# Now use state functions directly:
report = state.build_weekly_report()          # equivalent to fabric_report
results = state.search_entries("query")       # equivalent to fabric_search
results = state.recall("query", max_results=5)  # equivalent to fabric_recall
```

## Available State Functions

| Function | Equivalent Tool | Notes |
|----------|----------------|-------|
| `state.build_weekly_report()` | `fabric_report` | Returns corpus health stats |
| `state.search_entries(query)` | `fabric_search` | Searches by text match |
| `state.recall(query, max_results=N)` | `fabric_recall` | Semantic recall with embeddings |
| `state.read_pending()` | `fabric_pending` | Open tasks and reviews |
| `state.curate_entry(entry_id, training_value)` | `fabric_curate` | Set training_value |
| `state.write_entry(...)` | `fabric_write` | Create new entry |
| `state.build_brief()` | `fabric_brief` | Build morning brief |

## Pitfalls

- **search_entries doesn't support field:value syntax.** Queries like `training_value:high` or `status:completed` return 0 results. Use `recall()` for semantic search, or parse frontmatter directly from the filesystem.
- **Frontmatter values are quoted.** Fabric entry frontmatter uses `training_value: "high"` (with quotes), not `training_value: high`. Strip quotes when parsing: `value.strip().strip('"\'')`.
- **FABRIC_DIR must be set before import.** The state module reads `FABRIC_DIR` at import time. Set the env var before importing.
- **Agent name detection.** `state.AGENT_NAME` is derived from `HERMES_AGENT_NAME` env var or from `HERMES_HOME` path. In cron context, set `HERMES_AGENT_NAME` explicitly if needed.

## Filesystem Fallback

When the state module isn't available or import fails, read fabric entries directly:

```python
from pathlib import Path

fabric_dir = Path("/Users/noctis/Hermes Vault/Hermes/icarus")

for md_file in fabric_dir.glob("*.md"):
    content = md_file.read_text(encoding='utf-8')
    if content.startswith('---'):
        frontmatter_end = content.find('---', 3)
        frontmatter = content[3:frontmatter_end]
        # Parse frontmatter lines...
```

## Typical Cron Workflow

1. Call `state.build_weekly_report()` for corpus health
2. Parse frontmatter from filesystem for detailed filtering
3. Cross-reference against wiki `index.md` for promotion candidates
4. Create wiki pages for high-value entries (if any)
5. Log results to Notion databases
