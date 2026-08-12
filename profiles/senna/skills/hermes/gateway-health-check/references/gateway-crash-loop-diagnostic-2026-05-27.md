# Gateway Crash-Loop Diagnostic: Dual Source Trees + YAML Duplication

**Date:** 2026-05-27
**Symptoms:** Hermes gateway "stopped working completely" after moving hermes-agent files into senna profile.

## Root Causes Found

### 1. Two hermes-agent source trees at different commits

```
~/.hermes/hermes-agent/                  → commit 8386f8445 (older)
~/.hermes/profiles/senna/hermes-agent/   → commit 9919caff4 (newer)
```

Gateway processes used a MIX of venvs:
- senna, oracle: `~/.hermes/hermes-agent/venv/bin/python` (root)
- secretary, coder, foreman, architect, researcher: `~/.hermes/profiles/senna/hermes-agent/venv/bin/python` (senna)

### 2. Duplicate `platforms:` key in root config.yaml

```yaml
platforms:          # ← FIRST (telegram) — SILENTLY DROPPED
  telegram:
    enabled: true
platforms:          # ← SECOND (api_server) — THIS WINS
  api_server:
    enabled: true
```

Any process reading the root config instead of the profile config would see no telegram and no discord.

### 3. Gateway crash-loop pattern (14:37–17:21)

Exit diagnostics showed ~15 rapid restarts in 3 hours:

```
14:37:58  exit_nonzero  pid=1571
14:38:01  gateway.start pid=11690
14:38:40  exit_nonzero  pid=11690
14:38:41  gateway.start pid=11796
14:38:47  exit_nonzero  pid=11796
...pattern continues until 17:29...
17:29:35  gateway.start pid=21920  ← STABLE (lasted 1h14m+)
```

### 4. Discord 4004 errors

```
discord.errors.ConnectionClosed: Shard ID None WebSocket closed with 4004
```

Discord 4004 = Authentication failed. Caused by competing gateway instances fighting over the same bot token. When one grabs it, the other fails with 4004, both get SIGTERM'd, restart, repeat.

### 5. Telegram polling conflicts

```
Conflict: terminated by other getUpdates request; make sure that only one bot instance is running
```

Same root cause — multiple instances fighting over one bot token.

## Resolution

The crash storm self-resolved when competing processes killed each other off. The surviving gateway (PID 21920) stabilized and connected successfully:

```
12:29:39 INFO [Discord] Connected as Hermes Senna#9675
12:47:39 INFO inbound message: platform=discord user=Noctis msg='test'
12:47:56 INFO response ready: platform=discord time=16.1s
```

## Lessons

1. Always check for dual hermes-agent source trees after any profile migration
2. Duplicate YAML keys are a silent killer — Python's YAML parser keeps only the last
3. `hermes config set` creates duplicates — prefer direct `patch` for existing keys
4. Gateway exit diagnostics log (`gateway-exit-diag.log`) is the fastest way to detect crash-loop patterns
5. Discord 4004 almost always means token contention between multiple gateway instances
