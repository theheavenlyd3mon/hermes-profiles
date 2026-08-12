# Claude Code — Detailed Reference

## Prerequisites

- **Install:** `npm install -g @anthropic-ai/claude-code`
- **Auth:** run `claude` once to log in (browser OAuth for Pro/Max, or set `ANTHROPIC_API_KEY`)
- **Console auth:** `claude auth login --console` for API key billing
- **SSO auth:** `claude auth login --sso` for Enterprise
- **Check status:** `claude auth status` (JSON) or `claude auth status --text` (human-readable)
- **Health check:** `claude doctor` — checks auto-updater and installation health
- **Version check:** `claude --version` (requires v2.x+)
- **Update:** `claude update` or `claude upgrade`

## Print Mode Deep Dive

### Structured JSON Output
```
terminal(command="claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5", workdir="/project", timeout=120)
```

Returns a JSON object with:
```json
{
  "type": "result",
  "subtype": "success",
  "result": "The analysis text...",
  "session_id": "75e2167f-...",
  "num_turns": 3,
  "total_cost_usd": 0.0787,
  "duration_ms": 10276,
  "stop_reason": "end_turn",
  "terminal_reason": "completed",
  "usage": { "input_tokens": 5, "output_tokens": 603 },
  "modelUsage": { "claude-sonnet-4-6": { "costUSD": 0.078, "contextWindow": 200000 } }
}
```

**Key fields:** `session_id` for resumption, `num_turns` for agentic loop count, `total_cost_usd` for spend tracking, `subtype` for success/error detection (`success`, `error_max_turns`, `error_budget`).

### Streaming JSON Output
```
terminal(command="claude -p 'Write a summary' --output-format stream-json --verbose --include-partial-messages", timeout=60)
```

Returns newline-delimited JSON events. Filter with jq for live text:
```
claude -p "Explain X" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

### Piped Input
```
terminal(command="cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1", timeout=60)
terminal(command="git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1", timeout=60)
```

### JSON Schema for Structured Extraction
```
terminal(command="claude -p 'List all functions in src/' --output-format json --json-schema '{\"type\":\"object\",\"properties\":{\"functions\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}},\"required\":[\"functions\"]}' --max-turns 5", workdir="/project", timeout=90)
```

### Session Continuation
```
# Resume with session ID
terminal(command="claude -p 'Continue and add connection pooling' --resume <session-id> --max-turns 5", workdir="/project", timeout=120)

# Resume most recent session
terminal(command="claude -p 'What did you do last time?' --continue --max-turns 1", workdir="/project", timeout=30)

# Fork a session (new ID, keeps history)
terminal(command="claude -p 'Try a different approach' --resume <id> --fork-session --max-turns 10", workdir="/project", timeout=120)
```

### Bare Mode for CI/Scripting
```
terminal(command="claude --bare -p 'Run all tests and report failures' --allowedTools 'Read,Bash' --max-turns 10", workdir="/project", timeout=180)
```

`--bare` skips hooks, plugins, MCP discovery, and CLAUDE.md loading. Fastest startup. Requires `ANTHROPIC_API_KEY` (skips OAuth).

| To load in bare mode | Flag |
|---------------------|------|
| System prompt additions | `--append-system-prompt "text"` or `--append-system-prompt-file path` |
| Settings | `--settings <file-or-json>` |
| MCP servers | `--mcp-config <file-or-json>` |

### Fallback Model for Overload
```
terminal(command="claude -p 'task' --fallback-model haiku --max-turns 5", timeout=90)
```

## PTY Dialog Handling (Critical for Interactive Mode)

### Dialog 1: Workspace Trust (first visit to a directory)
```
❯ 1. Yes, I trust this folder    ← DEFAULT (just press Enter)
  2. No, exit
```
**Handling:** `tmux send-keys -t <session> Enter`

### Dialog 2: Bypass Permissions Warning (only with --dangerously-skip-permissions)
```
❯ 1. No, exit                    ← DEFAULT (WRONG choice!)
  2. Yes, I accept
```
**Handling:** Must navigate DOWN first, then Enter:
```
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

**Note:** Trust dialog only appears once per directory. Permissions dialog recurs each time you use `--dangerously-skip-permissions`.

## CLI Subcommands

| Subcommand | Purpose |
|------------|---------|
| `claude` | Start interactive REPL |
| `claude -p "query"` | Print mode (non-interactive, exits when done) |
| `cat file \| claude -p "query"` | Pipe content as stdin context |
| `claude -c` | Continue the most recent conversation in this directory |
| `claude -r "id"` | Resume a specific session by ID or name |
| `claude auth login` | Sign in (add `--console` for API billing, `--sso` for Enterprise) |
| `claude mcp add <name> -- <cmd>` | Add an MCP server |
| `claude mcp list` | List configured MCP servers |
| `claude agents` | List configured agents |
| `claude doctor` | Run health checks |
| `claude update` / `claude upgrade` | Update to latest version |
| `claude remote-control` | Start server to control from claude.ai or mobile app |

