---
name: hermes-maintenance
description: "Hermes maintenance: plugin audits, pre-update checks, health diagnostics. Use when auditing plugins/tools, preparing for hermes update, or diagnosing Hermes issues."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, audit, plugins, tools, diagnostics, health-check, update, maintenance]
    related_skills: [hermes-agent, system-audit]
---

IDENTITY: Auditor.Inspector. Audit Hermes plugins and tools — cross-reference `hermes plugins list` against actual API key availability, because "enabled" in the plugin list ≠ functional.
Law: EnabledInPluginListCheckDoesNotMeanFunctional — always verify key-gated plugins against actual .env.
WHENUSE: UserAsks{AuditMySetup,WhatPluginsDoIHave,WhatsActive}|AfterNewPluginInstall|Troubleshooting{WhyDoesntXWork,PluginShowsEnabledButFails}|PeriodicHealthCheck. ESPECIALLY:PluginShowsEnabledInBothLists->ButZeroKeysMeansSilentFailure. NoSkip:KeyGatedPluginDeepDive{check plugin.yaml requires_env vs actual .env}.
REDFLAGS: SecretTruncationViaPatchTool->UseTerminalOperationsForEnvEdits|ProfileScopedEnv->$HERMES_HOME/.env only, root never loaded|GitVsBundledPlugins->CheckBothLocations|EmptyRequiresEnvButKeysInOptionalEnv->DegradedCapability.
RATIONALIZATIONS: PluginIsEnabledItWorks->webSearchPlusCanonicalCounterExample|JustCheckPluginList->MustVerifyKeyHealth|EditEnvWithPatchTool->ReadFileDisplayTruncatesLongValues.
QUICKREF: Inventory{hermesPluginsList{name,status,version,source}+hermesToolsList{built-in+pluginToolsets}}->DeepDive{ForEachKeyGatedPlugin{FindPluginYaml,CheckRequiresEnv+OptionalEnv,CompareAgainstActiveEnv,RunSetup.pyStatus}}->Render{FullyFunctional->PartiallyFunctional->NonFunctional}->Report{PluginsSummary, ToolsetsSummary, KeyGatedHealthTable, OneSentenceExplanations}.

Audit installed plugins and built-in toolsets: what's active, what's inactive, and — critically — which "enabled" plugins are non-functional because of missing API keys.

## When to Use

- User asks "what plugins/tools do I have?", "what's active?", "audit my setup"
- After installing new plugins — verify they're functional, not just loaded
- Troubleshooting "why doesn't X work?" when the plugin shows as enabled
- Periodic health check on a Hermes installation

## Core Principle

**"Enabled" in the plugin list ≠ functional.** A plugin can be loaded and its tools registered, but if it depends on external API keys and none are set, every tool call will silently fail. Always cross-reference `plugin.yaml`'s `requires_env` / `optional_env` against the actual `.env` file.

## Step 1 — Plugin Inventory

```bash
hermes plugins list
```

This gives: name, status (enabled/not enabled), version, description, source (bundled/git).

Note which are **enabled** and which are **not enabled**.

## Step 2 — Built-in Toolset Inventory

```bash
hermes tools list
```

Two sections:
- **Built-in toolsets** — core Hermes tools (web, browser, terminal, file, code_execution, vision, image_gen, tts, skills, todo, memory, session_search, clarify, delegation, cronjob, messaging, computer_use, video, moa, rl, homeassistant, spotify, yuanbao)
- **Plugin toolsets** — tools provided by enabled plugins (fabric from icarus, web-search-plus tools, etc.)

Note which are ✓ enabled vs ✗ disabled.

## Step 3 — Key-Gated Plugin Deep Dive

For every **enabled** plugin that has `requires_env` or `optional_env` in its plugin.yaml, check whether the required keys actually exist.

### Find the plugin.yaml

```bash
# Bundled plugins
find ~/.hermes/hermes-agent/plugins -name "plugin.yaml" | xargs grep -l "<plugin-name>"

# Git-installed plugins (root or profile-local)
cat ~/.hermes/plugins/<plugin-name>/plugin.yaml
# Or: cat "$HERMES_HOME/plugins/<plugin-name>/plugin.yaml"
```

