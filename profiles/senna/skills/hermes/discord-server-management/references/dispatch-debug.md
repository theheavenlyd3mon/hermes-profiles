# Dispatch Debug Notes — Senna Fleet (2026-06-30)

## Observed State

| Profile | Token | Discord config | Gateway | Issue |
|---|---|---|---|---|
| senna | ✅ | ✅ | ✅ running | API server conflict on 8643 |
| creative | ✅ | ✅ | ✅ running | API server enabled (should be off) |
| security | ✅ | absent | ✅ running | No discord: section in config |
| code | ❌ | ❌ | ✅ running | Blocker |
| finance | ❌ | ❌ | ✅ running | Blocker |
| knowledge | ❌ | ❌ | ✅ running | Blocker |
| infra | ❌ | ❌ | ✅ running | Blocker |
| research | ❌ | ❌ | ✅ running | Blocker |

## API Server Error Pattern

`[Api_Server] Refusing to start: API_SERVER_KEY is required for the API server`

This only appears for profiles with `API_SERVER_ENABLED=true` in `.env`. It is harmless if the bot never needs an HTTP API server, but it floods logs with retry messages every 300 s.

## Port Collision

Only creative actually bound TCP `127.0.0.1:8643`, blocking senna’s own API server start. Fix: disable across all specialists first, then senna can use the default port alone.