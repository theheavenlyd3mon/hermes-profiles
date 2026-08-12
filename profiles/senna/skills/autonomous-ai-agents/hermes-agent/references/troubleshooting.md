### Troubleshooting

Common issues and how to resolve them.

**Symptom:** Gateway shows `Gateway running with 1 platform(s)` — Telegram never connects even though `TELEGRAM_BOT_TOKEN` exists in root `.env`.

**Root cause:** The gateway reads `.env` from `HERMES_HOME` (profile directory), NOT the root `~/.hermes/.env`. The profile `.env` may be a different file that's missing the Telegram vars.

**Quick diagnosis:**
```bash
grep "platform(s)" ~/.hermes/profiles/senna/logs/gateway.log         # 1 or 2+
grep "^TELEGRAM" ~/.hermes/profiles/senna/.env                        # profile (gateway reads this)
grep "^TELEGRAM" ~/.hermes/.env                                        # root (may not be read by gateway)
diff ~/.hermes/.env ~/.hermes/profiles/senna/.env 2>&1 | head -30     # are they in sync?
```

**Fix:** Add the Telegram vars to the profile `.env`, then restart the gateway.
See `references/gateway-telegram-not-connecting.md` for the full diagnosis flow, three fix options (targeted edit / symlink / profile-as-default), verification steps, and the macOS `~` path resolution quirk.

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider — Groq requires both `GROQ_API_KEY` in `.env` and the `openai` Python package; local requires `faster-whisper`
3. Config change requires process restart — CLI: exit and relaunch. Gateway: `/restart`. `/reset` is NOT enough for STT config changes.
4. Check the error log for the rejection reason: `grep -i "stt\|groq\|transcri" ~/.hermes/profiles/<profile>/logs/errors.log | tail -10`
5. For deeper diagnosis, walk the provider-resolve path: see `references/stt-setup-quickstart.md` → Deeper Diagnosis section

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes auth add <provider> --type oauth` — re-authenticate OAuth providers (replaces the removed `hermes login` command)
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Executable not found after installing from a profile session

When you install system-level tools (`uv tool install`, `pip install --user`,
`npm install -g`, `cargo install`, etc.) from inside a Hermes profile session,
`$HOME` is redirected to the profile's sandboxed home directory
(`~/.hermes/profiles/<name>/home/`). The binary lands in the sandboxed
`$HOME/.local/bin/` instead of the real `~/.local/bin/` — so the command is
installed but not found in the user's actual terminal.

**Diagnosis:** Run `echo $HOME` inside the session — if it shows
`/Users/<you>/.hermes/profiles/<name>/home/`, you're in the sandbox.

**Fix:** Override `$HOME` explicitly for binary installation commands:
```bash
HOME=~ uv tool install <package> --force
HOME=~ pip install --user <package>
```

Only override for **binary installation** — for profile-local data (skills,
plugins, config), the sandboxed `$HOME` is correct and intentional.

See `references/tool-installation-profile-sandbox.md` for the full diagnosis
flow, tool-by-tool table, and a worked example (hermesd install).

### `.env` files not found (macOS `~` path resolution)

On macOS, the terminal tool may resolve `~/.hermes/.env` differently than `/Users/<you>/.hermes/.env` due to shell environment variance or working directory context. This causes false negatives — `cat ~/.hermes/.env` returns empty even though the file has 400+ lines.

This is especially common when running inside a Hermes profile: `HERMES_HOME` can change how `~` is resolved. The `cat ~/.hermes/.env` might resolve to `~/.hermes/profiles/senna/home/.hermes/.env` (which doesn't exist) instead of the actual file at `/Users/<you>/.hermes/.env`.

**Diagnosis:** If `cat ~/.hermes/.env` produces empty output but a file exists at the absolute path, use absolute paths explicitly:
```bash
cat ~/.hermes/.env
test -f ~/.hermes/.env
wc -l ~/.hermes/.env
ls -la ~/.hermes/.env    # file size tells you if it's real
```

Also check the profile-level `.env`, which is what the gateway actually reads:
```bash
cat ~/.hermes/profiles/senna/.env | grep "^TELEGRAM"  # profile
cat ~/.hermes/.env | grep "^TELEGRAM"                 # root
diff ~/.hermes/.env ~/.hermes/profiles/senna/.env 2>&1 | head -30
```

**Verification:** `hermes status --all` shows which API keys Hermes itself detects at runtime. If a key shows as `✗ not set` but you see it in the raw `.env` file, the variable name may differ from what Hermes expects, or the `.env` may be in the wrong profile.

### `.env` file corrupted with `N|` line-number prefixes

If every line of a `.env` file starts with a digit-pipe prefix like `42|KEY=value`, the file was accidentally overwritten with `read_file` output. See `references/env-corruption-repair.md` for the one-line fix and verification steps. This is safe because the sed pattern only strips leading `[0-9]+|` — all `KEY=value` pairs, comments, and blank lines survive.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Post-upgrade config sections missing

After updating Hermes Agent (especially cross-major-version upgrades like v0.9 → v0.10), the profile config.yaml is regenerated from defaults. This can silently **remove entire sections** that don't exist in the default template:

| Section | What Gets Dropped | How to Detect |
|---------|-------------------|---------------|
| `plugins.enabled` | Entire list removed — plugins still on disk but not loaded | `grep -A5 '^plugins:' ~/.hermes/profiles/<profile>/config.yaml` returns nothing |
| `context.engine` | Resets to `compressor` (the Hermes default) | `grep 'engine:' ~/.hermes/profiles/<profile>/config.yaml` shows `compressor`, not `lcm` |
| `memory.provider` | Resets to empty string | `grep '^memory:' -A8 ~/.hermes/profiles/<profile>/config.yaml` shows `provider: ''` |

**Post-upgrade verification checklist:**

```bash
# 1. Context engine
grep 'engine:' ~/.hermes/profiles/senna/config.yaml     # should be 'lcm' if you use LCM

