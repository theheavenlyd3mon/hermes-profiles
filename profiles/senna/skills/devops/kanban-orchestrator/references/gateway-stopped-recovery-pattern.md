# Gateway-stopped Recovery Pattern

Validated in session 2026-05-16: all non-senna profiles showed `Gateway: stopped` in `hermes profile list`, yet workers recovered successfully on simple re-dispatch.

## The nonzero_exit(1) pattern

When a kanban worker crashes with `nonzero_exit(1)` on a profile showing `Gateway: stopped`:

1. **Do not change any config** — the gateway status is not the root cause. Kanban workers connect through the dispatcher's gateway, not the profile's own.
2. **Do not start the gateway** — `hermes gateway start` manages the messaging gateway (Telegram/Discord), not LLM provider connections.
3. **Recovery**: `hermes kanban unblock <id> && hermes kanban dispatch`

## The "pid NNNN not alive" pattern

Different crash signature — the worker process never came online. Crashes show `pid NNNN not alive` in the event log with `crashed` outcome, not `nonzero_exit(1)`.

When ALL tasks assigned to the same profile crash with `pid not alive` and that profile shows `Gateway: stopped`:

1. **Start the profile's gateway** — this resolved the issue in one session where the `coder` profile had stopped mid-run (T2.2 completed, then all subsequent tasks crashed with pid not alive). <br>`hermes -p <profile> gateway start`
2. **Verify** — check the profile's gateway is now running via `hermes profile list | grep <profile>` or `hermes -p <profile> gateway status`
3. **Unblock + dispatch** — `hermes kanban unblock <id> && hermes kanban dispatch`

**Note:** This is distinct from `nonzero_exit(1)` crashes where the worker connected and ran code before failing. The `pid not alive` error means the spawned subprocess never initialized — starting the profile's gateway seems to re-establish transport wiring that the dispatcher needs to communicate with the worker process on that specific profile.

## Session data

| Task | Profile | Model | Crashes | Recovery | Result |
|---|---|---|---|---|---|
| `t_71c773f5` — Liquid Glass research | researcher | deepseek/deepseek-v3.2 | 2x exit_code:1 (runs #78, #79) | unblock + dispatch (run #80) | Ran 15+ min, completed, spawned child task |
| `t_8d88c635` — Ingest to wiki | secretary | qwen/qwen3.6-flash | 2x exit_code:1 (runs #81, #82) | unblock + dispatch (run #83) | Ran, hit HTTP 503 (Nous capacity), recovered on retry 3, completed |

## Takeaways

- **Two profiles, different models, same recovery pattern** — the gateway-stopped status is a red herring for nonzero_exit(1) crashes, not just protocol_violation.
- **The "Unknown skill(s): kanban-worker" warning in logs is non-fatal** — workers run fine without it.
- **HTTP 503 on provider capacity limits** — the built-in retry mechanism (3 attempts with exponential backoff) handles these. No manual intervention needed.
- **Child tasks spawned by a successful worker inherit the same pattern** — the secretary child of the researcher task crashed identically and recovered identically.
