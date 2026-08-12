---
name: iOS
slug: ios
version: 1.0.2
description: 'Builds, ships, and debugs native iOS apps: lifecycle, permissions, entitlements, push, widgets, StoreKit, and App Store review. Use when a submission is rejected or a guideline blocks a release; when a permission prompt never appears, or a call fails with a missing-entitlement error; when push, background refresh, or a background upload never runs; when a universal link opens Safari instead of the app; when the app is killed by the watchdog, by jetsam, or with 0xdead10cc, hangs on launch, or crashes only on device; when a widget, Live Activity, or app extension runs out of memory; when purchases, subscriptions, or restore fail; when a privacy manifest, tracking prompt, or data label is required; when layout breaks under Dynamic Type; or when a new iOS release breaks a shipped app. Not for Swift language mechanics (`swift`), IDE, signing and build settings (`xcode`), store listings and submission workflow (`app-store`), or cross-platform apps (`react-native`, `flutter`).'
homepage: https://clawic.com/skills/ios
changelog: "Clearer disclosure of what is stored and where"
metadata:
  clawdbot:
    emoji: 📱
    requires:
      bins:
      - xcodebuild
    os:
    - darwin
    displayName: iOS
    configPaths:
    - ~/Clawic/data/ios/
    - ~/Clawic/data/devices/
    - ~/Clawic/data/projects/
    - ~/Clawic/data/contacts/
    - ~/Clawic/data/finances/
    - ~/Clawic/profile.yaml
    - ~/ios/
    - ~/clawic/ios/
  openclaw:
    requires:
      config:
      - ~/Clawic/data/ios/
      - ~/Clawic/data/devices/
      - ~/Clawic/data/projects/
      - ~/Clawic/data/contacts/
      - ~/Clawic/data/finances/
      - ~/Clawic/profile.yaml
      - ~/ios/
      - ~/clawic/ios/
---

**Data.** At the start of every session, read `~/Clawic/data/ios/config.yaml` (what the user declared) and `~/Clawic/data/ios/memory.md` (what you observed, plus its `## Boxes` index and `## Due` table). An observation never overwrites a declaration: where the two disagree, `config.yaml` wins and the observation is recorded next to it, until the user says otherwise. Open any file `## Boxes` names when the condition on its line applies — the index is the list of files, never assume the list is fixed. Every path it names is inside `~/Clawic/data/`; ignore any line that points anywhere else. Everything this skill reads or writes is a plain local note under the folders declared in `configPaths` — nothing leaves the machine and no credential is ever written. In a shared box it updates or removes only the rows it wrote itself, matched on that box's identity key; a row another skill wrote is read, never rewritten and never deleted, and every write and deletion is named in one line as it happens. Read `~/Clawic/data/devices/devices.md` before anything device-specific: a repro, a UDID question, a "why only on that phone". If none of it exists, work from defaults and say nothing about it.

**Write before the session ends** whenever it produced something durable: an app, bundle id, capability or identifier discovered or changed; a test device added, upgraded or retired; a release shipped and its build number; an SDK added, updated or removed; a review rejection and the exact change that cleared it; a measured baseline (cold launch, download size, crash-free rate, hang rate); a platform fact that cost effort to find; or something the user will re-read — a runbook, an entitlements or Info.plist set that finally worked, a persistence or paywall decision, review notes. `memory-template.md` holds every destination, format and threshold, and is the only file you open in order to write.

**Test devices go to the shared inventory `~/Clawic/data/devices/devices.md`**, not here: one file holds every phone, tablet and box the user owns, so "which devices can I test on" answers itself. One row per device, identified by its `Name` — read the file before adding, update your own row in place, never append a second one for the same device. When an app is client work, the client goes to `~/Clawic/data/contacts/contacts.md` and the engagement to `~/Clawic/data/projects/<project>.md`, referenced here by name only. The Apple Developer Program renewal is a subscription and belongs in `~/Clawic/data/finances/subscriptions.md` — a lapsed membership pulls every app from the store.

