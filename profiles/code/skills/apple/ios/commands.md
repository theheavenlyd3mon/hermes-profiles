# Command Toolkit

Everything here runs on macOS with Xcode's command-line tools. Destructive entries are marked; those are never emitted inside a copy-paste block with read-only commands.

**Contents:** [Simulator](#simulator) · [Physical Devices](#physical-devices) · [Logs and Diagnostics](#logs-and-diagnostics) · [Symbolication](#symbolication) · [Inspecting a Build](#inspecting-a-build) · [Build and Release](#build-and-release) · [Debugger Tricks](#debugger-tricks) · [Write It Down](#write-it-down)

## Simulator

```bash
xcrun simctl list devices available                      # what exists, and which are booted
xcrun simctl boot "iPhone SE (3rd generation)"
xcrun simctl install booted /path/to/App.app
xcrun simctl launch --console booted com.acme.app         # stdout in the terminal
xcrun simctl launch booted com.acme.app -ARGUMENT value   # launch arguments and -Key value defaults
xcrun simctl openurl booted "acme://order/8891"           # deep-link and URL-scheme testing
xcrun simctl push booted com.acme.app payload.apns        # simulated push; not APNs
xcrun simctl privacy booted reset all com.acme.app        # re-arm every permission prompt
xcrun simctl privacy booted grant photos com.acme.app     # also: revoke, and per-service names
xcrun simctl status_bar booted override --time "9:41" --batteryLevel 100 --cellularBars 4
xcrun simctl ui booted appearance dark
xcrun simctl io booted screenshot shot.png
xcrun simctl io booted recordVideo demo.mov               # ctrl-C to stop
xcrun simctl get_app_container booted com.acme.app data   # the container path, to inspect files
```

`payload.apns` is a JSON file whose top level includes `"Simulator Target Bundle": "com.acme.app"` alongside the `aps` dictionary. It exercises your handling code and nothing about APNs (`notifications.md`).

**Destructive**: `xcrun simctl erase <device|all>` wipes simulator data irreversibly — confirm before running.

## Physical Devices

```bash
xcrun devicectl list devices                                        # paired devices and their identifiers
xcrun devicectl device info details --device <id>                   # model, OS build, storage
xcrun devicectl device install app --device <id> /path/to/App.app
xcrun devicectl device process launch --device <id> com.acme.app
xcrun devicectl device process list --device <id>
```

Wireless debugging is enabled per device in Xcode's Devices and Simulators window; once paired, everything above works without a cable. Device slots, profiles and the 100-per-year limit are in `devices.md`.

## Logs and Diagnostics

```bash
# Live device log, filtered to one process — the only way to see OS-side messages your reporter misses
log stream --device --predicate 'process == "Acme"' --level debug

# The association subsystem, for universal-link debugging
log stream --device --predicate 'subsystem == "com.apple.swcd"'

# Collect a bounded window into a .logarchive for offline reading
log collect --device --start "2026-07-26 09:00:00" --output acme.logarchive
log show acme.logarchive --predicate 'process == "Acme"' --last 30m
```

- A `sysdiagnose` from the device (hold both volume buttons and the side button briefly, then share from Settings → Privacy & Security → Analytics & Improvements) carries crash reports, jetsam events and system state — the right ask when the affected person is not a developer.
- On-device crash logs live in Settings → Privacy & Security → Analytics & Improvements → Analytics Data, sorted by app name and date.

## Symbolication

```bash
dwarfdump --uuid Acme.app.dSYM                 # must match the report's Binary Images UUID
dwarfdump --uuid Acme.app/Acme
atos -o Acme.app.dSYM/Contents/Resources/DWARF/Acme -arch arm64 -l 0x1024b8000 0x1024c91a4
```

A dSYM whose UUID does not match produces plausible, wrong frames — check first, always (`crashes.md`).

## Inspecting a Build

```bash
codesign -d --entitlements :- Acme.app                     # what the binary is ACTUALLY entitled to
codesign -dvvv Acme.app                                    # signing identity, team, timestamp
security cms -D -i embedded.mobileprovision                # the profile as plain XML
plutil -p Acme.app/Info.plist                              # readable Info.plist
plutil -p Acme.app/PrivacyInfo.xcprivacy                   # the privacy manifest that shipped
lipo -info Acme.app/Acme                                   # architectures present
```

The binary is the only honest source for entitlements and Info.plist keys. Project settings, `.entitlements` files and profiles all lie in different ways (`capabilities.md`).

## Build and Release

```bash
xcodebuild -showsdks
xcodebuild -showdestinations -scheme Acme
xcodebuild -scheme Acme -destination 'platform=iOS Simulator,name=iPhone SE (3rd generation)' test
xcodebuild -scheme Acme -configuration Release -archivePath build/Acme.xcarchive archive
xcodebuild -exportArchive -archivePath build/Acme.xcarchive \
  -exportOptionsPlist ExportOptions.plist -exportPath build/
xcrun altool --validate-app -f build/Acme.ipa -t ios --apiKey <key-id> --apiIssuer <issuer-id>
```

Validate before uploading: it catches most automated-gate failures in seconds instead of after processing (`releases.md`). The API key id and issuer id are identifiers; the `.p8` behind them is a secret and is referenced by pointer only (`memory-template.md`). Which of these commands is canonical depends on `release_tooling`.

## Debugger Tricks

```
(lldb) po myObject                    # description; `p` prints the raw value
(lldb) v myVar                        # variable inspection without running code — safer in a frozen app
(lldb) bt all                         # every thread, when the main thread is stuck
(lldb) expression -l objc -- (void)[[BGTaskScheduler sharedScheduler] \
         _simulateLaunchForTaskWithIdentifier:@"com.acme.app.refresh"]
```

The last one is the only reliable way to run a `BGTask` handler on demand: pause the debugger, run it, resume. It proves the handler works and nothing about whether the system will ever schedule it (`background.md`).

Useful launch arguments, set in the scheme or passed via `simctl launch`: the Core Data SQL debug argument to print every query, the Core Data concurrency debug argument to trap threading violations, and the localization options for showing non-localized strings and forcing a right-to-left pseudolanguage (`localization.md`).

Main Thread Checker, Address Sanitizer, Thread Sanitizer and zombies are scheme diagnostics, not command-line flags — which one to enable for which symptom is in `crashes.md`.

## Write It Down

- **An identifier or entitlement discovered by inspecting a build** — the real `aps-environment`, an App Group that is not what the project claimed, a team id — updates that app's row in `## Apps` in `~/Clawic/data/ios/memory.md` (`memory-template.md`). Finding it twice is pure waste.
- **A command sequence that took real work to assemble** — an export options plist, a device log predicate that isolates the bug, a repeatable repro script — is `artifacts/<kebab-name>.md`, with its `## Boxes` line in the same turn.
