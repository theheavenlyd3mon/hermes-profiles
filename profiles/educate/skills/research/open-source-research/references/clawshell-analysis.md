# ClawShell — Runtime Security Layer for Hermes

**Source**: https://github.com/clawshell/clawshell
**Stars**: 255 (May 2026)
**License**: Apache-2.0
**Language**: Rust (NPM package available)
**Status**: Evaluated 2026-05-10 — not adopted. Documented for reference.

## What It Is

A security-privileged sidecar proxy that sits between Hermes/OpenClaw and LLM API providers (OpenAI, Anthropic, OpenRouter). It performs virtual-to-real API key mapping + DLP scanning.

## Key Capabilities

1. **Virtual API Key Mapping** — Hermes never holds real keys, only virtual ones. ClawShell swaps them before forwarding upstream. Real keys stored in `/etc/clawshell/clawshell.toml`, readable only by `clawshell` system user.

2. **PII DLP Scanning** — Configurable regex patterns scan request/response bodies. Can block or redact SSNs, credit cards, emails, etc. Streaming (SSE) responses pass through without scanning.

3. **Email Isolation** — Sender allowlist/denylist filtering. IMAP creds stored in privileged `/etc/clawshell/`. Built-in Gmail/Outlook presets.

4. **OAuth Support** — Device code flow for Codex/ChatGPT. Auto-refresh. Translates OpenAI Chat Completions API to ChatGPT Responses API format.

5. **Runtime Stats** — `/admin/stats` endpoint (loopback-only). Counters for requests protected, tokens processed, emails filtered. Persistent to disk every 30s.

## Architecture

```
Hermes ----virtual key----> ClawShell ----real key + DLP scan----> LLM Provider
                            |                                        |
                            +-- reads /etc/clawshell/ (privileged)  |
                            +-- /admin/stats (loopback only) --------+
```

Under 10MB memory. Written in Rust with Tokio.

## Installation

```bash
cargo install clawshell --locked
sudo clawshell onboard  # sets up security boundary
```

Or via NPM.

## Assessment for Our Stack

**Overlaps with existing hardening:**
- We already have: gitleaks 8.30.1, config at 600 permissions, approvals.mode=smart, redact_pii=true, gateway on localhost only
- ClawShell adds: virtual key isolation (Hermes never touches real keys), runtime DLP on API traffic

**Why not adopted:**
- Single-user macOS setup with terminal-based profile — key isolation overhead isn't justified
- We don't share keys across multiple agent instances
- Would require running ClawShell as a systemd service (or equivalent launchd plist)
- Existing security measures cover our threat model (single-user dev machine, no multi-tenant exposure)

**Would reconsider if:**
- We start running a multi-tenant Hermes gateway
- We need to share API credentials across agent team members
- Compliance requirements mandate key isolation (SOC2, etc.)