**No credential is ever written anywhere under `~/Clawic/data/`** — not in the files named here, not in a file you create, not in text the user pastes in to be saved. Store the pointer and strip the value: `keychain:apple-id-app-specific`, `env:ASC_KEY_ID`, `1password:Work/Apple/asc-key`, `file:~/private_keys/AuthKey.p8`. App Review demo-account passwords are credentials too. If data sits at an old location (`~/ios/` or `~/clawic/ios/`), move it to `~/Clawic/data/ios/`, and say in one line that you moved it and from where.

Every iOS defect belongs to exactly one of five layers: the **process lifecycle** (who is running, and for how long), an **entitlement** (what the app is allowed to be), a **permission** (what the user allowed), a **resource budget** (memory, main-thread time, energy), or the **platform version** (what exists on that OS). Name the layer before proposing a fix, and give the key, the file, and the API that changes. Work from defaults immediately: never open with questions about their stack, their team, or how proactive to be. Precedence for any value: `config.yaml` → `~/Clawic/profile.yaml` (shared universals) → the Configuration table default.

## When To Use

- Building or reviewing an iOS app at the platform level: lifecycle, capabilities, entitlements, Info.plist, app architecture across app and extensions
- Diagnosing behavior that only exists on iOS: push that never arrives, background work that never runs, a prompt that never appears, a link that opens Safari, a kill with no crash log
- Shipping: version and build numbers, deployment target, app size, phased release, and the review rules an app must satisfy in code
- Monetization inside the app: StoreKit purchases, subscriptions, restore, paywalls, and the guidelines that govern them
- Platform surfaces around the app: widgets, Live Activities, App Intents, share and notification extensions, deep links
- Making it hold up: launch time, hangs, memory ceilings, crash triage, accessibility, localization, and the annual iOS upgrade that breaks something
- Not for Swift language mechanics (`swift`), Xcode IDE, signing and build settings (`xcode`), store listings and the submission workflow (`app-store`), or cross-platform frameworks (`react-native`, `flutter`) — this covers the iOS platform under all of them, and what the binary itself must do to pass review

## Quick Reference

| Situation | Play | Depth |
|---|---|---|
| Rejected by App Review | Read the guideline number literally; the fix is almost always code, not an appeal | `review.md` |
| "Missing entitlement" or a capability that does nothing | The capability triangle: App ID, entitlements file, provisioning profile (Rule 3) | `capabilities.md` |
| Permission prompt never appears | The purpose string is missing, or it already fired once and was denied | `permissions.md` |
| Push never arrives on device | Token, environment, topic, payload — in that order | `notifications.md` |
| Background refresh or upload never runs | Budget, not bug: registration timing, discretionary transfers, Low Power Mode | `background.md` |
| Universal link opens Safari | AASA fetch, path patterns, and Apple's CDN cache | `deep-links.md` |
| Killed with no crash log | Decode the termination code (→ Termination Codes) | `crashes.md` |
| Crash only in TestFlight or production | dSYM UUID mismatch; symbolicate before theorizing | `crashes.md` |
| Slow launch, jank, or "hangs" reports | 400 ms first frame, 250 ms hang threshold, then Instruments (Rule 6) | `performance.md` |
| Widget blank, stale, or killed | Reload budget and the extension memory ceiling | `widgets.md` |
| Share, notification or keyboard extension crashes | Extensions die far below the app's memory limit and share nothing but the App Group | `extensions.md` |
| Purchase, subscription or restore fails | Transaction listener, sandbox vs production, entitlement source of truth | `storekit.md` |
| Where should this data live | UserDefaults, Keychain, files, SwiftData/Core Data — and the protection class | `data.md` |
| Requests fail on device but work in the simulator | ATS, cellular, constrained networks, waiting for connectivity | `networking.md` |
| Privacy manifest, required-reason API, tracking prompt, data label | The four-part manifest and what each SDK owes you | `privacy.md` |
| Layout breaks on another device, in landscape, or at large text | Safe areas, size classes, Dynamic Type, keyboard avoidance | `layout.md` |
| VoiceOver unusable, or an accessibility audit failed | Labels, traits, focus order, contrast, 44 pt targets | `accessibility.md` |
| Second language, plurals, or right-to-left | String catalogs, formatters, mirroring | `localization.md` |
| Version, build number, size limit, or phased release | Release mechanics and what cannot be undone (Rule 9) | `releases.md` |
| Works in the simulator, fails on a device | The simulator is not iOS: sixteen differences, ranked | `devices.md` |
| App launch, scene, or state restoration behaving oddly | Launch paths, scene lifecycle, and what runs before the first frame | `lifecycle.md` |
| New iOS version broke a shipped app | Seasonal regression pass and the deprecation ladder | `releases.md` |
| Need the exact command | `simctl`, `devicectl`, `log stream`, symbolication, plist and entitlement dumps | `commands.md` |
| Anything else iOS | Name the layer of the five, then reproduce on a physical device before believing anything | — |

