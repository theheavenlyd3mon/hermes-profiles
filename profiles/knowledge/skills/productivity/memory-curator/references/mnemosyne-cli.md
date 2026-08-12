# Mnemosyne CLI Reference

The `hermes mnemosyne` command manages the persistent memory layer — working memories (always-injected context) and episodic summaries (consolidated session knowledge).

## Commands

| Command | Purpose |
|---------|---------|
| `hermes mnemosyne stats` | Show memory counts (working + episodic) |
| `hermes mnemosyne sleep [--all-sessions] [--dry-run]` | Consolidate old working memories into episodic summaries |
| `hermes mnemosyne inspect` | Search/browse memories |
| `hermes mnemosyne doctor` | Run diagnostics, auto-fix missing dependencies |
| `hermes mnemosyne export` | Export all memories to JSON |
| `hermes mnemosyne import` | Import memories from JSON |
| `hermes mnemosyne clear` | Clear scratchpad |
| `hermes mnemosyne version` | Show Mnemosyne version |

## `stats` Output

```json
{
  "working": {"total": 20, "last": "2026-05-18T15:40:51.653944"},
  "episodic": {"total": 2, "last": "2026-05-15T08:58:12.065708", "vectors": 0, "vec_type": "none"}
}
```

- **working**: Always-injected memories (preferences, env facts, conventions). Never consolidated.
- **episodic**: Consolidated session summaries. Created by `sleep`.

## `sleep --all-sessions` Output

```json
{
  "status": "consolidated",
  "sessions_scanned": 6,
  "sessions_consolidated": 6,
  "items_consolidated": 15,
  "summaries_created": 7,
  "llm_used": 0,
  "errors": 0,
  "error_details": [],
  "session_results": [
    {
      "status": "consolidated",
      "items_consolidated": 3,
      "summaries_created": 2,
      "llm_used": 0,
      "method": "aaak",
      "consolidated_ids": ["2bc080df1ea38449", "..."],
      "degradation": {"status": "degraded", "tier1_to_tier2": 0, "tier2_to_tier3": 0},
      "session_id": "hermes_20260515_151704_4f9dfa",
      "eligible": 3
    }
  ],
  "degradation": {"status": "degraded", "tier1_to_tier2": 0, "tier2_to_tier3": 0}
}
```

Key fields:
- **method**: `"aaak"` = no LLM call needed (rule-based consolidation). May use LLM for complex sessions.
- **eligible**: Items eligible for consolidation from that session.
- **degradation**: Tracks tier loss (tier1→tier2→tier3). Status "degraded" means some info was compressed.

## Cron Integration Pattern

For periodic consolidation (e.g., nightly cron):

```bash
# Get before stats (fast, always completes)
mnemosyne stats

# Run consolidation IN BACKGROUND — can take 5+ minutes on large DBs
# Use terminal(command='mnemosyne sleep', background=true, notify_on_complete=true)

# Get after stats once background job completes
mnemosyne stats

# Log delta to Notion Agent Logbook
```

**Important:** Do NOT run `mnemosyne sleep` synchronously in cron jobs. It can timeout at 300s on databases with 2000+ working memories. Always background it.

## Updating Mnemosyne

Mnemosyne is a pip package (`mnemosyne-memory`) installed in the Hermes venv. The Hermes plugin integration (`hermes_memory_provider`) ships with the package.

```bash
# 1. Upgrade the package
~/.hermes/hermes-agent/venv/bin/pip install --upgrade mnemosyne-memory

# 2. Run the Hermes installer to verify/fix symlinks and config
~/.hermes/hermes-agent/venv/bin/python -m mnemosyne.install
```

The installer checks:
- Plugin symlink in `~/.hermes/plugins/mnemosyne` → `hermes_memory_provider` in venv
- `memory.provider = mnemosyne` in Hermes config
- Provider `is_available` status

After updating, restart the gateway: `hermes gateway start`

**Note:** The old system-Python 3.9 install (at `~/Library/Python/3.9/`) is separate. The Hermes venv uses Python 3.11. Always install/upgrade in the Hermes venv, not system Python.

## Pitfalls

- **LCM ≠ Mnemosyne.** LCM compresses session context (within a conversation). Mnemosyne consolidates across sessions (persistent memory). They are separate systems.
- **Working memories are never consolidated.** Only episodic/cross-session items get consolidated by `sleep`. Working memories (preferences, env facts) persist indefinitely.
- **`--dry-run` first.** Before a large consolidation, use `--dry-run` to preview what would change.
- **llm_used may be 0.** Most consolidations use the "aaak" rule-based method. LLM is only used for complex multi-session synthesis.
- **`sleep` can timeout on large databases.** With 2000+ working memories, `mnemosyne sleep` can exceed 5 minutes. For cron jobs, always run it in the background: `terminal(command='mnemosyne sleep', background=true, notify_on_complete=true)`. Grab `mnemosyne stats` first (fast) to report the before-state, then let sleep finish asynchronously. The standalone `mnemosyne` CLI works directly — no need for the `hermes mnemosyne` prefix.
- **`stats` output is plain text, not JSON.** The CLI prints a formatted table with `Working memory`, `Episodic memory`, `Knowledge triples`, `Banks`, and `DB path` — not the JSON structure shown in the `hermes mnemosyne stats` docs. Parse accordingly.
