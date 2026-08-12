---
name: macos-host-security
description: >
  Class-level skill for defensive macOS host reviews.
  Use when asked to audit FileVault, Gatekeeper, XProtect/MRT,
  Application Firewall, SIP, directory permissions, login items,
  launch agents, TCC exposure, network listeners, SSH hardening,
  and overall macOS risk posture.
  Produces a structured read-only report with CRITICAL/HIGH/MEDIUM/LOW/INFO
  findings plus concrete fixes.
  Also useful for attacker-eye reviews and CIS-style hardening checks.
---

# macOS Host Security

## Trigger
- User asks for macOS security check, hardening review, privacy posture, malware triage.
- Phrase hints: "security review", "audit my Mac", "check TCC", "is FileVault on?", "SSH risks", "suspicious launch agents".

## Role
You are a defensive-security reviewer with OS-level offensive awareness.
Do everything read-only. Enumerate, classify, recommend. Do not modify the system.

## Mandatory Output Structure
Deliver a structured Markdown report with these sections:
1. **Executive Summary** — 1-2 sentences + overall score.
2. **Findings** — grouped by category.
3. **Risk Matrix** — columns: Finding | Severity | Evidence | Recommended Fix
4. **High-Priority Fixes** — numbered list.
5. **Evidence Appendix** — key command outputs supporting findings.

Severity labels:
- **CRITICAL** — immediate exploitability or broken defense.
- **HIGH** — plausible bypass or missing control.
- **MEDIUM** — reduced defense-in-depth or bad hygiene.
- **LOW** — informational risk or best-practice gap.
- **INFO** — expected behavior or context.

Save the report to `~/<report-name>.md`.

## Review Checklist (Do This In Order)

### 1. Platform Fundamentals
- FileVault: `fdesetup status`
- Gatekeeper: `spctl --status`
- XProtect/MRT: version via `defaults read` or note limitation if unavailable
- SIP: `csrutil status`
- Application Firewall: `socketfilterfw --getglobalstate`
- Stealth mode: `socketfilterfw --getstealthmode`
- App Firewall apps: `socketfilterfw --listapps`

### 2. Directory / File Hygiene
- `~/Library` permissions
- `/usr/local` permissions
- `/opt/homebrew` permissions
- `~/Downloads` quarantine / xattr exposure
- `~/Library/LaunchAgents` non-Apple plist count

### 3. Account & Login Policy
- Login window: `defaults read com.apple.loginwindow`
- User setup: single-user, guest state
- Shell profiles: `.zshrc`, `.zprofile`, `.profile`, `.login`
- Login items: `osascript -e 'tell application "System Events" to get the name of every login item'` or note limitation

### 4. Persistence & Processes
- `ps` snapshot (BSD `ps -ax -o user,pid,stat,command`; avoid Linux-only flags)
- `launchctl list` (flag non-Apple agents)
- Compare every non-Apple launch agent label against installed apps and user expectation

### 5. Network Exposure
- `lsof -nP -i`
- Look for public listeners, unexpected outbound IPv6, non-Apple mDNS bursts.
- Map PIDs to processes when unclear.

### 6. TCC & Privacy
- TCC DB: `sqlite3 ~/Library/Application\\ Support/com.apple.TCC/TCC.db` often fails on modern macOS — treat "unreadable" as expected INFO.
- Quarantine data: `xattr -rl <paths>` for curated CLI tools and Downloads.

### 7. SSH Hardening
- `cat /etc/ssh/sshd_config` — check for `PasswordAuthentication`, `PermitRootLogin`, `AuthorizedKeysFile`
- User SSH config absent/present
- `~/.ssh/authorized_keys` presence

### 8. Extra Signals
- Non-Apple binaries in `$PATH`
- Suspicious domains in `lsof` connections
- Third-party updaters: Google Keystone, Discord ShipIt, Notion updater — categorize

## Attacker-Eye Lightweight External-Surface Review
Use when the goal is offensive reconnaissance on a macOS endpoint, not a standard defense audit.
Scope: external-visible attack surface, credential hygiene, and secret leakage from normal user workflow.

### 8a. Public-Facing Listeners
- `lsof -nP -iTCP -sTCP:LISTEN` then filter out `127.0.0.1` and loopback-only entries.
- Confirm adapter binding with `*:` or explicit non-loopback IP.
- Map PID to binary and label.