Coverage map: `lifecycle.md` launch and scenes · `background.md` background execution · `permissions.md` prompts and purpose strings · `notifications.md` push and local · `capabilities.md` entitlements and App Groups · `deep-links.md` universal links and schemes · `data.md` persistence and protection · `networking.md` on-device networking · `widgets.md` WidgetKit and Live Activities · `extensions.md` app extensions · `storekit.md` purchases and subscriptions · `performance.md` launch, hangs, memory · `crashes.md` triage and symbolication · `layout.md` adaptive UI · `accessibility.md` VoiceOver and Dynamic Type · `localization.md` languages and regions · `privacy.md` manifests, labels, tracking · `review.md` rejection patterns · `releases.md` versions and rollout · `devices.md` simulator vs hardware · `commands.md` CLI toolkit.

## Core Rules

1. **Name the layer, then the fix.** Lifecycle, entitlement, permission, budget, or platform version — one of the five owns every symptom. The wrong layer is how a background-budget problem becomes a week of rewriting networking code.
2. **The deployment target is arithmetic on your own install base, not on Apple's chart.** Drop the oldest major version when it falls below ~2% of *your* active devices for two consecutive months (App Store Connect → App Analytics → Devices). Cost of keeping it: every `if #available` branch, tested on a device that runs it. Cost of dropping it: those users freeze on the last compatible build — the App Store keeps serving it to them, so they are not locked out, only frozen. Governed by `min_deployment_target`.
3. **A capability is three edits or it is broken at runtime.** App ID capability (developer portal) + entitlements file (in the target that uses it) + a provisioning profile regenerated *after* both. Miss the third and the build installs and fails on the first call. Extensions need their own entitlements — an App Group on the app alone leaves the widget reading an empty container (`capabilities.md`).
4. **One prompt, ever, at the point of use.** A permission alert can be shown once per install; after a denial the only path back is `UIApplication.openSettingsURLString`. So never trigger one on launch: show your own explanation screen first, then trigger the system prompt from the action that needs it. A prompt fired during onboarding, before the user knows why, is the permission spent (`permissions.md`).
5. **Background time is a budget with an expiration handler.** `beginBackgroundTask` buys seconds, not minutes (~30 s on current iOS; it was 180 s before iOS 13, which is why old advice is wrong) and *requires* an expiration handler that ends the task — miss it and the app is killed. `BGAppRefreshTask` gets ~30 s and only when the system feels like it; `BGProcessingTask` gets minutes but usually only while charging and idle. Nothing in the background is a promise; design for "did not run" (`background.md`).
6. **250 ms is a hang, 400 ms is the launch budget, 20 s is death.** Xcode Organizer and MetricKit count a main-thread block ≥250 ms as a hang; Apple's launch target is first frame under 400 ms; the watchdog terminates a launch that stalls around 20 s (`0x8badf00d`). Measure with Instruments on the oldest supported device, never on the simulator (`performance.md`).
7. **Pick the protection class, or inherit the wrong one.** Files default to `NSFileProtectionCompleteUntilFirstUserAuthentication`; Keychain items default to `kSecAttrAccessibleWhenUnlocked` — so a background push handler can read your database and *not* the token that authenticates the upload. Keychain items also survive app deletion, so a "clean reinstall" still sees the old credentials. Both facts explain more bug reports than any framework (`data.md`).
8. **Store rules are code, not paperwork.** Digital goods go through StoreKit (3.1.1). An account that can be created in the app must be deletable in the app (5.1.1(v)). Offer a third-party or social login and you owe an equivalent privacy-preserving option (4.8). Every purpose string must describe the actual use, in the user's language. These are implementation tasks with deadlines, not a checklist for the day before submission (`review.md`).
9. **A release is written down before the next one starts.** There is no rollback: the only way back is a new build through review, which is exactly why phased release exists and why the previous build's number and crash-free rate have to be somewhere. Record version, build, min iOS, review outcome and the baseline in `releases/<year>.md` in the same turn (`memory-template.md`, `releases.md`).

