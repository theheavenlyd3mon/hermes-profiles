---
name: external-coding-agents
description: "Delegate coding tasks to external CLI agents (Claude Code, Codex, OpenCode) via Hermes terminal. Covers orchestration patterns, parallel work, PR reviews, and tool selection."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, CLI, Automation, Code-Review, Refactoring, PTY, Parallel, Claude, Codex, OpenCode]
    related_skills: [hermes-agent]
---

# External Coding Agents — Orchestration Guide

Delegate coding tasks to autonomous CLI agents via Hermes terminal tools. Three supported agents, one shared orchestration pattern.

## Tool Selection

| Agent | Best for | Install | Auth |
|-------|----------|---------|------|
| **Claude Code** | Complex multi-step work, structured output, CI/CD, subagents | `npm install -g @anthropic-ai/claude-code` | OAuth or `ANTHROPIC_API_KEY` |
| **Codex** | Sandboxed execution, batch fixes, full-auto mode | `npm install -g @openai/codex` | OAuth or `OPENAI_API_KEY` |
| **OpenCode** | Provider-agnostic tasks, long sessions, cost tracking | `npm i -g opencode-ai@latest` | `opencode auth login` or env vars |

**Default choice:** Claude Code for Anthropic users, Codex for OpenAI users, OpenCode for multi-provider setups. All three can do coding, refactoring, and PR reviews — pick based on your auth setup and preferred model.

## Two Orchestration Modes

### Mode 1: One-Shot (PREFERRED for most tasks)

Run a bounded task, get the result, exit. No PTY needed for Claude Code (`-p`) and OpenCode (`run`); Codex always needs PTY.

```
# Claude Code (print mode, no PTY)
terminal(command="claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)

# Codex (needs PTY)
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)

# OpenCode (no PTY for run)
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

### Mode 2: Interactive Background (for iterative work)

Start the TUI in background, send prompts, monitor progress. All three agents need PTY for interactive mode.

```
# Start in background
terminal(command="claude", workdir="~/project", background=true, pty=true)
# or: terminal(command="codex", ...)
# or: terminal(command="opencode", ...)

# Send task
process(action="submit", session_id="<id>", data="Refactor the auth module")

# Monitor
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Follow up
process(action="submit", session_id="<id>", data="Now add unit tests")

# Exit
process(action="kill", session_id="<id>")
```

**Claude Code tmux alternative:** For complex multi-turn sessions, tmux gives `capture-pane` for monitoring and `send-keys` for input — more reliable than raw PTY.

```
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Your task here' Enter")
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")
```

## PR Review Workflow

### Quick Review (diff piped to agent)
```
# Claude Code
terminal(command="git diff main...feature-branch | claude -p 'Review this diff for bugs and security issues' --max-turns 1", timeout=60)

# OpenCode
terminal(command="opencode pr 42", workdir="~/project", pty=true)

# Codex (temp clone)
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

### Deep Review (interactive + worktree)
```
terminal(command="tmux new-session -d -s review -x 140 -y 40")
terminal(command="tmux send-keys -t review 'cd /path/to/repo && claude -w pr-review' Enter")
# Handle trust dialog, then send review prompt
```

## Parallel Work with Worktrees

Run multiple agents on independent tasks without git conflicts:

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch agents in parallel
terminal(command="codex --yolo exec 'Fix issue #78. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## General Rules

1. **Always set `workdir`** — keep the agent focused on the right project
2. **Set turn/budget limits** in one-shot mode — prevents runaway costs
3. **Restrict tool access** — use `--allowedTools` (Claude Code), `--full-auto` (Codex), or task scoping (OpenCode)
4. **Monitor background sessions** — use `process(action="poll"|"log")` or `tmux capture-pane`
5. **Clean up** — kill sessions and remove worktrees when done
6. **Report results** — summarize what the agent did and what changed
7. **Don't kill slow sessions** — check progress first; the agent may be doing multi-step work
8. **Prefer one-shot for single tasks** — cleaner, no dialog handling, structured output

## Pitfalls

1. **Codex always needs PTY** — it's an interactive terminal app; hangs without it
2. **Claude Code `--dangerously-skip-permissions` dialog defaults to "No"** — must send Down+Enter to accept (print mode `-p` skips this entirely)
3. **OpenCode `/exit` is not a valid command** — it opens an agent selector; use Ctrl+C instead
4. **Session resumption requires same directory** — `--continue` finds the most recent session for the cwd
5. **Background tmux sessions persist** — always clean up with `tmux kill-session -t <name>`
6. **Codex requires a git repo** — won't run outside one; use `mktemp -d && git init` for scratch work
7. **PATH mismatch** — shell may resolve different binaries across environments; check with `which -a <agent>`
8. **Context degradation** — AI output quality degrades above 70% context window; use `/compact` (Claude Code) or new sessions

## Tool-Specific References

| Agent | Reference | What's in it |
|-------|-----------|-------------|
| Claude Code | `references/claude-code.md` | Print mode, JSON output, session resume, CLI flags, hooks, MCP, slash commands, cost tips |
| Codex | `references/codex.md` | Exec mode, sandbox modes, gateway caveat, batch reviews, parallel fixes |
| OpenCode | `references/opencode.md` | Run mode, TUI keybindings, session management, stats, verification |