# 2. Plugins
grep -A5 '^plugins:' ~/.hermes/profiles/senna/config.yaml  # should list enabled plugins

# 3. Memory provider
grep -A5 '^memory:' ~/.hermes/profiles/senna/config.yaml    # should have a provider set
```

**Fix:** Add the missing sections back manually via `hermes config edit` or `patch`. The plugin names must match directories in `~/.hermes/plugins/` or pip entry-point names. See `hermes-config-upgrade-pitfalls` in the LLM-Wiki (`Hermes Vault/Hermes/LLM-Wiki/concepts/`) for the full recovery procedure used in the Senna profile.

### Profile .env overrides root vault/wiki paths silently

A silent breakage pattern: the root `.env` correctly sets `OBSIDIAN_VAULT_PATH`, `FABRIC_DIR`, and/or `WIKI_PATH` to the real vault location, but the profile `.env` (generated from the same template) **overrides** these to a sandboxed path like `~/.hermes/profiles/<name>/vault`.

Why this happens: when the root `.env` and profile `.env` are both created from the same template, the profile's copy has placeholder path values that override the correctly-configured root values. Since profile `.env` loads SECOND and wins on duplicate keys, the agent silently reads/writes to the wrong directory — empty vault, empty Icarus fabric, no Wiki access.

**Diagnosis:**

```bash
# 1. Check which value actually wins at runtime
grep OBSIDIAN_VAULT_PATH ~/.hermes/.env                  # what root says
grep OBSIDIAN_VAULT_PATH ~/.hermes/profiles/senna/.env   # what profile overrides to

# 2. Verify the profile vault directory actually has content
ls ~/.hermes/profiles/senna/vault/                        # often empty or icarus/ only
ls "~/Hermes Vault/Hermes/"                   # compare to the real vault

