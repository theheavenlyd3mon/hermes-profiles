## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes auth add PROVIDER --type oauth  OAuth device-code login. Replaces the removed `hermes login` command. Example: `hermes auth add nous --type oauth`
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
hermes skills install ID    Install a skill (ID can be a hub identifier OR a direct https://…/SKILL.md URL; pass --name to override when frontmatter has no name)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### Skills vs Plugins: How to Tell Them Apart

Skills and plugins are stored in different directories and serve different purposes. Misplaced items cause confusion — here's how to identify each.

| Attribute | Skill | Plugin |
|-----------|-------|--------|
| Manifest file | `SKILL.md` file with YAML frontmatter | `plugin.yaml` manifest |
| Content | Markdown methodology, guidelines, procedures | Python code (`__init__.py`, `*.py`), templates, scripts |
| Purpose | Instructs the agent on how to approach a task | Registers new tools the agent can call |
| Install location | `~/.hermes/skills/` or `~/.hermes/profiles/<name>/skills/` | `~/.hermes/plugins/` or `~/.hermes/profiles/<name>/plugins/` |
| Install command | `hermes skills install <id>` | `hermes plugins install <repo> --enable` |
| Execution | Read as context by the agent | Runs as Python subprocess within the agent |
| Has `.git/`? | Usually not (installed as files) | Often yes (cloned from GitHub) |

**Quick detection:** If the directory has `plugin.yaml` instead of `SKILL.md`, or contains Python files (`__init__.py`, `search.py`, etc.), it's a **plugin** — not a skill.

**How to fix a misplaced plugin** (found in `skills/` instead of `plugins/`):

```bash
# 1. Move to the right location
mv ~/.hermes/skills/web-search-plus ~/.hermes/plugins/web-search-plus

# 2. Install properly to register tools and enable
hermes plugins install <github-repo> --enable

# 3. Clean up the orphaned copy
rm -rf ~/.hermes/plugins/web-search-plus  # if install created a new copy in plugins/

# 4. Restart gateway for tools to appear
hermes gateway restart
```

**Look for these signals when auditing:**
- Directory has `plugin.yaml` → it's a plugin, move it
- Directory has `SKILL.md` → it's a skill, leave it
- Directory has Python files (`__init__.py`, `search.py`) but no `SKILL.md` → likely a plugin
- A plugin listed in `config.yaml` under `plugins.enabled:` but nowhere on disk → stale config entry, remove it

See `references/plugin-audit-methodology.md` for the full audit workflow: concrete commands to scan for misplaced plugins, detect duplicates, clean up orphans after install, and handle stale config entries.

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

Run real language servers (pyright, gopls, rust-analyzer, typescript-language-server, clangd, ~20 more) as background subprocesses. Their semantic diagnostics feed into the post-write lint check used by `write_file` and `patch` — catching **type errors, undefined names, missing imports, and project-wide semantic issues**, not just syntax errors.

**Gated on git workspace detection:** runs only when working directory is inside a git worktree. Outside git repos: LSP stays dormant. Check is layered — in-process syntax check first (microseconds), then LSP when syntax is clean. **Fails silently** — flaky/missing language server never breaks a write.

**Flow on every successful `write_file`/`patch`:**
1. Capture baseline diagnostics for the file
2. Perform the write
3. Re-query language server, filter out baseline, surface only new diagnostics

Example output field on write results:
```json
"lsp_diagnostics": "LSP diagnostics introduced by this edit:\n<diagnostics file=\"/path/to/foo.py\">\nERROR [42:5] Cannot find name 'foo' [reportUndefinedVariable] (Pyright)\n</diagnostics>"
```

#### CLI

```bash
hermes lsp status          # service state + per-server install status
hermes lsp list            # registry, optionally --installed-only
hermes lsp install <id>    # eagerly install one server
hermes lsp install-all     # try every server with a known recipe
hermes lsp restart         # tear down running clients
hermes lsp which <id>      # print resolved binary path
```

`hermes lsp status` is the best starting point — shows which languages will get semantic diagnostics today.

#### Supported Languages & Servers

| Language | Server | Install |
|----------|--------|---------|
| Python | `pyright-langserver` | auto (npm) |
| TypeScript/JS/JSX/TSX | `typescript-language-server` | auto (npm) |
| Vue | `@vue/language-server` | auto (npm) |
| Svelte | `svelte-language-server` | auto (npm) |
| Astro | `@astrojs/language-server` | auto (npm) |
| Go | `gopls` | auto (`go install`) |
| Rust | `rust-analyzer` | manual |
| C/C++ | `clangd` | manual (LLVM) |
| Bash/Zsh | `bash-language-server` | auto (npm) |
| YAML | `yaml-language-server` | auto (npm) |
| Lua | `lua-language-server` | manual |
| PHP | `intelephense` | auto (npm) |
| OCaml | `ocaml-lsp` | manual |
| Dockerfile | `dockerfile-language-server-nodejs` | auto (npm) |
| Terraform | `terraform-ls` | manual |
| Dart | `dart language-server` | manual |
| Haskell | `haskell-language-server` | manual |
| Julia | `julia` + LanguageServer.jl | manual |
| Clojure | `clojure-lsp` | manual |
| Nix | `nixd` | manual |
| Zig | `zls` | manual |
| Gleam | `gleam lsp` | manual |
| Elixir | `elixir-ls` | manual |
| Prisma | `prisma language-server` | manual |
| Kotlin | `kotlin-language-server` | manual |
| Java | `jdtls` | manual |

Manual entries: Hermes auto-detects binary on PATH or in `<HERMES_HOME>/lsp/bin/`.

**Note:** `typescript-language-server` requires `typescript` SDK importable from same `node_modules` — Hermes installs both when auto-install fires.

#### Configuration

```yaml
lsp:
  enabled: true                   # Master toggle
  wait_mode: document             # "document" or "full"
  wait_timeout: 5.0              # Seconds to wait for diagnostics
  install_strategy: auto          # "auto" or "manual"
  servers:
    pyright:
      disabled: false
      command: ["/abs/path/to/pyright-langserver", "--stdio"]
      env: { PYRIGHT_LOG_LEVEL: "info" }
      initialization_options:
        python:
          analysis:
            typeCheckingMode: "strict"
    typescript:
      disabled: true              # skip TS even when extensions match
```

Per-server keys:
- `disabled: true` — skip server entirely
- `command: [bin, ...args]` — pin custom binary path (bypasses auto-install)
- `env: {KEY: value}` — extra env vars for the process
- `initialization_options: {...}` — merged into LSP `initializationOptions` payload (server-specific)

**Status as of v0.13.0:** This feature landed as a **post-release addition** (May 12, 2026, after v2026.5.7). It builds on the v0.13.0 post-write delta lint feature. Available on HEAD but not yet in any tagged release.

**Docs:** https://hermes-agent.nousresearch.com/docs/user-guide/features/lsp

### hermesd — TUI Monitoring Dashboard

`hermesd` is a separate TUI process that provides a live dashboard of gateway status, sessions, token/cost, cron jobs, tools, skills, logs, and memory. It reads from `gateway_state.json`, `channel_directory.json`, `state.db`, `lcm.db`, `cron/jobs.json`, and the gateway log.

**Important:** The `--profile senna` flag is currently broken (`Error: Profile 'senna' does not exist`). Workaround: run `hermesd` without `--profile` — it still detects the running gateway via process scan and shows correct data.

Key panels:
- **Panel 1**: Gateway status + platform connections (api_server, telegram, etc.)
- **Panel 2**: Active/total sessions, message count, tool calls
- **Panel 3**: Token usage, cache hits, estimated cost (today + all-time)
- **Panel 6**: Cron jobs, schedules, error count
- **Panel 8**: Live log tail
- **Panel 9**: Profile data source (shows "root" when no `--profile`)

See `references/hermesd-monitoring.md` for the full panel breakdown, data source layout, gateway_state.json schema, and troubleshooting steps.
See `references/hermesd-profile-sandbox-path.md` for the profile sandbox $HOME resolution issue when using `--profile`.

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), **API Server**, Webhooks. Open WebUI connects via the API Server adapter.

