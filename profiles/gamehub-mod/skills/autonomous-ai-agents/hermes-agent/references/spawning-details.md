## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Monitoring (hermesd)

The `hermesd` CLI is the TUI monitoring dashboard for Hermes Agent. It displays gateway status, session stats, token usage, cron jobs, logs, and profile data in a live terminal UI.

### Profile Resolution Quirk

When running inside a profile sandbox, `$HOME` and `$HERMES_HOME` both point to profile-scoped paths. This causes `hermesd --profile <name>` to look for `<profile_dir>/profiles/<name>` which doesn't exist.

**Fix:** Pass `--hermes-home` to point at the root hermes home:

```bash
hermesd --hermes-home ~/.hermes --profile senna
```

**Long-term:** Add a shell function to the user's real `~/.zshrc`:

```zsh
hermesd() { command hermesd --hermes-home ~/.hermes --profile senna "$@"; }
```

See `references/hermesd-profile-resolution.md` for full root cause analysis.

### Data Sources

hermesd reads from these locations for its dashboard data:

| Panel | Data Source |
|---|---|
| Gateway & Platforms | `gateway_state.json`, process list |
| Sessions | `state.db` |
| Tokens / Cost | `state.db` token analytics |
| Cron | `cron/jobs.json`, cron output dir |
| Skills | skills directory, plugins directory |
| Logs | `logs/gateway.log`, per-agent logs |
| Profiles | `profiles/` directory |
| Memory | mnemosyne provider status |

### Common Commands

```bash
hermesd                                             # default (reads $HERMES_HOME)
hermesd --hermes-home ~/.hermes --profile senna   # with profile
hermesd --snapshot                                  # one-shot text snapshot
hermesd --snapshot --snapshot-format json           # JSON machine-readable
hermesd --snapshot --snapshot-panel 1               # specific panel
```

---

## Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---
