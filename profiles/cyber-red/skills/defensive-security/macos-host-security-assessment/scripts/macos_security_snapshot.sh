#!/bin/bash
# macOS host security snapshot — read-only enumeration, safe to run anytime.
# Covers: baseline, patch status, persistence, processes/network, app integrity,
# macOS vectors, users/logins, hardening checks. ClamAV scan is a separate step.
# Usage: bash macos_security_snapshot.sh [outfile]
set -u
OUT="${1:-/tmp/macos_security_snapshot.txt}"
exec > >(tee "$OUT") 2>&1

echo "===== SYSTEM / BASELINE ====="
sw_vers; uname -a; uptime; whoami; id
csrutil status 2>&1 | head -1
spctl --status 2>&1
fdesetup status 2>&1
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>&1
/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode 2>&1

echo; echo "===== PATCH STATUS ====="
softwareupdate --list 2>&1 | head -20
command -v brew >/dev/null && brew outdated --verbose 2>/dev/null | head -45

echo; echo "===== PERSISTENCE ====="
ls -la ~/Library/LaunchAgents 2>/dev/null
ls -la /Library/LaunchAgents 2>/dev/null
ls -la /Library/LaunchDaemons 2>/dev/null
ls -la /Library/StartupItems 2>/dev/null
ls /usr/lib/cron/tabs 2>/dev/null; cat /etc/crontab 2>/dev/null
osascript -e 'tell application "System Events" to get the name of every login item' 2>/dev/null
echo "--- launchctl non-apple ---"
launchctl list 2>/dev/null | grep -v com.apple | head -30
echo "--- ssh keys ---"
ls -la ~/.ssh 2>/dev/null; cat ~/.ssh/authorized_keys 2>/dev/null
echo "--- /etc/hosts ---"
cat /etc/hosts
echo "--- launchd plists (Label/ProgramArguments) ---"
for f in ~/Library/LaunchAgents/*.plist /Library/LaunchAgents/*.plist /Library/LaunchDaemons/*.plist; do
  [ -f "$f" ] || continue
  echo "[$f]"
  /usr/libexec/PlistBuddy -c "Print :Label" "$f" 2>/dev/null
  /usr/libexec/PlistBuddy -c "Print :ProgramArguments" "$f" 2>/dev/null | tr '\n' ' ' | head -c 200; echo
done

echo; echo "===== PROCESSES / NETWORK ====="
ps aux -r | head -14
ps aux | grep -iE "miner|xmrig|kdevtmpfsi|kinsing|masscan|sliver|cobalt|meterpreter|netcat|socat|nc -" | grep -v grep || true
find /tmp /var/tmp -maxdepth 3 -type f -perm -111 2>/dev/null | head
echo "--- listening ---"
lsof -i -P -n 2>/dev/null | grep -i LISTEN | head -30
echo "--- remote login ports ---"
lsof -i -P -n 2>/dev/null | grep -E ":(22|5900|3283|548)\s" || echo "(none listening)"
echo "--- proxy ---"
scutil --proxy 2>/dev/null | head -15
echo "--- dns ---"
scutil --dns 2>/dev/null | grep "nameserver\[" | sort -u | head

echo; echo "===== APP INTEGRITY ====="
for a in /Applications/*.app; do
  echo "--- $(basename "$a")"
  codesign -dvv "$a" 2>&1 | grep -E "Authority=|flags=" | head -5
done
echo "--- quarantine xattrs ---"
for a in /Applications/*.app; do q=$(xattr -p com.apple.quarantine "$a" 2>/dev/null); [ -n "$q" ] && echo "$(basename "$a"): $q"; done

echo; echo "===== MACOS VECTORS ====="
ls -la ~/Library/Input\ Methods /Library/Input\ Methods 2>/dev/null
ls ~/Library/Internet\ Plug-Ins /Library/Internet\ Plug-Ins 2>/dev/null
ls ~/Library/Extensions /Library/Extensions 2>/dev/null
kextstat 2>/dev/null | grep -v com.apple | head -5 || echo "(no third-party kexts loaded)"
ls /Library/Audio/Plug-Ins/HAL /Library/QuickLook ~/Library/QuickLook 2>/dev/null
ls -la /Library/PrivilegedHelperTools 2>/dev/null
ls ~/Library/Application\ Support/Google/Chrome/Default/Extensions 2>/dev/null
ls ~/Library/Application\ Support/BraveSoftware/Brave-Browser/Default/Extensions 2>/dev/null
ls ~/Library/Safari/Extensions 2>/dev/null
echo "--- remote access tools ---"
ls /Applications ~/Applications 2>/dev/null | grep -iE "teamviewer|anydesk|parsec|rustdesk|splashtop|todesk" || echo "(none)"

echo; echo "===== USERS / LOGINS / HARDENING ====="
dscl . -list /Users 2>/dev/null | grep -viE "^_|root|<user>|nobody|daemon|Guest"
last -15 2>/dev/null | head -18
defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser 2>/dev/null || echo "(no autologin)"
defaults read com.apple.screensaver askForPassword 2>/dev/null || echo "(screensaver lock not set)"

echo; echo "===== DONE — snapshot at $OUT ====="