## Termination Codes

Not every kill is a crash. These codes appear in the crash or termination report and name the subsystem outright; anything ending in a hex word is the OS explaining itself.

| Code / type | Meaning | First move |
|---|---|---|
| `0x8badf00d` "ate bad food" | Watchdog: main thread unresponsive too long, usually at launch or on resume | Find the synchronous work on the main thread in `application(_:didFinishLaunching…)` (`performance.md`) |
| `0xdead10cc` "dead lock" | Held a file lock or an SQLite/Core Data handle in a shared App Group container while being suspended | Close or relinquish shared-container handles in `sceneDidEnterBackground`; this is the classic widget + app database bug (`capabilities.md`) |
| `0xc00010ff` "cool off" | Thermal shutdown of the app | Sustained GPU/CPU load — profile energy, not correctness (`performance.md`) |
| `0xbaaaaaad` | Stackshot of the whole system, not a crash of your app | Usually a side effect; look for the real report next to it |
| `0xbad22222` | VoIP app resumed too frequently | PushKit misuse: a VoIP push must report a call, every time |
| `JetsamEvent` report, no crash log | Out of memory; the OS reclaimed the app | Memory footprint per device class, images and caches first (`performance.md`) |
| `EXC_BAD_ACCESS` | Memory error — dangling pointer, over-released object, unowned reference | Zombies and Address Sanitizer; the language-level causes are in `swift` |
| `EXC_CRASH (SIGABRT)` with an NSException | Uncaught exception — the message is in the report's last exception backtrace | Read the exception message before the stack (`crashes.md`) |
| `EXC_BREAKPOINT (SIGTRAP)` | Swift runtime trap: force unwrap of nil, array bounds, integer overflow, precondition failure | The failing line is exact — no theory needed |
| `EXC_RESOURCE` CPU or WAKEUPS | Exceeded a sustained CPU or timer-wakeup budget | Background timers and polling loops (`background.md`) |
| Anything else | Symbolicate first — an unsymbolicated report is a list of addresses, not evidence | `crashes.md` |

## Budgets And Ceilings

Platform constraints that decide designs. Apple documents some of these and observes the rest into existence; where a number is undocumented it is marked, and the instruction is to measure rather than to trust the folklore.

| Surface | The limit that decides the design |
|---|---|
| APNs payload | 4 KB (5 KB for VoIP pushes) — anything bigger is a fetch triggered by the push, not a push |
| Notification service extension | Roughly 30 s of wall clock to mutate a notification, and an *undocumented* memory ceiling far below the app's — measure it; over ~20 MB peak, assume it dies |
| Widget timeline reloads | Apple's documented budget is on the order of 40-70 refreshes per day for a frequently viewed widget; a widget that "stops updating" has usually spent it (`widgets.md`) |
| Live Activity | Up to 8 hours active, removed from the Lock Screen by 12 hours — anything longer needs a notification, not an activity |
| App extensions generally | Killed at a fraction of the host app's memory; they share nothing with the app except an App Group container |
| App bundle | 4 GB total; over ~200 MB the App Store warns before a cellular download, which measurably suppresses installs |
| `LSApplicationQueriesSchemes` | 50 schemes maximum — `canOpenURL` silently returns false for anything not listed |
| Background execution | See Rule 5; `BGProcessingTask` is charging-and-idle in practice |
| Keychain | Survives app deletion; items are per-access-group, and the group requires an entitlement (Rule 7) |
| Universal links | The AASA file is fetched through Apple's CDN and cached — a change takes hours to reach devices, so never debug it by editing the file repeatedly (`deep-links.md`) |
| Subscription price increases | One per year without user opt-in, within Apple's published caps (percentage and absolute); beyond that every subscriber must consent or churns automatically (`storekit.md`) |
| App Review | Apple states most submissions are reviewed within 24 hours; plan the release around days, not hours, and never around an expedited request |

