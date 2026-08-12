# Look-Suspicious-But-Legit macOS Items (session-derived, 2026-08)

Items that alarm during a first pass but are legitimate. Verify the way listed
before spending time on them.

## CuaDriver.app (com.trycua.driver)
- Open-source "computer use agent" driver (Cua AI, Inc., YCK386LBJ7, Developer ID signed, runtime flag).
- Capabilities: screen capture + Apple Events (UI automation) on request from an agent.
- NOT malware; but it is agent-control software — confirm the user installed it intentionally.
- Verify: `codesign -dvv /Applications/CuaDriver.app`, `defaults read /Applications/CuaDriver.app/Contents/Info CFBundleIdentifier CFBundleShortVersionString`, and check it is not running (`ps aux | grep cua-driver`).

## ControlCenter binding *:5000 and *:7000
- AirPlay Receiver service. Looks like a weird daemon port pair; it is a first-party feature.
- Verify: `lsof -iTCP:5000 -iTCP:7000 -P -n` → COMMAND=ControlCe.
- Severity: at most MEDIUM (LAN exposure). Fix: System Settings > General > AirDrop & Handoff > AirPlay Receiver off.

## rapportd *:55632
- Apple "Nearby"/continuity handshake. Verify: `lsof -i -P -n | grep rapportd`.

## HighPointIOP.kext / HighPointRR.kext in /Library/Extensions
- HighPoint RAID drivers (com.highpoint-tech.kext.*, Developer ID signed, DX6G69M9N2).
- Common leftover on laptops from migrated images; NOT loaded (kextstat shows nothing).
- Low severity housekeeping: remove if no HighPoint hardware. Verify not loaded: `kextstat | grep -v com.apple`.

## SESSEReservationStorageV001.sqlite in ~/Library/Application Support/SESStorage/
- Tiny (24KB) dormant sqlite, no app references it, no process opens it.
- Believed leftover from an uninstalled app. Verify: `lsof <path>` returns nothing, targeted grep of app Resources finds no owner. Benign; deletable.

## Hermes gateway agents (ai.hermes.gateway-*)
- User's own Hermes Agent infra: `~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main --profile <name> gateway run --replace`.
- They open several 127.0.0.1 listeners and outbound 443 to Cloudflare (162.159.x.x) — expected on a machine running Hermes.

## Homebrew quarantine xattrs on cask apps
- MarkEdit etc. show `com.apple.quarantine` with `Homebrew Cask` as the agent — normal, not a finding.

## /etc/hosts entries blocking Session messenger endpoints
- e.g. `127.0.0.1 filev2.getsession.org seed1-3.getsession.org` labeled "Block ... exfiltration endpoints".
- Intentional privacy hardening, not hijack. Note it to the user; no action.

## MiniMax Hub data under ~/Library/Application Support/@hilo/
- Odd-looking dir name; contains "MiniMax Hub Global" — the legit app's data.

## Tailscale.app signed with "Apple Mac OS Application Signing" authority
- `codesign -dvv` shows `Authority=Apple Mac OS Application Signing` +
  `TeamIdentifier=W5364U7YZB`, NOT a Developer ID chain — looks off but is the
  legitimate Mac App Store build (`spctl -a -vv` → `accepted`, `source=Mac App Store`).
- Do not flag it; verify with spctl before spending time.

## Docker helpers "inside" /Library/QuickLook (snapshot-script artifact)
- `com.docker.socket` / `com.docker.vmnetd` actually live in
  `/Library/PrivilegedHelperTools` (standard Docker install). The snapshot
  script's multi-arg `ls ... /Library/QuickLook` prints the QuickLook header
  while the helper listing follows, so tee'd output can make them look like
  QuickLook contents. /Library/QuickLook itself is normally empty. Verify:
  `ls -la /Library/QuickLook/` vs `ls -la /Library/PrivilegedHelperTools/`.
