# Performance — Launch, Hangs, Memory, Energy

**Before optimizing anything**, read `## Baselines` in `~/Clawic/data/ios/memory.md`. An optimization with no prior measurement on the same device and OS is a story, not a result. Open `artifacts/launch-teardown-*.md` if `## Boxes` names one.

**Contents:** [The Four Budgets](#the-four-budgets) · [Launch](#launch) · [Hangs](#hangs) · [Memory](#memory) · [Scrolling](#scrolling) · [Energy](#energy) · [App Size](#app-size) · [Measuring Honestly](#measuring-honestly) · [Field Data](#field-data) · [Write It Down](#write-it-down)

## The Four Budgets

| Budget | Number | Where it comes from |
|---|---|---|
| Cold launch to first frame | **400 ms** target; the watchdog kills near **20 s** (`0x8badf00d`) | Apple's launch guidance and the watchdog |
| Main-thread block counted as a hang | **250 ms** | The threshold Xcode Organizer and MetricKit use |
| Frame budget | **16.7 ms** at 60 Hz, **8.3 ms** at 120 Hz ProMotion | Refresh rate arithmetic: 1000 ÷ Hz |
| Memory | Device-dependent jetsam limit; extensions far lower | `crashes.md` for JetsamEvent reports |

Every budget is measured on the **oldest supported device**, in a Release build, with the debugger detached. A number from the simulator or from a debug build on the newest phone is not evidence of anything.

## Launch

Three phases, and each has a different tool:

1. **Pre-main** — dyld loading, linking and rebasing every dynamic framework, then ObjC `+load` and C++ static initializers. Measured with `DYLD_PRINT_STATISTICS` or the App Launch instrument; invisible to a Time Profiler started at `main`. The lever is the *count* of dynamic frameworks and the SDKs that self-start (`lifecycle.md`).
2. **`didFinishLaunching` to first frame** — your code. Register, do not start: every SDK initializer, database open, network call and analytics flush that can wait, waits.
3. **First frame to usable** — the part users judge. A skeleton screen that appears in 300 ms and fills in beats a blank window that appears complete in 900 ms.

Concrete moves, in order of typical payoff: delete unused SDKs; merge or statically link small frameworks; defer third-party initialization behind the first screen that needs it; move the store open off the launch path when the first screen does not query it; replace an eager migration with a lazy one (`data.md`).

## Hangs

A hang is the main thread blocked ≥250 ms. The usual culprits, in order of frequency:

- Synchronous file or keychain access on the main thread. Keychain calls are surprisingly slow and are usually made during launch.
- JSON decoding, image decoding, or a large `Codable` round-trip on the main thread.
- A Core Data fetch on the view context with a predicate that cannot use an index, or a fetch that faults thousands of objects.
- Layout thrash: a synchronous layout pass inside a scroll callback, or a SwiftUI view whose body does real work.
- A semaphore or `DispatchQueue.sync` waiting on a queue that is itself waiting for the main thread. That is a deadlock, and the watchdog resolves it.
- A hidden `main.sync` inside a library callback — the reason to inspect third-party stack frames rather than assuming they are fine.

Find them with the Hangs instrument or Time Profiler filtered to the main thread; `os_signpost` around suspicious intervals turns a guess into an interval you can see. In SwiftUI, an expensive `body` is a hang with a different name — move work into the model and let the view read a prepared value (`swift` covers the language-level shape of that work).

## Memory

- **Decoded image size is `width × height × 4` bytes**, regardless of the file size on disk. A 4000 × 3000 photo is ~48 MB decoded from a 3 MB JPEG. Loading a handful of them is the most common jetsam kill in the platform.
- Downsample with ImageIO thumbnail creation at the size you will display, times the screen scale. Never `UIImage(contentsOfFile:)` a camera-resolution photo into a 120 pt thumbnail.
- `NSCache` evicts under memory pressure; a `Dictionary` does not. Any cache that is not an `NSCache` (or does not respond to memory warnings) is a leak with a schedule.
- `didReceiveMemoryWarning` is the last chance to drop caches before jetsam. Wire it, and drop image caches first.
- Jetsam limits scale with device RAM and are lower for extensions. A widget or notification-service extension has to live in a small fraction of the app's footprint (`extensions.md`).
- Leaks: retain cycles in closures and delegates are language-level (`swift`), but the platform-level version is a view controller or scene that never deallocates — check with the Memory Graph Debugger after popping a screen ten times, not once.
- Web views, video players and Core Data contexts each hold memory the allocations graph attributes elsewhere. Measure footprint (the number jetsam uses), not just allocations.

## Scrolling

- Reuse is the whole game. `UITableView`/`UICollectionView` recycle cells; SwiftUI `List` recycles too. `LazyVStack` inside a `ScrollView` creates views lazily but does **not** recycle them, so memory grows as the user scrolls — correct for a few dozen rows, wrong for thousands.
- Do no work in `cellForRow` beyond binding prepared values. Formatting dates and numbers there is measurable: create formatters once (`localization.md`).
- Prefetching (`UITableViewDataSourcePrefetching`, `.task` on appear) starts the network and decode before the row is on screen; cancel it when the row disappears, or a fast scroll queues hundreds of requests.
- Avoid off-screen rendering: shadows without an explicit `shadowPath`, masks, and rasterization are the classic hitch sources. The Animation Hitches instrument names the frame that missed and why.
- Fixed or estimated row heights that are close to reality prevent the layout recalculation storm; a badly estimated height is worse than none.

## Energy

- Energy cost is dominated by radio use, location, and keeping the CPU out of idle. Batch network requests; let `URLSession` schedule discretionary work (`background.md`).
- Continuous location at best accuracy is the most expensive thing an app can do. Match `desiredAccuracy` and `distanceFilter` to the feature, and stop updates the moment the screen that needs them disappears.
- Timers that fire every second keep the CPU awake; `EXC_RESOURCE (WAKEUPS)` is the OS telling you it noticed.
- Animations continuing while the app is not visible, and video decoding for an off-screen player, both bill the user's battery for nothing.
- The Energy Log instrument and the Organizer's battery metrics answer "is this us"; nothing else does.

## App Size

- Two numbers matter: **download size** (what the store transfers, thinned for the device) and **install size**. The store shows the first, the user's storage feels the second.
- Above roughly **200 MB** the App Store warns before a cellular download, which suppresses installs measurably. The hard bundle ceiling is 4 GB.
- Assets in an asset catalog are thinned per device and compressed; loose files in the bundle are not. This is the cheapest size win available.
- Strip debug symbols in Release and upload the dSYM separately (you need it for symbolication — `crashes.md`). Optimize for size (`-Osize`) where the app is not CPU-bound.
- On-demand resources move rarely used content out of the initial download at the cost of a fetch path that must handle failure.
- Measure from the App Store Connect app size report for a real build, not from the `.ipa` on disk — thinning and compression make the local file misleading.

## Measuring Honestly

- Release configuration, physical device, debugger detached, device warm (run twice, discard the first).
- Oldest supported device, then the newest. The gap between them is the design constraint.
- One change at a time, with the number before and after in the same conditions.
- Airplane mode or a network conditioner for anything network-adjacent — an unstable network makes every measurement noise.
- The simulator lies about launch time, memory ceilings, GPU cost and energy. It is honest about correctness only (`devices.md`).

## Field Data

- **Xcode Organizer** aggregates real-user launch time, hang rate, battery, disk writes, memory and termination reasons by version. It is the only view of the devices you do not own, and it is free.
- **MetricKit** delivers daily `MXMetricPayload` (histograms, not averages — read the 90th percentile) and `MXDiagnosticPayload` (crashes, hangs, CPU exceptions, disk writes) into your own backend if you want them beyond Apple's window.
- Regressions show up as a percentile moving, not a crash. Compare against the recorded baseline for the previous build, which is why the baseline is recorded at release (`releases.md`).

## Write It Down

- **Every measurement is a `## Baselines` row** in `~/Clawic/data/ios/memory.md`: date, app, build, device and OS, cold launch, download size, crash-free rate, hang rate (`memory-template.md`). A number in a chat message is gone by the next session.
- **A teardown of where the time or the memory went**, with what was tried and what worked, is `artifacts/launch-teardown-<app>.md` or `artifacts/memory-teardown-<app>.md`, with its `## Boxes` line in the same turn.
- **The budgets the team commits to** — the launch number, the size ceiling, the crash-free gate — belong in the `## Budgets` section that ships with `baselines.md` when the section is split out. Without a committed number, no measurement is ever a failure.
