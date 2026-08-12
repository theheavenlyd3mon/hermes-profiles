# Tailscale Connectivity Pitfalls for Custom Providers

When a Hermes custom provider points to a `*.ts.net` (Tailscale MagicDNS) endpoint, several Tailscale-specific failure modes can prevent connectivity even though the server is running. These are **not** Hermes bugs — they're Tailscale client quirks.

---

## 1. `--reset` Nukes Accepted Cross-Tailnet Shares

```
tailscale up --reset --accept-dns
```

This is the most destructive pitfall. `--reset` resets **all** local daemon state, including accepted device shares from **other tailnets**. If the target machine lives on a different tailnet (e.g. `tail3bf242.ts.net`) and was shared to yours, the share gets dropped. The hostname `*.tail3bf242.ts.net` stops resolving.

**Symptom:** `curl https://machine.other-tailnet.ts.net/v1/models` → `curl: (6) Could not resolve host`
`tailscale status` doesn't show the shared machine.

**Fix:**
1. Open https://login.tailscale.com/admin/machines
2. Re-accept the share (it's still active server-side)
3. Or `tailscale logout && tailscale up --accept-dns` to re-pull fresh server state

**Prevention:** Never pass `--reset` on a machine that depends on cross-tailnet shares. If you must reset, note which shares need re-accepting before running it.

---

## 2. App Store Tailscale (IPNExtension) — No Unix Socket

The Mac App Store version of Tailscale runs as an **IPNExtension** — a macOS network extension process — rather than a standalone `tailscaled` daemon. It does **not** expose `tailscaled.socket` at `/var/run/tailscaled.socket`.

**Symptom:**
```
$ tailscale status
failed to connect to local tailscaled (which appears to be running as
IPNExtension, pid 46381). Got error: Failed to connect to local Tailscale
daemon for /localapi/v0/status; not running? Error: dial unix
/var/run/tailscaled.socket: connect: no such file or directory
```

The tunnel **IS** active — `ifconfig` shows a `utun` interface with a `100.x.x.x` Tailscale IP — but CLI commands fail. This is a cosmetic CLI gap, not a connectivity problem.

**Detection:**
```bash
# Check for the tailscale IP directly
ifconfig | grep -A4 "utun" | grep "inet " | grep "^[[:space:]]*inet 100"
```

**Workarounds:**
- Install CLI-tailscale via Homebrew: `brew install tailscale` (runs alongside App Store version)
- Or bypass CLI entirely: use `curl` against the Tailscale IP directly
- The App Store menubar app shows connection status

**Pitfall inside pitfall:** The App Store CLI binary (`/usr/local/bin/tailscale`) may be a different version than the IPNExtension daemon, producing version-mismatch warnings:
```
Warning: client version "1.96.4-t41cb72f27" != tailscaled server version "1.98.5-t8f8fe6a2e-gc1619fb10"
```
This warning is informational — the tunnel still works. But it means `tailscale up/reset/status` CLI commands may behave differently than expected because the newer daemon processes them differently.

---

## 3. `tailscale up` Requires ALL Non-Default Flags

```
$ tailscale up --accept-dns
Error: changing settings via 'tailscale up' requires mentioning all
non-default flags. To proceed, either re-run your command with --reset or
use the command below to explicitly mention the current value of
all non-default settings:

    tailscale up --accept-dns --accept-routes --exit-node-allow-lan-access
```

You **cannot** add a single flag — you must state every non-default flag. If the current config has `--accept-routes` active and you only pass `--accept-dns`, it toggles `--accept-routes` off.

**Fix:** Copy the full suggested command from the error output and run that.

---

## 4. Cross-Tailnet Device Sharing — Only via Admin Console

When a device lives on `tailA.ts.net` and needs to reach a device on `tailB.ts.net`:

- The sharer (owner of `tailB`) must **share** the device via https://login.tailscale.com/admin/machines
- The recipient (on `tailA`) must **accept** the share in their admin console
- Shared devices appear in `tailscale status` on the receiving side
- MagicDNS resolves the shared device's `*.tailB.ts.net` hostname **only after acceptance is confirmed**

**This cannot be done from the CLI** — there is no `tailscale share accept` command. The admin console is the only path.

**Key diagnostic truth:** `tailscale status` only shows devices that are **direct members** of your tailnet. A shared-but-not-yet-accepted node is NOT listed. Curl to it times out with `(28)` — identical symptom to an offline or non-existent machine. The absence from `tailscale status` is NOT diagnostic of the share being inactive; it only means you haven't accepted it yet. Open the admin console and look under "External Devices" or "Shared to my tailnet" to check.

---

## 5. DNS Verification Quick Reference

```bash
# Check if you're on the same tailnet as the target
tailscale status

# Check if MagicDNS resolves your own machine
host $(hostname).ts.net

# Check if the target hostname resolves (via Tailscale DNS)
curl -s -w '\n%{http_code}' --connect-timeout 5 https://machine.ts.net/v1/models

# Fallback: use the Tailscale IP directly (100.x.x.x)
# Find it on the target machine or ask the operator
curl -s http://100.x.x.x:8080/v1/models
```

| curl exit code | Meaning | Likely root cause |
|---|---|---|
| `(6)` | DNS resolution failure | Not on same tailnet, share not accepted, or `--accept-dns` was reset |
| `(7)` | Connection refused | Server not running (llama.cpp/Ollama not started, wrong port) |
| `(28)` | Timeout | Firewall, host unreachable on permitted port |
| HTTP 200 | Reachable | Server is up — test model name next |

---

## 6. `tailscale switch` for Multi-Account Machines

If the same machine has credentials for multiple Tailscale accounts (e.g., work + personal), `tailscale switch --list` shows available profiles:

```
ID    Tailnet                  Account
7341  personal.ts.net          user@github*
7342  work.ts.net              user@company.com
```

Switch with:
```bash
tailscale switch 7342
```

The `*` indicates the active profile. Each profile has its own tailnet membership, MagicDNS zone, and shared devices.
