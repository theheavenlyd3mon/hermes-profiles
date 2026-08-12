# App Lifecycle — Launch, Scenes, and What Runs Before the First Frame

**Before changing anything at startup**, read `## Apps` and `## Platform Facts` in `~/Clawic/data/ios/memory.md`, and open `artifacts/launch-teardown-*.md` if the `## Boxes` index names one — the previous measurement is the only way to know whether a change helped.

**Contents:** [The Six Ways an App Starts](#the-six-ways-an-app-starts) · [What Happens Before main()](#what-happens-before-main) · [Scene Phases](#scene-phases) · [Backgrounding Is Not Termination](#backgrounding-is-not-termination) · [State Restoration](#state-restoration) · [First Run and Upgrades](#first-run-and-upgrades) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## The Six Ways an App Starts

`didFinishLaunching` runs for all of them, and only one has a user looking at the screen. Anything expensive there is paid six times over.

| Start | What triggered it | What is different |
|---|---|---|
| Cold, user tap | Process does not exist | The only one where the 400 ms budget is visible to a human |
| Warm / resume | Process suspended, memory intact | No launch sequence at all — `scenePhase` goes background → active |
| Prewarm | The system predicted a launch (iOS 15+) | `didFinishLaunching` may run minutes before the user taps, with no UI. Never treat launch as user intent, and never start a session timer there |
| Background launch | Silent push, `BGTask`, background URLSession completion, location event, Bluetooth | No window, no scene in foreground. UI work here is wasted or crashes |
| Launch into a destination | Notification tap, universal link, widget URL, quick action, Shortcut | The destination arrives *after* launch, in a delegate callback or `onOpenURL` — the app must be able to jump from the root, not from a half-built stack |
| Relaunch after termination | Killed by jetsam, watchdog, crash, or the user | Indistinguishable at launch. If it matters, record the reason on the way down, not on the way up |

Rule of thumb: `didFinishLaunching` should register things (delegates, task identifiers, notification categories) and start nothing. Every network call, database migration, SDK initializer and analytics flush moves behind the first frame or behind the feature that needs it.

## What Happens Before main()

Pre-main time is dyld: loading and linking dynamic libraries, rebasing and binding pointers, ObjC runtime setup (`+load`, category registration), then C++ static initializers. It happens before a single line of your code runs, and it scales with the number of dynamic frameworks.

- The dominant lever is **framework count**, not app size: each embedded dynamic framework adds load, link and sign-verification work. Merging small frameworks into a static library or using mergeable libraries is the fix; deleting an unused SDK is the same fix and is free.
- `+load` and static initializers run for every linked SDK before you can intervene. An SDK that "starts automatically" is doing it here, and its cost is invisible in a Time Profiler trace started at `main`.
- Measure with the environment variable `DYLD_PRINT_STATISTICS` on a physical device, or the App Launch template in Instruments. The simulator's numbers are meaningless — no code signing, different linker path, host CPU.
- Budget: first frame under 400 ms (Apple's stated target); the watchdog kills around 20 s (`0x8badf00d`). Between those two lies every real app — measure on the oldest supported device (`performance.md`).

## Scene Phases

`active` → `inactive` → `background`, and back. In SwiftUI, `@Environment(\.scenePhase)`; in UIKit, the scene delegate callbacks.

- **`inactive` is not backgrounding.** It fires for the app switcher, Control Center, an incoming call, and a system alert. Pausing a game belongs here; saving state does not.
- **The app switcher snapshot is taken as you leave.** Sensitive content must be hidden at `willResignActive`/`inactive` — doing it at `didEnterBackground` is one frame too late and the snapshot already has it.
- **After `didEnterBackground` returns you have roughly five seconds** before suspension. Work that needs longer takes a background task assertion with an expiration handler (`background.md`).
- iPad and Stage Manager mean **multiple scenes of one app**: singletons that assume one window produce two windows fighting over one state object. Scene-scoped state, or explicit coordination.
- With `ui_framework: swiftui`, push registration and other UIKit-only delegate callbacks still need `@UIApplicationDelegateAdaptor` — the SwiftUI `App` protocol has no equivalent for them.

## Backgrounding Is Not Termination

- `applicationWillTerminate` **does not fire** when the system kills a suspended app — which is how most apps die. Save on `didEnterBackground`, treat terminate as an optimization you never rely on.
- Suspended apps keep memory but run no code, including timers. A timer scheduled for 30 minutes from now fires when the app is next resumed, if it fires at all.
- Files and Core Data handles held across suspension in a shared App Group container produce `0xdead10cc`. Close or relinquish them on the way down (`capabilities.md`).
- Jetsam kills the largest memory offender under pressure with no callback. `didReceiveMemoryWarning` fires earlier, and is the only chance to drop caches — image caches first (`performance.md`).

## State Restoration

- The unit of restoration is `NSUserActivity`: build one when the user reaches a meaningful screen, hand it back on relaunch. It also powers Handoff, Spotlight and Siri suggestions from the same object.
- SwiftUI `@SceneStorage` restores per-scene UI state; `@AppStorage` is UserDefaults with a different name and is not restoration — it persists across everything, including a state the user wanted to leave.
- Restore *position*, never in-flight work. Restoring a half-completed upload or a stale search result is worse than starting clean.
- Test it the way the system does it: background the app, kill it from Xcode (not from the app switcher — a user-initiated kill deliberately clears restoration), relaunch.

## First Run and Upgrades

- Detect an upgrade by comparing a stored version string in UserDefaults against the current bundle version. There is no system callback for "first launch after update".
- Migration on first launch must be **resumable and bounded**: it runs inside the launch budget, sometimes on a prewarm, sometimes on a device at 1% battery. A migration that must not be interrupted needs a progress screen and a completion flag, not optimism.
- The App Store serves the last compatible build to devices below the deployment target, so a user can jump three versions in one update. Migration paths must chain, and the chain must be tested from the oldest version still in the wild (`releases.md`).
- Keychain items survive deletion and reinstall, so "first run" and "new user" are different questions (`data.md`).

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| Analytics reports launches nobody made | Prewarming counted as a session | Start sessions from the first `active` scene phase, not from `didFinishLaunching` |
| Notification tap opens the app at the root | The destination arrived before the UI was ready and was dropped | Buffer the pending destination and consume it once the root scene is active |
| App killed a few seconds after backgrounding | Work continued past the ~5 s window with no task assertion | Take the assertion, or move the work to a `BGTask` (`background.md`) |
| Two windows disagree on iPad | Scene-shared singleton | Scope the state to the scene |
| Crash only on relaunch after a long absence | Restoration handing back a state the current build cannot build | Version the restoration payload and discard unknown versions |
| Slow launch that Instruments cannot see | Time is pre-main | `DYLD_PRINT_STATISTICS`, then count dynamic frameworks |

## Write It Down

- **A verified launch path** — that a widget URL lands here, that prewarm runs this SDK, that the app can be launched into the background by this event — is a `## Platform Facts` line in `~/Clawic/data/ios/memory.md`. It is the fact the next session would otherwise re-derive with a stopwatch.
- **A launch measurement** (cold launch on a named device and OS) is a row in `## Baselines`, never a sentence in the chat: a launch time with no earlier number is not evidence of anything.
- **A teardown of where launch time goes** — pre-main, initializers, first frame, with what was cut — is `artifacts/launch-teardown-<app>.md`, with its `## Boxes` line in the same turn (`memory-template.md`).