### Check what keys it needs

Look for `requires_env` (hard requirements, plugin won't work without them) and `optional_env` (the plugin works with any subset, but needs at least one for functionality).

### Compare against the active .env

```bash
# Find the effective .env (profile-level when active, root when not)
grep -E "KEY_NAME_1|KEY_NAME_2" "$HERMES_HOME/.env"
```

If the plugin has a `setup.py status` command, run it:

```bash
python3 ~/.hermes/plugins/<plugin-name>/setup.py status
```

### Render the verdict

For each key-gated plugin, report:
- **Fully functional** — all required keys present
- **Partially functional** — some optional keys present, limited routing
- **Non-functional** — zero keys configured (plugin is loaded but unusable)

## Step 4 — Update Check

### Git-Sourced Plugins

For plugins installed from git sources, periodically check whether updates are available. The `hermes plugins list` output shows the `Source` column — `git` means updateable, `bundled` means it ships with Hermes itself.

### Find the plugin repository

Git plugins can live in two locations:

```bash
# Root plugins (shared across profiles)
ls ~/.hermes/plugins/

# Profile-local plugins (scoped to active profile — uses $HERMES_HOME)
ls "$HERMES_HOME/plugins/"
```

Some plugins are symlinked between both locations. Check both.

> **⚠️ `~` and `$HOME` are unreliable here.** When a Hermes profile is active, `$HOME` is overridden to the profile's sandbox directory (e.g. `~/.hermes/profiles/senna/home`). This means `~/.hermes/plugins/` silently resolves to a nonexistent doubled path like `.../senna/home/.hermes/plugins/`. Always use the absolute real-user-home path for root plugins, and `$HERMES_HOME` for profile-local ones.

### Check for available updates

```bash
# Use absolute path for root plugins, $HERMES_HOME for profile-local
cd ~/.hermes/plugins/<plugin-name>
# Or: cd "$HERMES_HOME/plugins/<plugin-name>"

# Fetch latest from origin without merging
git remote update

# How many commits behind origin/main?
git rev-list HEAD..origin/main --count

# What's the latest version tag?
git tag -l 'v*' --sort=-version:refname | head -3

# See what changed
git log --oneline HEAD..origin/main | head -10
```

For plugins on a branch other than `main`, substitute `origin/<branch-name>` in the commands above.

### Apply the update

```bash
hermes plugins update <plugin-name>
```

This runs `git pull` in the plugin's working directory.

### Profile-scoped plugin paths

Git plugins installed per-profile (e.g. `profiles/senna/plugins/icarus/`) won't be found at the root `~/.hermes/plugins/` path. Check the active profile's plugins directory as shown above.

For a compact command reference, pitfalls, and plugin-source semantics, see `references/plugin-update-check.md`.

### Pip-Installed Plugins (e.g. Mnemosyne)

Some plugins are installed as pip packages in the Hermes venv, not as git repos. They may appear as symlinks in the plugins directory but won't show in `hermes plugins list` with a `git` source. Mnemosyne (`mnemosyne-memory`) is the canonical example — symlinked from `hermes_memory_provider/` in site-packages.

To check for updates:
```bash
# Find the venv's pip (pip3, not pip — pip may not exist)
HERMES_VENV=$(dirname $(dirname $(which python3 2>/dev/null || echo "~/.hermes/hermes-agent/venv/bin/python3")))
# Or check known locations:
ls ~/.hermes/hermes-agent/venv/bin/pip3

# Check installed vs available
HERMES_PIP="~/.hermes/hermes-agent/venv/bin/pip3"
$HERMES_PIP show mnemosyne-memory 2>/dev/null | grep Version

# Upgrade
$HERMES_PIP install --upgrade mnemosyne-memory
```

To find which pip packages are plugin-related:
```bash
$HERMES_PIP list 2>/dev/null | grep -iE "mnemosyne|hermes-memory|memory-provider"
```

After upgrading, verify the plugin still loads:
```bash
hermes mnemosyne stats 2>&1 | head -5
```

### Bundled Plugins

Bundled plugins update when Hermes itself updates (`hermes update`). No separate pull needed.

## Step 5 — Known Provider-Key Mappings

Common plugins and their key dependencies:

| Plugin/Toolset | Key(s) | Where to get it |
|---|---|---|
| web-search-plus | TAVILY_API_KEY, BRAVE_API_KEY, SERPER_API_KEY (any 1+) | tavily.com, api.search.brave.com, serper.dev |
| spotify | SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET | developer.spotify.com |
| google_meet | GOOGLE_APPLICATION_CREDENTIALS | GCP console |
| image_gen (FAL) | FAL_KEY (or Nous managed gateway — no key needed) | fal.ai/dashboard/keys |
| image_gen (OpenAI) | OPENAI_API_KEY | platform.openai.com/api-keys |
| image_gen (OpenAI Codex) | None — uses ChatGPT/Codex OAuth | `hermes auth codex` |
| image_gen (xAI) | XAI_API_KEY or xAI OAuth | x.ai or `hermes model` → xAI |
| image_gen (Krea) | KREA_API_KEY | krea.ai/settings/api-tokens |

For full image gen provider details (models, config, aspect ratios, unique features), see `references/image-gen-providers.md`.

For detailed web-search-plus setup (key acquisition, smoke test, .env location gotcha), see `references/web-search-plus-setup.md`.
For multi-profile .env consolidation (single key source, symlink pattern), see `references/env-consolidation.md`.

## Step 6 — Report Format

Present findings in a scannable structure:

1. **Plugins summary** — enabled count, disabled count, which are key-gated
2. **Toolsets summary** — enabled/disabled built-in + plugin toolsets
3. **Key-gated health** — table: plugin name, required keys, keys found, verdict (functional / partial / non-functional)
4. **Brief explanations** — one sentence per plugin/toolset describing what it does

## Pitfalls

1. **Don't conflate plugin identities** — Mnemosyne (memory system, pip-based) and hermes-lcm (context compression, git-based) are completely different plugins solving different problems. Conflating them during audits gives wrong advice (different update mechanisms, different purposes, different failure modes). Same applies to icarus (Fabric memory/training) vs web-search-plus (search routing). Always verify each plugin's plugin.yaml description before reporting. See references/plugin-roster.md for a cheat sheet.
2. **"Enabled" but dead** — web-search-plus is the canonical example. It shows ✓ enabled in both `hermes plugins list` and `hermes tools list`, but zero API keys means every search silently fails. Always verify key-gated plugins.
2. **Profile-scoped .env** — Hermes loads exactly ONE `.env`: `$HERMES_HOME/.env` (see `hermes_cli/env_loader.py` — `load_dotenv(hermes_home / ".env")`, no chaining). When a profile is active, `HERMES_HOME` points to `~/.hermes/profiles/<name>/`, so root `~/.hermes/.env` is NEVER loaded unless HERMES_HOME is unset (defaults to `~/.hermes`). To verify: `echo $HERMES_HOME`. **Consolidation fix:** symlink all profile `.env` files to root `~/.hermes/.env` so every profile shares the same key source. See `references/env-consolidation.md` for the step-by-step workflow.
3. **Secret truncation via patch tool** — when editing `.env` files, `read_file` display-truncates long values (e.g. `bb_liv...3KrI`). If that truncated string is passed to a `patch` call as `old_string`, the patch tool will match the real line and replace it with the literal truncated text, destroying the secret. **Always use terminal-based operations (sed, Python heredocs) for .env edits.** If you must use patch, verify afterward with `xxd` or hex dump — never trust display output for credential files.
4. **Git plugins vs bundled** — git-installed plugins live in `~/.hermes/plugins/`; bundled plugins live inside the hermes-agent source at `~/.hermes/hermes-agent/plugins/`. Check both locations.
5. **setup.py path differences** — when running from inside a profile, the Python path may be masked. Use the full absolute path: `python3 ~/.hermes/plugins/<name>/setup.py status`.
6. **"requires_env: []"** — some plugins declare empty requires_env but list keys in optional_env or in their README. The plugin works without keys but with degraded capability. Note this in the report.
7. **`plugins.enabled` stored as stringified JSON** — if set via `hermes config set plugins.enabled '["a","b"]'`, YAML may store it as a quoted string (`enabled: '["a","b"]'`) instead of a proper list. The plugin loader may fail to parse it. Verify the config shows `- item` lines under `enabled:`, not a single quoted string. Fix: rewrite using Python `yaml.dump()` with a proper list. Also watch for ghost entries (plugins in the list that don't exist on disk) — remove them to avoid confusing "enabled but not found" states.
8. **Pip-installed plugins vanish on venv recreation.** `hermes update` or profile migration can recreate the venv, wiping packages like `rtk-hermes` and `mnemosyne-memory`. Git-installed plugins in `~/.hermes/plugins/` survive. After venv changes, verify: `pip3 show rtk-hermes mnemosyne-memory`.
7. **Tilde (~) path expansion breaks under profile sandbox** — When a Hermes profile is active, `$HOME` is overridden to the profile's sandbox home (e.g. `~/.hermes/profiles/senna/home`). This means `~` in shell commands expands to the sandbox path, not the real user home. Commands like `cd ~/.hermes/plugins/...` silently resolve to the wrong directory. **Always use absolute paths** (`~/.hermes/...`) in terminal commands for plugin operations. Check `echo $HOME` if paths aren't resolving. This affects all `~`-based paths — git operations, file reads, directory listings.

## Plugin Development

This skill also covers building new Hermes Agent plugins. For full lifecycle management — creating a plugin, registering tools/slash commands, running standalone HTTP endpoints, and testing — see this section.

### A. Plugin System Architecture

**Discovery order (later sources override on name collision):**
```
1. Bundled:  <repo>/plugins/<name>/     (shipped with hermes-agent)
2. User:     ~/.hermes/plugins/<name>/   (your plugins — survives hermes update)
3. Project:  ./.hermes/plugins/<name>/   (opt-in via HERMES_ENABLE_PROJECT_PLUGINS)
4. Pip:      entry-point group hermes_agent.plugins
```

### B. Required Files

```
~/.hermes/plugins/<name>/
├── plugin.yaml           # Manifest
└── __init__.py           # Must expose register(ctx) function
```

**plugin.yaml manifest:**
```yaml
name: my-plugin
version: 1.0.0
description: What it does
author: YourName
kind: standalone          # standalone | backend | exclusive | platform | model-provider
requires_env: []
provides_tools: []
provides_hooks: []
```

### C. Plugin Registration API

The `register(ctx)` function receives a `PluginContext` with:

| Method | Purpose |
|--------|---------|
| `register_tool()` | Register a tool for Hermes |
| `register_cli_command()` | Register `hermes <command>` |
| `register_command()` | Register `/slash` command |
| `register_platform()` | Register a gateway platform adapter |
| `register_hook()` | Register a lifecycle hook |
| `register_skill()` | Register a read-only skill |

**Available lifecycle hooks:** `pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`, `on_session_start`, `on_session_end`, `transform_terminal_output`, `transform_tool_result`, `transform_llm_output`, `pre_api_request`, `post_api_request`, `on_session_finalize`, `on_session_reset`, `subagent_stop`, `pre_gateway_dispatch`, `pre_approval_request`, `post_approval_response`. For detailed kwargs and return-value contracts (especially the `pre_tool_call` block contract and `pre_gateway_dispatch` rewrite contract), see `references/hook-contracts.md`.

> **⚠️ No hook for adding HTTP routes.** The plugin system has no `register_api_route()` method. For API endpoints, use the standalone HTTP server pattern below.

### D. Standalone HTTP Server Pattern

For plugins needing HTTP endpoints, run a lightweight aiohttp server in a background thread:

```python
import asyncio, aiohttp.web, threading

def _run():
    app = aiohttp.web.Application()
    app.router.add_get("/api/endpoint", _handler)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    runner = aiohttp.web.AppRunner(app, handle_signals=False)
    loop.run_until_complete(runner.setup())
    site = aiohttp.web.TCPSite(runner, host="127.0.0.1", port=8643)
    loop.run_until_complete(site.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()

thread = threading.Thread(target=_run, daemon=True)
thread.start()
```

**Critical:** `handle_signals=False` and `new_event_loop()` are required — `run_app()` sets signal handlers that only work in the main thread. See `references/aiohttp-thread-safety.md`.

### E. Plugin Kind Types

| Kind | Use case |
|------|----------|
| `standalone` (default) | Hooks/tools of its own; opt-in via `plugins.enabled` |
| `backend` | Backend service the agent depends on |
| `exclusive` | Backend that replaces the default backend for a capability |
| `platform` | Gateway messaging platform adapter |
| `model-provider` | Model provider integration |

### F. Development Pitfalls

1. **Signal handlers in threads** — always use `AppRunner(handle_signals=False)` + `new_event_loop()`.
2. **Empty stdout** — Node.js/Python buffer stdout when not on a TTY. Use `script` or file output with `line_buffering=True`.
3. **Plugin not showing up** — check `plugins.enabled` in `config.yaml`; the system is opt-in.
4. **Port conflicts** — `lsof -i :PORT` before starting.
5. **Missing aiohttp** — `pip install aiohttp` in the Hermes venv.
6. **CORS on cross-origin requests** — add CORS headers for browser-based clients.

## Fail-Open Pattern (from hermes-plugin-dev)

Security plugins MUST fail open — if the scanner package is missing or errors, the tool call proceeds normally. Never block on import errors or scan exceptions.

```python
_katana = None
_katana_error = None

def _get_katana():
    global _katana, _katana_error
    if _katana is not None:
        return _katana
    if _katana_error is not None:
        return None
    try:
        from hermes_katana import scan_command, scan_input, scan_output
        _katana = {"scan_command": scan_command, ...}
        return _katana
    except ImportError as e:
        _katana_error = str(e)
        logger.warning("package not available: %s — hooks disabled", e)
        return None

def pre_tool_call(tool_name, args=None, **kwargs):
    k = _get_katana()
    if k is None:
        return None  # fail open
    try:
        result = k["scan_command"](args.get("command", ""))
        if result.verdict == BLOCK:
            return {"action": "block", "message": f"Blocked: {findings}"}
    except Exception as e:
        logger.debug("scan error: %s", e)
    return None
```

## Config Loading Pattern (from hermes-plugin-dev)

```python
_CONFIG = None
_CONFIG_PATH = Path(__file__).parent / "config.yaml"

def _load_config() -> dict:
    global _CONFIG
    if _CONFIG is not None:
        return _CONFIG
    defaults = {"enabled": True, ...}
    try:
        import yaml
        if _CONFIG_PATH.exists():
            with open(_CONFIG_PATH) as f:
                user = yaml.safe_load(f) or {}
            defaults.update(user)
    except Exception:
        pass
    _CONFIG = defaults
    return _CONFIG
```

## Runtime Security Middleware

For building runtime security plugins (command scanning, output filtering, audit trails, prompt injection defense), see `references/runtime-security-patterns.md`. This covers scanner pattern files (commands.json, injections.json, secrets.json), hash-chained JSONL audit trails, and policy engine presets (max/balanced/permissive).

## Mnemosyne Plugin Debugging

For debugging Mnemosyne vector search issues (dense_score=0.0, sqlite-vec not loading), see `references/mnemosyne-vector-debugging.md`. Covers the two-database architecture, the known `memory._get_connection` bug, and the fix.

---

## Pre-Update Audit

When the user says they're about to run `hermes update`, run this audit FIRST.
`hermes update` does a `git pull` on the hermes-agent repo and restarts gateways.
Uncommitted changes, stale processes, and stale auth will cause problems.

### Checklist (run in order, stop at first CRITICAL)

#### 1. Git Status (CRITICAL if dirty)
```bash
cd ~/.hermes/hermes-agent && git status --short
```
Any modified files will cause merge conflicts on `git pull`. Two fix paths:

**Option A — Stash** (quick, small changes):
```bash
cd ~/.hermes/hermes-agent && git stash
# After update:
cd ~/.hermes/hermes-agent && git stash pop
```

**Option B — Format patch** (persistent, survives branch switches, recommended):
```bash
cd ~/.hermes/hermes-agent
git checkout -b senna-patches-v0.X
git add -A && git commit -m "local patches"
git format-patch main..senna-patches-v0.X -o ~/.hermes/patches/
git checkout main
# After update:
cd ~/.hermes/hermes-agent && git apply ../patches/0001-*.patch
```

#### 2. Stale Processes
```bash
ps aux | grep -E "(hermes|vite|webui|dashboard)" | grep -v grep
```
Kill before updating to avoid port conflicts and zombie state.

#### 3. Disk Bloat
```bash
du -sh ~/.hermes/*/ | sort -rh | head -15
```
Common culprits:
- `mnemosyne/models/` — local LLM GGUF files (often 500MB+)
- `cache/fastembed/` — embedding model cache
- Stale `.tmp.*` files in `shared/`

#### 4. Auth State
```bash
hermes status 2>/dev/null | head -60
```
Check Nous Portal token expiry, profile auth.json symlinks.

#### 5. Profile Auth Files
```bash
for f in ~/.hermes/profiles/*/auth.json; do
  name=$(echo "$f" | sed 's|.*/profiles/||;s|/auth.json||')
  if [ -L "$f" ]; then echo "$name -> $(readlink "$f")"
  else echo "$name: standalone ($(wc -c < "$f") bytes)"; fi
done
```

#### 6. Config Health
```bash
cat ~/.hermes/config.yaml
```
Check for deprecated keys that a new version may warn about.

#### 7. MCP Servers
```bash
hermes mcp list
```
Verify servers are connected.

#### 8. Running Gateways
Count active profile gateways — they'll all restart during update.

### Report Format

```
━━━ PRE-UPDATE AUDIT ━━━

🔴 BLOCKERS (fix before updating):
  1. [issue + fix command]

🟡 WARNINGS (address after updating):
  1. [issue + recommended action]

✅ CLEAR:
  - [item verified healthy]

━━━ RECOMMENDED SEQUENCE ━━━
  1. [step]
  2. [step]
```

### Post-Update Verification
```bash
hermes --version          # confirm new version
hermes status             # auth still valid
hermes mcp list           # servers reconnected
hermes doctor             # any new warnings
```

### Post-Update Stash Recovery

`hermes update` auto-stashes local changes, but the restore prompt can silently skip. If you see "Skipped restoring local changes":

```bash
# 1. Verify the stash exists
cd ~/.hermes/hermes-agent && git stash list

# 2. See what files were stashed
git diff stash@{0}^..stash@{0} --name-only

# 3. See the actual diff
git stash show -p stash@{0}

# 4. Check if the update already includes those changes
grep -n 'your_function_name' path/to/affected_file.py

# 5a. If changes are NOT in the updated code — try auto-apply first
git stash pop

# 5b. If changes ARE already in the update — safe to drop
git stash drop stash@{0}
```

### Pre-Update Pitfalls

- **Uncommitted changes are the #1 update blocker.** Always check git first.
- **Profile auth.json**: most are symlinks to `~/.hermes/auth.json`. If the main file gets corrupted during update, ALL profiles break. Backup: `cp ~/.hermes/auth.json ~/.hermes/auth.json.bak`
- **The venv gets rebuilt** — `pip install -e .` may upgrade/downgrade deps. Verify custom plugins after.
- **Profile configs are NOT touched by update** — config.yaml, .env, auth.json, skills, and plugins in profiles are safe.

## Reference Files

- `references/hook-contracts.md` — detailed kwargs and return-value contracts for all 17 lifecycle hooks (especially pre_tool_call block semantics and pre_gateway_dispatch rewrite contract)
- `references/web-search-plus-setup.md` — detailed web-search-plus setup (key acquisition, smoke test, .env location gotcha)
- `references/plugin-update-check.md` — compact command reference for git-backed plugin update checks
- `references/env-consolidation.md` — multi-profile .env consolidation (single key source, symlink pattern)
- `references/plugin-roster.md` — plugin identity cheat sheet to avoid conflating different plugins
- `references/aiohttp-thread-safety.md` — aiohttp signal handler pitfall for background-thread HTTP servers
- `references/image-gen-providers.md` — all 5 image gen providers: auth, models, config, aspect ratios, unique features, health check