**User-specific optimization reference:** see `references/senna-profile-optimization-audit.md` for the read-only audit sequence, Senna lean-profile config, pnpm-cache disk finding, and gateway/workspace alignment rule discovered during the 2026-05 Senna optimization session.

**Capability inventory reference:** see `references/capability-inventory-audit.md` for the systematic methodology to catalog every plugin and skill, cross-reference against config, and assess cron-automation feasibility with a tiered risk/value/complexity framework. Use this when the user asks "review all my plugins and skills" or "what can run on a schedule."

**Important:** Do NOT use `~/.hermes/archive/.env` for active API keys — that directory holds state snapshots only. Place keys in either the root `.env` (shared across all profiles) or profile-specific `.env` (takes precedence). See `references/env-architecture.md` for the full loading-order guide and consolidation strategy.

**API Server environment variable:** Set `API_SERVER_ENABLED=true` in `~/.hermes/profiles/<profile>/.env` to expose the gateway's OpenAI-compatible HTTP API on port 8642. Without this, the gateway runs with only internal TUI pipes — chat UIs and third-party tools cannot connect. This variable must be set **before** the gateway starts, because it is snapshotted at process startup.

```bash
# Persist for all future gateway starts
echo "API_SERVER_ENABLED=true" >> ~/.hermes/profiles/senna/.env
```

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Gateway Consolidation: Moving Platform Config to Root

