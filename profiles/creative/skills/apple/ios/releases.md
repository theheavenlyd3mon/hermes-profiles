# Releases — Versions, Rollout, and the Annual OS Season

**Before shipping**, read `releases/<year>.md` (the last build, its outcome, its crash-free rate), `## Baselines` and `## Due` in `~/Clawic/data/ios/memory.md`. **Write the release row in the same turn it ships** — there is no rollback, and the previous build's numbers are the only safety net (SKILL.md Rule 9).

**Contents:** [Version and Build Numbers](#version-and-build-numbers) · [The Pipeline](#the-pipeline) · [Phased Release Is the Only Rollback](#phased-release-is-the-only-rollback) · [Deployment Target](#deployment-target) · [App Size](#app-size) · [TestFlight](#testflight) · [Metadata Without a Build](#metadata-without-a-build) · [The Annual OS Season](#the-annual-os-season) · [Expiries](#expiries) · [The Checklist](#the-checklist) · [Write It Down](#write-it-down)

## Version and Build Numbers

- `CFBundleShortVersionString` is the marketing version (`3.2.0`) users see; `CFBundleVersion` is the build number, and it must **increase** within a version. A duplicate build number is rejected at upload, not at review.
- **Every extension's version and build must match the app's.** This is the most common upload rejection in apps with widgets, and it is trivially automatable (`extensions.md`).
- `build_number_scheme` decides how the next one is produced: monotonic increment, CI run number, or timestamp. Timestamps never collide across branches; CI run numbers make a build traceable to a job; increments require discipline.
- Record version, build and dSYM UUID together in that release's row in `~/Clawic/data/ios/releases/<year>.md`. Months later, a crash report names a build number, and nothing else connects it to a commit (`crashes.md`).

## The Pipeline

Archive → validate → upload → processing → TestFlight → submit → review → release. The steps that surprise people:

- **Processing** can take from minutes to hours, and export-compliance answers block it. Set `ITSAppUsesNonExemptEncryption` in Info.plist so it never asks (`data.md`).
- **Validation** catches most automated-gate failures locally, before the upload. Run it; it is faster than discovering the same thing after processing.
- **Release options**: automatic on approval, manual, or scheduled for a date. Manual plus phased is the default worth having — approval at 3 a.m. should not be a launch at 3 a.m.
- Uploads go through `release_tooling`; whichever it is, the same artifacts (the archive and its dSYMs) must be kept somewhere durable, because an ephemeral CI machine deletes the only copy of your symbols.

## Phased Release Is the Only Rollback

- Phased release rolls an automatic update out over about a week in increasing percentages. It can be **paused** at any point, and resumed.
- It only affects users with automatic updates on. Anyone who opens the App Store page gets the new version immediately, so a phased release is a shock absorber, not a containment barrier.
- **There is no way to re-release a previous build.** Pausing stops the spread; fixing means a new build through review, expedited if it is bad enough. Removing the app from sale does not remove it from devices that have it.
- Gate the phases on the numbers: crash-free rate and hang rate against the recorded baseline for the previous build (`performance.md`). Without a recorded baseline, "is this release worse" is unanswerable in the window when it matters.
- Keep the previous build's tag and dSYM. Rolling forward from the last good commit is the fastest recovery, and it requires knowing exactly which commit that was.

## Deployment Target

- The arithmetic is in SKILL.md Rule 2: drop the oldest major when it falls below ~2% of *your* active devices for two consecutive months, measured in App Store Connect's device and OS breakdown.
- Users below the target are **not** cut off: the App Store keeps serving them the last compatible build. That build is frozen, including its bugs and its API endpoints — which is the real cost, and the reason server compatibility has a longer tail than the app.
- Raising the target removes availability checks and unlocks APIs; the win is in code you delete, and it should be counted before the decision.
- Every raise is a support decision too: the users who freeze are disproportionately the ones with old devices and the least tolerance for a broken app.

## App Size

- Two numbers: download size (thinned per device) and install size. Get them from the App Store Connect size report for a real build, not from the local archive.
- Above roughly **200 MB** the store warns before a cellular download; the hard bundle ceiling is 4 GB.
- Asset catalogs are thinned and compressed; loose bundle files are not. On-demand resources move rarely used content out of the first download at the cost of a fetch path that must fail gracefully.
- Track size per release like any other baseline; it creeps by a few megabytes per version and nobody notices until a user does (`performance.md`).

## TestFlight

Depth lives in `testflight`; the facts that change a release plan:

- Builds expire after **90 days**. A beta that has been running longer is testing nothing.
- Internal testers get builds immediately; the first build for external testers goes through a review of its own, and later builds usually do not.
- TestFlight builds use the **production** APNs environment and the **production** CloudKit container. Testers write real data to real backends (`notifications.md`, `capabilities.md`).
- Purchases in TestFlight are free sandbox purchases and prove the flow, not the billing (`storekit.md`).
- Crash reports from TestFlight appear in Xcode Organizer alongside App Store ones, for testers who share analytics.

## Metadata Without a Build

Changing these does not need a new binary, and knowing that saves days:

- Screenshots, description, keywords, subtitle, promotional text, support and marketing URLs, per locale.
- **Promotional text** can be changed at any time without any review — the right place for a "known issue" notice.
- Price and availability, in-app purchase metadata, phased release state.
- What *does* need a build: anything in the bundle, the privacy manifest, purpose strings, entitlements, and the app name if it is in the bundle rather than the store listing.

## The Annual OS Season

A predictable cycle worth having in `## Due`:

- **June**: the new iOS is announced and betas begin. Install it on a dedicated beta device, never on the floor device (`devices.md`). Run the regression pass now — a break found in June is a fix; the same break found in September is an incident.
- **Summer**: deprecations and behavior changes land. With `beta_os_policy: wait-for-x1`, adopt nothing new yet, but test everything.
- **September**: the release ships to users within days, and a large share of the install base updates in the first weeks. Watch crash-free rate by OS version, not in aggregate — a new-OS-only crash is invisible in the average for a week.
- **Spring**: Apple sets an annual deadline requiring new submissions to be built with a recent SDK. Verify the current date and put it in `## Due` — missing it blocks submissions, including urgent fixes.

## Expiries

Everything here breaks shipping on a date, silently, and each belongs in `## Due` with its date:

| Thing | Typical life | What breaks |
|---|---|---|
| Apple Developer Program membership | 1 year | Apps removed from sale; nothing can be submitted (`memory-template.md`, shared subscriptions) |
| Distribution certificate | 3 years | Cannot sign a release build |
| Provisioning profiles | 1 year | Cannot build or install |
| Push certificate (`.p12`) | 1 year | Push stops, silently — use an auth key instead (`notifications.md`) |
| APNs auth key (`.p8`) | No expiry | Nothing, which is the point |
| TestFlight build | 90 days | Testers lose access |

## The Checklist

| Step | Gate |
|---|---|
| Version and build bumped, extensions matched | Upload will reject otherwise |
| Baseline measured on the floor device | Cold launch, size, memory (`performance.md`) |
| Privacy manifest and SDK inventory current | Automated gate (`privacy.md`) |
| Review notes updated, demo account verified | The most common human-pass failure (`review.md`) |
| Accessibility audit on changed screens | Regression happens feature by feature (`accessibility.md`) |
| Localization pass: new strings translated, screenshots per locale | (`localization.md`) |
| dSYMs archived somewhere durable | Otherwise crashes are unreadable (`crashes.md`) |
| Release set to manual + phased, gate defined | The only rollback there is |
| Release row written | Same turn it ships |

## Write It Down

- **The release row** goes in `~/Clawic/data/ios/releases/<year>.md` the day it ships: date, app, version, build, min iOS, submitted date, outcome, rollout state, crash-free at seven days (`memory-template.md`). Append-only, cut by year.
- **A paused or halted rollout** is recorded the day it happens, with the number that triggered it, in that file's `## Notes`.
- **Baselines** for the build (launch, size, crash-free, hang rate) are `## Baselines` rows — the comparison target for the next release.
- **Every expiry date discovered** becomes a `## Due` row immediately, including the Apple Developer Program renewal, which also belongs in the shared `~/Clawic/data/finances/subscriptions.md`.
