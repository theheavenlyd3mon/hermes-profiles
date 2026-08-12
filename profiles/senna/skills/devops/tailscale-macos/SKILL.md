---
name: tailscale-macos
description: Get Tailscale running and connected on macOS when the daemon won't start or `tailscale status` fails. Covers the dual-install conflict (native Tailscale.app vs Homebrew CLI) and the macOS system network-extension approval gate that only a human can click.
---

# Tailscale on macOS — bring-up & troubleshooting

## When to use
- User asks to "turn on / connect / start Tailscale" on a Mac and it isn't coming up.
- `tailscale status` returns any of:
  - `failed to connect to local Tailscale service; is Tailscale running?`
  - `Failed to connect to local Tailscale daemon ... dial unix /var/run/tailscaled.socket: connect: no such file or directory`
- No `100.x` address from `tailscale ip`, or no tailscale interface in `ifconfig`.

## Core diagnosis (run in order)
1. `which tailscale` then `tailscale status` — confirm the binary is present and capture the EXACT error string.
2. Identify what's installed:
   - `ls -d "/Applications/Tailscale.app"` → native app present?
   - `brew list tailscale` → Homebrew install present?
   - `launchctl list | grep -i tailscale` → anything registered?
3. **Dual-install conflict is the usual root cause.** Homebrew's `tailscale` CLI hardcodes the global daemon socket `/var/run/tailscaled.socket`. The native app runs its daemon as a macOS **network extension** (`IPNExtension`) with a *different* local API path. When both exist, the `$PATH` CLI (Homebrew) talks to a socket that doesn't exist → every command fails even if the app's extension is alive.
4. **Check the network-extension approval gate:** `systemextensionsctl list`.
   - If Tailscale is NOT in the `activated enabled` list, the tunnel can never come up. This is a **GUI-only gate** — no CLI or agent can click "Allow". The user must approve it (see below).
5. Process check: `pgrep -fl IPNExtension`, `pgrep -fl tailscaled`.

## The macOS network-extension approval gate (critical)
- Tailscale on macOS uses a system network extension. First launch triggers an approval prompt ("Tailscale would like to add a VPN configuration") plus a System Settings approval step. **A human must click Allow/Enable.** This cannot be automated — the agent must hand this step to the user.
- Path for the user: System Settings → General → Login Items & Extensions → Network Extensions (or approve the prompt when the app launches).
- `systemextensionsctl list` shows approved extensions. If only Proton VPN / WireGuard appears and Tailscale is absent, the extension isn't activated → connection is impossible until the user approves. Note: other VPNs (e.g. Proton VPN) can coexist in the approved list; their presence doesn't mean Tailscale is approved.

## Recommended fix path — two viable strategies

**Strategy A: Consolidate on the native app (recommended if no terminal CLI needed).** Uninstall the Homebrew CLI so it stops shadowing the GUI's socket story in `$PATH`. The app owns the daemon; use the GUI for status/control.
```bash
brew services stop tailscale 2>/dev/null
pkill -f tailscaled 2>/dev/null
brew uninstall tailscale 2>&1 | tail -3
rm -f /Library/LaunchDaemons/*tailscale* ~/Library/LaunchAgents/*tailscale* 2>/dev/null
open -a Tailscale
```
**Strategy B: Keep BOTH — GUI daemon + Homebrew CLI via `TS_SOCKET` routing (recommended if the user wants a terminal CLI).** This is the key fix: the GUI's LocalAPI is on a **TCP port**, and you route the CLI to it instead of the nonexistent unix socket. You do NOT need to remove either install.
```bash
brew install tailscale                                   # CLI binary only; GUI owns the daemon
PG="$HOME/Library/Group Containers/W5364U7YZB.group.io.tailscale.ipn.macos"
PORT=$(basename "$PG"/sameuserproof-* | sed -E 's/sameuserproof-([0-9]+)-.*/\1/')
TS_SOCKET="localhost:$PORT" tailscale status             # now talks to the GUI daemon
```
`W5364U7YZB.group.io.tailscale.ipn.macos` is Tailscale's stable Apple team ID — identical on every Mac. The `sameuserproof-<port>-<token>` file reveals the live LocalAPI port. A wrapper that auto-detects the port (and survives app restarts / `brew upgrade`) is provided at `scripts/tailscale-wrapper.sh` — install to `~/.local/bin/tailscale` and put `~/.local/bin` FIRST in PATH so it wins over the Homebrew symlink.

