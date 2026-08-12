# Privacy — Manifests, Labels, Tracking

**Before an SDK integration or a submission**, read `## SDKs` in `~/Clawic/data/ios/memory.md` (what is embedded, and whether each one ships a manifest and a signature) and `tracking_policy` plus `audience` in `config.yaml` — a kids-category app answers most of this file differently.

**Contents:** [Four Things Apple Checks](#four-things-apple-checks) · [The Privacy Manifest](#the-privacy-manifest) · [Required-Reason APIs](#required-reason-apis) · [Third-Party SDKs](#third-party-sdks) · [Nutrition Labels](#nutrition-labels) · [Tracking and ATT](#tracking-and-att) · [Special Categories](#special-categories) · [Data Deletion](#data-deletion) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## Four Things Apple Checks

| Surface | Where it lives | Enforced by |
|---|---|---|
| Privacy manifest | `PrivacyInfo.xcprivacy` in the app and in each SDK | Automated check at upload |
| SDK signatures | Inside the embedded framework | Automated check at upload |
| Nutrition labels | App Store Connect, per app version | Review, and user-visible on the product page |
| Runtime consent | ATT prompt, purpose strings, permission flows | Review, and the OS itself |

The first two block the upload — minutes after you thought you were done. The last two are judged by a human, and by users comparing your labels against the App Privacy Report on their own device.

## The Privacy Manifest

`PrivacyInfo.xcprivacy` is a plist with four keys:

- `NSPrivacyTracking` — boolean, whether the app or SDK tracks as Apple defines it.
- `NSPrivacyTrackingDomains` — domains used for tracking. Any domain listed here is **blocked** by the system when the user has denied ATT, which is the enforcement mechanism, not a formality.
- `NSPrivacyCollectedDataTypes` — what is collected, whether it is linked to the user, whether it is used for tracking, and the purposes.
- `NSPrivacyAccessedAPITypes` — the required-reason APIs used, each with an approved reason code.

Xcode can produce an aggregate privacy report from an archive, merging your manifest with every embedded SDK's. Generate it before submitting: it is the same view Apple assembles, and it is where an SDK's undeclared collection becomes your problem.

## Required-Reason APIs

A small set of APIs, all previously used for fingerprinting, that require a declared reason code:

| API family | Typical legitimate reason |
|---|---|
| File timestamps (creation, modification) | Displaying dates to the user, or app-internal file management |
| System boot time | Measuring elapsed time inside the app |
| Disk space | Checking there is room before a download or a write |
| Active keyboard list | Providing a keyboard extension's own functionality |
| `UserDefaults` | Reading and writing the app's own preferences |

`UserDefaults` is on the list, which surprises people: nearly every app needs a declaration. Using one of these without a valid reason code fails the automated check with a message naming the API — the fix is the declaration, unless the use really has no approved reason, in which case it is the use that must change.

## Third-Party SDKs

- SDKs on Apple's designated list must ship **both** a privacy manifest and a code signature. An outdated copy of such an SDK blocks your upload, and the error names the SDK, not the file.
- Update SDKs before a submission window, never during one. The privacy-manifest failure mode turns a Tuesday release into a Thursday release.
- An SDK's manifest declares what *it* collects; your app's labels must include it. "We didn't know the analytics SDK collected that" is not a defence anyone accepts, least of all users reading the App Privacy Report.
- Audit what SDKs send at integration time with a proxy on a test device. Attribution and analytics SDKs in particular default to more collection than their documentation implies, and device fingerprinting as an ATT fallback is prohibited and enforced.
- Keep the `## SDKs` inventory in `~/Clawic/data/ios/memory.md` current — name, version, purpose, manifest present, signature present, data collected. It is the checklist for every submission and the answer when a customer asks what is inside the app.

## Nutrition Labels

- Declared per app in App Store Connect: data types, whether each is linked to identity, and whether any is used for tracking. They are visible on the product page before download.
- **They must match reality including SDK behavior.** Apple checks, users check with the App Privacy Report, and a mismatch is both a rejection and a trust problem.
- "Data not collected" is a strong claim and a real competitive advantage — it requires that no embedded SDK collects either.
- Revisit the labels at every release that adds an SDK or a feature. They are not set-and-forget metadata.

## Tracking and ATT

- Tracking means linking user or device data with data from other companies for advertising or measurement, or sharing it with a data broker. Analytics you keep to yourself is not tracking; passing an identifier to an ad network is.
- The ATT prompt is required *before* tracking, must be shown while the app is active, and can be shown once. Denial zeroes the IDFA — the value returns as all zeros rather than failing.
- You may not gate app functionality or offer an incentive for accepting. A pre-prompt explaining the value is allowed and is where the conversion is won or lost (`permissions.md`).
- Fingerprinting as a fallback — deriving a stable identifier from device characteristics — is prohibited regardless of ATT status, and Apple enforces it against apps and SDKs.
- With `tracking_policy: none`, none of this UI exists and the labels say so; that is a shipping decision, not an omission.

## Special Categories

- **Kids (`audience: kids`)**: no tracking at all, no third-party analytics or ads beyond what the kids category permits, parental gates for outbound links and purchases, and COPPA-shaped obligations. The category is reviewed strictly and is not reversible without consequences.
- **Health**: HealthKit data may not be used for advertising or sold, may not be shared without consent, and may not be stored in iCloud. Apps that write to HealthKit need clinically sensible values, which reviewers do check.
- **Finance**: identity verification data, account numbers and transaction history are all high-sensitivity labels; regional financial regulations add requirements beyond Apple's.
- **User-generated content**: not a privacy rule but the adjacent one — filtering, reporting, blocking and a published contact are required (`review.md`).

## Data Deletion

- An app that supports account creation must support account **deletion** in-app (5.1.1(v)) — not a link to a support email, not a form the user fills out and waits for.
- The deletion must actually delete, or clearly state the retention obligation that prevents it.
- Deleting the app does not delete the account, and users assume it does. Say so where the account is created.
- The keychain survives app deletion, so a "deleted" account can leave credentials behind on device (`data.md`).

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| Upload rejected naming a missing API declaration | A required-reason API with no reason code, in your code or an SDK | Add the reason, or update the SDK |
| Upload rejected naming an SDK | That SDK lacks a manifest or a signature | Update it to a version that ships both |
| Review flags the labels | Declared collection does not match the aggregate privacy report | Generate the report from the archive and reconcile |
| ATT prompt never appears | Asked while not active, already answered, or device-level tracking disabled | `permissions.md` |
| IDFA is all zeros | ATT denied, as designed | Do not fall back to fingerprinting |
| Users report domains the app "shouldn't" contact | An SDK phoning home | Proxy the app on a test device |
| Kids app rejected for analytics | Third-party analytics not permitted in that category | Remove it or leave the category |

## Write It Down

- **The SDK inventory** — name, version, purpose, manifest, signature, what it collects — is `## SDKs` in `~/Clawic/data/ios/memory.md`, and moves to `sdks.md` when it outgrows the section (`memory-template.md`). This is the table that makes each submission a check instead of an investigation.
- **The manifest and label decisions** — which data types are declared, why each is collected, what was deliberately not collected — are `artifacts/privacy-declarations-<app>.md`, with its `## Boxes` line in the same turn. Labels are re-derived at every release, and the reasoning is what nobody remembers.
- **A privacy-related rejection or upload failure** is a `## Rejections` row with its guideline or error identifier — these repeat by SDK and by API, and the row is the fix next time.
