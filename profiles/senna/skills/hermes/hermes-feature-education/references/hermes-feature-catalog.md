# Hermes Feature Catalog

Comprehensive reference of all Hermes Agent features, organized by category. Generated from a feature-education session (June 2026, v0.17.0). Use as a lookup when educating users or exploring capabilities.

## A. Slash Commands (In-Session)

### Session Control
| Command | Description |
|---------|-------------|
| `/new` (`/reset`) | Fresh session |
| `/clear` | Clear screen + new session (CLI) |
| `/retry` | Resend last message |
| `/undo` | Remove last exchange |
| `/title [name]` | Name the session |
| `/compress` | Manually compress context |
| `/stop` | Kill background processes |
| `/rollback [N]` | Restore filesystem checkpoint |
| `/background <prompt>` | Run prompt in background |
| `/queue <prompt>` | Queue for next turn |
| `/resume [name]` | Resume a named session |

### Configuration
| Command | Description |
|---------|-------------|
| `/config` | Show config (CLI) |
| `/model [name]` | Show or change model |
| `/personality [name]` | Set personality (15+ built-in) |
| `/reasoning [level]` | Set reasoning (none/minimal/low/medium/high/xhigh/show/hide) |
| `/verbose` | Cycle verbosity |
| `/voice [on/off/tts]` | Voice mode |
| `/yolo` | Toggle approval bypass |
| `/skin [name]` | Change theme (CLI) |
| `/statusbar` | Toggle status bar (CLI) |

### Tools & Skills
| Command | Description |
|---------|-------------|
| `/tools` | Manage tools (CLI) |
| `/toolsets` | List toolsets (CLI) |
| `/skills` | Search/install skills (CLI) |
| `/skill <name>` | Load a skill into session |
| `/cron` | Manage cron jobs (CLI) |
| `/reload-mcp` | Reload MCP servers |
| `/plugins` | List plugins (CLI) |

### Gateway
| Command | Description |
|---------|-------------|
| `/approve` | Approve pending command (gateway) |
| `/deny` | Deny pending command (gateway) |
| `/restart` | Restart gateway (gateway) |
| `/sethome` | Set current chat as home channel |
| `/update` | Update Hermes to latest |
| `/platforms` (`/gateway`) | Show platform connections |

### Utility
| Command | Description |
|---------|-------------|
| `/branch` (`/fork`) | Branch current session |
| `/fast` | Toggle priority processing |
| `/browser` | Open CDP browser connection |
| `/history` | Show conversation history (CLI) |
| `/save` | Save conversation to file (CLI) |
| `/paste` | Attach clipboard image (CLI) |
| `/image` | Attach local image file (CLI) |

### Info
| Command | Description |
|---------|-------------|
| `/help` | Show commands |
| `/commands [page]` | Browse all commands (gateway) |
| `/usage` | Token usage |
| `/insights [days]` | Usage analytics |
| `/status` | Session info (gateway) |
| `/profile` | Active profile info |
| `/quit` (`/exit`, `/q`) | Exit CLI |

## B. CLI Commands (Outside Session)

### Global Flags
```
hermes [flags] [command]
  --version/-V        Show version
  --resume/-r SESSION Resume session by ID or title
  --continue/-c [NAME] Resume by name, or most recent
  --worktree/-w       Isolated git worktree mode
  --skills/-s SKILL   Preload skills (comma-separate)
  --profile/-p NAME   Use a named profile
  --yolo              Skip dangerous command approval
```

### Chat
```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model override
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner/spinner
  --checkpoints             Enable filesystem checkpoints
  --source TAG              Session source tag (default: cli)
```

### Configuration
```
hermes setup [section]      Interactive wizard
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes auth add PROVIDER --type oauth  OAuth login
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills
```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (hub ID or URL)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers
```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### LSP — Semantic Diagnostics
```
hermes lsp status           Service state + per-server install status
hermes lsp list             Registry, optionally --installed-only
hermes lsp install <id>     Eagerly install one server
hermes lsp install-all      Try every server with a known recipe
hermes lsp restart          Tear down running clients
hermes lsp which <id>       Print resolved binary path
```

### Gateway
```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, DingTalk, Feishu, WeCom, Weixin, BlueBubbles (iMessage), Home Assistant, Teams, Google Chat (20+), **API Server**, Webhooks.