**In both strategies, the GUI gate must still be passed by the user:** approve the network extension + sign in to the tailnet (hand to user — see the gate section above).

**Verify after approval + login:**
- `tailscale status` lists peers with no socket error.
- `tailscale ip` returns a `100.x.x.x` address.
- `ifconfig` shows a tailscale interface (often a `utun` with mtu 1380).
- `tailscale ping --timeout 4s --c 1 <peer-ip>` returns `pong` (end-to-end proof).

## Verification checklist
- [ ] `tailscale status` → nodes listed, no socket error
- [ ] `tailscale ip` → `100.x.x.x` returned
- [ ] `ifconfig` → tailscale interface present
- [ ] `systemextensionsctl list` → Tailscale extension `activated enabled`

## Pitfalls
- **Don't assume `open -a Tailscale` fixed it.** It starts the extension but does NOT resolve the dual-install CLI/socket mismatch, nor the approval gate.
- **Don't treat "IPNExtension running" as "connected."** The extension can be alive while the tunnel/interface is down and no login token exists (`tailscale status` still fails).
- **`security` command can be shadowed.** In this environment `security find-generic-password ...` returned a `hermes` usage dump — the `security` binary was intercepted by an alias/function named `hermes`. If you get a `hermes [-h]` usage dump instead of keychain output, invoke it by absolute path: `/usr/bin/security find-generic-password ...`.
- A coexisting VPN (e.g. Proton VPN WireGuard) in `systemextensionsctl list` does NOT imply Tailscale is approved — check for Tailscale's own entry specifically.
- **`TS_SOCKET` must be TCP, not the default unix socket.** Homebrew's CLI defaults to `/var/run/tailscaled.socket` (unix), which the GUI never creates. Force `TS_SOCKET=localhost:<port>` (TCP). This is the actual fix that makes `tailscale status` work alongside the native app.
- **The LocalAPI port changes between app launches** — auto-detect it from `sameuserproof-*`; never hardcode a port.
- **macOS has no GNU `timeout` binary.** Use `tailscale ping --timeout 4s --c 1 <ip>` for bounded waits; do not call `timeout`.
- **Client/server version-mismatch warning** (e.g. `client 1.98.8 ... != tailscaled server 1.98.5`) is harmless and clears on the next Tailscale.app update — no action needed.

## New-user education & live tailnet reconciliation
When the user is new to Tailscale or wants to *compare past session state to current live state* (e.g. "we discussed X, how does it look now?"), use this flow:
1. Recall the prior session: `session_search(query="tailscale")`, then read the relevant `session_id`.
2. Capture the **then** state (node list, IPs, what services were open).
3. Run live checks from this Mac (the admin machine):
   - `tailscale status` — current peers + online/offline + last-seen.
   - `tailscale ping --timeout 5s --c 1 <peer-ip>` — end-to-end proof. A **direct** path prints `pong from <host> (<ip>) via <lan-ip>:<port>`; a relayed path shows a DERP hop. Offline peers time out — expected for asleep phones, not a failure.
   - Avoid `tailscale whois me` — it errors with `400 Bad Request: invalid 'addr' parameter`. Use `tailscale status` or `tailscale whois <ip>`.
4. Present a **Then vs Now** table: Device | Tailscale IP | OS | Then-state | Now-state | Reachable from this Mac?.

See `references/tailscale-concepts.md` for the conceptual deep-dive (what Tailscale is, the security model, Headscale as a self-hosted alternative, and the provider comparison) to hand the user when they say "educate me, I'm new."

## References
- `references/diagnosis-command-sequence.md` — the exact command sequence and findings from a real dual-install failure, for reproduction.
- `references/tailscale-concepts.md` — beginner-to-intermediate knowledge bank: what Tailscale is, mental model, security model, Headscale alternative, provider comparison, and the live tailnet "then vs now" reconciliation technique.
