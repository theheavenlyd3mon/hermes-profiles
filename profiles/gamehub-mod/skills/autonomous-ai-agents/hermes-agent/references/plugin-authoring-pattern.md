# Plugin Authoring: Background HTTP Server Pattern

How to create a Hermes plugin that runs a standalone HTTP server to extend the gateway with custom API endpoints — without modifying core Hermes code.

## When to Use

- You need a custom REST endpoint (e.g. `/api/kanban/board`) that the Hermes gateway doesn't provide
- You want the endpoint to survive `hermes update` without being overwritten
- The endpoint reads from Hermes internals (kanban DB, session store, etc.)

## Architecture

The built-in API server (port 8642, `gateway/platforms/api_server.py`) has no plugin hook for adding routes. Instead, create a **standalone platform plugin** that runs its own aiohttp server on a separate port:

```
Hermes Gateway (8642)         Your Plugin (8643)
  ┌──────────────┐             ┌──────────────────┐
  │ /health      │             │ /api/your/thing  │──→ Hermes DB/API
  │ /v1/chat/... │             └──────────────────┘
  │ /api/jobs    │                      ↑
  └──────────────┘                      │ polls
                                 ┌──────────────┐
                                 │ External client│
                                 └──────────────┘
```

## Plugin Structure

```
~/.hermes/plugins/<plugin-name>/
├── plugin.yaml          # Manifest
└── __init__.py          # register(ctx) entry point + server
```

## plugin.yaml

```yaml
name: my-plugin
version: 1.0.0
description: Serves custom API data
author: Your Name
kind: standalone
requires_env: []
provides_tools: []
provides_hooks: []
```

## __init__.py — The Background Server Pattern

aiohttp's `web.run_app()` calls `loop.add_signal_handler()` which crashes in background threads. Use the **AppRunner + TCPSite** pattern instead:

```python
"""My Hermes plugin — background HTTP server."""

import asyncio
import json
import logging
import threading
import time

logger = logging.getLogger(__name__)

_PORT = 8643
_HOST = "127.0.0.1"

_server_instance = None


async def _handle_endpoint(request):
    """Handler for your custom endpoint."""
    from aiohttp import web
    return web.json_response({"status": "ok"})


async def _handle_health(request):
    from aiohttp import web
    return web.json_response({"status": "ok", "service": "my-plugin"})


def _run_server():
    """Run the aiohttp server in a background thread.

    Uses AppRunner + TCPSite with handle_signals=False to avoid
    ``RuntimeError: set_wakeup_fd only works in main thread``.
    """
    import aiohttp.web

    app = aiohttp.web.Application()
    app.router.add_get("/health", _handle_health)
    app.router.add_get("/api/your/thing", _handle_endpoint)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    runner = aiohttp.web.AppRunner(app, handle_signals=False)
    loop.run_until_complete(runner.setup())
    site = aiohttp.web.TCPSite(runner, host=_HOST, port=_PORT)
    loop.run_until_complete(site.start())

    logger.info("my-plugin: server running on %s:%d", _HOST, _PORT)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()


def start():
    """Start the server in a background daemon thread."""
    global _server_instance
    if _server_instance is not None:
        return
    t = threading.Thread(target=_run_server, daemon=True, name="my-plugin")
    t.start()
    _server_instance = True


def register(ctx):
    """Plugin entry point — called by the Hermes plugin loader."""
    try:
        import aiohttp
    except ImportError:
        logger.error("my-plugin: aiohttp not available — skipping")
        return
    start()
```

## Enabling the Plugin

Add to `~/.hermes/config.yaml`:

```yaml
plugins:
  enabled:
    - my-plugin
```

Then restart the Hermes gateway for it to take effect.

## Pitfalls

1. **Signal handlers in threads** — Never use `aiohttp.web.run_app()` in a background thread. Always use `AppRunner(handle_signals=False)` + manual loop management.

2. **CORS** — The browser client that calls your endpoint may need CORS headers. Add them per-handler or as middleware if clients connect from a different origin/port.

3. **Port conflicts** — If the gateway shares the port, the plugin won't start. Use a unique port and document it.

4. **No hot-reload** — Plugin changes require a gateway restart. The `register()` function runs once at startup.

5. **Kanban DB example** — To read from the kanban DB in a plugin:
   ```python
   from hermes_cli import kanban_db as kb
   conn = kb.connect()
   tasks = kb.list_tasks(conn, include_archived=False)
   # Tasks have .id, .title, .status, .assignee, .priority, .created_at, etc.
   ```
