---
name: macos-endpoint-security-assessment
description: Scan a Mac for malware, persistence, and overlooked vulns.
domain: cybersecurity
subdomain: endpoint-security
version: '1.0'
---

# macOS Endpoint Security Assessment

Defensive workflow: hunt malware, enumerate persistence, and surface overlooked vulnerabilities on a macOS host (authorized/owned machine). Complements the Windows/Linux persistence skill — macOS has no registry; use LaunchAgents/Daemons instead.

## When to Use
- "Scan my Mac for malware / anything suspicious"
- "Find vulnerabilities that were overlooked on this machine"
- Baseline/health check of a macOS endpoint

## Workflow

1. **Baseline posture** (read-only, no sudo for most)
   - `sw_vers` / `uname -a`, `uptime`, `id` (note admin groups)
   - `csrutil status` (SIP), `spctl --status` (Gatekeeper), `fdesetup status` (FileVault)
   - `socketfilterfw --getglobalstate` and `--getstealthmode` (firewall + stealth)
   - `softwareupdate --list` (pending patches), autologin, screensaver lock prefs

2. **Persistence** (macOS equivalents of Run keys / scheduled tasks)
   - `~/Library/LaunchAgents`, `/Library/LaunchAgents`, `/Library/LaunchDaemons`, `/Library/StartupItems`
   - Inspect non-Apple plists with `/usr/libexec/PlistBuddy` (Print :Label / :Program / :ProgramArguments)
   - `/usr/lib/cron/tabs`, `/etc/crontab`, `/etc/periodic/*`, login items via `osascript`
   - `launchctl list | grep -v com.apple`; `profiles -P` (needs root — note if unavailable)

3. **Credential / exfil surfaces**
   - `~/.ssh/authorized_keys`, `/etc/hosts`, shell rc files (`~/.zshrc` etc.)
   - `scutil --proxy` (proxy hijack), `scutil --dns` (DNS hijack)
   - Plaintext secrets in Downloads/Desktop (recovery codes, tokens) — common finding

4. **Process & network**
   - `ps aux -r` / `-m` (top CPU/MEM), suspicious-name grep (miners, known malware)
   - `lsof -i -P -n | grep LISTEN` — flag ControlCenter `*:5000`/`*:7000` = AirPlay Receiver
   - Outbound connections; `/tmp` + `/var/tmp` executables (`find -perm -111`)

5. **Integrity**
   - `codesign -dvv` on every `/Applications/*.app` — Authority lines must show a Developer ID; blank/adhoc = finding
   - `xattr -p com.apple.quarantine` — non-empty means downloaded-from-internet (origin evidence, NOT malice)
   - `dscl . -list /Users` (non-system users), `last` (login history)

6. **macOS-specific vectors** (classic malware homes)
   - Input Methods (`~/Library/Input Methods`, `/Library/Input Methods`), Internet Plug-Ins
   - `/Library/Extensions` + `kextstat` (loaded third-party kexts), `/Library/Audio/Plug-Ins/HAL`
   - `/Library/QuickLook`, `/Library/PrivilegedHelperTools`
   - Browser extensions: Chrome/Brave `.../Default/Extensions`, Safari `~/Library/Safari/Extensions`
   - `~/Library/Application Support` odd dirs, `/Users/Shared`

7. **Malware scan (ClamAV)**
   - `brew install clamav`; copy freshclam.conf.sample to freshclam.conf and COMMENT the `Example` line or freshclam refuses; `freshclam` (~3.6M sigs, few min); then `clamscan --recursive -i --max-filesize=400M --max-scansize=800M <targets>`
   - Targets: `/Applications /Library /Users/Shared ~/Downloads ~/Desktop ~/Documents ~/Library/LaunchAgents ~/Library/Application Support` — skip `/System`, `/usr/local`
   - The Application Support pass takes 15-30 min: run in background with notify_on_complete

8. **Patch debt / vuln inventory**
   - `brew outdated --verbose` (flag security-relevant: certifi, openssl, tailscale, python, postgresql, sqlite)
   - App versions vs current stable (quick web check for Chrome/Brave/etc.)

9. **Report**
   - Deliver findings IN CHAT — this user's stated preference; only write a file if explicitly asked
   - Severity buckets: HIGH = pending OS updates / sec-relevant patch debt; MEDIUM = plaintext secrets, AirPlay exposure; LOW = firewall stealth off, no lock password, unused kexts, staged SSH keys; INFO = agent-control apps, privacy apps, /etc/hosts edits
   - State clearly what needed root and wasn't checked (TCC db, `/var/db/launchd.db`, `profiles -P`)

## Pitfalls
- macOS persistence != Windows: no registry; the Windows/Linux persistence skill does NOT cover macOS locations
- `freshclam` refuses to run until the `Example` line in freshclam.conf is commented out
- Don't string-grep all of /Applications (times out ~180s); target likely apps only
- `codesign -dvv`: judge by Authority lines; their absence = unsigned/ad-hoc (Gatekeeper bypass risk)
- SSH group membership (`com.apple.access_ssh`) != SSH enabled; confirm via `lsof` for port 22
- AirPlay Receiver binds `*:5000`/`*:7000` via ControlCenter even when prefs look unset — real LAN exposure
- Long ClamAV pass goes in background; never block the session on it
- Quarantine xattr is normal for downloaded apps — it's evidence of origin, not a verdict
- When the trigger is a named supply-chain advisory (npm/PyPI package compromise), run the targeted triage FIRST via the `npm-supply-chain-sweep` skill — it is usually conclusive and this user prefers prompt results over the long ClamAV pass

## Support files
- `references/command-bank.md` — full tested command bank for this workflow (macOS 15 Sequoia, Intel)
