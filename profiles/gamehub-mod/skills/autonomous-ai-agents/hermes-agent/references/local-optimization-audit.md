# Local Optimization Audit Pattern

Use this when optimizing Hermes Agent for speed/efficiency on a user's own machine.

## Session-derived context

In one optimization session, the user had:
- macOS 15.6 x86_64
- Intel i7-9750H
- 16GB RAM
- Hermes install at `~/.hermes/hermes-agent`
- canonical profile intended to be `senna`
- profiles for specialist team agents, but not default
- plugins: `gbrain`, `icarus`
- Hermes Workspace expected to connect via gateway/API server on localhost:8642
- large profile size: `~/.hermes/profiles/senna` around 1.5G

## Audit targets

Check profile size before deleting anything:

```bash
du -sh ~/.hermes/profiles/senna/* 2>/dev/null
du -sh ~/.hermes/profiles/senna/sessions 2>/dev/null
du -sh ~/.hermes/profiles/senna/checkpoints 2>/dev/null
du -sh ~/.hermes/profiles/senna/skills 2>/dev/null
du -sh ~/.hermes/profiles/senna/cache ~/.hermes/profiles/senna/.cache ~/.hermes/profiles/senna/home 2>/dev/null
find ~/.hermes/profiles/senna -type f -size +50M -print
find ~/.hermes/profiles/senna -type d -name node_modules -prune -print
find ~/.hermes/profiles/senna -type d -name .git -prune -print
```

Interpretation:
- `sessions/`: useful recall history; prune only after review.
- `checkpoints/`: rollback safety; prefer bounded retention over deletion.
- `skills/`: may duplicate central `~/.hermes/skills`; do not prune without a keep-list.
- `home`, `.cache`, `node_modules`, accidental `.git` dirs: common source of surprise gigabytes.

## Gateway alignment for Workspace

Hermes Workspace / dashboards usually connect to Hermes via the gateway API server on `localhost:8642`.

Before changing services:

```bash
hermes profile list
hermes gateway status
hermes --profile senna gateway status
lsof -nP -iTCP:8642 -sTCP:LISTEN
ps aux | grep -i "hermes gateway" | grep -v grep
```

If the user's canonical profile is Senna, ensure Workspace connects to the Senna gateway rather than an old/default profile gateway. The env var `API_SERVER_ENABLED=true` must be present in `~/.hermes/profiles/senna/.env` before starting/restarting the Senna gateway. This variable is snapshotted at gateway startup.

Never edit `.env`, stop/start gateways, or restart services without explicit approval.

## Safe first-pass config changes

After approval, a conservative first pass is:

```bash
hermes config set display.compact true
hermes config set display.streaming true
hermes config set display.tool_progress new
hermes config set display.interim_assistant_messages false
hermes config set delegation.max_concurrent_children 2
hermes config set delegation.max_iterations 30
```

Optional storage guardrail:

```bash
hermes config set checkpoints.max_snapshots 20
hermes config set checkpoints.auto_prune true
```

Keep security controls enabled: secret redaction, Tirith, private URL protections, and approvals.