## Complete CLI Flags Reference

### Session & Environment
| Flag | Effect |
|------|--------|
| `-p, --print` | Non-interactive one-shot mode |
| `-c, --continue` | Resume most recent conversation in current directory |
| `-r, --resume <id>` | Resume specific session by ID or name |
| `--fork-session` | Create new session ID when resuming |
| `--session-id <uuid>` | Use a specific UUID |
| `--no-session-persistence` | Don't save session to disk (print mode only) |
| `--add-dir <paths...>` | Grant access to additional working directories |
| `-w, --worktree [name]` | Run in isolated git worktree at `.claude/worktrees/<name>` |
| `--tmux` | Create tmux session for worktree |
| `--from-pr [number]` | Resume session linked to a GitHub PR |

### Model & Performance
| Flag | Effect |
|------|--------|
| `--model <alias>` | `sonnet`, `opus`, `haiku`, or full name |
| `--effort <level>` | `low`, `medium`, `high`, `max`, `auto` |
| `--max-turns <n>` | Limit agentic loops (print mode only) |
| `--max-budget-usd <n>` | Cap API spend in dollars (print mode only) |
| `--fallback-model <model>` | Auto-fallback when overloaded (print mode only) |

### Permission & Safety
| Flag | Effect |
|------|--------|
| `--dangerously-skip-permissions` | Auto-approve ALL tool use |
| `--permission-mode <mode>` | `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `--allowedTools <tools...>` | Whitelist specific tools |
| `--disallowedTools <tools...>` | Blacklist specific tools |

### Output & Input Format
| Flag | Effect |
|------|--------|
| `--output-format <fmt>` | `text` (default), `json`, `stream-json` |
| `--input-format <fmt>` | `text` (default), `stream-json` |
| `--json-schema <schema>` | Force structured JSON output matching a schema |
| `--verbose` | Full turn-by-turn output |
| `--replay-user-messages` | Re-emit user messages on stdout (bidirectional streaming) |

### System Prompt & Context
| Flag | Effect |
|------|--------|
| `--append-system-prompt <text>` | Add to the default system prompt |
| `--system-prompt <text>` | Replace the entire system prompt |
| `--bare` | Skip hooks, plugins, MCP discovery, CLAUDE.md, OAuth |
| `--agents '<json>'` | Define custom subagents dynamically |
| `--mcp-config <path>` | Load MCP servers from JSON file |

### Tool Name Syntax for --allowedTools / --disallowedTools
```
Read                    # All file reading
Edit                    # File editing (existing files)
Write                   # File creation (new files)
Bash                    # All shell commands
Bash(git *)             # Only git commands
Bash(git commit *)      # Only git commit commands
Bash(npm run lint:*)    # Pattern matching with wildcards
WebSearch               # Web search capability
mcp__<server>__<tool>   # Specific MCP tool
```

## Settings & Configuration

### Settings Hierarchy (highest to lowest priority)
1. **CLI flags** — override everything
2. **Local project:** `.claude/settings.local.json` (personal, gitignored)
3. **Project:** `.claude/settings.json` (shared, git-tracked)
4. **User:** `~/.claude/settings.json` (global)

### Permissions in Settings
```json
{
  "permissions": {
    "allow": ["Bash(npm run lint:*)", "WebSearch", "Read"],
    "ask": ["Write(*.ts)", "Bash(git push*)"],
    "deny": ["Read(.env)", "Bash(rm -rf *)"]
  }
}
```

## Interactive Session: Slash Commands

### Session & Context
| Command | Purpose |
|---------|---------|
| `/help` | Show all commands |
| `/compact [focus]` | Compress context to save tokens |
| `/clear` | Wipe conversation history |
| `/context` | Visualize context usage as colored grid |
| `/cost` | View token usage with per-model breakdowns |
| `/resume` | Switch to or resume a different session |
| `/rewind` | Revert to a previous checkpoint |
| `/btw <question>` | Side question without adding to context cost |

### Development & Review
| Command | Purpose |
|---------|---------|
| `/review` | Code review of current changes |
| `/security-review` | Security analysis |
| `/plan [description]` | Enter Plan mode |
| `/batch` | Auto-create worktrees for parallel changes |

### Configuration
| Command | Purpose |
|---------|---------|
| `/model [model]` | Switch models mid-session |
| `/effort [level] | Set reasoning effort |
| `/init` | Create CLAUDE.md |
| `/memory` | Open CLAUDE.md for editing |
| `/voice` | Enable push-to-talk voice mode |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Cancel current input or generation |
| `Ctrl+D` | Exit session |
| `Ctrl+B` | Background a running task |
| `Ctrl+V` | Paste image into conversation |
| `Ctrl+O` | Transcript mode — see thinking process |
| `Esc Esc` | Rewind conversation or code state |
| `Shift+Tab` | Cycle permission modes |
| `Alt+P` | Switch model |
| `Alt+T` | Toggle thinking mode |
| `!` | Execute bash directly (shell mode toggle) |
| `@` | Reference files/directories with autocomplete |
| `#` | Quick add to CLAUDE.md memory |

