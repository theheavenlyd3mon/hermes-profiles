# Session API Plugin — Implementation Reference

> Plugin at `~/.hermes/plugins/session-api/` that serves Hermes session conversation data via HTTP to the HermesMirror hermes-chat module.

## Why a separate plugin (not extending kanban-api)

- Clean separation: kanban = task board, session = conversation transcript
- Independent lifecycle — can restart one without the other
- Different data source (LCM SQLite vs kanban DB)
- Same port allocation pattern: 8643 (kanban), 8644 (session)

## File structure

```
~/.hermes/plugins/session-api/
├── plugin.yaml
└── __init__.py
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | `{"status": "ok", "service": "session-api"}` |
| GET | `/api/session/messages` | Recent messages from active session |
| GET | `/api/session/messages?session_id=X` | Messages from specific session |
| GET | `/api/session/messages?limit=N` | Limit to N messages (default: 50, max: 200) |

## Response shape

```json
{
  "session_id": "20260604_093356_fbe166",
  "messages": [
    {"store_id": 42, "role": "user", "content": "...", "timestamp": 1780583673.2},
    {"store_id": 43, "role": "assistant", "content": "...", "timestamp": 1780583674.1}
  ],
  "updated_at": 1780583700
}
```

## LCM Database Access

Reads directly from SQLite — no Hermes CLI dependency.

```python
import sqlite3, os

def _find_lcm_db() -> str:
    hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    profile_db = os.path.join(hermes_home, "profiles", "senna", "lcm.db")
    if os.path.isfile(profile_db):
        return profile_db
    # fallback: search all profiles for newest lcm.db
    ...
```

### LCM messages table schema

```sql
CREATE TABLE messages (
    store_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    source TEXT DEFAULT '',
    role TEXT NOT NULL,          -- user, assistant, tool, system
    content TEXT,
    tool_call_id TEXT,
    tool_calls TEXT,
    tool_name TEXT,
    timestamp REAL NOT NULL,
    token_estimate INTEGER DEFAULT 0,
    pinned INTEGER DEFAULT 0
);
CREATE INDEX idx_msg_session ON messages(session_id, store_id);
```

### Query pattern

```sql
SELECT store_id, role, content, timestamp
FROM messages
WHERE session_id = ?
  AND role IN ('user', 'assistant')   -- filter out tool/system
  AND content IS NOT NULL
  AND content != ''
ORDER BY store_id ASC
LIMIT ?
```

### Auto-discover active session

```sql
SELECT session_id FROM messages ORDER BY store_id DESC LIMIT 1
```

## Pitfalls

- **LCM DB path varies by profile** — `~/.hermes/profiles/<profile>/lcm.db`. The active profile is `senna` but could change.
- **Content size cap** — truncate `content` to 4000 chars before returning to avoid huge JSON payloads.
- **SQLite concurrency** — lcm.db is written by the LCM engine during conversations. Use `timeout=5` on connect.
- **Role filtering** — only return `user` and `assistant` roles. Tool calls and system messages are noise for the mirror display.
- **Session switching** — when the user starts a new session, the auto-discover query returns the new session_id. The mirror module detects the change and re-renders.

## Verification

```bash
curl http://127.0.0.1:8644/health
# {"status": "ok", "service": "session-api"}

curl http://127.0.0.1:8644/api/session/messages?limit=5
# {"session_id": "...", "messages": [...], "updated_at": ...}
```
