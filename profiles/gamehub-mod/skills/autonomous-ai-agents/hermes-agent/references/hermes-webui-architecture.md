# Hermes WebUI (nesquena) — Architecture & Session Model

## Overview

[nesquena/hermes-webui](https://github.com/nesquena/hermes-webui) is a lightweight, dark-themed web interface for Hermes Agent. Vanilla JS + Python stdlib — no build step, no framework. Talks to the gateway's OpenAI-compatible HTTP API (port 8642).

## How It Runs

The server is a single Python process using `ThreadingHTTPServer` — no framework, no WSGI:

```
~/hermes-webui/server.py
    → api/routes.py (handles all GET/POST routing)
    → imports session management from api/session_ops.py
    → state stored in SESSION_DIR (default: ~/.hermes/webui-mvp/sessions/)
```

Port defaults to **8787**, bound to `127.0.0.1` by default (or `0.0.0.0` if `HERMES_WEBUI_HOST` is set that way).

## Session Tracking: The #1 Confusion

The WebUI has **two separate session systems**, and the naming overlap is what causes confusion.

### 1. Hermes Agent Sessions (the "real" sessions)

Tracked in the Hermes agent's SQLite store (`~/.hermes/sessions/state.db`). These are the sessions you see in `hermes sessions list` — they span all interfaces (CLI, Telegram, API, WebUI). A single conversation can start on Telegram and its messages become part of one of these sessions.

### 2. WebUI In-Memory Sessions (the health count)

Tracked in the WebUI server's Python process as `SESSIONS` — an `OrderedDict` in `config.py`:

```python
SESSIONS_MAX = 100
SESSIONS: collections.OrderedDict = collections.OrderedDict()
```

**What counts as a "session" here:**
- Every new conversation created in the WebUI
- Every existing conversation loaded into the WebUI's memory (clicked in the sidebar)
- Sessions that were restored from disk (`STATE_DIR/sessions/`)

**What the health endpoint reports:**
```json
{"status": "ok", "sessions": 7, "active_streams": 0, "uptime_seconds": 81204.7}
```
`sessions` = `len(SESSIONS)` — number of conversation objects currently in this OrderedDict in memory.

**Key differences from Hermes agent sessions:**

| | WebUI Sessions (in-memory) | Hermes Agent Sessions (state.db) |
|---|---|---|
| Storage | RAM + JSON files per session | SQLite database |
| Scope | Only conversations opened in the WebUI | All conversations across all interfaces |
| Persistence | Lost on WebUI server restart (rebuilt as conversations are opened) | Survives restarts |
| Max | 100 (LRU eviction — oldest evicted when full) | Unlimited (configurable) |
| `hermes sessions list` | Not visible here | Visible here |

## Common Questions

### "Why does the health endpoint say 3/7/15 sessions but I only started 2 chats?"

Every time you load a conversation in the WebUI sidebar, the server creates a `Session` object in the SESSIONS dict. Page refreshes, tests, and the onboarding flow can also create lightweight sessions. These are counted even if they have no messages yet — though sessions younger than 60 seconds with no title are hidden from the sidebar.

### "Why doesn't the WebUI show my Telegram sessions?"

The WebUI has a `show_cli_sessions` setting (config option, default: false). When enabled, it merges Hermes agent sessions from `state.db` into the sidebar alongside WebUI-local sessions. When disabled (default), the WebUI only shows sessions that were started within the WebUI itself.

### "Can I see my CLI/Telegram conversations in the WebUI?"

Yes — if `show_cli_sessions` is toggled on in the WebUI settings, it reads the agent's SQLite store and deduplicates overlapping sessions before displaying.

## Startup & Connection Flow

```
WebUI starts (port 8787)
  → runs its own ThreadingHTTPServer
  → connects to gateway API at http://127.0.0.1:8642
  → when user sends a message, WebUI sends POST to gateway's /v1/chat/completions
  → gateway spawns a conversation loop in the Hermes agent process
  → streaming responses back to WebUI via SSE or chunked encoding
```

The WebUI does NOT start the gateway — it expects the gateway to already be running with `API_SERVER_ENABLED=true`. Verify:
```bash
hermes gateway status            # gateway must be running
grep API_SERVER_ENABLED ~/.hermes/profiles/senna/.env  # must be true
curl http://127.0.0.1:8642/health  # gateway health check
```

## Checking WebUI Status

```bash
# Health endpoint
curl http://127.0.0.1:8787/health

# Process check
ps aux | grep hermes-webui/server.py | grep -v grep

# Port check
lsof -nP -iTCP:8787 -sTCP:LISTEN

# Logs
tail -50 ~/.hermes/webui.log
```

## Key Paths

| Thing | Path |
|-------|------|
| Server entry point | `~/hermes-webui/server.py` |
| API routes | `~/hermes-webui/api/routes.py` |
| Session ops | `~/hermes-webui/api/session_ops.py` |
| Config (ports, limits) | `~/hermes-webui/api/config.py` |
| State directory (default) | `~/.hermes/webui-mvp/` |
| WebUI log | `~/.hermes/webui.log` |