### 8b. Cron / Launchd Persistence
- User crontab: `crontab -l`
- System cron dirs: `/etc/crontab`, `/etc/cron.d`, `/etc/cron.{daily,hourly,weekly,monthly}`
- `launchctl list` — capture *everything*, not just Hermes agents.
- enumerate `/Library/LaunchAgents`, `/Library/LaunchDaemons`, `~/Library/LaunchAgents`, `~/Library/LaunchDaemons`
- flag non-Apple `RunAtLoad`, world-writable plists, `KeepAlive == 1`, and long-lived Python/Node daemons with broad filesystem access.

### 8c. World-Writable and Legacy Files in Sensitive Paths
- Scan home, `/etc`, `/var`, `/usr/local`, `/Applications` with `find ... -perm -0002 -type f`
- de-noise cache paths: `.bun/install/cache`, `.docker`, `.cache`, `venv/.lock`
- remaining matches are notable unless they are expected temp/log artifacts

### 8d. Keychain and Browser Credential Cache Exposure
- Keychain DB path: `~/Library/Keychains/login.keychain-db` and `keychain-2.db`
- Native `security add-generic-password` / `security find-generic-password` usage is safe for CLI redaction, but inspect shell history for inline plaintext values
- browser credential stores paths: Chrome/Brave `Default/Login Data`, all `Cookies`/`Cookies-journal`
- Mail envelope stores if present: `~/Library/Mail`
- permissions should be `600` (`-rw-------`) or tighter

### 8e. Shell History, Downloads, Documents Secret Traces
- scan `~/.zsh_history`, `~/.bash_history` for provider key regexes:
  `AKIA[0-9A-Z]{16}`, `AIza[0-9A-Za-z\-_]{35}`, `sk-live-[A-Za-z0-9]{24,}`, `ghp_[A-Za-z0-9]{36}`, `github_pat_`, PGP/RSA private key headers, and inline `security add-generic-password -w "..."` with redaction markers
- downloads, desktop, screenshots: `find ~/Downloads ~/Desktop -maxdepth 2 -type f -printf '%TY-%Tm-%Td %p\n' | sort -r`
- document metadata: `mdls <pdf/doc/xls/pptx>` for author/title/content leaks

### 8f. Social Engineering and Metadata Footholds
- username/repo names inferred from `git config --global user.name`, remote URLs in history, and `.ssh/authorized_keys` comments
- OAuth tokens in `~/.config/gh/hosts.yml`
- embedded credentials in prior remote URLs in shell history: `https://<user>:<token>@github.com/...`
- any plaintext `.env.bak`, `.env.tmp`, or `pastes/` cache entries with partial credentials

### Required Output for This Path
- 3 worst issues with concise proof and exact remediation commands
- 5 quick wins with copyable commands

## Pitfalls
- BSD `ps` differs from GNU `ps` — use `ps -ax -o user,pid,stat,command`, not `ps aux --no-headers`.
- `/System/Library/CoreServices/CoreTypes.bundle/Contents/Info.plist` is often not useful for Gatekeeper/MRT version; use `softwareupdate --history` instead.
- Quarantine and `com.apple.provenance` on CLI binaries are common after first run; not inherently malicious.
- `sqlite3` access to TCC.db is usually blocked — do not treat this as a failure.
- Do not write to another Hermes profile's directories unless explicitly instructed.
- Secret backups are still attacksurface: `.env.bak` and `.env.tmp` live next to live `.env` files very often. If `.env` is strict `600`, `.env.tmp` with group/other read is still readable to other local users/processes. Include backup and temp secret files in hygiene checks.

## Session Evidence Bank
Use these session-specific notes to calibrate command success/failure patterns and common macOS anomalies:
- XProtect/MRT version via `defaults read` often returns `Unavailable`; use `softwareupdate --history` instead.
- `PlistBuddy` on `ManagedInstall` paths often reports `File Doesn't Exist, Will Create` under minimal quoting.
- BSD `ps` differs from GNU `ps`; use `ps -ax -o user,pid,stat,command` on macOS.
- TCC SQLite DB is usually unreadable on modern macOS; treat “unreadable” as expected INFO rather than audit failure.
- SSH hardening commonly lands at defaults that still allow password auth—verify and enforce key-only.
- Offensive external-surface sessions frequently surface:
  - Apple remote-facing listeners such as ControlCenter/ControlCe and rapportd on public ports; prefer calibrating PF rules only, not uninstalling system components.
  - shell-history redaction markers that still leak provider key fragments and embedded-PAT remote URLs.

## Tone
- Concise, scannable, evidence-first.
- No coaching narrative.
- Every recommendation must include a concrete command or setting change.
