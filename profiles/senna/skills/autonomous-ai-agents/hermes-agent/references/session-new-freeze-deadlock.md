# `/new` Freeze — Session-Transition Deadlock (2026-05-11)

See also: `/ready` CLI/TUI command — built-in pre-flight check before issuing `/new`. Checks DB lock, background processes, and gateway pulse. Type `/ready` from any session prompt.

## `/ready` Command — Implementation & Dispatch

**Registration:** `CommandDef("ready", ...)` in `hermes_cli/commands.py` (line ~195).  
**Handler:** `HermesCLI._check_ready()` in `cli.py` (line ~6926).  
**Bash equivalent:** `scripts/check-agent-idle.sh` — portable, no gateway dependency.

**CLI path:** prompt_toolkit intercepts `/ready` → `process_command()` dispatches `canonical == "ready"` → `self._check_ready()` → prints directly to stdout.

**TUI path (fallback):** The command was originally `cli_only=True` (hidden from TUI autocomplete/help), but still functional via the `slash.exec` RPC fallback:

```
TUI input → looksLikeSlashCommand("/ready")
  → findSlashCommand("ready") → MISS (not in TUI frontend registry)
  → gw.request('slash.exec', {command: "ready"})
    → tui_gateway/server.py: _SlashWorker.run("/ready")
      → tui_gateway/slash_worker.py: _run()
        → contextlib.redirect_stdout(buf)
        → cli.process_command("/ready")
          → _check_ready() → prints to buf
        → return buf.getvalue()  (JSON: {ok, output})
    → frontend shows r.output
```

**Pitfall:** If the slash worker subprocess (one per TUI session) is dead or timed out, `/ready` silently produces no output. Restart the gateway to recreate it.

**Verification (2026-05-11):** `check-agent-idle.sh` confirmed accurate busy-state detection — it correctly flagged 10+ Hermes processes and large WAL files (state.db-wal: 5.6MB, lcm.db-wal: 2.0MB) when the system was genuinely busy.

## Overview

Two distinct scenarios cause `/new` to freeze. **Scenario A** (mid-turn contention) was discovered first; **Scenario B** (idle-state post-turn housekeeping) was confirmed later. Both produce the same symptom — a new session with 0 messages and an unresponsive TUI — but have different root causes and require different workarounds.

---

## Scenario A: Mid-Turn Contention (Agent Still Processing)

### Context
- Profile: `senna` (default)
- Model: `deepseek-v4-flash` via `deepseek` provider
- Session: 194 messages, 78 API calls into a Hermes Update Review
- Running with `display.streaming: false` (non-streaming mode — longer turns)

### Sequence of Events

1. Long-running session (`20260511_071541_5ea49f`) is processing turn #73–78
2. User types `/new` at 07:51:27
3. CLI/TUI creates session `20260511_075127_f25a0f` in the session DB
4. `new_session()` calls `commit_memory_session()` on the old session's history
5. Old session's agent thread is still writing to `state.db` (65MB SQLite)
6. `end_session()` / `create_session()` blocks on DB write lock
7. The new session has 0 messages — its agent was never initialized because `new_session()` never returned
8. Old session continues running until 07:51:57 (finishes naturally)
9. User kills the TUI and restarts at 07:54

### Evidence

```bash
# Session_search showing the frozen session
session_id=20260511_075127_f25a0f  message_count=0  source=cli

# Agent log showing old session still running AFTER /new was typed
2026-05-11 07:51:46 ... tool mnemosyne_remember completed
2026-05-11 07:51:49 ... API call #77
2026-05-11 07:51:57 ... API call #78
2026-05-11 07:51:57 ... Turn ended: reason=text_response(finish_reason=stop)

# No entries at all for the frozen session in agent.log
grep 075127_f25a0f agent.log → (empty)
```

### System State at Time of Freeze