# 3. Check FABRIC_DIR and WIKI_PATH the same way
grep 'FABRIC_DIR\|WIKI_PATH' ~/.hermes/.env
grep 'FABRIC_DIR\|WIKI_PATH' ~/.hermes/profiles/senna/.env
```

**Fix:** Remove the path variable override from the profile `.env` so the root value takes effect:

```bash
sed -i '' '/^OBSIDIAN_VAULT_PATH=/d' ~/.hermes/profiles/senna/.env
sed -i '' '/^FABRIC_DIR=/d' ~/.hermes/profiles/senna/.env
# WIKI_PATH is usually only in root — check first
grep WIKI_PATH ~/.hermes/profiles/senna/.env && sed -i '' '/^WIKI_PATH=/d' ~/.hermes/profiles/senna/.env
```

**Rule of thumb:** Path variables (`OBSIDIAN_VAULT_PATH`, `FABRIC_DIR`, `WIKI_PATH`) should live in the **root** `.env` as the single canonical source. Only put them in a profile `.env` if that profile genuinely needs to point at a DIFFERENT vault than the rest of the team. Otherwise you get silent breakage.

Full .env architecture reference: `references/env-architecture.md`

### `/new` freezes or creates a 0-message session (session-transition deadlock)

**Symptom:** You type `/new` during a session, the prompt returns immediately but the new session has 0 messages and is unresponsive. The old session's log entries continue appearing for several more seconds in `agent.log`. The new session appears in `session_search` with 0 message count.

**Root cause:** SQLite database lock contention. When `/new` is issued while the agent is still mid-turn (a 60+ API-call session that's actively writing to `state.db` or `lcm.db`), `new_session()` tries to:
1. Call `commit_memory_session()` on the old session's conversation history
2. End the old session in the DB (`end_session()`)
3. Create a new session in the DB (`create_session()`)

If the old session's agent thread is still holding a SQLite write lock, step 2 or 3 blocks indefinitely. The CLI/TUI appears to freeze because `new_session()` never returns to the input loop.

**Evidence pattern in logs:**

```bash
# 1. Session_search shows a session with 0 messages
session_search()  # look for sessions with message_count=0

# 2. Agent log shows old session still running AFTER the new session was created
grep "<old_session_id>" ~/.hermes/profiles/senna/logs/agent.log | tail -5
# Shows tool calls and API calls continuing past the /new timestamp

# 3. Error log may show "Agent thread still alive after interrupt"
grep "thread still alive" ~/.hermes/profiles/senna/logs/errors.log

# 4. The frozen session has NO entries in agent.log at all
grep "<new_session_id>" ~/.hermes/profiles/senna/logs/agent.log
# Empty — the new session's agent was never properly initialized
```

**Diagnosis commands:**

```bash
# Check recent sessions for 0-message orphans
hermes sessions list | head -10

# Check if state.db is locked
lsof ~/.hermes/profiles/senna/state.db 2>/dev/null

# Check for concurrent agent threads
ps aux | grep "run_agent\|AIAgent" | grep -v grep