When a profile (e.g. Senna) has platform keys like `TELEGRAM_BOT_TOKEN` in its own `.env` while the root `.env` has the same keys commented out, you get a confusing two-gateway situation — the default profile's gateway can't serve Telegram, but the profile-specific gateway can. The fix mirrors the plugins symlink pattern: move the canonical source to root, then make that profile the default.

**Diagnosis — when there might be a problem:**
```bash
grep "^TELEGRAM_BOT_TOKEN" ~/.hermes/.env                    # root — active?
grep "^TELEGRAM_BOT_TOKEN" ~/.hermes/profiles/senna/.env     # profile — active or commented?
hermes gateway status                                           # which profile's gateway is running?
hermes profile list                                             # which profile is default (◆)?
ps aux | grep -i "hermes.*gateway" | grep -v grep              # how many gateways are running?
```

**Consolidation workflow (4 steps):**

1. **Move the keys from profile .env to root .env** — copy the active lines (e.g. `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `TELEGRAM_HOME_CHANNEL`) from `~/.hermes/profiles/<name>/.env` to `~/.hermes/.env`, replacing the commented-out placeholders.

2. **Remove the active keys from the profile .env** — so root values win (profile loads second and overrides on duplicates):
   ```bash
   sed -i '' '/^TELEGRAM_BOT_TOKEN=/d' ~/.hermes/profiles/<name>/.env
   sed -i '' '/^TELEGRAM_ALLOWED_USERS=/d' ~/.hermes/profiles/<name>/.env
   ```
   Verify only comments remain: `grep "TELEGRAM" ~/.hermes/profiles/<name>/.env`

3. **Make the profile the sticky default:**
   ```bash
   hermes profile use <name>
   ```
   Now `hermes gateway start` (without `--profile`) runs this profile.

4. **Stop the old default gateway and start the new one:**
   ```bash
   hermes --profile default gateway stop    # stop the useless one
   hermes gateway start                     # starts <name> (now the default)
   ```

**Pitfall — what if the old default profile has NO directory?** The profile list may show a "default" profile with a running gateway, but `ls ~/.hermes/profiles/default/` returns nothing. This is fine — it's using the root config directly. `hermes --profile default gateway stop` handles it. The key verification is `hermes profile list` showing the old default as "stopped" and your profile with the ◆ marker as "running".

**Verification:**
```bash
hermes profile list                     # ◆ should be on <name>, default should be stopped
hermes gateway status                   # should show <name>'s launchd plist loaded, PID running
ps aux | grep -i "hermes" | grep -v grep  # one gateway process (launchd with ?? terminal)
```

**When to do this vs leaving it per-profile:**
- **Do it** when a profile is your primary/daily driver and you want `hermes gateway start` to "just work" without `--profile` flags
- **Don't do it** if you need multiple profiles with different platform bots running concurrently (rare)

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

```bash
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Cron Automation Design Patterns

When designing cron automations for a user, consider these patterns:

**Delivery modes:**
- `deliver: local` — silent execution. Use for maintenance tasks (memory consolidation, session pruning, backups) where only errors matter.
- `deliver: origin` — reports to the user's home channel (e.g. Telegram). Use for briefing summaries, weekly reports, and any output the user should see.
- Omit (defaults to origin) — same as explicit origin.

**Pipeline ordering:** Stack jobs so earlier ones feed later ones naturally. Example overnight pipeline:
```
2am — knowledge work (wiki research, web crawling)  [deliver: local]
3am — memory consolidation                           [deliver: local]
4am — integrity checks (wiki lint, health check)     [deliver: local]
5am — cleanup (session prune, temp file cleanup)     [deliver: local]
7am — user briefing (summarizes overnight results)   [deliver: origin]
```

**Silent vs. reporting:** Maintenance jobs should be silent unless errors occur. Reporting jobs should deliver to the user. The morning briefing cron can pick up and summarize results from earlier silent jobs.

**User preference for automation:** Users who want to "minimise the extra user input and automate it" benefit from a complete overnight pipeline. Walk them through what each job does, confirm their interest, then set them up in batch. Reference: `references/cron-automation-patterns.md` for full session examples.

**Memory consolidation via cron:** The `sleep_all_sessions()` call on Mnemosyne consolidates old working memory into episodic summaries. This is the mechanism behind the `3am — memory consolidation` job. However, inside a profile cron context, `Path.home()` resolves to the sandboxed profile home — so Mnemosyne's `_default_db_path()` silently targets the wrong database. **Always pass the global db_path explicitly.** See `references/mnemosyne-consolidation-cron.md` for the exact API invocation, the db_path pitfall, the fix, and a ready-to-use cron prompt template.

**no_agent mode for deterministic checks:** Some cron jobs only need to run shell commands and report output — no LLM reasoning needed. Examples: `npm audit`, `du` disk checks, `find` file scans, health pings. For these, use **no_agent mode** with a `script=` field instead of the default agent-based mode.

```bash
cronjob update JOB_ID --script "my-scan.sh" --no-agent true
```

The script runs `bash ~/.hermes/profiles/<profile>/scripts/<script>` each tick. On success, its stdout is delivered verbatim. On empty stdout, nothing is sent (silent tick). On failure, an error alert is generated.

**When to use no_agent vs agent-based:**

| Concern | no_agent (script) | Agent-based (default) |
|---------|-------------------|-----------------------|
| Reliability | Maximal — shell always runs | Depends on skill loading + LLM availability |
| Cost | Zero tokens | Token cost per run |
| Output | Raw script stdout | LLM-synthesized summary |
| Research/web access | No (pure shell) | Full tool access |
| Best for | `npm audit`, disk usage, file counts, health pings | Web research, knowledge synthesis, multi-step reasoning |

**Pitfall:** An agent-based cron job that only runs deterministic shell commands can fail silently when skill loading or tool execution times out in the short-lived cron session environment. The error message won't persist in LCM for debugging. If your agent-based cron job keeps erroring with no visible output, convert it to no_agent script mode. See the supply-chain-hardening skill (`security/supply-chain-hardening/SKILL.md`, pitfall #7) for a real example of this conversion.

### Gateway Consolidation (Profile Streamlining)

When a user has multiple profile gateways (e.g. a "default" gateway and a "senna" gateway), consolidate to one:

1. **Move canonical config to root** — API keys, bot tokens, and path vars belong in `~/.hermes/.env` (root), not in profile `.env`. Profile `.env` should only contain overrides for things that genuinely differ per profile.
2. **Set the target profile as default** — `hermes profile use <name>` makes it the sticky default so `hermes gateway start` (no `--profile` flag) runs the right one.
3. **Stop the old gateway** — `hermes --profile <old> gateway stop`
4. **Start the new unified gateway** — `hermes gateway start` (now runs the target profile)

This mirrors the plugins symlink pattern: canonical source in one place, all profiles inherit. Verifiable with `hermes profile list` (◆ marks the default) and `hermes gateway status`.

See `references/gateway-consolidation.md` for a full walkthrough with before/after states.

**Service watchdog pattern:** see `references/cron-watchdog-pattern.md` for using cron jobs to auto-start dependent services (e.g., workspace dashboard) when the gateway is healthy. Includes port health checks, the two-dashboard architecture (built-in vs workspace), and a full service sweep script.

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profile Model Batch Updates

When the user wants to change the model across multiple specialist profiles simultaneously:

**Context:** Each profile has its own `config.yaml` with `model.default: <model-string>` and `model.provider: <provider>`. The Kanban `--assignee` flag routes to a profile, but the model used is set by that profile's `config.yaml`.

**Batch update all profiles:**
```bash
for p in architect coder reviewer debugger researcher devops security foreman secretary data-analyst; do
  sed -i '' 's|default: <old-model>|default: <new-model>|g' ~/.hermes/profiles/$p/config.yaml
done
```

**Verify:**
```bash
grep 'default:' ~/.hermes/profiles/*/config.yaml
```

**Note:** Use absolute paths (`~/.hermes/profiles/...`) when running inside a profile sandboxed context — `~/.hermes` may resolve incorrectly. `hermes model` requires an interactive terminal; `sed` direct-edit is the non-interactive path.

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

**Important: OAuth credentials are per-profile.** `hermes login --provider nous` stores the token in the **current profile's** `auth.json`. Team profiles spawned by Kanban have their own separate credential pools that start empty. If you authenticate in one profile (e.g. Senna) and your Kanban workers all crash with `protocol_violation`, the auth token likely doesn't exist in the team profiles. See `references/auth-consolidation-pattern.md` for the symlink-based fix (mirrors the plugins pattern: one canonical `auth.json` at root, all profiles symlink to it).

#### Credential pools are per-profile — they do not share

This is the most important thing to understand: **each profile has its own isolated credential pool**, stored in `~/.hermes/profiles/<name>/auth.json`. The root `~/.hermes/auth.json` does NOT exist unless created directly (and even then, may not be read by profile-scoped agents).

When you run `hermes login --provider nous` or `hermes auth add`, the credential is stored in the **current profile's** `auth.json` only. Other profiles (architect, coder, etc.) have their own empty pools and cannot see it.

**How this differs from `.env`:** API keys in `.env` follow a root-then-profile loading order (root is the default, profile overrides). Credential pools have NO inheritance — each profile starts with an empty `auth.json` and must be populated individually.

**Signs of an empty credential pool:**
- `hermes auth list <provider>` returns nothing when run from a team profile
- The profile directory has `auth.lock` (0 bytes lock file) but no `auth.json`
- A kanban worker assigned to this profile crashes with `protocol_violation` because it can't authenticate to its configured provider

**How to check which profiles have credentials:**
```bash
for p in architect coder debugger reviewer; do
  json="~/.hermes/profiles/$p/auth.json"
  if [ -f "$json" ]; then
    echo "$p: $(python3 -c \"import json; d=json.load(open('$json')); print(d.get('providers', d.get('credential_pool', '??')))\" 2>/dev/null || echo 'has auth.json')"
  else
    echo "$p: no auth.json — empty pool"
  fi
done
```

#### Syncing credentials across profiles

If one profile (e.g. Senna) has successfully authenticated with an OAuth provider (e.g. Nous Portal), you have two options to make that credential available to other profiles:

**Option A — Copy `auth.json` (fastest):**
```bash
cp ~/.hermes/profiles/senna/auth.json \
   ~/.hermes/profiles/architect/
```
This replicates the entire credential pool. Works because OAuth tokens are just serialized data — they don't depend on the profile name.

**Option B — Run login per profile (more correct):**
```bash
hermes -p architect login --provider nous
hermes -p coder login --provider nous
```
Each profile runs its own OAuth device-code flow. Time-consuming but guarantees each auth is fresh.

**Option C — Symlink to root (preferred for unified setups):** Mirrors the plugins symlink pattern. Create a canonical `auth.json` at root, then symlink from every profile:

```bash
# 1. Copy canonical auth.json to root
cp ~/.hermes/profiles/senna/auth.json ~/.hermes/auth.json

# 2. Replace source profile's copy with symlink (backup first)
mv ~/.hermes/profiles/senna/auth.json \
   ~/.hermes/profiles/senna/auth.json.bak
ln -s ~/.hermes/auth.json ~/.hermes/profiles/senna/auth.json

# 3. Create symlinks in all team profiles
for p in architect coder debugger reviewer; do
  ln -s ~/.hermes/auth.json ~/.hermes/profiles/$p/auth.json
done

# 4. Verify
for p in architect coder debugger reviewer senna; do
  target=$(readlink ~/.hermes/profiles/$p/auth.json 2>/dev/null)
  echo "$p -> $target"
done
```

Now all profiles share one canonical `auth.json` at `~/.hermes/auth.json`. Any profile that obtains a new OAuth token updates the shared file. The `auth.lock` files (0-byte mutexes) remain per-profile and are not symlinked.

See `references/profile-auth-architecture.md` for the full architecture and verification steps.

**For API-key-based providers** (OpenRouter, DeepSeek, etc.): keys in `.env` work across all profiles naturally (root `.env` is the canonical source). Only OAuth tokens (Nous Portal, OpenAI Codex, Qwen OAuth) are per-profile and need this sync step.

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

