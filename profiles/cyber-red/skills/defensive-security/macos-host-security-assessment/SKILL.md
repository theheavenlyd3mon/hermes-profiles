---
name: macos-host-security-assessment
description: Audit a macOS host for malware and vulnerabilities.
domain: cybersecurity
subdomain: host-security
tags:
- macos
- malware-scanning
- vulnerability-assessment
- persistence
- clamav
- codesign
- incident-response
mitre_attack:
- T1543.001
- T1547.001
- T1059.004
- T1078
version: '1.0'
---

# macOS Host Security Assessment

## When to Use
- User asks to "look for malware", "check for vulnerabilities", or "see what was overlooked" on a Mac (their own machine, authorized defensive work)
- Pre-purchase / post-migration health check of a macOS host
- Threat-hunting on a Mac: persistence, unsigned apps, exposed services, patch debt
- Advisory-driven npm supply-chain sweep (poisoned package list from a tweet/blog)? That is a different class — load `npm-supply-chain-sweep` (version-based verdicts, publish-time proof). This skill covers the host itself.

## Delivery Preference (IMPORTANT)
- Deliver ALL findings in the chat reply, severity-ordered, plain text — do NOT make a written report file the deliverable.
- The user has explicitly corrected this: findings belong in chat ("share all of your findings here with us in chat"). A saved copy on disk is optional and secondary; if you write one, say its path in one line and keep the chat reply complete on its own.
- Structure chat output: bottom line first, then MALWARE SCAN results, then findings ordered HIGH/MEDIUM/LOW/INFO with concrete fix commands, then "worth knowing" notes.

## Workflow

### Step 1: System state & security baseline
```bash
sw_vers; uname -a; uptime; whoami; id
csrutil status                    # SIP: must be enabled
spctl --status                    # Gatekeeper: "assessments enabled"
fdesetup status                   # FileVault: On/Off
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode
```

### Step 2: Patch status
```bash
softwareupdate --list             # pending OS/Safari updates (recommended labels = HIGH finding)
brew outdated --verbose           # outdated formulae w/ version deltas
# Security-relevant brew packages to call out: certifi, postgresql, tailscale, python, sqlite, openssl, curl, wget
```

### Step 3: Persistence enumeration (macOS equivalents — the loaded Windows/Linux persistence skill does NOT cover these)
```bash
ls -la ~/Library/LaunchAgents /Library/LaunchAgents /Library/LaunchDaemons /Library/StartupItems
ls /usr/lib/cron/tabs; cat /etc/crontab; ls /etc/periodic/daily /etc/periodic/weekly /etc/periodic/monthly
osascript -e 'tell application "System Events" to get the name of every login item'
launchctl list | grep -v com.apple
ls -la ~/.ssh/; cat ~/.ssh/authorized_keys
cat /etc/hosts                    # look for intentional blocks vs hijack
for f in ~/.zshrc ~/.zprofile ~/.bash_profile /etc/zprofile /etc/zshrc; do [ -f "$f" ] && cat "$f"; done
profiles -P                       # config profiles (needs root — note if unavailable)
```
Inspect every non-Apple plist's Label/Program/ProgramArguments:
```bash
for f in ~/Library/LaunchAgents/*.plist /Library/LaunchAgents/*.plist /Library/LaunchDaemons/*.plist; do
  [ -f "$f" ] || continue
  echo "[$f]"
  /usr/libexec/PlistBuddy -c "Print :Label" "$f" 2>/dev/null
  /usr/libexec/PlistBuddy -c "Print :ProgramArguments" "$f" 2>/dev/null | tr '\n' ' ' | head -c 200; echo
done
```

### Step 4: Processes & network
```bash
ps aux -r | head -14              # top CPU
ps aux -m | head -10              # top mem
ps aux | grep -iE "miner|xmrig|kdevtmpfsi|kinsing|masscan|sliver|cobalt|meterpreter|netcat|socat|nc -" | grep -v grep
find /tmp /var/tmp -maxdepth 3 -type f -perm -111 2>/dev/null | head
lsof -i -P -n | grep -i LISTEN    # listening sockets
scutil --proxy                    # proxy hijack check
scutil --dns | grep "nameserver\[" | sort -u   # DNS hijack check
lsof -i -P -n | grep -E ":(22|5900|3283|548)\s"   # ssh/screensharing/smb listening
```

### Step 5: App integrity (codesign + quarantine)
```bash
for a in /Applications/*.app; do
  echo "--- $(basename "$a")"
  codesign -dvv "$a" 2>&1 | grep -E "Authority=|flags=" | head -5   # use -dvv, NOT --verbose=4 (format differs, Authority lines get missed)
done
for a in /Applications/*.app; do q=$(xattr -p com.apple.quarantine "$a" 2>/dev/null); [ -n "$q" ] && echo "$(basename "$a"): $q"; done
```
- Every app should show `Authority=Developer ID Application: <vendor>` — unsigned/ad-hoc = finding.
- Quarantine xattr present = downloaded from internet, Gatekeeper assessed it.