### Sessions
```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs
```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks
```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles
```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools
```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other
```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
hermesd                     TUI monitoring dashboard
```

## C. Toolset Reference

Available toolsets (toggled via `hermes tools`):

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |

Tool changes take effect on `/reset` (new session).

## D. Eikons

Eikons are animated ASCII art avatars for the Hermes TUI. Displayed in the terminal header with animation, color, and a glyph icon.

### Commands
```
hermes eikon search [query]     Browse catalog
hermes eikon install <name>     Install from public catalog or URL
hermes eikon list               List installed eikons
hermes eikon use <name>         Activate an eikon
hermes eikon update <name>      Update an installed eikon
hermes eikon remove <name>      Remove an eikon
```

### Catalog (June 2026)
- **ares** — warrior/sword theme, purple palette, 48x24, 65 frames at 16 FPS, author: kaio
- **mono** — minimal style, author: kaio
- **nous** — Nous Research branded, author: kaio (may have empty file on some installs)
- **nous-cat** — cat variant, author: TunaDev
- **ovo** — egg/ominous shape, author: kaio

### File Format
An eikon is a `.eikon` JSON file containing:
- Metadata: name, width, height, author, glyph, source_url
- Animation states: each state has fps, color, frame_count, loop_from
- Frame data: each frame has f (frame number), data (ASCII art lines)

## E. ACP — Agent Communication Protocol

ACP is a standard that lets Hermes interoperate with other agent frameworks:
- **GitHub Copilot CLI** — spawn Copilot as a subagent
- **OpenClaw / Codex / Claude Code** — any ACP-compatible agent
- Other ACP clients connect *to* Hermes when it runs in `hermes acp` mode

### Commands
```
hermes acp   # start Hermes as an ACP server (listens for IDE/agent connections)
```

### How Delegation Works
When `delegate_task` is called without an ACP CLI configured, Hermes spawns Hermes subagents (default). With an ACP CLI configured (set `delegation.acp_command` in config.yaml), `delegate_task` spawns that CLI's agent instead.

ACP subagents have: isolated conversation, isolated terminal session, bounded duration, no user interaction capability.

## F. LSP — Language Server Protocol (Semantic Diagnostics)

Hermes runs full language servers as background subprocesses. After every `write_file` or `patch`, the agent sees **semantic diagnostics** — type errors, undefined names, missing imports, project-wide issues — not just syntax errors.

### Supported Languages (26 total)
Python (pyright), TypeScript/JS/JSX/TSX, Vue, Svelte, Astro, Go (gopls), Rust (rust-analyzer), C/C++ (clangd), Bash/Zsh, YAML, Lua, PHP, OCaml, Dockerfile, Terraform, Dart, Haskell, Julia, Clojure, Nix, Zig, Gleam, Elixir, Prisma, Kotlin, Java

### When LSP Runs
- Gated on **git workspace detection** — inside a git repo only
- Outside git: stays dormant (syntax check only)
- Check is layered: syntax check first (microseconds), then LSP

### Example `lsp status` Output
```
LSP Service
  enabled:         True
  wait_mode:       document
  wait_timeout:    5.0s
  active clients:  none

Registered Servers
  ✓ pyright                  [installed  ] .py, .pyi
  ✓ typescript               [installed  ] .ts, .tsx, .js, .jsx, .mjs, …
  · vue-language-server      [missing    ] .vue
  ? rust-analyzer            [manual-only] .rs
  ✓ clangd                   [installed  ] .c, .cpp, .cc, .h, …
```

### Key Config
```yaml
lsp:
  enabled: true              # Master toggle
  wait_mode: document        # "document" or "full"
  wait_timeout: 5.0
  install_strategy: auto     # "auto" or "manual"
  servers:
    pyright:
      disabled: false
      command: ["/path/to/pyright-langserver", "--stdio"]
