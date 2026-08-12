# Hermes Workspace Launcher Script

Full launcher script for `~/.local/bin/hermes-workspace`. Starts dashboard + workspace, connects to senna profile.

```bash
#!/usr/bin/env bash
# hermes-workspace — Start Hermes Workspace + Dashboard for senna profile
# Usage: hermes-workspace [--stop]

set -euo pipefail

# ⚠️ MUST use absolute paths — $HOME resolves to profile sandbox inside hermes subcommands
SENNA_HOME="~/.hermes/profiles/senna"
LOGS_DIR="~/.hermes/profiles/senna/logs"
WORKSPACE_DIR="~/hermes-workspace"
DASHBOARD_PORT=9119
WORKSPACE_PORT=3000

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { printf "${CYAN}[workspace]${NC} %s\n" "$*"; }
ok()   { printf "${GREEN}[  ✓  ]${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}[  !  ]${NC} %s\n" "$*"; }
err()  { printf "${RED}[  ✗  ]${NC} %s\n" "$*"; }

# --- Stop mode ---
if [[ "${1:-}" == "--stop" ]]; then
    log "Stopping workspace and dashboard..."
    lsof -ti :$WORKSPACE_PORT 2>/dev/null | xargs kill 2>/dev/null && ok "Workspace stopped (:${WORKSPACE_PORT})" || warn "Workspace was not running"
    lsof -ti :$DASHBOARD_PORT 2>/dev/null | xargs kill 2>/dev/null && ok "Dashboard stopped (:${DASHBOARD_PORT})" || warn "Dashboard was not running"
    exit 0
fi

# --- Check workspace dir ---
if [[ ! -d "$WORKSPACE_DIR" ]]; then
    err "Workspace not found at $WORKSPACE_DIR"
    err "Clone it first: git clone https://github.com/outsourc-e/hermes-workspace.git $WORKSPACE_DIR"
    exit 1
fi

# --- Check gateway ---
if ! lsof -i :8642 -sTCP:LISTEN &>/dev/null; then
    warn "Senna gateway not running on :8642"
    log "Starting senna gateway..."
    hermes --profile senna gateway start 2>/dev/null || true
    sleep 3
    if lsof -i :8642 -sTCP:LISTEN &>/dev/null; then
        ok "Gateway started (:8642)"
    else
        err "Failed to start gateway. Run: hermes --profile senna gateway start"
        exit 1
    fi
else
    ok "Gateway running (:8642)"
fi

# --- Start dashboard (if not running) ---
if lsof -i :$DASHBOARD_PORT -sTCP:LISTEN &>/dev/null; then
    ok "Dashboard already running (:${DASHBOARD_PORT})"
else
    log "Starting dashboard on :${DASHBOARD_PORT}..."
    mkdir -p "$LOGS_DIR"
    nohup hermes --profile senna dashboard --port $DASHBOARD_PORT --no-open \
        > "$LOGS_DIR/dashboard.log" 2>&1 &
    sleep 15  # First run builds web UI — takes ~15s
    if lsof -i :$DASHBOARD_PORT -sTCP:LISTEN &>/dev/null; then
        ok "Dashboard started (:${DASHBOARD_PORT})"
    else
        err "Dashboard failed to start. Check: $LOGS_DIR/dashboard.log"
        exit 1
    fi
fi

# --- Start workspace (if not running) ---
if lsof -i :$WORKSPACE_PORT -sTCP:LISTEN &>/dev/null; then
    ok "Workspace already running (:${WORKSPACE_PORT})"
else
    log "Starting workspace on :${WORKSPACE_PORT}..."
    cd "$WORKSPACE_DIR"
    nohup pnpm dev > "$WORKSPACE_DIR/.workspace.log" 2>&1 &
    sleep 6
    if lsof -i :$WORKSPACE_PORT -sTCP:LISTEN &>/dev/null; then
        ok "Workspace started (:${WORKSPACE_PORT})"
    else
        err "Workspace failed to start. Check: $WORKSPACE_DIR/.workspace.log"
        exit 1
    fi
fi

# --- Summary ---
echo ""
printf "${GREEN}══════════════════════════════════════════════════${NC}\n"
printf "${GREEN}  Hermes Workspace (senna)${NC}\n"
printf "${GREEN}══════════════════════════════════════════════════${NC}\n"
printf "  Workspace:   ${CYAN}http://127.0.0.1:${WORKSPACE_PORT}${NC}\n"
printf "  Dashboard:   ${CYAN}http://127.0.0.1:${DASHBOARD_PORT}${NC}\n"
printf "  Gateway:     ${CYAN}http://127.0.0.1:8642${NC}\n"
printf "  Profile:     senna\n"
printf "${GREEN}══════════════════════════════════════════════════${NC}\n"
echo ""
printf "  Stop with:   ${YELLOW}hermes-workspace --stop${NC}\n"
echo ""
```

## .env Template

```bash
# Hermes Workspace — connected to senna profile
HERMES_API_URL=http://127.0.0.1:8642
PORT=3000
HOST=127.0.0.1
HERMES_DASHBOARD_URL=http://127.0.0.1:9119
VITE_HERMESWORLD_ENABLED=true
```

## Service Architecture

```
┌──────────────────┐     :8642 (gateway API)     ┌─────────────────┐
│  Workspace UI    │ ──────────────────────────▶  │  Hermes Agent   │
│  :3000           │ ◀──────────────────────────  │  (senna)        │
└──────────────────┘     :9119 (dashboard)        └─────────────────┘
         │                        │
         │                        │
    Browser                  Dashboard
    (user)                   (monitoring)
```

## Logs

| Service | Log Path |
|---------|----------|
| Dashboard | `~/.hermes/profiles/<profile>/logs/dashboard.log` |
| Workspace | `~/hermes-workspace/.workspace.log` |
| Gateway | `~/.hermes/profiles/<profile>/logs/gateway.log` |
