---
name: tailscale-concepts
description: Condensed Tailscale knowledge bank — what it is, mental model, security model, Headscale alternative, provider comparison. For new-user education and architecture decisions.
---

# Tailscale — Conceptual Knowledge Bank

## What Tailscale is
- **Zero-config mesh VPN** built on **WireGuard** (modern, fast, secure VPN protocol).
- Devices connect **peer-to-peer** (direct), not through a central server. Tailscale automates key exchange, NAT traversal, peer discovery, and access control.
- Mental model: a *magic overlay network*. Each device gets a `100.x.x.x` IP (and a `fd7a:115c:...` IPv6) that works from anywhere — your iPhone on cellular reaches your home PC as if on the same LAN. No port forwarding, no router config, no firewall holes.

## Key concepts
| Term | Meaning |
|---|---|
| **Tailnet** | Your private network of authorized devices |
| **MagicDNS** | Human names (e.g. `xaviers-macbook-pro`) instead of `100.x` IPs |
| **DERP** | Tailscale's relay servers — used only when a direct peer path is impossible |
| **ACL / policy** | Granular rules for which devices can reach which services |
| **Exit node** | Route all your traffic through one device's internet connection |
| **Subnet router** | Expose an entire LAN (e.g. home lab) to the tailnet without installing clients on every device |

## Security model (the "doors = services" framing)
- Each device generates its **own keypair**; the private key never leaves the device.
- Devices register only their **public key** with the coordination (control) server — which brokers connections but **never sees traffic**.
- "Connected to the tailnet" ≠ "exposed." A node on the network is just *addressable*. You still open specific **services** (SSH, file sharing, RDP, screen sharing) — each is a *door*, each a potential attack surface. **Only open what you need.**
- Tailscale auth is **per-device**. Joining a new device to your account gives it no access to others it wasn't granted.
- Prefer **key-based auth** over passwords (ed25519 keys are effectively unguessable).
- Lock down exposed services with **ACLs** so only your own devices can reach them.

## Headscale — self-hosted control server
- Tailscale's coordination server is SaaS (their infra). **Headscale** is an open-source, self-hosted replacement for that control plane — same clients, you run the server.
- Use it when you want **zero dependency on Tailscale's servers** (data residency, no account/ToS, full control). Trade-off: you operate and secure the server yourself.
- Mentioned (not deployed) in prior sessions; the infra profile carries Magnus Hedemark's `headscale-*` skills (deploy / backup / derp / node-lifecycle / routing).

## Provider comparison (quick)
| | Tailscale | Raw WireGuard | ZeroTier | Cloudflare Tunnel |
|---|---|---|---|---|
| Setup effort | Zero-config | Manual keys/peers | Low | App-specific |
| NAT traversal | Automatic | Manual | Automatic | N/A (outbound) |
| Control plane | Tailscale SaaS (or Headscale) | None (you) | ZeroTier Inc | Cloudflare |
| Best for | Easy secure mesh | Max control/perf | Mesh + LAN | Expose a service to web |

## Home-lab usage
- Yes — people commonly run Tailscale for home labs. It **overlays** your existing network; it does not replace your router or WiFi. Use a **subnet router** to bring whole VLANs onto the tailnet without client installs on every device.
- Reduce exposure: only route the subnets you actually need.

## Live tailnet verification (from the admin Mac)
- `tailscale status` — peers, online/offline, last-seen.
- `tailscale ping --timeout 5s --c 1 <peer-ip>` — direct path prints `pong from <host> (<ip>) via <lan-ip>:<port>`; a relayed path shows a DERP hop; offline peers time out (expected for asleep phones, not a failure).
- `tailscale whois <ip>` for node ownership — NOT `tailscale whois me` (errors with `invalid 'addr' parameter`).
- Minor client/server version-mismatch warning is harmless; clears on next app update.
