# Background Execution — Budgets, Not Promises

**Before debugging "it never runs"**, read `## Platform Facts` in `~/Clawic/data/ios/memory.md`: whether background refresh has ever been observed to fire for this app, and on which device, is the difference between a bug and a working system behaving correctly.

**Contents:** [The Five Ways Code Runs in the Background](#the-five-ways-code-runs-in-the-background) · [Task Assertions](#task-assertions) · [BGTaskScheduler](#bgtaskscheduler) · [Background URLSession](#background-urlsession) · [Silent Push](#silent-push) · [Location, Audio, and the Always-On Modes](#location-audio-and-the-always-on-modes) · [Why It Never Runs](#why-it-never-runs) · [Write It Down](#write-it-down)

## The Five Ways Code Runs in the Background

| Mechanism | Time you get | Triggered by | Use it for |
|---|---|---|---|
| Task assertion (`beginBackgroundTask`) | Seconds — ~30 s on current iOS, 180 s before iOS 13 | You, as the app leaves the foreground | Finishing something already in flight |
| `BGAppRefreshTask` | ~30 s, when the system chooses | The scheduler, no earlier than your requested date | Small content refresh |
| `BGProcessingTask` | Minutes, in practice while charging and idle | The scheduler, typically overnight | Migrations, cleanup, model training, batch upload |
| Background `URLSession` | Unlimited — the *system* transfers, not your process | Your request; the app is relaunched into the background when it completes | Any upload or download that must survive the app closing |
| Background modes (audio, location, VoIP, external accessory, BLE, `remote-notification`) | Continuous while the condition holds | The declared activity actually happening | Only the app's real, user-visible function |

Nothing here is a promise. Design so that "it never ran" is a correct outcome the user never notices: every background path must also be reachable in the foreground, and must be idempotent — the same refresh may run twice.

## Task Assertions

```swift
var id: UIBackgroundTaskIdentifier = .invalid
id = UIApplication.shared.beginBackgroundTask(withName: "flush-queue") {
    // Expiration handler: cancel work and END the task, or the app is killed.
    cancelFlush()
    UIApplication.shared.endBackgroundTask(id); id = .invalid
}
```

- The expiration handler is mandatory. Failing to call `endBackgroundTask` before the time runs out terminates the app, and the report looks like a random crash.
- Every `begin` needs exactly one `end`, on every path including errors. Leaked assertions burn the budget the next one needed.
- Assertions do not extend into a new launch. Work that genuinely needs more time is a background `URLSession` or a `BGProcessingTask`, not a longer assertion.

## BGTaskScheduler

Three edits, all required, and the order matters:

1. Add the `Background fetch` and/or `Background processing` background modes.
2. List every identifier in `BGTaskSchedulerPermittedIdentifiers` in Info.plist. An identifier not listed throws on registration.
3. **Register handlers before `didFinishLaunching` returns** — registration after that point raises an exception, and background launches give you no second chance.

```swift
BGTaskScheduler.shared.register(forTaskWithIdentifier: "com.acme.app.refresh", using: nil) { task in
    handle(task as! BGAppRefreshTask)   // must call task.setTaskCompleted(success:)
}
```

- Submit the request when leaving the foreground, not at launch: a request is consumed when it runs, and only one pending request exists per identifier.
- `earliestBeginDate` is a floor, never a schedule. The system weighs how often the user opens the app, battery, thermal state and network. An app the user opens once a month gets nothing, correctly.
- `task.expirationHandler` must cancel the work and call `setTaskCompleted(success: false)`. A task that is killed without completing lowers the app's future priority — the penalty compounds silently.
- Low Power Mode disables background refresh entirely, as does the per-app Settings toggle and the global Background App Refresh switch. Check all three before debugging code.
- Force a run in the debugger by pausing and issuing the private simulate-launch call for your identifier (`commands.md`) — the only reliable way to test the handler. It proves the handler works; it proves nothing about scheduling.

## Background URLSession

The only mechanism whose work continues after the app is gone. It is also the fussiest.

- One session per identifier, created once and kept — recreating a session with a live identifier throws.
- **Uploads must be from a file**, not `Data`. Download completion hands you a temp URL that is deleted when the delegate returns: move it synchronously.
- The app is relaunched into the background on completion; implement `application(_:handleEventsForBackgroundURLSession:completionHandler:)`, store the handler, and call it on the main thread after `urlSessionDidFinishEvents`. Skip it and the system stops relaunching you.
- `isDiscretionary` transfers wait for Wi-Fi and power; sessions created while the app is in the background are discretionary whether you asked or not. Time-sensitive transfers must start in the foreground.
- No interactive authentication: a challenge that needs UI fails. Pre-fetch tokens before the transfer starts.
- Redirects, `waitsForConnectivity` and cellular policy behave differently here than in a default session (`networking.md`).

## Silent Push

`content-available: 1` with no alert wakes the app to fetch. Three requirements and two throttles:

- Requires the `remote-notification` background mode **and** the user having notifications enabled — silent pushes to an app the user denied notifications for are dropped.
- APNs requires `apns-push-type: background` and `apns-priority: 5`. Sending priority 10 for a background push is rejected or throttled.
- The system rate-limits silent pushes per app, drops them in Low Power Mode, and prefers apps the user actually opens. Treat delivery as a hint, never as transport.
- Anything that must arrive is a visible notification or a fetch on next foreground. A silent push that carries the only copy of the data is a data-loss design.

## Location, Audio, and the Always-On Modes

- Continuous background location needs the background mode, `allowsBackgroundLocationUpdates = true`, **and** Always authorization. The blue indicator is not optional and is part of the deal.
- Significant-change location and region monitoring relaunch a terminated app; continuous updates do not survive termination. Region monitoring is capped at 20 regions per app — build a rolling window around the user, not a static list.
- Background audio must play audible audio. Silent audio to stay alive is a 2.5.4 rejection and, separately, drains the battery in a way users report.
- VoIP is PushKit only, and every PushKit push **must** report a call to CallKit — failing to do so revokes the entitlement's behavior and terminates the app with `0xbad22222`.
- `EXC_RESOURCE (WAKEUPS)` means timers or polling woke the process too often. Coalesce work; the OS is counting.

## Why It Never Runs

| Symptom | Cause | Check |
|---|---|---|
| `BGAppRefreshTask` never fires in testing | Testing on a device the user does not use, or from the simulator | Simulate the launch in the debugger, then verify on a real, used device over days |
| Registration throws at launch | Identifier missing from `BGTaskSchedulerPermittedIdentifiers`, or registered too late | Both fixes are in BGTaskScheduler above |
| Runs once, never again | Handler never called `setTaskCompleted`, or never resubmitted the next request | Resubmit inside the handler, first thing |
| Works on Wi-Fi, never on cellular | Discretionary transfer | Set `isDiscretionary = false` and start it in the foreground |
| Silent push works in dev, not in TestFlight | Sandbox vs production APNs environment | `notifications.md` |
| Upload dies when the app is swiped away | Default session, not a background session | Background `URLSession` — a user-killed app runs nothing else |
| App killed shortly after backgrounding | Assertion never ended, or work continued past the ~5 s window | Task Assertions above (`lifecycle.md`) |

## Write It Down

- **Observed scheduling behavior** — that refresh fires roughly nightly on this user's phone, that Low Power Mode kills it, that a `BGProcessingTask` only ever ran while charging — goes in `## Platform Facts` of `~/Clawic/data/ios/memory.md`, one line. Nobody can re-derive this in a session; it takes days of observation.
- **A background configuration that finally worked** — identifiers, modes, submission points, the completion-handler wiring — is `artifacts/background-config-<app>.md`, with its `## Boxes` line in the same turn (`memory-template.md`).
- **A termination traced to a background mechanism** (`0xdead10cc`, `EXC_RESOURCE`, an expired assertion) is a `## Pain Points` line; the second occurrence earns a runbook in `artifacts/`.
