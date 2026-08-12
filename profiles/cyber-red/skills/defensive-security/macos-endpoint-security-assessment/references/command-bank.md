# macOS Assessment Command Bank

Tested on macOS 15 Sequoia (Intel, x86_64). Read-only unless noted. Root-gated checks are marked.

## Baseline
```bash
sw_vers; uname -a; uptime; id
csrutil status                                   # SIP
spctl --status                                   # Gatekeeper
fdesetup status                                  # FileVault
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode
softwareupdate --list                            # pending patches (no sudo needed)
defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser
defaults read com.apple.screensaver askForPassword
```

## Persistence
```bash
ls -la ~/Library/LaunchAgents /Library/LaunchAgents /Library/LaunchDaemons /Library/StartupItems
for d in ~/Library/LaunchAgents /Library/LaunchAgents /Library/LaunchDaemons; do
  for f in "$d"/*.plist; do
    [ -f "$f" ] || continue
    echo "[$f]"
    /usr/libexec/PlistBuddy -c "Print :Label" "$f" 2>/dev/null
    /usr/libexec/PlistBuddy -c "Print :ProgramArguments" "$f" 2>/dev/null | tr '\n' ' ' | head -c 200
    echo
  done
done
ls /usr/lib/cron/tabs; cat /etc/crontab 2>/dev/null
ls /etc/periodic/daily /etc/periodic/weekly /etc/periodic/monthly
osascript -e 'tell application "System Events" to get the name of every login item'
launchctl list | grep -v com.apple
profiles -P                                      # ROOT required — note as gap if it fails
```

## Credential / config surfaces
```bash
ls -la ~/.ssh/; cat ~/.ssh/authorized_keys
cat /etc/hosts                                   # ad-block / exfil-block edits: intentional or not?
for f in ~/.zshrc ~/.zprofile ~/.bash_profile ~/.bashrc ~/.profile; do [ -f "$f" ] && echo "--- $f" && cat "$f"; done
scutil --proxy
scutil --dns | grep nameserver | sort -u          # hijacked DNS = unexpected nameservers
ls -lt ~/Downloads ~/Desktop | head -30           # plaintext recovery codes / tokens live here
```

## Processes / network
```bash
ps aux -r | head -15; ps aux -m | head -10
ps aux | grep -iE "miner|xmrig|kdevtmpfsi|kinsing|sliver|cobalt|meterpreter|netcat|socat" | grep -v grep
lsof -i -P -n | grep LISTEN
# ControlCenter binding *:5000 and *:7000 = AirPlay Receiver (LAN exposure finding)
find /tmp /var/tmp -maxdepth 3 -type f -perm -111 2>/dev/null
lsof -i -P -n | grep -E ":(22|5900|3283|548) "   # sshd / screensharing / SMB listening?
```

## Integrity
```bash
for a in /Applications/*.app; do echo "--- $(basename "$a")"; codesign -dvv "$a" 2>&1 | grep -E "Authority|Signature=" | head -5; done
# Authority=Developer ID Application: <vendor> (TEAMID) = properly signed; blank = ad-hoc/unsigned
xattr -p com.apple.quarantine "/Applications/App.app"   # non-empty = downloaded from internet
dscl . -list /Users | grep -viE "^_|root|nobody|daemon|Guest"
last -15
```

## macOS-specific malware homes
```bash
ls ~/Library/Input\ Methods /Library/Input\ Methods
ls ~/Library/Internet\ Plug-Ins /Library/Internet\ Plug-Ins
ls /Library/Extensions; kextstat | grep -v com.apple        # loaded third-party kexts
ls /Library/Audio/Plug-Ins/HAL /Library/QuickLook /Library/PrivilegedHelperTools
ls ~/Library/Application\ Support/Google/Chrome/Default/Extensions
ls ~/Library/Application\ Support/BraveSoftware/Brave-Browser/Default/Extensions
ls ~/Library/Safari/Extensions
ls ~/Library/Application\ Support
```
Known Mac malware name greps: mackeeper|searchawesome|genieo|advanced.?mac.?cleaner|vsearch|bundlore|macbooster|shlayer|installcore|superfish

## ClamAV setup + scan (Homebrew)
```bash
brew install clamav
cp /usr/local/etc/clamav/freshclam.conf.sample /usr/local/etc/clamav/freshclam.conf
sed -i '' 's/^Example/#Example/' /usr/local/etc/clamav/freshclam.conf   # REQUIRED or freshclam refuses
freshclam                                    # ~3.6M signatures; a few minutes
clamscan --recursive -i --max-filesize=400M --max-scansize=800M \
  /Applications /Library /Users/Shared \
  ~/Downloads ~/Desktop ~/Documents \
  ~/Library/LaunchAgents ~/Library/Application\ Support
# -i = infected-only output. The Application Support pass takes 15-30 min -> run background + notify_on_complete
```

## Patch debt
```bash
brew outdated --verbose
# Flag security-relevant updates: certifi (CA bundle), openssl, tailscale, python, postgresql, sqlite, libtiff
```

## Findings framing (delivered in chat, not a report file unless asked)
- HIGH: pending OS security updates (`softwareupdate --list`), outdated sec-relevant brew packages
- MEDIUM: plaintext recovery codes in Downloads/Desktop, AirPlay Receiver on all interfaces, browser 1 minor behind
- LOW: firewall stealth off, no lock-screen password, unused signed kexts, staged SSH authorized_keys
- INFO: agent-control apps (e.g. CuaDriver/com.trycua.driver — screen capture + AppleEvents), voice-recording apps, /etc/hosts edits
- Always list root-gated gaps: TCC db, /var/db/launchd.db, profiles -P
