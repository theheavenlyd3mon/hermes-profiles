## Local Optimization & Gateway Alignment

When the user asks to optimize Hermes for speed/efficiency on their own machine, treat it as a **read-only audit first**, then propose small reversible config changes. This user prefers explicit approval before service changes or file modifications.

**Audit before changing:**
```bash
hermes profile list
hermes status --all
hermes config
hermes tools list
hermes plugins list
hermes mcp list
hermes cron list --all
hermes sessions stats
du -sh ~/.hermes ~/.hermes/profiles/* ~/.hermes/profiles/senna/* 2>/dev/null
find ~/.hermes/profiles/senna -type f -size +50M -print
find ~/.hermes/profiles/senna -type d -name node_modules -prune -print
find ~/.hermes/profiles/senna -type d -name .git -prune -print
```

**Common safe speed levers, after approval:**
```bash
hermes config set display.compact true
hermes config set display.streaming true
hermes config set display.tool_progress new
hermes config set display.interim_assistant_messages false
hermes config set delegation.max_concurrent_children 2
hermes config set delegation.max_iterations 30
hermes config set checkpoints.max_snapshots 20
hermes config set checkpoints.auto_prune true
```

**Do not optimize by disabling safety:** keep `security.redact_secrets`, Tirith, private URL protections, and approval prompts enabled unless the user explicitly accepts the risk.

### Service Stack Health Verification

When asked to verify or restore the full Hermes stack (gateway + workspace + any dashboards), follow this ordered workflow. See `references/service-stack-health.md` for detailed commands. For a broader audit covering config, .env hygiene, plugins, MCP, cron, Obsidian vaults, knowledge bases, and orphan detection, see `references/comprehensive-health-audit.md`., macOS-specific port checks (Python socket fallback since macOS lacks `timeout`), and background process verification when Vite dev servers produce no observable stdout.

**Quick checklist:**
1. Check gateway status: `hermes gateway status` + `hermes status --all`
2. Scan for port conflicts on all expected ports (8642, 3000, 3099, 5173+) with `lsof`
3. Verify `API_SERVER_ENABLED=true` is set in the active profile's `.env` (snapshotted at gateway startup)
4. Check workspace vite.config.ts for its port config (defaults to 3000, `$PORT` env var overrides)
5. **Ordered startup:** start the workspace first (`pnpm dev` in background), then restart the gateway — because restarting the gateway disconnects Telegram/messaging sessions. If both need cycling, workspace first, gateway second.
6. Verify each service is actually listening: `lsof -nP -iTCP:<port> -sTCP:LISTEN`, or fall back to `python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',<port>)); s.close(); print('ok')"` on macOS.
7. Note any missing upstream components (e.g., `workspace-daemon` directory absent from the repo — not a config issue, it's an upstream gap).

**Common pitfalls:**
- Background `pnpm dev` may show no stdout in the process log even when Vite is running. Verify via `lsof` or socket check, not stdout.
- `API_SERVER_ENABLED` is snapshotted at gateway startup — editing `.env` requires a restart to take effect.
- Duplicate `API_SERVER_ENABLED=true` lines in `.env` are harmless but can confuse casual reading.

### Dashboard / Workspace Gateway Alignment

Hermes Workspace and WebUI-style dashboards need the gateway API server on localhost port 8642. For the user's canonical setup, Senna is the default profile, so the gateway should be checked for profile alignment before restarting anything:
```bash
hermes gateway status
hermes --profile senna gateway status
lsof -nP -iTCP:8642 -sTCP:LISTEN
ps aux | grep -i "hermes gateway" | grep -v grep
```
If Workspace is meant to talk to Senna, `API_SERVER_ENABLED=true` must exist in `~/.hermes/profiles/senna/.env` before the Senna gateway starts. Explain why this is needed and ask approval before editing `.env`, stopping a gateway, or starting/restarting a service.

**Full service audit procedure** — when verifying all Hermes services are healthy and conflict-free:

1. Check gateway status and confirm the right profile is running
2. List ALL listening ports (`lsof -nP -iTCP -sTCP:LISTEN`) — look for 8642 (gateway), 3000 (workspace Vite), 3099 (workspace daemon)
3. Check if the workspace is actually running (`ps aux | grep -E 'pnpm dev|vite' | grep -v grep`) — not every Vite instance belongs to Hermes; check `cwd` to confirm it's `hermes-workspace` not another project
4. Check if `workspace-daemon/` directory exists inside the workspace repo — it's **missing from the upstream repo** (outsourc-e/hermes-workspace), so port-3099 features will be non-functional regardless of what the vite config expects
5. Verify `API_SERVER_ENABLED=true` is actually set in the profile's `.env` (not just the template) — check with `grep API_SERVER_ENABLED ~/.hermes/profiles/<profile>/.env`
6. Check for duplicate env vars in `.env` (harmless but worth noting for clarity)
7. Present a clean port map: service → port → running? → notes

Pitfall: When the workspace dashboard shows features depending on port 3099 that don't work, the root cause is likely the missing `workspace-daemon/` directory — the vite config references it but the upstream repo never shipped it. Do not spend time debugging the workspace connectivity; route to the missing directory check first.

See `references/local-optimization-audit.md` for an example audit plan and `references/service-audit-pattern.md` for a session-derived full service audit.

**Hermes WebUI (nesquena):** see `references/hermes-webui-architecture.md` for the lightweight web client — its standalone architecture, how its in-memory session tracking differs from the Hermes agent's SQLite sessions, the startup/connection flow, and common confusion points (what `sessions` means in the health endpoint vs `hermes sessions list`).

**Third-party frontends (herm, Hermes Desktop, hermes-swift-mac):** see `references/third-party-frontends.mds.md` for the landscape, architecture, install steps, and troubleshooting (including the `HERMES_PYTHON` / `HERMES_CWD` env vars needed by herm to find `tui_gateway`).

---

### Dashboard (hermesd)

`hermesd` is the TUI monitoring dashboard. See `references/hermesd-profile-resolution.md` for a known issue when running `--profile` from inside a profile sandbox (resolved by passing `--hermes-home`).

### Auxiliary Vision