# Look at the exact timing in agent.log
grep "Turn ended" ~/.hermes/profiles/senna/logs/agent.log | tail -5
```

**Pre-flight check (recommended):**

Type `/ready` before issuing `/new` or `/clear`. It checks three things in one shot:
1. **DB lock** — PRAGMA wal_checkpoint against state.db with 100ms timeout
2. **Background processes** — scans for other Hermes processes beyond the current session
3. **Gateway pulse** — lsof/socket check on the gateway port

Output is either a green `✔️ Ready` or an `⚠️ Issues detected` with details. If busy, wait a couple seconds and try `/ready` again.

This is a native slash command — no script installation needed. In the CLI it works directly via `cli.py:_check_ready()`. In the TUI, it dispatches through the `slash.exec` RPC fallback path: TUI frontend → `createSlashHandler` → slash worker subprocess → `cli.process_command("/ready")` → `_check_ready()`. The command was originally `cli_only=True` (hidden from TUI autocomplete/help) but still functional in TUI via this fallback. If `/ready` produces no output in TUI, verify the slash worker subprocess is alive (the gateway spawns one per session; a gateway restart recreates it). The bash equivalent is `scripts/check-agent-idle.sh` in this skill directory.

**Workarounds (from shallowest to deepest):**

1. **Interrupt first, then `/new`** — If the agent is generating, press Ctrl-C (CLI) or tap the interrupt button (TUI), wait 2-3 seconds for the turn to stop, then type `/new`. This gives the old session's thread time to release its DB handles.

2. **Use `/clear` instead of `/new` in TUI** — `/clear` is a TUI-local handler that resets the Ink state without calling the heavy `new_session()` path on the Python backend. It still goes through the gateway RPC but skips the memory commit / DB finalize cycle.

3. **Wait for the turn to finish naturally** — If the agent is mid-response, let it finish before typing `/new`.

**Reference file:** `references/session-new-freeze-deadlock.md` — full reproduction recipe, evidence, and two distinct scenarios (mid-turn vs idle-state).
**Script:** `scripts/check-agent-idle.sh` — pre-flight check before issuing `/new`. Make executable with `chmod +x`, then run to verify the DB is not locked before session transition.

**Code locations (for deeper investigation):**

- `cli.py` ~line 5394 — `new_session()` — the synchronous session transition that can block
- `cli.py` ~line 8651 — `_confirm_destructive_slash()` — the confirmation prompt before destructive commands
- `tui_gateway/server.py` ~line 2090 — `session.create` RPC handler (TUI path)
- `tui_gateway/server.py` ~line 2632 — `session.close` RPC handler (TUI path)
- `ui-tui/src/app/useSessionLifecycle.ts` ~line 125 — `newSession()` — TUI's async session creation flow
- `ui-tui/src/app/slash/commands/core.ts` ~line 114 — `/new` mapped as alias for `clear` command in TUI

**Reference file:** See `references/session-new-freeze-deadlock.md` for the full reproduction recipe, evidence transcript, and SQLite lock analysis from the 2026-05-11 debugging session.

### Config looks set but feature not active (duplicate key bug)

A feature can appear configured in `config.yaml` but fail to activate at runtime. This typically happens when there are **duplicate keys** in the YAML — the last occurrence wins, silently overriding earlier values.

**Example:** Mnemosyne configured but not running:
```yaml
memory:
  provider: mnemosyne    # Line 297 - wanted
  ...
  provider: ""           # Line 302 - OVERRIDES the above to empty!
```

**Diagnosis steps:**
1. Check config with `hermes config show` — look for duplicate keys in the output
2. Check runtime status: `hermes memory status` shows actual active provider vs "Provider: (none — built-in only)"
3. For plugins: verify in the actual runtime via tools, not just `plugins.enabled` list in config
4. Search the raw config file for duplicate keys: `grep -n "provider:" ~/.hermes/profiles/<profile>/config..yaml`

**Fix:** Remove the duplicate/override line from the config file, then restart the gateway or CLI.

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:

- **Dual-gateway fight (Telegram shutdown loop)**: If you get shutdown notifications every few seconds, two launchd plists (`ai.hermes.gateway` + `ai.hermes.gateway-senna`) are fighting over port 8642. See `references/dual-gateway-fight.md` for diagnosis and fix.
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

### Plugin not found in profile context (profile sandboxing)

When running inside a Hermes profile, plugins installed globally at `~/.hermes/plugins/` may not be discovered — even when the config correctly lists them in `plugins.enabled`.

**Root cause:** `get_hermes_home()` returns `~/.hermes/profiles/<name>/` in a profile context, so `_plugins_dir()` creates and scans `~/.hermes/profiles/<name>/plugins/`, NOT the global `~/.hermes/plugins/`. The plugin scanner never sees the global directory.

**Compounding confusion — `$HOME` vs `HERMES_HOME`:** Within a profile, `$HOME` is sandboxed to `~/.hermes/profiles/<name>/home/` (where `~` resolves in shell commands), but `get_hermes_home()` returns `~/.hermes/profiles/<name>/`. These are **different paths**. A stray plugin copy at `~/.hermes/profiles/<name>/home/.hermes/plugins/<name>/` is invisible to the scanner — it looks at `HERMES_HOME/plugins/`, not `$HOME/.hermes/plugins/`.

**Diagnosis:**
```bash
# 1. Check what get_hermes_home() returns for this profile
echo $HERMES_HOME   # usually ~/.hermes/profiles/<name>

# 2. List what's actually in the profile's plugins dir
ls ~/.hermes/profiles/<name>/plugins/

# 3. Compare with global plugins
ls ~/.hermes/plugins/

