# Trifecta Deploy Guide

## AWS EC2 Deployment

Architecture: Mobile app → WebSocket → EC2 Docker container → Trifecta Server → Agent CLIs

### Step 1 — Launch EC2
- AMI: Ubuntu Server 24.04 LTS (x86)
- Instance: t3.small or t3.medium
- Security group: TCP 22 (SSH) + TCP 3773 (Trifecta)
- Storage: 15 GB gp3 minimum

### Step 2 — Install Docker & Auth
```bash
ssh -i your-key.pem ubuntu@<ec2-ip>
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu && newgrp docker
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Step 3 — Build & Run
```bash
docker build --platform=linux/amd64 -t trifecta-server ./trifecta-desktop
docker run -d --name trifecta --restart unless-stopped -p 3773:3773 \
  -v /opt/trifecta/data:/data \
  -e TRIFECTA_HOST=0.0.0.0 -e TRIFECTA_PORT=3773 -e TRIFECTA_HOME=/data \
  trifecta-server
```

### Step 4 — Verify
```bash
curl http://localhost:3773/.well-known/belweave/environment | jq .
docker logs trifecta 2>&1 | grep "Pairing URL"
```

### Step 5 — Create project
```bash
docker exec -it trifecta mkdir -p /home/trifecta/test-project
docker exec -it trifecta bun /app/apps/server/dist/bin.mjs project add /home/trifecta/test-project --title "Test"
```

## Pairing System
- One-time owner pairing token issued on first connect
- Token exchanged for authenticated session
- Future access is session-based
- Use `trifecta auth` to manage sessions, issue new tokens, revoke old ones

## Remote Access Options
1. **Desktop app GUI** — Settings → Connections → toggle Network access
2. **Headless CLI** — `npx @belweave/trifecta serve --host "<ip>"`
3. **SSH launch** — Desktop app can start/reuse server on remote host via SSH

## Environment Variables
| Var | Default | Purpose |
|-----|---------|---------|
| TRIFECTA_HOST | 127.0.0.1 | Bind address |
| TRIFECTA_PORT | 3773 | Server port |
| TRIFECTA_HOME | ~/.trifecta | Data directory |
| TRIFECTA_LOG_LEVEL | info | Log verbosity |

## Hermes-Specific Config
Trifecta spawns `hermes acp` as a subprocess. To use a named profile:
```bash
HERMES_HOME=~/.hermes/profiles/senna npx @belweave/trifecta
```
Without `HERMES_HOME`, it uses the default profile.

## Tech Stack Detail
- Server: Node.js, Effect-TS, Electron 41
- Web UI: React 19, Vite 8, Tailwind CSS 4, Zustand, Lexical
- Mobile: Expo SDK 56, React Native 0.85
- Build: Turborepo, Bun
- Protocol: WebSocket with Effect-style RPC, ACP over stdio for agents

## Troubleshooting
- "Codex not installed" in provider list → rebuild Docker with `--build-arg INSTALL_CODEX=true`
- No native root CA cert error → ensure Docker image has ca-certificates package
- Mobile can't connect → verify port 3773 is open, check firewall rules
- Pairing URL expired → run `trifecta auth` to issue new one
