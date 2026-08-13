---
name: ios-local-build-run
description: Use when building or running an iOS app from the terminal.
version: 1.0.0
author: Senna
license: MIT
---

# iOS Local Build & Run

Build/run/verify an iOS app from the terminal — old-Xcode install, xcodegen+SPM
pitfalls, simctl run loop. Verified end-to-end 2026-08-05 (SLP app: xcodegen
project, SPM local package, iPad simulator).

## Xcode on Macs the App Store rejects

App Store only serves the LATEST Xcode (Apple-Silicon/Tahoe-only as of Xcode 26).
Older/Intel Macs install an older Xcode directly:

1. Compatibility matrix: https://xcodereleases.com/ — **Xcode 16.4 is the last
   Intel-compatible** (needs macOS 15.3+, Swift 6.1, iOS 18.5 SDK).
2. Direct xip (free Apple ID sign-in):
   `https://developer.apple.com/services-account/download?path=/Developer_Tools/Xcode_16.4/Xcode_16.4.xip`
3. Expand the .xip, `mv Xcode.app /Applications/`, then:
   ```bash
   osascript -e 'do shell script "xcode-select -s /Applications/Xcode.app/Contents/Developer && xcodebuild -license accept" with administrator privileges'
   xcodebuild -runFirstLaunch
   xcodebuild -downloadPlatform iOS   # simulator runtime, several GB, background it
   ```
   The osascript form pops a GUI password prompt — works from a non-interactive
   shell where bare `sudo` cannot.

## xcodegen + SPM: the module-flattening pitfall

Listing `Sources/*` as app-target `sources:` in project.yml compiles everything
into ONE target → `error: no such module 'ContentKit'` on every cross-module
import. Fix: keep modules as the local Swift package and link products:

```yaml
packages:
  SLPAppCore:
    path: .
targets:
  SLPApp:
    dependencies:
      - package: SLPAppCore
        product: ContentKit
```

Run `xcodegen` after editing project.yml, then rebuild.

## Swift 6 strict concurrency

UIKit haptic generators called from nonisolated static helpers fail with
"call to main actor-isolated initializer in a synchronous nonisolated context".
Fix is `@MainActor` on the helper — correct anyway since haptics are main-thread.

## simctl run loop (no Xcode GUI needed)

```bash
xcodebuild -scheme <S> -configuration Debug -destination 'platform=iOS Simulator,name=iPad (A16)' build
# simulator builds need NO signing team; device builds do
xcrun simctl boot "iPad (A16)"; open -a Simulator
xcrun simctl install booted <DerivedData path>/Debug-iphonesimulator/<App>.app
xcrun simctl launch booted <bundle.id>   # first launch can flake — just retry
xcrun simctl io booted screenshot /tmp/shot.png   # verify UI, feed to vision
```

Notes:
- `xcrun simctl list devices` shows exact available names/ids — don't guess
  marketing names ("iPad Pro (13-inch) (M4)" ≠ "iPad Pro 13-inch (M4)").
- `xcodebuild` must run from the project dir (or pass `-project`).
- A libxpc "assertion failed" log line on simulator launch is benign noise.

## No Developer Program? Native macOS target (zero cost, no expiry)

When the user balks at the $99 Apple Developer Program for a personal/internal
app, offer the ladder — and default to rung 1:

1. **macOS target** — free forever, no Apple ID, no expiry. If Package.swift
   already declares `.macOS(...)` and UIKit use is `#if canImport(UIKit)`-guarded
   (with AppKit fallbacks like `NSImage`), it's nearly free:

   ```yaml
   SLPAppMac:
     type: application
     platform: macOS
     deploymentTarget: "14.0"
     sources:
       - path: App/SLPApp
         excludes:
           - "Support/Info.plist"            # iOS-flavored keys
           - "Support/PrivacyInfo.xcprivacy" # iOS-only manifest
       - path: content
         type: folder
     dependencies: [same package products as the iOS target]
     settings:
       base:
         GENERATE_INFOPLIST_FILE: YES        # don't reuse the iOS plist
         CODE_SIGN_IDENTITY: "-"             # ad-hoc: runs locally, no Apple ID
   ```

   Then `xcodegen && xcodebuild -scheme <MacScheme> -destination 'platform=macOS'
   build` and copy the .app out of DerivedData to `~/Applications/` (DerivedData
   gets purged). Same codebase, same bundle resources.

2. **Free Apple ID → device** — works, but apps expire every 7 days and need a
   re-deploy from Xcode. Fine for a trial, annoying as a weekly ritual.
3. **$99 program** — what it actually buys is TestFlight's 1-year installs, i.e.
   not the App Store, just freedom from the re-signing treadmill. Recommend only
   after the user has tried the free path and felt the pain.

There is no "zip the app to an iPad" path — iOS has no file-based sideloading;
SideStore/AltStore are just the same 7-day signing with extra moving parts.
