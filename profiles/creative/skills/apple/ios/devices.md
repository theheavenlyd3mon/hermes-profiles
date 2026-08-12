# Devices and the Simulator — What Only Hardware Proves

**Before planning a test pass or reproducing a report**, read `~/Clawic/data/devices/devices.md` (the shared inventory: which physical devices exist, their models and OS versions) and `## Platform Facts` in `~/Clawic/data/ios/memory.md` for device-specific findings already recorded.

**Contents:** [The Simulator Is Not iOS](#the-simulator-is-not-ios) · [What Only Hardware Proves](#what-only-hardware-proves) · [The Device Matrix](#the-device-matrix) · [Registering Devices](#registering-devices) · [Test Conditions](#test-conditions) · [Beta OS Devices](#beta-os-devices) · [Reproducing a User's Report](#reproducing-a-users-report) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## The Simulator Is Not iOS

It is your Mac running iOS frameworks. Ranked by how often each difference produces a wrong conclusion:

| Difference | Consequence |
|---|---|
| Host CPU, host memory, no jetsam ceiling | Every performance and memory number is fiction (`performance.md`) |
| No camera, no real microphone | Capture code paths "work" by not running |
| Different keychain, no Secure Enclave | Biometrics and secure-enclave keys are simulated or absent (`data.md`) |
| Push arrives only via a simulated payload file | Environment, topic and token errors never surface (`notifications.md`) |
| StoreKit runs from a local configuration file | Nothing about the real store, receipts or sandbox is exercised (`storekit.md`) |
| Case-insensitive filesystem by default | An import that differs only by case works locally, fails everywhere else |
| No thermal state, no battery, no Low Power Mode | Energy behavior and thermal throttling are invisible |
| No cellular, no Low Data Mode, no carrier | Constrained-network paths never run (`networking.md`) |
| Background scheduling is not the real scheduler | `BGTask` behavior proves only that the handler compiles (`background.md`) |
| Entitlements are not enforced identically | A missing entitlement can pass here and fail on device (`capabilities.md`) |
| GPU is the Mac's, via a translation layer | Rendering performance and some Metal behavior differ |
| No motion sensors, NFC, or accessory hardware | Whole features are untestable |
| App Attest and DeviceCheck fail by design | Attestation flows must be exercised on hardware |
| Different pointer and keyboard behavior | Hardware-keyboard bugs hide |
| No device-specific quirks | The bug that only affects one model is invisible |
| Installs are not App Store installs | Thinning, on-demand resources and download size are not represented |

The simulator is excellent for what it is: fast iteration on correctness, layout across many screen sizes, and localization pseudolanguages. Use it for that and claim nothing else from it.

## What Only Hardware Proves

Launch time · memory ceilings and jetsam · push delivery · StoreKit purchases · camera, microphone, sensors · biometrics · background scheduling · thermal and energy · NFC and accessories · real network conditions · App Attest · widget and extension memory limits.

Any claim in that list, made from a simulator run, is unverified. That is the rule; the disagreement is only ever about which claims (SKILL.md, Where Experts Disagree).

## The Device Matrix

Small and deliberate beats large and dusty:

| Slot | What it is | What it answers |
|---|---|---|
| Floor device | Oldest model at the deployment target, on an older OS | Performance, memory, layout at the limit — the device that decides the budgets |
| Current device | A recent phone on the current OS | What most users see |
| Tablet | Only if `target_devices` includes iPad | Size classes, multitasking, pointer (`layout.md`) |
| Beta device | Anything, running the next OS | The September regression, found in June (`releases.md`) |

Keep OS diversity, not just model diversity: the current OS and the one before it cover most of the install base, and the interesting bugs are usually OS-version bugs rather than model bugs.

Record each device in the shared inventory — model, OS, and what it is for — so the matrix survives the person who assembled it (`memory-template.md`).

## Registering Devices

- A membership allows **100 devices of each type per membership year** for development and ad-hoc distribution. Removing a device does not free the slot until the annual renewal window.
- Adding a device requires regenerating the development and ad-hoc provisioning profiles that include it (`capabilities.md`). Automatic signing does it; manual signing means a new profile everywhere it is used.
- TestFlight does not consume device slots — this is the main reason to prefer it over ad-hoc distribution for anything beyond the team (`releases.md`).
- Record UDIDs in the shared devices inventory prefixed as identifiers (`udid:…`); they are identifiers, not secrets, and they are needed every time a profile changes.

## Test Conditions

The conditions that produce bug reports, and how to create them:

- **Slow or lossy network**: Network Link Conditioner (on device via the Developer settings, or on the Mac) with a 3G or 100%-loss profile. Most timeout and retry bugs need this (`networking.md`).
- **Low Power Mode**: disables background refresh and throttles the CPU. Half of "the background task never runs" is this (`background.md`).
- **Low storage**: `Caches/` gets purged aggressively, downloads fail, and the app must survive it (`data.md`).
- **Locked device**: protection classes decide what background code can read (SKILL.md Rule 7).
- **Focus and Do Not Disturb**: changes notification delivery and presentation (`notifications.md`).
- **VPN or a corporate proxy**: TLS interception, DNS oddities, and MTU issues.
- **A full-day battery run**: the only way to see energy problems before users do.

## Beta OS Devices

- Never put a beta OS on the floor device or on the phone used for daily work. A beta device is a dedicated device, and the inventory row says so.
- Downgrading is painful or impossible depending on the point in the cycle; treat installing a beta as one-way.
- File feedback for OS bugs during the beta window; that is the period where a report can still change something.
- With `beta_os_policy: adopt-early`, the beta device is also the development device for the new APIs — with the understanding that they change until the release candidate (`releases.md`).

## Reproducing a User's Report

Ask for, or read from the report, the five facts that determine reproducibility: **device model, OS version, app build, locale/region, and accessibility settings**. A crash report has the first three; the last two explain the bugs the report cannot.

Then match the environment as closely as the matrix allows, and if the bug still hides, get a `sysdiagnose` or the device's own analytics data rather than guessing (`commands.md`, `crashes.md`).

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| Works in the simulator, crashes on device | Entitlement, architecture, or a case-sensitive path | Dump entitlements; check the import casing |
| Works on device, fails in the simulator | Hardware-dependent code path with no fallback | Guard it and provide a simulator path for development |
| Works in debug, fails in Release | Optimization, stripped assertions, or timing | Build Release locally and attach (`crashes.md`) |
| Only one user's device fails | OS version or a locale/accessibility setting | The five facts above |
| Fast for us, slow for users | Measured on the newest device only | Measure on the floor device (`performance.md`) |
| Push works for the team, not for testers | Environment difference between builds | `notifications.md` |
| Cannot install on a new tester's phone | Device slot or profile not regenerated | Registering Devices, above; or move to TestFlight |

## Write It Down

- **Every physical device** goes in the shared `~/Clawic/data/devices/devices.md` — name, kind, model, OS, `udid:` identifier, what it is for — read before adding, updated in place, row deleted when the device is retired (`memory-template.md`).
- **A device- or OS-specific finding** ("only this model shows the safe-area gap", "iOS 26.1 changed keyboard timing") is a `## Platform Facts` line. It is the most reusable kind of fact and the easiest to lose.
- **Measurements taken on a device** are `## Baselines` rows, always with the device and OS in the row — a launch time without them is not comparable to anything.