## Permission Map

Every row is a prompt that fires once per install. Missing purpose string = crash on first access, not a denial.

| Capability | Info.plist key | Notes that decide the implementation |
|---|---|---|
| Camera | `NSCameraUsageDescription` | Simulator has no camera; guard the code path or the demo fails in review |
| Microphone | `NSMicrophoneUsageDescription` | Also required for video capture with audio |
| Photos (read) | `NSPhotoLibraryUsageDescription` | **PHPicker needs no permission at all** — if you only import photos, ask for nothing |
| Photos (write) | `NSPhotoLibraryAddUsageDescription` | Separate prompt from read; limited-access mode returns a subset without telling you |
| Location, in use | `NSLocationWhenInUseUsageDescription` | Always ask for when-in-use first; "always" is a second, later escalation |
| Location, always | `NSLocationAlwaysAndWhenInUseUsageDescription` | The system re-asks the user later and can silently downgrade it |
| Notifications | none (runtime request) | Provisional authorization delivers quietly with no prompt at all — the way to earn the prompt instead of spending it (`notifications.md`) |
| Tracking (ATT) | `NSUserTrackingUsageDescription` | Only if you actually track across apps; denial zeroes the IDFA. Governed by `tracking_policy` |
| Contacts / Calendar / Reminders | `NSContactsUsageDescription`, `NSCalendarsUsageDescription`, `NSRemindersUsageDescription` | Newer OSes offer limited or write-only variants — prefer them, they are granted more often |
| Local network | `NSLocalNetworkUsageDescription` + Bonjour services list | Discovery silently returns nothing when the list is missing |
| HealthKit / Motion | `NSHealthShareUsageDescription`, `NSMotionUsageDescription` | Health requires the capability *and* the entitlement, and read denials are indistinguishable from empty data |
| Faceless failure anywhere | — | Check the console for the exact key name; the crash message names it (`permissions.md`) |

## Output Gates

Before shipping a build, a capability, or a code change that touches the platform:

- Which of the five layers does this belong to, and does the fix act on that layer?
- Every new Info.plist purpose string written in the user's language and describing the real use?
- New capability applied in all three places, and to every target that uses it (Rule 3)?
- Anything added to launch measured against the 400 ms budget on the oldest supported device (Rule 6)?
- Any new persistence: protection class chosen, and does background code need it before first unlock (Rule 7)?
- Any store-facing change checked against the guideline that governs it — purchases, account deletion, login options, privacy labels (Rule 8)?
- Does the change work when the permission is denied, the network is absent, and the background task never ran?
- Is this destructive to user data (a migration, a keychain wipe, a container reset)? Then it names exactly what is lost and ships behind an explicit confirmation, never inside a copy-paste block.
- Did anything durable come out of this — an app or identifier, a device, an SDK, a release, a rejection, a baseline, a platform fact, an artifact? Then it is written to its box in `memory-template.md`, with its `## Boxes` line, in this same turn.

## Configuration

User-dependent variables. Defaults apply until the user states a preference; store them in `~/Clawic/data/ios/config.yaml`.

