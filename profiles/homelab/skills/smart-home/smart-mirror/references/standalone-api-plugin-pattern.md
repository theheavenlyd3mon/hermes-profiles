# Standalone HTTP API Plugin — General Pattern

> Reusable pattern for building Hermes plugins that expose data over HTTP.  
> Used by: kanban-api (port 8643), session-api (port 8644).  
> Reference: `kanban-api-plugin.md` for worked kanban example, `session-api-plugin.md` for session example.

## When to use

- Need to expose Hermes data (kanban, sessions, fabric, cron, etc.) to external consumers (MagicMirror, dashboards, scripts)
- The Hermes plugin system has no `register_api_route()` — can't add routes to the gateway directly
- Want a self-contained server that survives `hermes update`

## File structure

```
~/.hermes/plugins/<name>/
├── plugin.yaml        # manifest
└── __init__.py        # register(ctx) + server logic
```

## plugin.yaml template

```yaml
name: <name>
version: 1.0.0
description: <what it serves>
author: Senna
kind: standalone
requires_env: []
provides_tools: []
provides_hooks: []
```

## __init__.py skeleton

```python
import json
import logging
import threading
import time

logger = logging.getLogger(__name__)

_PORT = <port>       # 8643 for kanban, 8644 for session, etc.
_HOST = "127.0.0.1"

_server_instance = None
_thread_instance = None

# ─── Data access ───

def _build_response() -> tuple[bytes, int]:
    """Query data source and return (json_bytes, status_code)."""
    try:
        # ... read from hermes_cli, sqlite, etc.
        return (json.dumps(data).encode("utf-8"), 200)
    except Exception as exc:
        logger.error("%s: fetch failed: %s", __name__, exc)
        return (json.dumps({"error": str(exc)}).encode("utf-8"), 500)

# ─── Handlers ───

async def _handle_data(request):
    from aiohttp import web
    body, status = _build_response()
    return web.Response(
        body=body, status=status, content_type="application/json",
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, OPTIONS"},
    )

async def _handle_health(request):
    from aiohttp import web
    return web.json_response({"status": "ok", "service": "<name>"})

# ─── Server ───

def _run_server():
    import asyncio, aiohttp.web

    app = aiohttp.web.Application()
    app.router.add_get("/health", _handle_health)
    app.router.add_get("/api/<endpoint>", _handle_data)
    app.router.add_route("OPTIONS", "/api/<endpoint>", _handle_data)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    runner = aiohttp.web.AppRunner(app, handle_signals=False)
    loop.run_until_complete(runner.setup())
    site = aiohttp.web.TCPSite(runner, host=_HOST, port=_PORT)
    loop.run_until_complete(site.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()

def start():
    global _server_instance, _thread_instance
    if _server_instance is not None:
        return
    _thread_instance = threading.Thread(target=_run_server, daemon=True, name="<name>")
    _thread_instance.start()
    _server_instance = True

def stop():
    global _server_instance, _thread_instance
    _server_instance = None
    _thread_instance = None

def register(ctx):
    try:
        import aiohttp  # noqa: F401
    except ImportError:
        logger.error("%s: aiohttp not available — skipping", __name__)
        return
    start()
```

## Data source options

| Source | Import | Notes |
|--------|--------|-------|
| Kanban DB | `from hermes_cli import kanban_db as kb` | `kb.connect()` → `kb.list_tasks(conn)` |
| LCM SQLite | `sqlite3.connect(db_path)` | Direct SQL, no Hermes CLI dependency. DB at `~/.hermes/profiles/<profile>/lcm.db` |
| Fabric | Read `~/.hermes/profiles/<profile>/fabric/` directory | File-based, scan for entries |
| Cron | `from hermes_cli import cron_db` or read `~/.hermes/cron/` | Depends on Hermes version |

## Port allocation

| Port | Plugin | Data |
|------|--------|------|
| 8642 | Hermes gateway | Health, chat, jobs, runs |
| 8643 | kanban-api | Task board |
| 8644 | session-api | Conversation messages |
| 8645+ | future plugins | Use sequential ports |

## Pitfalls

- **`run_app()` crashes in background thread** — signal handlers only work in main thread. Always use `AppRunner(handle_signals=False)` + `TCPSite`.
- **SQLite locking** — lcm.db is written by the LCM engine. Use `timeout=5` on connect and keep read transactions short.
- **Cross-profile plugin writes** — plugins at `~/.hermes/plugins/` belong to the default profile. Writing from senna profile requires `cross_profile=True`.
- **CORS** — MagicMirror client connects from `localhost:8080`. Always set `Access-Control-Allow-Origin: *`.
- **Module size cap** — per-message content should be capped (e.g., `[:4000]`) to avoid huge JSON payloads.

## Verification

```bash
curl http://127.0.0.1:<port>/health
# {"status": "ok", "service": "<name>"}

curl http://127.0.0.1:<port>/api/<endpoint>
# {"data": [...], "updated_at": ...}
```