# 4. Check if config entries match anything discoverable
grep -A5 '^plugins:' ~/.hermes/profiles/<name>/config.yaml
# If a plugin is listed here but not in the profile plugins dir, it won't load.

# 5. Verify in runtime logs — look for the context engine fallback
grep 'context engine.*not found' ~/.hermes/profiles/<name>/logs/errors.log
grep 'falling back to built-in' ~/.hermes/profiles/<name>/logs/errors.log
```

**Context engine fallback is the canary:** If the LCM plugin isn't loaded, the agent logs `"Context engine 'lcm' not found — falling back to built-in compressor"` in `errors.log`. The UI gives no indication — only the error log reveals it.

**Fix — three options:**

**Option A — Install via `hermes plugins install` (preferred):**
```bash
# From within the profile — installs to the right directory automatically
hermes plugins install https://github.com/<owner>/<plugin>.git --enable
```

**Option B — Copy with history (for already-installed global plugins):**
```bash
cp -a ~/.hermes/plugins/<name> ~/.hermes/profiles/<name>/plugins/
# Verify
hermes plugins list | grep <name>
```

**Verification:**
```bash
# Check plugin listing now shows it
hermes plugins list

# For context engines specifically, restart and check the error log
hermes config check   # should pass
grep 'context engine' ~/.hermes/profiles/<name>/logs/errors.log  # should NOT mention fallback
```

**Option C — Symlink profile plugins directory to global (permanent, update-proof):**

For a profile that is the main/primary profile, the symlink approach makes all globally-installed plugins immediately visible and prevents recurrence after updates:

```bash
mv ~/.hermes/profiles/<name>/plugins{~,.old}
ln -s ~/.hermes/plugins ~/.hermes/profiles/<name>/plugins
```

**How it works:** The symlink makes `HERMES_HOME/plugins/` resolve to `~/.hermes/plugins/`. The plugin scanner follows the symlink transparently. When you run `hermes plugins install` from within the profile, it writes to `~/.hermes/plugins/` (since the symlink resolves there). All profiles can share one canonical plugin set.

**Advantages over Option A/B:**
- No need to install plugins per-profile — one global install, all profiles see it
- If a future update adds more profiles, they inherit the same global plugins
- `hermes plugins update` updates once, not N times
- If the `~/.hermes/plugins/` directory already has plugins installed globally, they're immediately visible — no copy needed

**When NOT to use Option C:**
- If the profile needs ISOLATED plugins that no other profile should see
- If you want per-profile version pinning of plugins

**If a future update replaces the symlink with a real directory**, recreate it with the one-liner above. The old profile/data is preserved in `plugins.old` if the `mv` command was used.

**Recurrence prevention:** After applying Option C, save the fix in your knowledge base along with the one-liner. If the symlink is ever broken (e.g., by a profile recreation), the fix is the same two commands regardless of how many plugins are involved.

### Peeking at what an update pulled

`hermes update` is a black box — it just runs and says "updated." To see what
commits actually came in, check the repo directly:

```bash
cd ~/.hermes/hermes-agent

# 1. Latest commits
git log --oneline -20

# 2. What was fetched (confirm remote + branch)
cat .git/FETCH_HEAD

# 3. What was merged (check reflog for the pull action)
git reflog -5

# 4. Diff between previous HEAD and current — the actual changelog
git log <prev_hash>..HEAD --oneline

# Full message for each commit
git log <prev_hash>..HEAD
```

The first `OID` in `FETCH_HEAD` is the tip that was pulled. The reflog shows
which `pull --ff-only` brought you there. Use the old HEAD (one entry up in
reflog) as `<prev_hash>` to see the exact diff — that's your update's
changelog.

### Checking git-source plugins for updates

Not all plugins ship bundled with Hermes. Git-source plugins (installed from
GitHub repos) need manual update checks — `hermes plugins list` shows their
source as `git` rather than `bundled`. To check for available updates:

```bash
cd ~/.hermes/plugins/<plugin-name>
git fetch --prune
git log --oneline HEAD..origin/main        # commits behind
git log --oneline -3                        # current HEAD for reference
```

You can run this across all git-source plugins in one loop:

```bash
for p in hermes-lcm icarus web-search-plus; do
  echo "--- $p ---"
  cd ~/.hermes/plugins/$p && git fetch --prune 2>&1
  behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
  echo "Behind origin/main: $behind commits"
  echo ""