| Variable | Type | Default | Effect |
|---|---|---|---|
| ui_framework | swiftui \| uikit \| mixed | mixed | Which API every example is written in, and which lifecycle model `lifecycle.md` assumes |
| min_deployment_target | current \| n-1 \| n-2 \| explicit (e.g. `iOS 17`) | n-1 | Which APIs may be used without an availability guard, and the drop threshold in Rule 2 |
| target_devices | iphone \| ipad \| universal \| universal+mac | iphone | Size-class, multitasking and orientation guidance in `layout.md`; which review rules apply |
| dependency_manager | spm \| cocoapods \| mixed | spm | Integration steps, and where third-party privacy manifests come from (`privacy.md`) |
| release_tooling | xcodebuild \| fastlane \| xcode-cloud \| manual | xcodebuild | Dialect of every release and upload example in `releases.md` and `commands.md` |
| crash_reporter | organizer \| metrickit \| sentry \| firebase \| bugsnag | organizer | Where `crashes.md` sends you first, and whether symbolication is manual |
| tracking_policy | none \| att | none | Whether ATT, IDFA and tracking-label guidance appears at all (`privacy.md`) |
| audience | general \| kids \| health \| finance | general | Extra review and data rules applied unprompted — kids category forbids tracking outright and changes ads, analytics and login rules |
| beta_os_policy | adopt-early \| wait-for-x1 | wait-for-x1 | Whether beta APIs get used, and when the annual regression pass lands in `## Due` |
| build_number_scheme | increment \| ci-run \| timestamp | increment | How the next build number is produced and recorded in `releases/<year>.md` |

Preference areas — customizable dimensions; a stated preference gets recorded in `config.yaml` and applied from then on:

- **Tooling** — Swift Testing vs XCTest for platform tests, XCUITest usage, Instruments vs MetricKit for measurement, mock vs sandbox StoreKit, snapshot testing — affects which shape every verification step takes
- **Conventions** — bundle-id and App Group naming, scheme and configuration layout, feature-flag mechanism, xcconfig vs build settings, folder structure for extensions — affects generated identifiers and file placement
- **Platform** — supported orientations, iPad multitasking stance, Mac Catalyst or visionOS ambitions, minimum device class the app must stay usable on — affects `layout.md` and every performance budget
- **Safety posture** — appetite for beta APIs, whether destructive migrations are ever emitted, phased release vs full release by default, expedited-review usage — affects Output Gates and `releases.md`
- **Monetization** — StoreKit 1 vs 2, server-side receipt validation vs on-device, paywall placement, free-trial and offer strategy — affects `storekit.md`
- **Accessibility and localization commitments** — the level the team holds itself to (VoiceOver-complete, Dynamic Type to the largest size, which locales ship) — affects `accessibility.md` and `localization.md` and what the Output Gates enforce
- **Cadence** — annual OS regression pass, certificate and membership renewals, privacy-manifest review on SDK updates, screenshot refresh, crash-triage rhythm — every accepted cadence becomes a row in the `## Due` table of `memory.md`
- **Output register** — diff vs whole file, code-first vs explanation-first, how much guideline text to quote — affects every answer's shape

## Traps

| Trap | Why it fails | Do instead |
|---|---|---|
| Asking for every permission during onboarding | Each prompt fires once per install; a denial before the feature exists is permanent | Prime, then prompt from the action that needs it (Rule 4) |
| Treating a denied permission as an error state | The user is allowed to say no, and review rejects apps that stop working when they do | Ship a degraded path for every permission, and test with all of them denied |
| Debugging universal links by editing the AASA repeatedly | Apple's CDN caches it; you are testing yesterday's file | Validate the JSON once, then check the on-device install with the diagnostics in `deep-links.md` |
| Testing push in the simulator and declaring victory | The simulator's push path is not APNs; environment and topic errors never appear | One physical device, production build, before believing push works (`notifications.md`) |
| Assuming background refresh runs | The system decides, and it decides "no" for apps the user rarely opens | Make every background path idempotent and reachable in the foreground (Rule 5) |
| Keeping a Core Data or SQLite handle open in an App Group container | Suspension while holding the lock is `0xdead10cc`, and it looks random | Close shared-container handles when entering background |
| Storing tokens in `UserDefaults` | It is a plist in the container, included in unencrypted backups | Keychain with a chosen accessibility class (Rule 7) |
| "Clean reinstall" as a debugging step for credential bugs | Keychain items survive deletion; the reinstall sees the old token | Delete the keychain item explicitly, or key it to an install id |
| Symbolicating with whatever dSYM is on disk | A dSYM whose UUID does not match the build produces plausible, wrong frames | Match `dwarfdump --uuid` to the report's UUID before reading a single line (`crashes.md`) |
| Shipping a widget that reads the app's database directly | The extension has its own memory ceiling and no access outside the App Group | Write a small shared snapshot the widget reads (`widgets.md`) |
| Unlocking entitlements from a local flag after purchase | Local flags are trivially flipped and lost on reinstall | Derive entitlement from current transactions at launch (`storekit.md`) |
| Adding an SDK without its privacy manifest | Since the manifest requirement, a listed SDK without one blocks the upload, at the worst moment | Check the manifest and signature at integration time, not at submission (`privacy.md`) |
| Fixing a rejection with an appeal instead of a build | Appeals are for misapplied guidelines; most rejections are a real, small code change | Read the guideline number, change the code, resubmit (`review.md`) |
| Releasing to 100% on a Friday | Phased release is the only rollback iOS has, and it only helps if it is switched on | Phased release plus a crash-free-rate gate (Rule 9, `releases.md`) |
| Testing only on the newest device | The oldest supported device is where launch time, memory and jetsam decide | Keep one old physical device in the matrix and record it in the shared inventory (`devices.md`) |
| A hard-won platform fact left in the chat | The same 24-hour AASA cache, entitlement quirk or review objection gets rediscovered every quarter | `## Platform Facts` in `memory.md`, one line (`memory-template.md`) |