```

## G. Cron Jobs — Advanced Modes

### Schedule Formats
- Relative: `30m`, `2h`, `1d`
- Interval: `every 30m`, `every 2h`, `every 1d`
- Cron: `0 9 * * *`, `0 9 * * 1-5`, `0 */6 * * *`
- ISO: `2026-06-01T09:00:00`

### Delivery Options
- `origin` — back to where the job was created
- `local` — save to local files only
- `telegram`, `discord`, `slack`, `whatsapp`, `signal`, `matrix`, `email`, `sms`, `homeassistant`, `feishu`, etc.
- `all` — fan out to every connected home channel
- `origin,all` — origin plus all other channels

### No-Agent Mode
For pure script watchdogs (disk/memory/uptime checks). Zero LLM cost.
```
cronjob(action="create", schedule="every 5m",
        script="memory-watchdog.sh", no_agent=True,
        deliver="telegram", name="memory-watchdog")
```
Empty stdout = silent tick. Non-zero exit = error alert.

### WakeAgent Gate
A pre-check script emits `{"wakeAgent": false}` to skip the LLM run when nothing changed. Skips $0 ticks.

### Job Chaining (context_from)
Job B receives Job A's output as context prepended to its prompt.
```python
cronjob(action="create", schedule="30 7 * * *",
        context_from="<job1_id>",
        prompt="Process the data from the collector job.")
```

## H. Session Statistics Reference

Common session DB stats from production use:
- 1,224 sessions / 50,826 messages / 748.7 MB is a real measured data point (Senna profile, June 2026)
- Breakdown: 334 CLI, 29 Telegram, 66 Discord
- Prune command: `hermes sessions prune --older-than N` (N = days)

## I. Personality System

### Built-in Personalities
`helpful`, `concise`, `technical`, `creative`, `teacher`, `kawaii`, `catgirl`, `pirate`, `shakespeare`, `surfer`, `noir`, `uwu`, `philosopher`, `hype`

### Custom Personalities
Define in `~/.hermes/config.yaml`:
```yaml
agent:
  personalities:
    codereviewer: >
      You are a meticulous code reviewer. Identify bugs, security issues,
      performance concerns, and unclear design choices. Be precise and constructive.
```
Switch with `/personality codereviewer`.

## J. Context Files

| File | Purpose | Discovery |
|------|---------|-----------|
| `.hermes.md` / `HERMES.md` | Project instructions (highest priority) | Walks to git root |
| `AGENTS.md` | Project instructions, conventions, architecture | CWD + subdirectories |
| `CLAUDE.md` | Claude Code context files | CWD + subdirectories |
| `SOUL.md` | Global personality/identity | `HERMES_HOME/SOUL.md` only |
| `.cursorrules` | Cursor IDE conventions | CWD only |
| `.cursor/rules/*.mdc` | Cursor IDE rule modules | CWD only |

Priority: `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`. Only one project type loads per session. `SOUL.md` always loads independently.

Progressive subdirectory discovery: reads `frontend/AGENTS.md` when you touch frontend files, etc. No system prompt bloat.

## K. Skills vs Plugins

| Attribute | Skill | Plugin |
|-----------|-------|--------|
| Manifest | `SKILL.md` with YAML frontmatter | `plugin.yaml` |
| Content | Markdown methodology, guidelines | Python code (`__init__.py`) |
| Purpose | Instructs agent | Registers new tools |
| Location | `skills/` dir | `plugins/` dir |
| Install command | `hermes skills install` | `hermes plugins install` |
| Execution | Read as context | Runs as Python subprocess |

## L. Recommended First Actions (For New Users)

1. **Prune old sessions** — if 500+ sessions, reclaim space
2. **Edit `~/.hermes/SOUL.md`** — set your identity
3. **Drop `AGENTS.md` in projects** — so the agent knows architecture
4. **`hermes lsp status`** — see what language servers are ready
5. **Run `hermesd`** — TUI dashboard to see live activity
6. **Try `/personality concise` or `/personality noir`** — instant voice change
7. **Explore `/model`** — hot-swap models mid-session
8. **Set up a cron watchdog** — e.g., RAM/disk alert
9. **Browse eikons** — install an avatar