done
```

**Pitfall — `~` path resolution inside a Hermes profile:** When running
`terminal` commands from within a live Hermes session, `~/.hermes/plugins/`
may resolve to the profile's sandboxed home directory
(`~/.hermes/profiles/senna/home/.hermes/plugins/`) instead of the real global
plugins directory. This causes false negatives — the `cd` silently fails or
lands in a non-existent path. **Always use absolute paths**
(`~/.hermes/plugins/`) when accessing plugin directories inside a
profile session.

To pull the updates:

```bash
cd ~/.hermes/plugins/<plugin-name>
git pull --ff-only     # fast-forward only — fails if local has diverged
```

After pulling, check errors logs for issues (especially context engine fallback
for hermes-lcm) — see the checklist below.

### Post-update plugin verification checklist

After every `hermes update`, run this short checklist to catch silent failures
before they cause problems. Context engine fallback and missing plugins are
totally silent — no banner, no CLI warning, no gateway notification.

```bash
# 1. Config version and structure
hermes config check                  # should pass with no warnings
grep '_config_version:' ~/.hermes/profiles/senna/config.yaml   # expected value for current version

# 2. Plugin discovery — list what's found vs what's enabled
hermes plugins list                  # expect all enabled plugins to show
# If a plugin shows as "(missing)" or doesn't appear at all, investigate

# 3. Context engine — canary for LCM/hermes-lcm loading
grep 'context engine' ~/.hermes/profiles/senna/logs/errors.log
# Expected: NOTHING (no matches = context engine loaded successfully)
# Bad: "Context engine 'lcm' not found — falling back to built-in compressor"

# 4. Memory provider
hermes memory status                 # should show configured provider, not "built-in only"

# 5. Quick functional test — verify plugins expose their tools
hermes --version                     # verify version updated as expected
```

**If the error log shows context engine fallback:**
1. Verify the plugin directory exists in the scanner's path (profile plugins dir)
2. Check if the symlink was broken by the update
3. Re-apply the symlink fix if needed, or install the plugin directly

**If a plugin listed in config.yaml doesn't appear in `hermes plugins list`:**
1. Check if it's a pip-installed entry-point plugin (no directory on disk — see section below)
2. If it's a directory-based plugin: check if it's in the profile's plugins dir or the global one
3. Run the diagnosis commands from the "Plugin not found in profile context" section above

**Reference file:** See `references/post-update-plugin-verification.md` for the
full session-specific migration steps and before/after state from the 2026-05-11
v0.13.0 recovery.

### Plugin not appearing in `hermes plugins list` (pip-installed entry-point plugins)

Some plugins (e.g. `rtk-hermes`) are installed as pip packages with entry points, not git-cloned directories with `plugin.yaml`. They will NOT show up in `hermes plugins list` and will NOT appear in a `find ~/.hermes -name plugin.yaml` audit.

**How they register:** The pip package's `entry_points.txt` uses the `hermes_agent.plugins` entry point group (note: underscore, not `hermes.plugins`):

```
[hermes_agent.plugins]
rtk-rewrite = rtk_hermes
```

**How to verify they're installed:**

```bash
# 1. Check the package is installed in the Hermes venv
~/.hermes/hermes-agent/venv/bin/python -c "import <package>; print(<package>.__version__)"

# 2. Check the entry point registration
cat ~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/<package>-<version>.dist-info/entry_points.txt

# 3. Confirm it's in config.yaml's plugins.enabled list
grep -A20 "^plugins:" ~/.hermes/profiles/senna/config.yaml | grep "^  - " | grep <package>
```

**Pitfall:** If you can't find a plugin on disk or in `hermes plugins list`, don't assume the config entry is stale. Check if it's a pip-installed plugin first using the commands above. The config entry `rtk-rewrite` in `plugins.enabled` is valid for pip-installed plugins — it is NOT a stale entry even though the plugin has no directory on disk.

---
