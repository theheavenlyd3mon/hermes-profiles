# Crashes, Hangs and Silent Kills

**Before theorizing**, read `## Pain Points` in `~/Clawic/data/ios/memory.md` and open any `artifacts/runbook-*.md` the `## Boxes` index names for this symptom — most repeat incidents are the same incident. The code table lives in SKILL.md (Termination Codes); this is the workflow around it.

**Contents:** [First, Classify](#first-classify) · [Reading a Report](#reading-a-report) · [Symbolication](#symbolication) · [Where Reports Come From](#where-reports-come-from) · [What Crash Reporters Cannot See](#what-crash-reporters-cannot-see) · [Memory Kills](#memory-kills) · [Watchdog Kills](#watchdog-kills) · [Reproducing](#reproducing) · [The Diagnostic Tools](#the-diagnostic-tools) · [Crash-Free Rate](#crash-free-rate) · [Write It Down](#write-it-down)

## First, Classify

Five different things get reported as "it crashed", and they have nothing in common:

| What happened | Evidence | Goes to |
|---|---|---|
| Code crashed | A crash report with an exception type and a backtrace | Reading a Report, below |
| Main thread stalled and the OS killed it | `0x8badf00d`, termination reason from SPRINGBOARD/FRONTBOARD | Watchdog Kills |
| Ran out of memory | A `JetsamEvent` report, no exception, no backtrace of yours | Memory Kills |
| Held a lock in a shared container while suspended | `0xdead10cc` | `capabilities.md` |
| The user swiped it away | Nothing at all | Not a bug |

Getting this wrong costs days: a jetsam kill investigated as a crash produces a hunt for a nil pointer that does not exist.

## Reading a Report

Read in this order, not top to bottom:

1. **Exception Type and Subtype** — what the kernel did and why (`EXC_BAD_ACCESS (SIGSEGV)` with `KERN_INVALID_ADDRESS` is a dangling pointer; `KERN_PROTECTION_FAILURE` is a write to read-only memory).
2. **Termination Reason** — present for OS-initiated kills, with a namespace and a code that name the subsystem outright.
3. **Last Exception Backtrace**, if any — for `SIGABRT` this is where the `NSException` message lives, and the message usually *is* the answer.
4. **Triggered by Thread**, then that thread's frames from the top down until you reach your own binary.
5. **Binary Images** — confirms which build and which architecture, and holds the UUIDs symbolication needs.

`EXC_BREAKPOINT (SIGTRAP)` is a Swift runtime trap: force-unwrapped nil, array out of bounds, integer overflow, failed precondition. The line is exact; there is nothing to deduce, only to read (`swift` covers the language-level causes).

## Symbolication

- The dSYM must match the build exactly. Compare `dwarfdump --uuid` on the dSYM against the UUID in the report's Binary Images (`commands.md`). A mismatched dSYM produces plausible, wrong function names — worse than no symbols at all.
- Archive builds keep their dSYMs in the Xcode archive. If the build machine is ephemeral, the dSYM must be uploaded somewhere durable in the same job, or the crash is permanently unreadable.
- With "Upload symbols" enabled at submission, Organizer symbolicates automatically; with bitcode gone, Apple no longer recompiles the binary, so the dSYM you produced is the one that matches.
- For a single address, `atos` against the dSYM answers faster than re-symbolicating a whole report.
- A dSYM UUID and the build number that produced it belong together in the release record (`releases.md`).

## Where Reports Come From

| Source | Covers | Caveat |
|---|---|---|
| Xcode Organizer | App Store and TestFlight users who agreed to share analytics | A sample, not a census — absolute counts are lower than reality, rates are comparable |
| MetricKit `MXDiagnosticPayload` | Crashes, hangs, CPU and disk exceptions, delivered to your own code daily | Only from devices that share diagnostics; arrives up to a day later |
| Device console / crash logs on the device | Everything, immediately, for a device you hold | Settings → Privacy & Security → Analytics & Improvements → Analytics Data |
| Third-party reporter (`crash_reporter`) | Signals and mach exceptions, with breadcrumbs and custom keys | See the next section for what it structurally cannot see |
| TestFlight | Feedback with attached crash logs when the tester submits it | Depends on the tester bothering |

## What Crash Reporters Cannot See

A structural distinction that saves the "our crash-free rate is 99.9% but users complain" argument:

- **Jetsam kills** have no signal and no in-process handler. No SDK catches them; only Organizer and MetricKit report them.
- **Watchdog kills** arrive as `SIGKILL`, which is uncatchable by definition.
- **Hangs** are not crashes at all: the app recovers, the user quits, and nothing is reported unless you measure hang rate.
- Therefore: a third-party reporter measures *code* crashes; Organizer and MetricKit measure what users actually experience. Use both, and compare against the recorded baseline (`performance.md`).

## Memory Kills

- A `JetsamEvent` report lists every process with its footprint at the moment of the kill, and names the largest. If your app is at the top, this is a footprint problem, not a leak in the classical sense.
- Extensions have their own, much lower ceilings, and their kills show up as "the widget is blank" rather than as a crash (`extensions.md`).
- The most common cause by far is decoded image memory: `width × height × 4` bytes per image, independent of file size (`performance.md`).
- The increased-memory-limit entitlement exists and is a request, not a fix (`capabilities.md`).

## Watchdog Kills

- `0x8badf00d` at launch means the main thread did not finish launching in time — synchronous work in `didFinishLaunching`, a migration, a keychain call, a network request on the main thread.
- On resume, the same code kills the app when the scene takes too long to become active.
- The report's termination reason names the phase (scene creation, resume, suspend), which tells you which callback to look at.
- Reproduce by launching on the oldest device with a full dataset and a slow network — not on a developer phone with a warm cache (`devices.md`).

## Reproducing

- Get the device's own logs first: the console shows what happened before the kill, including OS-side messages your reporter never saw (`commands.md`).
- A `sysdiagnose` from the affected device carries the crash reports, jetsam events, and system state; it is the right ask when the user is not a developer.
- Reproduce with the same OS version, the same device class, and — when the bug smells like data — a copy of a real container rather than a fresh install.
- If it only happens in Release, suspect optimization-sensitive code, `assert`s compiled out, or timing (`devices.md`).

## The Diagnostic Tools

| Symptom | Tool |
|---|---|
| `EXC_BAD_ACCESS`, over-release, use-after-free | Zombies, then Address Sanitizer |
| Random corruption, data races | Thread Sanitizer (never together with ASan) |
| UI updated off the main thread | Main Thread Checker (on by default in debug — do not silence it) |
| Undefined behavior, overflow | Undefined Behavior Sanitizer |
| Core Data threading violations | The Core Data concurrency debug argument |
| A leak that only appears after navigation | Memory Graph Debugger after repeating the flow ten times |

## Crash-Free Rate

- Define it once and stick to it: crash-free **sessions** and crash-free **users** give different numbers, and comparing across the two is meaningless.
- Set a release gate — a phased release paused below the gate is the only rollback iOS offers (`releases.md`).
- 99.5% crash-free sessions is a common floor for consumer apps; the number that matters is *your* previous release, recorded, on the same OS mix.
- Hang rate belongs next to it. An app with no crashes and a 2% hang rate is a bad app with good metrics.

## Write It Down

- **A root cause that took more than a few minutes** is a `## Pain Points` line in `~/Clawic/data/ios/memory.md`: date, symptom, actual cause, what changed (`memory-template.md`). This is what stops the next session re-walking the chain.
- **The second occurrence of the same failure** stops being a note and becomes `artifacts/runbook-<symptom>.md`: the ordered checks, the fix, and the build to roll forward from — with its `## Boxes` line naming the symptom as the read condition.
- **Crash-free rate and hang rate at each release** are `## Baselines` rows, per build and per device class. Without them, "this release is worse" is an opinion.
- **A platform-level cause** — an OS version that breaks a framework, a device model with a unique failure — is a `## Platform Facts` line.
