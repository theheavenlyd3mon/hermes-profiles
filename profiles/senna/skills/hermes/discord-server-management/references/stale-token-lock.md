# Stale Discord Token Lock (false "already in use")

## Symptom

A gateway's Discord platform won't connect. Log shows, repeatedly, even after
the *real* owner of the token is stopped:

```
ERROR [Discord] Discord bot token already in use (PID <N>). Stop the other gateway first.
WARNING Reconnect discord failed, next retry in 240s
```

`hermes gateway list` may show the profile as running (its api_server bound)
but Discord never connects — the reconnect watcher keeps failing.

## Root cause

Discord token locks live in:

```
~/.local/state/hermes/gateway-locks/discord-bot-token-<sha256[:16]>.lock
```

(`<sha256[:16]>` = first 16 hex chars of `sha256(token)`. Lock dir comes from
`gateway/status.py::_get_lock_dir()` → `$XDG_STATE_HOME/hermes/gateway-locks`,
default `~/.local/state/hermes/gateway-locks`. Overridable via
`HERMES_GATEWAY_LOCK_DIR`.)

The staleness check in `acquire_scoped_lock()` only verifies the **PID in the
lock file is alive** — it does NOT verify that process actually holds the
token. So a lock misattributed to a *live but unrelated* process (e.g. another
profile's gateway that is running but has an empty/different token) passes the
check forever. The lock is stale in substance but "valid" by the liveness test.

This happens after token swaps / profile migrations where a lock was written
under one token and the owning process got reused or replaced without releasing
it cleanly.

## Diagnosis

```bash
LOCKDIR=~/.local/state/hermes/gateway-locks

# 1. Which lock does the failing profile want? (hash its token)
python3 - <<'EOF'
import hashlib, os
prof = "novel"   # <-- the profile that won't connect
with open(os.path.expanduser(f"~/.hermes/profiles/{prof}/.env")) as f:
    for line in f:
        if line.startswith("DISCORD_BOT_TOKEN="):
            tok = line.strip().split("=", 1)[1]
            print(f"wants: discord-bot-token-{hashlib.sha256(tok.encode()).hexdigest()[:16]}.lock")
            break
EOF

# 2. Who does that lock file say owns it, and is that PID alive?
for f in "$LOCKDIR"/discord-bot-token-*.lock; do
  [ -f "$f" ] || continue
  pid=$(python3 -c "import json;print(json.load(open('$f')).get('pid','?'))")
  alive=$(ps -p "$pid" >/dev/null 2>&1 && echo ALIVE || echo dead)
  echo "$(basename "$f") -> PID $pid ($alive)"
done

# 3. CRITICAL — does that PID actually hold the token? Check its live env.
#    (macOS: ps eww exposes process environment.)
ps eww -p <PID> | tr ' ' '\n' | grep -c '^DISCORD_BOT_TOKEN='
#    0 = the process has NO token -> the lock is a false positive.
```

Confirm with the bot identity the suspect PID actually connected as:

```bash
grep "Connected as" ~/.hermes/profiles/<suspect-profile>/logs/gateway.log | tail -1
```

If the suspect PID is alive but (a) has no `DISCORD_BOT_TOKEN` in its env and
(b) connected as a *different* bot name, the lock is stale — safe to remove.

## Fix

```bash
# Remove the false-positive lock
rm -f ~/.local/state/hermes/gateway-locks/discord-bot-token-<hash>.lock
```

Then either restart the failing gateway, or — if it's already running — just
wait for its reconnect watcher. The Discord reconnect backoff grows (120s →
240s → ...); after the lock is gone the next retry acquires it and connects:

```
INFO [Discord] Connected as <BotName>#<disc>
INFO ✓ discord reconnected successfully
```

## Notes

- Do NOT kill the suspect PID just to free the lock if it's an unrelated live
  gateway — removing the lock file is enough and avoids taking down a healthy
  bot.
- A genuinely-held lock (the named PID really is connected with that token) is
  NOT stale — stop that gateway first (Token Handoff Sequence in SKILL.md),
  don't delete the lock out from under a live connection.
- Distinguish from the clean handoff failure: if the *real* owner is still
  running, that's the documented "stop A before starting B" case, not this bug.
```
