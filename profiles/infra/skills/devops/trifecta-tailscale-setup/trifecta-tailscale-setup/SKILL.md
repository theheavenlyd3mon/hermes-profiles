---
name: trifecta-tailscale-setup
description: Trifecta + Tailscale setup — always-on mobile access to Hermes agent via private mesh network.
triggers:
  - "trifecta"
  - "mobile hermes"
  - "phone agent"
  - "tailscale trifecta"
version: 1.0.0
author: senna
metadata:
  hermes:
    tags: [trifecta, tailscale, mobile, remote, acp]
    homepage: https://github.com/pkyanam/trifecta
---

# Trifecta + Tailscale: Always-On Mobile Hermes

## What It Is
Trifecta is a cross-platform coding agent platform (Belweave, alpha v0.0.37).
Desktop server + iOS/Android apps + VS Code extension. Talks to Hermes via ACP (JSON-RPC over stdio).

Architecture:
```
Phone (Tailscale) → Trifecta Server (Node.js, port 3773) → hermes acp → models/tools/skills
```

## Prerequisites
- Tailscale installed + running on MBP and phone (same tailnet)
- Hermes ACP ready: `hermes acp --check` → "Hermes ACP check OK"
- MBP must stay awake (lid open, external display, or `pmset -c sleep 0`)

## Installation Options

### Option A: Quick Test (no install)
```bash
npx @belweave/trifecta
```

### Option B: Desktop App (persistent)
```bash
brew install --cask belweave-code
```

### Option C: Self-Hosted VPS (Docker)
```bash
docker build --platform=linux/amd64 --build-arg INSTALL_CODEX=true -t trifecta-server ./trifecta-desktop
docker run -d --name trifecta --restart unless-stopped -p 3773:3773 \
  -v /opt/trifecta/data:/data \
  -e TRIFECTA_HOST=0.0.0.0 -e TRIFECTA_PORT=3773 -e TRIFECTA_HOME=/data \
  trifecta-server
```

## Launch with Tailscale

### Plain HTTP/WS (simplest)
```bash
npx @belweave/trifecta serve --host "$(tailscale ip -4)"
```

### HTTPS/WSS (recommended — auto-TLS via Tailscale)
```bash
npx @belweave/trifecta serve --tailscale-serve
# Optional custom port:
npx @belweave/trifecta serve --tailscale-serve --tailscale-serve-port 8443
```

Both print a pairing URL + QR code.

## Pairing Flow
1. Install Trifecta app on iOS/Android
2. Install Tailscale on phone, join same tailnet
3. Open pairing URL or scan QR in Trifecta app
4. Select Hermes as agent provider
5. Chat from anywhere

## Tailscale Integration Details
- Trifecta auto-detects Tailnet IP, MagicDNS name, HTTPS endpoints
- Settings → Connections → Manage Local Backend → toggle Network access
- `trifecta auth` manages pairing tokens and sessions (revoke, inspect)
- Tailscale HTTPS pairing works with hosted web app at app.trifecta.belweave.ai
- Token is in URL hash (never sent to hosted server)

## Keeping It Persistent
- Tailscale: add as login item in System Settings
- Trifecta desktop app: auto-starts with login
- CLI mode: create launchd plist for headless operation
- Prevent sleep: `sudo pmset -c sleep 0` (when plugged in)

## Remote Access (outside home)
```bash
# Desktop-managed SSH launch (Settings → Connections → Remote Environments)
# Or headless on a VPS:
npx @belweave/trifecta serve --host "$(tailscale ip -4)"
```

## Supported Agents (all via stdio)
| Agent    | Protocol   | Auth                     |
|----------|------------|--------------------------|
| Hermes   | ACP        | `hermes setup`           |
| Codex    | JSON-RPC   | `codex login`            |
| Claude   | JSON-RPC   | `claude auth login`      |
| OpenCode | JSON-RPC   | `opencode auth login`    |
| Gemini   | Headless   | `npm i -g @google/gemini-cli` |
| Cursor   | ACP        | bundled cursor-agent     |
| Devin    | ACP        | `devin acp`              |

## Pitfalls
- MBP 2018 sleep kills everything — use pmset or external display
- Tailscale daemon must be running (check: `tailscale status`)
- Trifecta is alpha — expect bugs, especially on mobile
- Model API calls still go to providers (need valid keys in Hermes config)
- HTTPS endpoints required for hosted web app (browser mixed-content rules)
- `trifecta project add` must be done CLI-side for remote environments

## Health Check
```bash
curl http://localhost:3773/.well-known/belweave/environment | jq .
```

## Links
- Repo: https://github.com/pkyanam/trifecta
- Releases: https://github.com/pkyanam/trifecta/releases
- Discord: https://discord.gg/jn4EGJjrvv
- Tailscale Serve docs: https://tailscale.com/docs/features/tailscale-serve
