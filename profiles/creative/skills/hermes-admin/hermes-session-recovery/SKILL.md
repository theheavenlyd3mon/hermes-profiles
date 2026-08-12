---
name: hermes-session-recovery
description: "Use when session_search misses a known past session."
---

# Hermes Session & State Recovery

## Trigger
- `session_search` returns nothing, or the wrong sessions, for something you KNOW
  happened (a recent session, a just-reset session, a session whose title you recall).
- A session was `/reset` (or `/new`-continued) and you need the PRE-reset content.
- You need to inspect Hermes state directly (sessions, cron runs, kanban, memory DB).
- You need ground-truth ordering/timing of messages that the FTS index hasn't caught.

`session_search` is FTS5-backed and is the right first call — but it lags, can miss
very recent or just-reset sessions, and its discovery shape sometimes returns 0 rows
for content that IS in the DB. The raw SQLite store under `~/.hermes/` is ground truth.
Fall back to it; do not conclude "it didn't happen" from an empty `session_search`.

## Where the data lives
Each profile has its own `state.db` (SQLite). Active profile path pattern:
`~/.hermes/profiles/<profile>/state.db`. The session DB is the SAME file across a
reset — a reset does not start a new DB, it continues in the same `state.db`.

Key tables (verified schema):
- `sessions` — one row per session. Useful cols: `id` (TEXT, e.g.
  `20260731_090857_d1cfb9`), `source` (`tui`/`cli`/`discord`/...), `title`,
  `started_at` (REAL unix), `ended_at`, `message_count`, `model`, `cwd`,
  `profile_name`, `archived`, `pinned`.
- `messages` — one row per message. Useful cols: `id` (INTEGER, monotonic — use for
  ordering), `session_id` (TEXT), `role` (`user`/`assistant`/`tool`), `content`,
  `tool_calls`, `tool_name`, `timestamp` (REAL), `active`, `compacted`.
- FTS tables `messages_fts*` exist but you usually don't need them — a `LIKE` on
  `messages.content` is simpler and catches what FTS missed.

Other state DBs you may want (same per-profile / global layout):
- cron runs: `<profile>/cron/executions.db`
- kanban: `kanban/boards/main/kanban.db`
- memory (mnemosyne): `<profile>/mnemosyne/data/mnemosyne.db`
- response store / verification: `<profile>/response_store.db`, `verification_evidence.db`

## Recipes (run via terminal + sqlite3)
Set `DB=~/.hermes/profiles/<profile>/state.db` first. Use `-separator` for readability.

1) Recent sessions by source:
```
sqlite3 -separator ' | ' "$DB" "SELECT id, source,
  datetime(started_at,'unixepoch','localtime'), title, message_count
  FROM sessions WHERE source='tui' ORDER BY started_at DESC LIMIT 8;"
```

2) Find sessions containing a keyword (join to messages):
```
sqlite3 -separator ' | ' "$DB" "SELECT s.id, s.title,
  datetime(min(m.timestamp),'unixepoch','localtime') AS first, COUNT(*) n
  FROM messages m JOIN sessions s ON s.id=m.session_id
  WHERE m.content LIKE '%KEYWORD%' AND m.role IN ('user','assistant')
  GROUP BY s.id ORDER BY first DESC LIMIT 6;"
```

3) Read the tail (or head) of one session:
```
sqlite3 -separator $'\n\n===MSG===\n\n' "$DB" "SELECT role||' [id='||id||']: '||
  substr(content,1,2500) FROM messages WHERE session_id='SID'
  AND role IN ('user','assistant') AND content IS NOT NULL AND content!=''
  ORDER BY id DESC LIMIT 8;"
```
(Flip to `ORDER BY id ASC` for the head. `substr` keeps huge tool outputs out of view.)

A ready-made probe is in `scripts/session_probe.sh` — pass profile + keyword.

## GOTCHAS (the part that actually costs time)
1. **Session-ID reuse after a reset.** When a session is `/reset`, the new session
   frequently INHERITS the old session's `id`. So `WHERE session_id='SID'` returns
   BOTH the pre-reset and post-reset messages mixed together — and your OWN current
   queries/messages may share that id too. To read only the pre-reset content, anchor
   on a known message id (e.g. the reset marker or the first new user message) and
   filter `AND id < ANCHOR_ID`. Find the anchor first:
   `SELECT id FROM messages WHERE session_id='SID' AND content LIKE '%<reset cue>%' LIMIT 1;`

2. **Order by message `id`, not `timestamp`.** `id` is monotonic within the DB and is
   the reliable within-session order. `timestamp < X` filters can behave unexpectedly
   (clock skew, REAL precision); when a time cutoff misbehaves, switch to an `id` cutoff.

3. **`session_search` lag / misses.** Discovery can return 0 rows for sessions that
   ARE present (FTS not yet committed, or just-reset sessions). Empty result ≠ absent.
   Confirm against the raw DB before telling the user something wasn't found.

4. **Your own session pollutes self-referential queries.** If you search for text you
   just typed this session, you'll match your own messages. Restrict by `id < ANCHOR`
   or exclude the current session window when hunting for PRIOR-session content.

## Pitfalls
- Don't `cat`/dump whole tables — they're large. Always `LIMIT`, `substr(content,...)`,
  and filter `role IN ('user','assistant')` (tool rows are noisy and huge).
- Don't write to these DBs. Read-only inspection; Hermes owns the write path.
- Don't conclude a session is gone from an empty `session_search` — verify in `state.db`.
- This skill is READ forensics. For configuring/using Hermes broadly, the bundled
  `hermes-agent` skill is the reference; this one only covers direct-DB recovery.
