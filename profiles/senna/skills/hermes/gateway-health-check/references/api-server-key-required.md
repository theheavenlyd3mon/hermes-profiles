# API_SERVER_KEY Required — Fleet-Wide Crash (June 2026)

## Incident

A hermes-agent update introduced a mandatory `API_SERVER_KEY` for the api_server platform. All 8 gateway profiles crashed simultaneously because none had the key set.

**Error message** (from `gateway.error.log`):
```
ERROR gateway.platforms.api_server: [Api_Server] Refusing to start: API_SERVER_KEY is required for the API server, including loopback-only binds on 127.0.0.1.
```

**Behavior**: Profiles with api_server explicitly configured (senna) crashed with exit=1 in a restart loop. Profiles inheriting api_server from root config also crashed. Launchd showed exit=-15 (SIGTERM) for most — launchd killed them after repeated failures. Zero gateway processes were running.

**Key observation**: The `gateway.error.log` accumulates across restarts. The repeated error line appeared ~30 times per profile from repeated crash-restart cycles. Always `tail` the error log, don't `grep` — old errors persist.

## Fix

1. Generate a random key (value doesn't matter for local-only API servers):
```bash
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
```

2. Add to all profiles that have api_server enabled (explicitly or inherited):
```bash
for p in ~/.hermes/profiles/*/; do
  grep -q '^API_SERVER_KEY=' "$p/.env" 2>/dev/null || echo "API_SERVER_KEY=$API_KEY" >> "$p/.env"
done
```

3. Restart the fleet:
```bash
for p in senna code creative security infra knowledge research finance; do
  hermes --profile "$p" gateway restart
done
```

4. Verify (5s settle time, then check processes):
```bash
sleep 5
ps aux | grep "hermes_cli.main.*gateway" | grep -v grep
```

## Why All Profiles Are Affected

Even profiles without explicit `api_server` config inherit it from the root config at `~/.hermes/config.yaml`. The inheritance chain is:
1. `~/.hermes/profiles/<name>/config.yaml` — profile's own
2. `~/.hermes/profiles/<name>/home/.hermes/config.yaml` — profile's HERMES_HOME
3. `~/.hermes/config.yaml` — root (all profiles inherit from this)

If the root config has `platforms.api_server.enabled: true` (or `API_SERVER_ENABLED=true` in `.env`), ALL profiles try to start the API server and ALL need the key.

## Prevention

After any `hermes update`, check the changelog for new required env vars. A fleet-wide crash with the same error across all profiles is a signal that a new mandatory config was introduced.

## Lesson: error.log Is Append-Only

The error log doesn't rotate or clear between restarts. A single missing-key error gets repeated 20-30 times as launchd retries the gateway. This makes `grep` misleading — it looks like the error is current when it may be from 10 restarts ago. Always use `tail -20` to see the most recent state.
