# Crash-on-Conversation: connected but dies on first reply

Reproduced 2026-07-18. All 9 Discord gateways were *running* (live PIDs
confirmed via `ps`), launchctl showed stale exit codes (1 / -15) from old
crash-restart cycles, and Discord showed the bots as online. But every bot
threw `unexpected error` / `try /reset` the instant a real message arrived.

## Root cause
A `hermes-agent` update added new symbols to the source:
- `reset_conversation_context` in `agent/portal_tags.py`
- `TELEGRAM_RICH_MESSAGES_HINT` in `agent/prompt_builder.py`

The gateways were NOT fleet-restarted after the update. They kept running the
pre-update in-memory modules. Login code is unchanged (so they connect), but
`run_conversation` does `from agent.portal_tags import reset_conversation_context`
→ `ImportError` → the reply dies. The symbols exist on disk in the new code;
only the *running* process has the stale copy.

This is distinct from the "dual hermes-agent source tree" failure (step 8):
a single `hermes_cli/main.py` exists. It is purely "running process predates
the on-disk code". Stale `__pycache__` timestamps newer than source confirmed
it (running process had imported the older bytecode).

## How to tell it apart from "bots are down"
- `ps aux | grep "gateway run"` shows live PIDs → NOT down.
- `gateway.log` shows recent `Connected as <Bot>#<tag>` → NOT an auth/token issue.
- Crash appears in `gateway.error.log` only as an `ImportError` / `cannot import name`
  inside `run_conversation` / `run_sync` → stale in-memory code.
- User-facing symptom: bot is present in the channel, replies with a session-reset
  notice, then dies on the next real message.

## Confirmation recipe
```
for p in ~/.hermes/profiles/*/; do
  f="$p/logs/gateway.error.log"
  hit=$(grep -E "ImportError|cannot import name" "$f" 2>/dev/null | tail -1)
  [ -n "$hit" ] && echo "$(basename $p): $hit"
done
```

## Fix
1. `find ~/.hermes/hermes-agent -name __pycache__ -type d -exec rm -rf {} +`
2. Restart the fleet (every Discord profile) so each gateway re-imports current code.
3. Verify: `ps` for PIDs + `grep "Connected as"` per profile + a test ping in the channel.

After restart the import errors are gone and bots reply normally. This is the
same trigger as the `API_SERVER_KEY` incident (June 2026): **a `hermes update`
without a fleet restart leaves gateways serving stale code.**

## Other signatures seen in the same scan (context, not the blocker)
- `MCP server 'codegraph'/'iknowkungfu' initial connection failed` → parked
  WARNING, non-fatal, separate investigation (MCP server not reachable).
- `ERROR ... API_SERVER_KEY is required for the API server` on profiles missing the
  key (root `config.yaml` sets `platforms.api_server.enabled: true`, so every
  profile inherits it). Non-fatal to Discord: gateway keeps running, just no API server.
- `Discord liveness probe failed ... 522 Connection timed out` → transient Discord-side
  blip, not a local fault.