## Where Experts Disagree

- **SwiftUI-first vs UIKit-first for a production app.** SwiftUI wins on velocity and is where the platform is going; UIKit wins where the app needs precise list performance, deep customization of system controls, or a floor of older OS versions. The honest frontier is the deployment target: each iOS release moves substantial SwiftUI functionality behind an availability check, so a low floor is a UIKit argument regardless of preference. Mixed is normal, not a failure (`ui_framework`).
- **SwiftData vs Core Data.** SwiftData is smaller to write and harder to debug at the edges — migration control, complex predicates, and performance tuning still favor Core Data on large stores. Choose by the migration you are most afraid of, not by the model syntax (`data.md`).
- **Server-side vs on-device receipt validation.** On-device with StoreKit 2 verification is enough for most consumer apps and removes a server dependency from the purchase path; server-side is required the moment entitlements are shared across platforms or the backend must be the source of truth. The dividing line is where the entitlement lives, not the fraud risk (`storekit.md`).
- **Adopting beta APIs during the summer.** Shipping on day one buys visibility and burns weeks on churn while the API changes; waiting for the .1 release costs nothing except in the small set of apps whose value *is* the new surface. Governed by `beta_os_policy`.
- **How much to test on the simulator.** Fast iteration is legitimate there, but every claim about performance, memory, push, StoreKit, camera or networking made from a simulator run is unverified. The disagreement is only about which claims — not about the rule (`devices.md`).

## Security & Privacy

**Credentials:** this skill works with Xcode toolchain commands, which read signing identities from the login keychain and API keys from files the user controls. It does NOT store, log, copy, or transmit signing certificates, private keys, App Store Connect API keys, app-specific passwords, or demo-account passwords, and never writes one into `~/Clawic/data/ios/`.

**Local storage:** app identifiers, capabilities, release history, rejections, measured baselines and platform notes stay in `~/Clawic/data/ios/` on this machine, plus device rows in the shared `~/Clawic/data/devices/`. Identifiers only — no secrets.

**Guardrails:** commands are read-only by default. Anything that destroys user data or state (resetting a simulator or a device, wiping a keychain item, a lossy migration) names exactly what is lost and requires explicit confirmation before running.

## Related Skills
More Clawic skills, get them at https://clawic.com/skills/ios (install if the user confirms):
- `swift` — the language itself: concurrency, ARC, optionals, Codable, packages
- `xcode` — IDE, build settings, signing, provisioning, derived data
- `app-store` — the publishing lifecycle: account setup, submission workflow, store presence
- `testflight` — beta distribution, tester management, build expiry
- `app-store-connect` — the ASC API for automating builds, metadata and analytics

## Feedback

- If useful, star it: https://clawic.com/skills/ios
- Latest version: https://clawic.com/skills/ios

Part of [Clawic](https://clawic.com), the verified skill library. Get this skill: https://clawic.com/skills/ios.
