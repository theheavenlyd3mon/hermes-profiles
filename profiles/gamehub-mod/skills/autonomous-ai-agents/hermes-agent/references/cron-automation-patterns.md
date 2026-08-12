# Cron Automation Patterns

Session-derived patterns from the 2026-05-11 cron setup session on macOS (Senna profile, gateway running via launchd).

## Session Context

User profile: not originally a developer. Prefers plain-language explanations and analogies (gateway as phone line, terminal as shop counter). Strong automation preference: "minimise the extra user input". All cron jobs run through the Senna profile gateway.

## The 8-Job Roster After This Session

| Job | Schedule | Deliver | Purpose |
|-----|----------|---------|---------|
| overnight-wiki-research | 2am daily | local | Research stale wiki page, append updates |
| memory-consolidation | 3am daily | local | Compress old sessions into episodic summaries |
| wiki-health-check | 4am daily | local | Lint wiki for orphans, broken links, staleness |
| session-prune | 5am daily | local | Delete sessions older than 90 days |
| dojo-nightly | 6am daily | origin | Existing dojo count |
| morning-briefing | 7am daily | origin | Summarize overnight results to Telegram |
| weekly-vault-summary | 8am Sunday | origin | New/modified notes, orphans, stale pages |
| disk-audit | 1st month 6am | local | Track disk usage trends |

## Cron Prompt Patterns