### Step 6: macOS-specific malware vectors
```bash
ls -la ~/Library/Input\ Methods /Library/Input\ Methods     # input method implants
ls ~/Library/Internet\ Plug-Ins /Library/Internet\ Plug-Ins
ls ~/Library/Extensions /Library/Extensions; kextstat | grep -v com.apple   # kexts loaded?
ls /Library/Audio/Plug-Ins/HAL /Library/QuickLook ~/Library/QuickLook
ls -la /Library/PrivilegedHelperTools
ls ~/Library/Application\ Support/Google/Chrome/Default/Extensions 2>/dev/null   # Chrome ext IDs
ls ~/Library/Application\ Support/BraveSoftware/Brave-Browser/Default/Extensions 2>/dev/null
ls ~/Library/Safari/Extensions 2>/dev/null
ls ~/Library/Application\ Support/                        # odd dir names worth a look
```

### Step 6.5: Targeted advisory triage (do this BEFORE any scan)
When the trigger is a named compromise advisory (npm/PyPI supply-chain packages, dropper filenames, C2 domains), run the TARGETED sweep first — do NOT default to the long ClamAV pass. Load `npm-supply-chain-sweep` (version-vs-poison verdict, dropper files, caches, publish-date proof). A conclusive targeted sweep makes the ClamAV pass unnecessary — this user said exactly that: "stop the scan, we don't need it" when the targeted evidence already decided it. ClamAV is for general suspicion with no named IOCs.

### Step 7: Malware scan with ClamAV (installed on demand via Homebrew)
```bash
brew install clamav                       # run in background; takes minutes
cp /usr/local/etc/clamav/freshclam.conf.sample /usr/local/etc/clamav/freshclam.conf
sed -i '' 's/^Example/#Example/' /usr/local/etc/clamav/freshclam.conf   # REQUIRED or freshclam refuses
freshclam                                 # signature download ~3.6M sigs, background it
clamscan --recursive -i --max-filesize=400M --max-scansize=800M \
  /Applications /Library /Users/Shared ~/Downloads ~/Desktop ~/Documents \
  ~/Library/LaunchAgents ~/Library/Application\ Support   # -i = infected only
```
- Full user-library scan takes 5–15 min: run in background, report the `Infected files:` summary line.
- Skip /System and ~/.hermes (huge, protected, self).

### Step 8: Users, logins, misc hardening
```bash
dscl . -list /Users | grep -viE "^_|root|<user>|nobody|daemon|Guest"
last -15
defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser   # autologin
defaults read com.apple.screensaver askForPassword                        # lock on screensaver
ls /Applications ~/Applications | grep -iE "teamviewer|anydesk|parsec|rustdesk|splashtop|todesk"  # RAT/remote tools
```

## Known macOS services that LOOK suspicious but are legit
- `ControlCenter` binding `*:5000` and `*:7000` = AirPlay Receiver (not malware; MEDIUM finding at most — disable in System Settings if unused).
- `rapportd` `*:55632` = Apple Nearby/continuity.
- HighPointIOP.kext / HighPointRR.kext in /Library/Extensions, not loaded = leftover RAID drivers on a laptop, low-severity housekeeping.
- See references/known-benign-macos-items.md for the full session-derived list (incl. CuaDriver).

## Report Format
Bottom line first (malware found or not, posture good/bad), then:
1. MALWARE SCAN results (persistence, processes, extensions, codesign, ClamAV)
2. Findings ordered HIGH / MEDIUM / LOW / INFO — each with what was found, why it matters, exact fix command
3. "Worth knowing" notes (privacy-relevant apps, agent-control software, intentional hosts edits)

## Pitfalls
- The Anthropic `performing-malware-persistence-investigation` skill is Windows/Linux-only (registry, schtasks, WMI). On macOS use LaunchAgents/Daemons + cron + login items (Step 3) — do not try to port its commands literally.
- NEVER recursive-grep /Applications/*.app/Contents to find which app owns a file — times out (180s+). Grep only specific app `Contents/Resources` dirs.
- `codesign --verbose=4` changes output format and hides Authority lines; use `-dvv` for the signature chain.
- `freshclam` needs the Example line commented out in freshclam.conf before first run.
- Check `lsof -iTCP:PORT` to confirm what binds a suspicious port before flagging it.
- Homebrew cask-installed apps (MarkEdit etc.) carry quarantine xattrs — that's normal, not a finding.
- `profiles -P` and most /Library/Preferences writes need root: note "could not verify without sudo" rather than guessing.
- Package DIR NAMES in node_modules are NOT findings (keyv, file-entry-cache, cacheable-request are benign eslint/stylelint transitive deps) — the exact installed version vs the poisoned version is the verdict; see `npm-supply-chain-sweep`.
- After a backgrounded `brew upgrade` (especially through a wrapper like rtk whose tail output looks like planning, not completion), verify ground truth with `brew outdated --verbose` — empty means done. Use `brew uses --installed <pkg>` before removing a formula to confirm nothing else depends on it, then `brew autoremove` for orphans (removing llama.cpp also freed ggml + libomp).

## Support Files
- scripts/macos_security_snapshot.sh — re-runnable enumeration script covering Steps 1–8 (safe, read-only).
- references/known-benign-macos-items.md — session-derived list of look-suspicious-but-legit apps/services and how to verify each.
