# App Review — Passing It, and Reading a Rejection

The submission workflow itself (accounts, metadata, store presence) belongs to `app-store`; this is the app-side work: what the binary must do to pass, and what to do when it does not.

**Before submitting**, read `## Rejections` in `~/Clawic/data/ios/memory.md` — rejections repeat by guideline, and this app's history is the most accurate checklist that exists — and open `artifacts/review-notes-*.md` if `## Boxes` names one.

**Contents:** [What Review Actually Is](#what-review-actually-is) · [The Automated Gate](#the-automated-gate) · [The Human Pass](#the-human-pass) · [The Guidelines That Reject Most Often](#the-guidelines-that-reject-most-often) · [Review Notes](#review-notes) · [When You Are Rejected](#when-you-are-rejected) · [Appeals and Expedites](#appeals-and-expedites) · [Regional and Category Obligations](#regional-and-category-obligations) · [Write It Down](#write-it-down)

## What Review Actually Is

Two things, in sequence:

1. **An automated gate at upload** — Info.plist keys, entitlements, privacy manifests, SDK signatures, icons, architectures, version numbers. Failures arrive within minutes, name the exact problem, and require a new build.
2. **A human running the app for a few minutes**, usually on one device, from a fresh install, in whatever locale and network conditions they have. Apple states most submissions are reviewed within 24 hours; plan in days.

Nearly everything that fails the human pass fails because the reviewer could not get in, could not find the feature, or hit a wall the developer never sees: onboarding on a clean install, a demo account that expired, a permission prompt with no explanation, an offline state.

## The Automated Gate

Fix these before uploading, in this order — each one costs a build:

- Privacy manifest present, with every required-reason API declared; every listed SDK shipping a manifest and a signature (`privacy.md`).
- Every purpose string present for every API the app or an SDK touches, localized (`permissions.md`).
- Entitlements matching the provisioning profile, for the app **and** every extension (`capabilities.md`).
- App and extension versions and build numbers matching, build number higher than anything previously uploaded for that version (`releases.md`).
- Complete icon set, supported architectures, no simulator slices, no non-public API symbols.
- `ITSAppUsesNonExemptEncryption` set truthfully so export compliance does not stall the build (`data.md`).

## The Human Pass

Rehearse it before submitting, on a device wiped of your app:

1. Install fresh; delete the keychain items a previous install left behind (`data.md`).
2. Launch on the **floor device** and on the network the reviewer might have. A crash on an older device is the most common 2.1 rejection.
3. Reach the paid feature with the demo credentials from the review notes, following the notes literally.
4. Deny every permission and use the app anyway.
5. Turn on Airplane Mode and use the app: every screen must explain itself, none may be blank or spin forever.
6. Open every link in the app, including the ones in the paywall and the settings screen.
7. Check the app at the largest Dynamic Type size with VoiceOver on (`accessibility.md`).

## The Guidelines That Reject Most Often

| Guideline | What it means in practice | The fix that works |
|---|---|---|
| 2.1 Completeness | Crashes, placeholder content, broken demo account, a feature that needs hardware the reviewer lacks | Demo credentials that work, a video for hardware features, a full pass on the floor device |
| 2.3 Accurate metadata | Screenshots that are not the app, descriptions promising what is not there | Screenshots from the shipping build |
| 2.5.1 Private API | A symbol from a non-public framework, sometimes inside an SDK | Remove it; the error names the symbol |
| 2.5.4 Background modes | A declared mode the app does not genuinely use — silent audio to stay alive is the classic | Remove the mode, or implement the real feature (`background.md`) |
| 3.1.1 In-app purchase | Any external payment path for digital content | StoreKit only (`storekit.md`) |
| 3.1.2 Subscriptions | Paywall missing price, duration, renewal disclosure, Terms and Privacy links, or Restore | The paywall checklist in `storekit.md` |
| 4.2 Minimum functionality | A web wrapper, or an app that could be a web page | Native features that justify an app; not a re-argument |
| 4.3 Spam | Near-duplicate of another app on the account | One app, or a genuinely different product |
| 4.8 Login services | A social login with no privacy-preserving equivalent | Sign in with Apple, or an equivalent that meets the criteria (`capabilities.md`) |
| 5.1.1 Data collection | Vague purpose strings, permissions requested before use, forced account creation for browsing | Purpose strings that name the feature; login skippable |
| 5.1.1(v) Account deletion | Account creation without in-app deletion | An actual delete flow (`privacy.md`) |
| 1.2 User-generated content | Missing filtering, reporting, blocking, or a published contact | All four, plus a EULA covering objectionable content |
| 2.3.10 / age rating | Mentions of other platforms in metadata, or a rating that does not match the content | Metadata cleanup, honest rating questionnaire |

Two rules that are code, not policy, and that people keep discovering the hard way: **login must be skippable** if the app has content that does not need an account, and **Sign in with Apple is required** the moment another third-party login exists.

## Review Notes

The single highest-return artifact in this whole domain. It must contain:

- Demo account credentials that work — username in the notes, **password stored as a pointer in our own files** (`memory-template.md`), and an account that does not expire between submissions.
- Exact steps to reach the feature that is not obvious, numbered.
- Why each unusual permission is needed, in one line each.
- A note about hardware requirements, with a demo video URL when the feature needs a device or an accessory the reviewer will not have.
- Anything a reviewer would otherwise flag: an empty state that looks broken, a region-locked feature, a scheduled event.

Keep it in `artifacts/review-notes-<app>.md`, update it whenever the app changes, and paste it at every submission. Two rejections in a row for "we could not locate the feature" is the normal cost of not having it.

## When You Are Rejected

1. **Read the guideline number**, not just the prose. The number tells you which of the categories above you are in.
2. **Reproduce the reviewer's steps.** They include screenshots and a device model; use that device class, that OS, that locale.
3. **Decide: metadata or binary.** A metadata rejection is fixed in App Store Connect with no new build; a binary rejection needs an upload.
4. **Fix the code.** Most rejections are a small, real change — the guideline is usually right even when the prose is terse.
5. **Reply in Resolution Center** stating what changed, specifically. A reply that argues without a change restarts the clock for nothing.
6. **Record it** in `## Rejections` with the guideline, what they said, what changed, and how many days it cost.

The rejection does not lose your place beyond the review time; the risk is a release date, so the release plan should assume one rejection in the schedule for anything touching purchases, permissions or accounts.

## Appeals and Expedites

- **Appeal** when the guideline was misapplied — the app genuinely does not do the thing described. Bring evidence, not argument. Appeals take days and occasionally reverse.
- **Do not appeal** a correct rejection; fixing is faster than being right.
- **Expedited review** exists for critical bug fixes and time-sensitive events. It is discretionary, tracked, and using it for a normal release makes the next genuine request less likely to be granted.
- A rejection of a **new version** does not remove the current version from the store. A rejection during a **first submission** means there is nothing live at all — plan more buffer for a launch than for an update (`releases.md`).

## Regional and Category Obligations

- Distributing in the EU requires trader information to be verified and displayed; missing it removes the app from EU storefronts. This is an account-level obligation with an app-level consequence.
- Some markets require local filings or licences before an app can be distributed (China's ICP filing for apps distributed there is the widely-known example); these take weeks and are not something review resolves.
- Regulated categories — health, finance, gambling, dating, kids — carry extra documentation, entitlement or ownership requirements, and are the most common cause of a submission stalled "In Review" for days.
- Because these rules change, verify the current requirement for the storefronts the app ships to before planning a launch date, and record the answer with its date as a `## Platform Facts` line in `~/Clawic/data/ios/memory.md`.

## Write It Down

- **Every rejection is a `## Rejections` row**: date, guideline, what they said, what changed, days lost (`memory-template.md`). This table is the pre-submission checklist that is actually about this app.
- **The review notes** are `artifacts/review-notes-<app>.md`, with the demo password replaced by its pointer and its `## Boxes` line read condition "before every submission".
- **A release checklist that has survived a few submissions** — the automated gate, the human pass, the app-specific traps — is `artifacts/release-checklist-<app>.md`. A guideline that rejected the app twice earns a permanent line in it.
- **A regional or category requirement, with the date it was verified**, is a `## Platform Facts` line — these expire, and a stale one is worse than none.