**Pro Tip:** Use "ultrathink" in your prompt for maximum reasoning effort on a specific turn.

## CLAUDE.md — Project Context File

Claude Code auto-loads `CLAUDE.md` from the project root:

```markdown
# Project: My API

## Architecture
- FastAPI backend with SQLAlchemy ORM

## Key Commands
- `make test` — run full test suite
- `make lint` — ruff + mypy

## Code Standards
- Type hints on all public functions
- 2-space indentation for YAML, 4-space for Python
```

**Rules directory** (modular CLAUDE.md):
- `.claude/rules/*.md` — team-shared, git-tracked
- `~/.claude/rules/*.md` — personal, global

## Custom Subagents

Define in `.claude/agents/` (project) or `~/.claude/agents/` (personal):

```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Security-focused code review
model: opus
tools: [Read, Bash]
---
You are a senior security engineer. Review code for injection vulnerabilities, auth flaws, secrets in code.
```

Invoke via: `@security-reviewer review the auth module`

## Hooks — Automation on Events

Configure in `.claude/settings.json` or `~/.claude/settings.json`:

| Hook | When it fires | Common use |
|------|--------------|------------|
| `UserPromptSubmit` | Before processing prompt | Input validation |
| `PreToolUse` | Before tool execution | Security gates (exit 2 = block) |
| `PostToolUse` | After tool finishes | Auto-format, linters |
| `Notification` | On permission requests | Desktop notifications |
| `Stop` | When Claude finishes response | Completion logging |
| `SubagentStop` | When subagent completes | Agent orchestration |
| `PreCompact` | Before context compression | Backup transcripts |
| `SessionStart` | Session begins | Load dev context |

## MCP Integration

```
# GitHub integration
terminal(command="claude mcp add -s user github -- npx @modelcontextprotocol/server-github", timeout=30)

# PostgreSQL queries
terminal(command="claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres --connection-string postgresql://localhost/mydb", timeout=30)
```

MCP Scopes: `-s user` (global), `-s local` (project, gitignored), `-s project` (project, git-tracked).

## Environment Variables

| Variable | Effect |
|----------|--------|
| `ANTHROPIC_API_KEY` | API key for authentication |
| `CLAUDE_CODE_EFFORT_LEVEL` | Default effort level |
| `MAX_THINKING_TOKENS` | Cap thinking tokens (0 to disable) |
| `MAX_MCP_OUTPUT_TOKENS` | Cap output from MCP servers |

## Cost & Performance Tips

1. **Use `--max-turns`** in print mode to prevent runaway loops (start with 5-10)
2. **Use `--max-budget-usd`** for cost caps (minimum ~$0.05 for system prompt cache)
3. **Use `--effort low`** for simple tasks; `high`/`max` for complex reasoning
4. **Use `--bare`** for CI/scripting to skip plugin/hook discovery
5. **Use `--allowedTools`** to restrict to only what's needed
6. **Use `/compact`** when context gets large (>70%)
7. **Pipe input** instead of having Claude read files for known content
8. **Use `--model haiku`** for simple tasks; `--model opus` for complex work
9. **Start new sessions for distinct tasks** — sessions last 5 hours
10. **Use `--no-session-persistence`** in CI to avoid accumulating saved sessions

## Claude Code-Specific Pitfalls

1. **Interactive mode REQUIRES tmux** — Claude Code is a full TUI app. tmux gives `capture-pane` and `send-keys` for orchestration.
2. **`--dangerously-skip-permissions` dialog defaults to "No, exit"** — must send Down then Enter. Print mode (`-p`) skips this entirely.
3. **`--max-budget-usd` minimum is ~$0.05** — system prompt cache creation alone costs this much.
4. **`--max-turns` is print-mode only** — ignored in interactive sessions.
5. **Claude may use `python` instead of `python3`** — self-corrects on first failure.
6. **Session resumption requires same directory** — `--continue` finds the most recent session for cwd.
7. **`--json-schema` needs enough `--max-turns`** — Claude must read files before producing structured output.
8. **Trust dialog only appears once per directory** — first-time only, then cached.
9. **Slash commands only work in interactive mode** — in `-p` mode, describe the task in natural language.
10. **`--bare` skips OAuth** — requires `ANTHROPIC_API_KEY` env var or `apiKeyHelper` in settings.
11. **Context degradation is real** — output quality degrades above 70% context window. Monitor with `/context`.