- `state.db`: 65.7 MB (SQLite — session history store)
- `lcm.db` + `lcm.db-wal`: 442 KB (context engine)
- Gateway process (PID 10925): running since Friday, not involved
- Active TUI process (PID 90632): started at 07:54 (post-crash restart)

### Workaround Effectiveness

| Workaround | Works? | Notes |
|------------|--------|-------|
| `/ready` pre-flight check | Yes | Type `/ready` first — if it reports issues, wait and retry |
| Ctrl-C then `/new` | Yes | Gives old thread time to release DB lock |
| `/clear` in TUI | Partial | Skips `new_session()` but still goes through gateway RPC |
| Wait for turn to finish | Yes | Most reliable — no concurrent DB access |

---

## Scenario B: Idle-State Post-Turn Housekeeping (Agent Appears Idle)

Confirmed 2026-05-11: the agent had finished responding and was waiting at the prompt, but `/new` still froze the TUI. No Ctrl-C intercept was needed — the terminal became unresponsive immediately after approving the `/new` confirmation prompt.

### System State at Time of Freeze

- **context.engine:** `lcm` — asynchronous background compression after each turn
- **memory.provider:** `mnemosyne` — post-turn memory commits writing to state.db
- **terminal.persistent_shell:** `true` — keeps a persistent shell session with its own DB handle
- **gateway PID 10925:** running since Friday, stable
- **Active TUI PID 91800:** current session, waiting at prompt
- **Hermes PID 11156 (port 9119):** secondary Hermes process (workspace/API)

### Probable Root Cause

Post-turn housekeeping tasks (LCM compression, Mnemosyne memory commit) finish asynchronously after the agent response is delivered. These write to `state.db` and `lcm.db`. If `/new` is issued during the brief window (~200ms–2s post-response) where these writes are still flushing, `new_session()`'s call to `commit_memory_session()` / `end_session()` / `create_session()` encounters a SQLite lock on `state.db` and blocks.

Unlike Scenario A (where the old agent thread is actively running turns), Scenario B is purely a timing collision with post-processing — no visible activity to the user, no spinner, no output.

### Config Context (from senna profile)

```yaml
context:
  engine: lcm                           # background compression
memory:
  provider: mnemosyne                   # post-turn memory writes
compression:
  enabled: true
  threshold: 0.5
  target_ratio: 0.2
terminal:
  persistent_shell: true                # additional DB handle
```

### Workaround Effectiveness (Idle State)

| Workaround | Works? | Notes |
|------------|--------|-------|
| `/clear` instead of `/new` | **Best** | Skips `commit_memory_session()` entirely — avoids DB lock collision |
| Wait 3-5 seconds after last output | Yes | Housekeeping typically finishes within 2s |
| Ctrl-C then `/new` | Yes | Interrupt forces DB handle release |
| Run `check-agent-idle.sh` first | Yes | Script-based pre-flight check (see scripts/) |
| Force-kill and restart | Yes | Last resort |

**Recommended protocol:** Wait 3 seconds after the agent finishes speaking, then use `/clear` in TUI instead of `/new`. Or run the ready-check script before issuing `/new`.

---

## Shared Code Analysis

**CLI path (`cli.py` ~5394):**
```python
def new_session(self, silent=False, title=None):
    if self.agent and self.conversation_history:
        self.agent.commit_memory_session(self.conversation_history)
        self._notify_session_boundary("on_session_finalize")
    ...
    self._session_db.end_session(old_session_id, "new_session")
    ...
    self._session_db.create_session(...)
```

**TUI path (`useSessionLifecycle.ts` ~125):**
```typescript
const newSession = async (msg?, title?) => {
    await closeSession(getUiState().sid)   // RPC: session.close
    const r = await rpc('session.create', ...)  // RPC: session.create
    resetSession()
}
```

### Related Log Evidence

From `errors.log` (May 8):
```
WARNING cli: Agent thread still alive after interrupt (thread 123145431683072). 
Daemon thread will be cleaned up on exit.
```

This confirms the agent thread doesn't always die cleanly on interrupt, leaving DB handles open.