### Silent maintenance (deliver: local)
```
Prompt: "Run XYZ. Do NOT report the output to the user unless there were errors. Silent success is the expected behavior."
```
Used for: memory-consolidation, session-prune, wiki-health-check (doesn't report unless errors)

**Memory consolidation details:** See `references/mnemosyne-consolidation-cron.md` for the exact Python API invocation (`Mnemosyne(db_path=...).sleep_all_sessions()`), the critical `Path.home()` sandboxing pitfall that silently targets the wrong database inside a profile cron context, and the prompt template.

### Research + update (deliver: local, but modifies vault)
```
Prompt: "Research topic X. Read current content. Do web search. If new findings exist, append '## Updates' section. Brief summary of what was done and whether it was updated."
```
Used for: overnight-wiki-research

### User-facing reports (deliver: origin)
```
Prompt: "Deliver a [briefing/summary] to the user. Check: [specific things to look up]. Keep it concise — [N] bullet points. No technical jargon. Frame it naturally."
```
Used for: morning-briefing, weekly-vault-summary

## Chaining Pattern

The overnight pipeline chains naturally:
- 2am wiki research updates knowledge base (no report)
- 3-5am maintenance runs silently
- 7am briefing summarizes overnight results including what the wiki research found
- Briefing uses session_search and cron job awareness rather than explicit context_from chaining

## Hybrid Script + Agent Pattern (Token-Efficient Monitoring)

The most token-efficient approach for monitoring/alerting: a **script** collects data (0 tokens), and an **agent** only fires when there's signal.

### Architecture

```
TIER 1 — Script (no_agent=true, 0 tokens)
  Runs frequently (every 30m-1h)
  Fetches data, compares thresholds, checks for notable events
  If NOTHING notable: exits silently (empty stdout → cron sends nothing)
  If SOMETHING notable: prints data dump to stdout

TIER 2 — Agent (context_from chains from Tier 1)
  Runs on same schedule as Tier 1
  Reads the script's output via context_from
  If context is empty → responds [SILENT] (minimal tokens)
  If context has data → does deeper analysis, writes trade ideas, etc.
```

### Implementation

**Step 1: Create the script** in `~/.hermes/<domain>/scripts/`:
```python
#!/usr/bin/env python3
"""Monitor X, alert only on notable events. Empty stdout = silent."""
import os, sys, json
from pathlib import Path

BASE_DIR = Path(os.environ.get("HOME", "~") + "/.hermes/<domain>")
STATE = BASE_DIR / "state.json"

def run():
    state = load_json(STATE, {})
    alerts = []
    # ... fetch data, compare thresholds, build alerts ...
    if alerts:
        print("ALERT DATA:\n" + "\n".join(alerts))
    # else: silent (empty stdout)

if __name__ == "__main__":
    run()
```

**Step 2: Symlink into profile scripts dir** (cron resolves scripts from `~/.hermes/profiles/<profile>/scripts/`):
```bash
ln -sf /path/to/actual/script.py ~/.hermes/profiles/senna/scripts/script-name.py
```

**Step 3: Create the script cron job:**
```python
cronjob(action="create", name="<domain>-monitor", schedule="every 1h",
        script="script-name.py", no_agent=True, deliver="local",
        profile="<domain>")
```

**Step 4: Create the agent cron job that chains from it:**
```python
cronjob(action="create", name="<domain>-analyst", schedule="every 1h",
        context_from=["<script-job-id>"],
        prompt="""If context is empty, respond [SILENT].
        If notable events exist, analyze them...""",
        skills=["<relevant-skill>"], profile="<domain>",
        deliver="discord:<channel-id>")
```

### Real-World Example: Oracle Market Monitor

- **Script:** `~/.hermes/oracle/scripts/market-monitor.py` — fetches stocks (Yahoo Finance), crypto (CoinGecko), Fear & Greed (Alternative.me). Compares against thresholds in `watchlist.json`. Outputs only on notable moves.
- **Agent:** `oracle-alert-analyst` (profile: oracle, skill: oracle-analyst) — reads script output, searches for news, produces trade ideas with entry/target/stop.
- **State:** `~/.hermes/oracle/state.json` (current prices, overwritten), `daily/YYYY-MM-DD.json` (snapshots), `alerts.log` (append-only).

### Why This Works

| Component | Tokens | Frequency |
|-----------|--------|-----------|
| Script (Tier 1) | 0 | every 1h |
| Agent silent (Tier 2, no signal) | ~500 (system prompt + [SILENT]) | every 1h |
| Agent alert (Tier 2, signal found) | ~3,000-8,000 | only when notable |

vs. full agent loop every time: ~3,000-8,000 tokens per tick regardless.

## ⚠️ General Pitfall: `Path.home()` in Cron Scripts

**When running inside a Hermes profile context (cron jobs, `execute_code`, tool calls), `Path.home()` resolves to the sandboxed profile home**, not the real user home.

```python
# Inside profile context:
Path.home()  # → ~/.hermes/profiles/senna/home/  (WRONG!)
os.environ.get("HOME")  # → ~/.hermes/profiles/senna/home/  (ALSO WRONG in some contexts)
```

**This affects ANY Python script that uses `Path.home()` or `os.path.expanduser("~")` to locate files outside the profile sandbox.** Known casualties:
- Mnemosyne `db_path` (see `references/mnemosyne-consolidation-cron.md`)
- Market monitor scripts referencing `~/.hermes/oracle/`
- Any script reading/writing to shared directories

**The fix — always use an explicit absolute path or environment variable:**

```python
# Option 1: Hardcode the real home (most reliable)
BASE_DIR = Path("~/.hermes/oracle")

# Option 2: Use ORACLE_DIR env var with fallback
BASE_DIR = Path(os.environ.get("ORACLE_DIR", "~/.hermes/oracle"))

# Option 3: Use os.environ.get("HOME") — works for terminal() calls
# but STILL returns profile home inside some cron contexts
BASE_DIR = Path(os.environ.get("HOME", "~") + "/.hermes/oracle")
```

**Rule of thumb:** If your script needs to access files outside the profile sandbox, never use `Path.home()`, `os.path.expanduser("~")`, or `Path("~")`. Use absolute paths.

## Cron `script:` Resolution Path

Cron jobs with `script:` resolve the script path relative to **`~/.hermes/profiles/<profile>/scripts/`** (where `<profile>` is the job's profile, or `senna` if no profile set).

If your actual script lives elsewhere (e.g., `~/.hermes/oracle/scripts/`), create a symlink:
```bash
ln -sf ~/.hermes/oracle/scripts/market-monitor.py \
       ~/.hermes/profiles/senna/scripts/market-monitor.py
```

The `script:` value in the cron job should be just the filename (`market-monitor.py`), not a full path.

## Key Decisions Made
- All cron jobs created via the cronjob tool (not terminal commands)
- Schedules chosen to avoid overlap and provide a logical order
- Maintenance jobs set to silent; user-facing jobs set to deliver: origin
- Plain-language prompts that tell the agent what to check and how to respond
- Hybrid script+agent pattern for token-efficient monitoring (script = 0 tokens, agent only on signal)
