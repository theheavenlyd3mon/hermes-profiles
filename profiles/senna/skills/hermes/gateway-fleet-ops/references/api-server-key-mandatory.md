# API_SERVER_KEY Is Mandatory (Post-June 2026)

When `.env` files in the fleet are missing `API_SERVER_KEY`, the affected gateways do **not** just fail to boot — they enter a **continuous reconnect loop** with backoff to 300s and keep retrying indefinitely.

## Log signature
```
ERROR gateway.platforms.api_server: Refusing to start: API_SERVER_KEY is required for the API server, including loopback-only binds on 127.0.0.1.
INFO  gateway.run: Reconnecting api_server (attempt N)...
```

## Fleet-wide recipe (single key)
```bash
API_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
for p in $(for dir in ~/.hermes/profiles/*/; do profile=$(basename "$dir"); [ -f "$dir/.env" ] && grep -q '^DISCORD_BOT_TOKEN=' "$dir/.env" 2>/dev/null && echo "$profile"; done); do
  grep -q '^API_SERVER_KEY=' ~/.hermes/profiles/$p/.env 2>/dev/null || echo "API_SERVER_KEY=$API_KEY" >> ~/.hermes/profiles/$p/.env
done
for p in $(for dir in ~/.hermes/profiles/*/; do profile=$(basename "$dir"); [ -f "$dir/.env" ] && grep -q '^DISCORD_BOT_TOKEN=' "$dir/.env" 2>/dev/null && echo "$profile"; done); do
  hermes --profile "$p" gateway restart 2>&1
done
```

## Port-holder race condition
If one profile already binds `platforms.api_server.port=8643` (default) and **others** lack the key, both errors fire in the same second — some profiles fail on key check, others fail on port check because the first one already bound. Fix the key first; only then address which profiles actually need `api_server` enabled.
