# Working File Templates — iOS

Read this file only when WRITING. `config.yaml` is what the user **declared**; `memory.md` and everything it indexes is what you **observed** or produced. An observation never overwrites a declaration.

## Where each thing goes

| Data | Home | How it grows |
|---|---|---|
| Declared preferences — Configuration table keys and preference areas alike | `~/Clawic/data/ios/config.yaml` | Key by key, read-modify-write |
| Apps, identifiers, platform facts, baselines, rejections, pain points, due dates, box index | `~/Clawic/data/ios/memory.md` | Rewritten in place; stays small |
| Apps and their identifiers — bundle id, team, App Store id, App Group, capabilities, min iOS | `## Apps` in `memory.md`; `~/Clawic/data/ios/apps.md` once it outgrows the section | One row per app or target |
| Measured baselines — cold launch, download size, crash-free rate, hang rate, memory peak | `## Baselines` in `memory.md`; `~/Clawic/data/ios/baselines.md` once it outgrows the section | One row per measurement, per app and device |
| Review rejections and what cleared them | `## Rejections` in `memory.md`; `~/Clawic/data/ios/rejections.md` once it outgrows the section | One row per rejection, keyed by guideline |
| Embedded third-party SDKs — version, purpose, privacy manifest, signature, what it collects | `## SDKs` in `memory.md`; `~/Clawic/data/ios/sdks.md` once it outgrows the section | One row per SDK, per app |
| Releases: version, build, min iOS, review outcome, rollout | `~/Clawic/data/ios/releases/<year>.md` | Append-only, cut by year |
| Physical test devices | `~/Clawic/data/devices/devices.md` (**shared**) | One row per device, every kind of device in one inventory |
| The Apple Developer Program membership and other recurring Apple charges | `~/Clawic/data/finances/subscriptions.md` (**shared**) | One row per subscription |
| A client the app is built for | `~/Clawic/data/contacts/contacts.md` (**shared**) | One row per person; referenced from here by name only |
| The app as a tracked engagement — goal, status, milestones | `~/Clawic/data/projects/<project>.md` (**shared**) | One file per project |
| Things you produced that get re-read — a runbook, an entitlements or Info.plist set that finally worked, a persistence or paywall decision, App Review notes, a launch-time teardown, a release checklist | `~/Clawic/data/ios/artifacts/<kebab-name>.md` | Born as its own file, from the first one |
| **Anything durable this table does not name** | `~/Clawic/data/ios/<plural-noun>.md`, or `artifacts/<kebab-name>.md` if it is a long text read whole | Name the file after what it holds, never after when it was made; add its `## Boxes` line in the same turn |
| Credentials of any kind | Nowhere under `~/Clawic/data/` | Pointer only — see Secrets |

Deciding where something unnamed goes, in this order: (1) would another skill want to read it — a device, a person, a project, a recurring charge? Then it belongs in the shared box, not here. (2) Is it a text read whole when its subject comes up — a procedure, a configuration that took work to derive, a decision with its reasoning? Then `artifacts/`, its own file from the first one. (3) Is it one more row of something that accumulates? Then a section of `memory.md` until the split threshold.

## When to write

No permission needed; every write is announced in one line that names the file. Writes and deletions stay inside the paths declared in this skill's `configPaths`. A deletion is named in that same line, and in a shared box only rows this skill itself wrote are ever updated or removed.

| It happened | Write |
|---|---|
| An app, extension target, bundle id, App Group, or App Store id was created or discovered | `## Apps` |
| A capability was enabled, or an entitlement changed | The app's row in `## Apps`, in the `Capabilities` column |
| A physical test device was added, upgraded, lent out, or retired | Its row in `devices.md` (shared) |
| A build was submitted, approved, or released | A row in `releases/<year>.md` |
| A submission was rejected | `## Rejections` — guideline number, what they said, what changed, days lost |
| An SDK was added, updated, or removed | `## SDKs` — version, whether it ships a privacy manifest and a signature, what it collects |
| Cold launch, app size, crash-free rate, hang rate or a memory peak was measured | `## Baselines`, with the device and OS it was measured on |
| A platform fact cost effort to find — an AASA cache delay, an entitlement quirk, a device-specific failure, a locale bug, a reviewer's stance | `## Platform Facts` |
| A failure's cause was not obvious, or the same failure appeared twice | `## Pain Points`; the second occurrence earns a runbook in `artifacts/` |
| An entitlements file, Info.plist set, privacy manifest or paywall configuration finally worked | `artifacts/` |
| A persistence, architecture, monetization or deployment-target decision was made | `artifacts/`, with what was rejected and why |
| App Review notes or demo instructions were written | `artifacts/review-notes-<app>.md`, with the demo password replaced by its pointer |
| The Apple Developer Program was renewed, or its renewal date became known | Its row in `finances/subscriptions.md` (shared) and a `## Due` line |
| A certificate, provisioning profile, or push key expiry date became known | `## Due` |
| A regression pass, screenshot refresh, or crash triage was scheduled or run | `## Due` |
| The user declared a preference | Its key in `config.yaml` |

## Start flat, split only when it hurts

Everything except artifacts, release logs and the shared boxes begins inside `memory.md`. Splitting is a procedure, not a suggestion:

1. Before appending to a section, count its entries.
2. If the append would take it past **~15 entries or ~40 lines of real content** — scaffolding, headings and comments do not count — then, in the same turn: create the new file in `~/Clawic/data/ios/`, move the whole section into it, **delete the section from `memory.md`**, add its line to `## Boxes`, and append the new entry to the new file.
3. Keep the headings identical on both sides of the move, so the split is a copy-paste and never a rewrite.
4. Never leave a copy behind. If the same data ever appears in both places, the extracted file wins and the `memory.md` copy is deleted.

Artifacts are the exception: a runbook, a working entitlements set or a decision is born as its own file whatever its size, because it is read whole and only when its subject comes up.

## Secrets

Nothing under `~/Clawic/data/` ever holds a secret value — not the files named here, not files you create, not text the user pastes in and asks you to keep. A pasted `ExportOptions.plist`, xcconfig, fastlane `Appfile`/`Matchfile`, CI log or App Review note is a dense source of secrets: strip each value **before** writing and leave its pointer in place, in this shape: `<kind>:<locator>`.

`keychain:apple-id-app-specific` · `env:ASC_KEY_ID` · `env:ASC_ISSUER_ID` · `1password:Work/Apple/asc-key` · `bitwarden:Apple/distribution-p12` · `vault:secret/ios/apns` · `file:~/private_keys/AuthKey_ABC123DEFG.p8` · `file:~/certs/distribution.p12`

In a text, the pointer goes where the value was: `demo_password: <1password:Work/Acme/review-demo>`. Say in one line that you did it.

In this domain — **not secrets, keep them**: bundle identifiers, Team ID, App Store app id (adam id), App Group and iCloud container ids, App Store Connect Key ID and Issuer ID (the identifiers, never the `.p8` body), APNs auth key id, provisioning-profile and certificate *names* and expiry dates, entitlement keys, device names, models, OS versions and UDIDs, StoreKit product ids, version and build numbers, dSYM UUIDs, guideline numbers, SDK and framework names.

**Secrets, strip them**: the contents of any `.p8`, `.p12`, `.cer` private key or its passphrase, App Store Connect API private keys, Apple ID passwords and app-specific passwords, keychain passwords, App Review demo-account passwords, the App Store shared secret used for receipt validation, any API token found in an xcconfig, Info.plist, or CI environment, and signing certificate export passwords.

**Contents:** [config.yaml](#configyaml) · [memory.md](#memorymd) · [shared devices inventory](#shared-devices-inventory) · [shared subscriptions](#shared-subscriptions) · [shared contacts and projects](#shared-contacts-and-projects) · [artifacts/](#artifacts) · [releases/](#releases) · [split-out files](#split-out-files)

## config.yaml

Keys come from the Configuration table in `SKILL.md`, plus free-form keys nested under a preference area. Write a key only when the user states the preference.

**Writing is read-modify-write**: load the existing file, set or replace only the key just declared, keep every other key byte for byte. Never emit a `config.yaml` from this template — the template shows shape, not content. Create `~/Clawic/data/ios/` if it does not exist.

```yaml
ui_framework: swiftui
min_deployment_target: n-1
target_devices: universal
dependency_manager: spm
release_tooling: fastlane
crash_reporter: sentry
tracking_policy: none
audience: general
beta_os_policy: wait-for-x1
build_number_scheme: ci-run

# Preference areas — free-form keys added as the user reveals them.
# A preference the user states is a declaration and belongs here, never in memory.md.
conventions:
  bundle_prefix: com.acme
  app_group: group.com.acme.shared
  config_via: xcconfig
platform:
  orientations: [portrait]
  ipad_multitasking: false
  oldest_supported_device: iPhone SE 3rd gen
monetization:
  storekit: 2
  validation: on-device
accessibility:
  commitment: voiceover-complete
localization:
  locales: [en, es, de]
cadence:
  os_regression_pass: september
  crash_triage: week
```

If you find a preference recorded in `memory.md`, move it here and note the move.

## memory.md

Write only the sections you have content for — a heading with nothing under it is noise, and it inflates the line count that decides a split. Never copy these hints into the user's file. `## Boxes` is the one section that is never dropped when `memory.md` is rewritten: deleting a line there orphans a file forever. This is what a populated file looks like:

```markdown
# iOS Memory

## Status
status: ongoing
last: 2026-07-26

## Boxes
- Releases and review outcomes (2026) → `releases/2026.md`; read before any submission or version bump
- Rejections by guideline (11) → `rejections.md`; read before submitting, and the moment a rejection arrives
- Entitlements + Info.plist that pass review → `artifacts/entitlements-acme.md`; read before adding any capability
- Launch-time teardown → `artifacts/launch-teardown-acme.md`; read before touching app startup
- Review notes and demo instructions → `artifacts/review-notes-acme.md`; read before every submission

## Due
| What | Every | Last run | Next due |
|------|-------|----------|----------|
| Apple Developer Program renewal | year | 2025-11-04 | 2026-11-04 |
| APNs auth key / distribution cert expiry check | quarter | 2026-07-01 | 2026-10-01 |
| New-iOS regression pass on the oldest device | year, September | 2025-09-18 | 2026-09-17 |
| Crash and hang triage in Organizer | week | 2026-07-20 | 2026-07-27 |
| Privacy manifest review after SDK updates | quarter | 2026-06-30 | 2026-09-30 |

## Apps
| App | Bundle id | Team | App Store id | Min iOS | Capabilities | Notes |
|---|---|---|---|---|---|---|
| Acme | com.acme.app | ABCDE12345 | 6470000001 | 17.0 | push, app groups, associated domains, in-app purchase | universal; SwiftUI + one UIKit list |
| Acme Widget | com.acme.app.widget | ABCDE12345 | — | 17.0 | app groups | reads `group.com.acme.shared` snapshot only |

## SDKs
| App | SDK | Version | Purpose | Manifest | Signature | Collects |
|---|---|---|---|---|---|---|
| Acme | Sentry | 8.44.0 | crash reporting | yes | yes | crash data, device id (not linked) |
| Acme | RevenueCat | 5.14.0 | subscriptions | yes | yes | purchase history, app user id |

## Platform Facts
AASA changes take ~a day to reach devices through Apple's CDN; validated once, then verified on-device.
iPhone SE 3rd gen is the floor device: cold launch there is 2.1× the iPhone 15 Pro number.
Reviewer objected twice to the paywall's restore button placement; current layout is the one that passed.
Push works only from the production APNs environment for TestFlight builds — sandbox tokens fail silently.

## Baselines
| Date | App | Build | Device / OS | Cold launch | Download size | Crash-free | Hang rate |
|---|---|---|---|---|---|---|---|
| 2026-07-20 | Acme | 412 | iPhone SE 3, iOS 26.0 | 780 ms | 61 MB | 99.7% | 0.4% |
| 2026-07-20 | Acme | 412 | iPhone 15 Pro, iOS 26.0 | 370 ms | 61 MB | 99.9% | 0.1% |

## Rejections
| Date | Guideline | What they said | What changed | Days lost |
|---|---|---|---|---|
| 2026-03-11 | 5.1.1(v) | No way to delete the account in-app | Added delete flow in Settings | 4 |
| 2026-05-02 | 3.1.1 | External payment link in the upgrade screen | Removed link, StoreKit only | 2 |

## Pain Points
2026-02: three days lost to a widget reading an empty container — App Group was on the app target only.
2026-06: `0xdead10cc` terminations traced to the Core Data handle left open in the shared container.

## How They Work
Solo developer, ships monthly, uses fastlane. Wants the exact key and API, not the concept. Will not run a destructive migration without seeing what it deletes.

---
*Updated: 2026-07-26*
```

Rules that keep this readable next month:

- **`## Boxes`**: one line per file that exists — `<what> (<volume>) → <file>; read when <condition>`. Written in the same turn the file is created. Never delete a line without deleting the file it points to. A box with no index line does not exist.
- **`## Due`**: check it against today's date at the start of a session and state any overdue item in one line — a statement, not a question. Certificate, profile, push-key and membership expiries live here because each one silently breaks shipping on the day it passes; cadences come from `cadence` in `config.yaml` when the user has declared them.
- **`## Apps`**: `Capabilities` is what is actually enabled in all three places (SKILL.md Rule 3), not what was intended. Extensions get their own row — that is the row that explains half the App Group bugs.
- **`## Baselines`**: a measurement without its device and OS is not a baseline. Always record the oldest supported device; it is the one that decides. Percentages carry their unit, durations carry `ms`.
- **`## Rejections`**: keyed by guideline number, because rejections repeat by guideline and not by date. `Days lost` is what makes the case for fixing the class of problem instead of the instance.
- **`## SDKs`**: updated at integration time, not at submission. `Manifest` and `Signature` are what the automated upload gate checks, and a `no` in either column is a blocked release waiting to happen (`privacy.md`).
- **`## Platform Facts`**: one line each, for facts about the platform, the account or the reviewer that changed a decision. This is what stops the same AASA delay or entitlement quirk from being rediscovered every few months.
- These headings are exactly the ones `apps.md`, `baselines.md`, `rejections.md` and `sdks.md` get when their sections outgrow this file, so each split stays a copy-paste.

| Status | Meaning |
|---|---|
| `ongoing` | Still learning their apps and workflow |
| `complete` | Know their targets, identifiers, devices and release rhythm well |

## Shared devices inventory

Lives at `~/Clawic/data/devices/devices.md` and is shared with every other skill that knows about the user's hardware — the user may not have any of them installed, so the format travels with this skill.

```markdown
# Devices

| Name | Kind | Model | OS | Identifier | Location / owner | Notes |
|------|------|-------|----|------------|------------------|-------|
| Iván's iPhone | phone | iPhone 15 Pro | iOS 26.0 | udid:00008130-000… | daily driver | main dev device, registered in the portal |
| Test SE | phone | iPhone SE 3rd gen | iOS 17.6 | udid:00008101-001… | desk drawer | floor device: min deployment target lives here |
| Test iPad | tablet | iPad 10th gen | iPadOS 26.0 | udid:00008103-002… | desk | multitasking and size-class checks |
```

- **Identity is `Name`** — the name the device reports, the same one Xcode and Finder show. Read the file before adding. If the name is already there, update the row in place; only its absence justifies a new row. If the file you find keys rows by MAC address or by network name instead, use its key — never introduce a second convention.
- **Foreign columns win.** If `devices.md` already exists with a different column set (a smart-home skill may have written `Room`, `IP`, `MAC`), match its columns and add anything missing as a trailing note. Never rewrite its header.
- **Retirement is part of the inventory.** When a device is sold, wiped or stops being a test target, delete its row and note the date in `## Platform Facts`. An inventory that only grows stops being an inventory. Never touch a row this skill did not write.
- **The UDID is an identifier, not a secret** — it is what a provisioning profile embeds. Record it prefixed (`udid:…`) so it is never mistaken for a credential. Nothing that authenticates goes in this file.
- **Units and currency in the value.** If the file carries a cost or a capacity column, write `1099 USD`, `256 GB` — never a bare number, because rows here come from several skills.
- **Scale cut**: one row per device while there are ≤15. Past that, one file per device at `~/Clawic/data/devices/<name>.md` with the same fields, and `devices.md` becomes the index (`Name | Kind | Model | → file`). If you arrive and the folder already looks like that, follow it — do not start a parallel `devices.md`.

## Shared subscriptions

The Apple Developer Program is a recurring charge whose lapse removes every app from the store, so it belongs where the user's other subscriptions are: `~/Clawic/data/finances/subscriptions.md`.

```markdown
# Subscriptions

| Name | Provider | Amount | Cycle | Renews | Payment reference | Notes |
|------|----------|--------|-------|--------|-------------------|-------|
| Apple Developer Program | Apple | 99 USD | year | 2026-11-04 | 1password:Personal/Apple ID | individual; lapse pulls all apps from sale |
```

- **Identity is `Name`.** Read the file first; if the row exists, update it in place. This skill owns the Apple rows and touches no others.
- **Amounts carry their currency in the value** (`99 USD`, `109 EUR` where the store charges locally), because rows here come from every provider and someone will add the column up. Prices vary by country — write what was charged, not the US list price.
- **Foreign columns win.** If `subscriptions.md` already exists with a different column set (a `money` or `subscriptions` skill may have written `Category`, `Account`, `Auto-renew`, `Annualized`), match its columns and put anything missing in its freest text column. Never rewrite its header and never start a second table below it.
- **`subscriptions.md` is a single table and is not split**: it stays small because cancellation deletes the row. When the membership lapses or is cancelled, delete the row and note the date in `## Platform Facts`.
- Mirror the renewal date as a `## Due` row in `memory.md`, because the consequence is an iOS consequence.

## Shared contacts and projects

When the app is built for someone else, the person goes in `~/Clawic/data/contacts/contacts.md` and the engagement in `~/Clawic/data/projects/<project>.md`. Both are shared with every skill that knows people and work, and the user may have none of those installed, so the format and the protocol travel with this skill. Never duplicate the person or the project inside an iOS file — here they appear as a name in the app's `Notes` only.

```markdown
# Contacts

| Name | Key | Role | Preferred channel | Context | Last contact | File |
|------|-----|------|-------------------|---------|--------------|------|
| Marta Ruiz | marta@acme.example | client — Acme | email | commissions the Acme app, approves submissions | 2026-07-22 | |
| Dan Okafor | dan-okafor-acme | client PM — Acme | Slack | owns the release calendar on their side | 2026-07-24 | dan-okafor.md |
```

- **Identity is `Key`**, and it is a column of the row, never implicit: lowercase email → handle → `<kebab-name>` plus a stable disambiguator. Read the file and match on `Key` before adding; if the person is there, update the row in place — only absence justifies a new row. `Preferred channel` is the kind of channel, not the address, so it never serves as the key.
- **Foreign columns win.** If `contacts.md` already exists with a different column set (a CRM or people skill may have written `Company`, `Tags`, `Owner`), match its columns and put anything missing in its freest text column. Never rewrite its header and never start a second table below it.
- **Scale cut**: one row per person while there are ≤15, or until someone stops fitting in a row. Past that, one `~/Clawic/data/contacts/<name>.md` per person with the same fields, and `contacts.md` becomes the index, with the `File` column carrying the pointer. If you arrive and the folder already looks like that, follow it — never start a parallel `contacts.md`.
- **Retirement**: an ended engagement never deletes a person. Set `Context` to `former client — <date>` and leave the row; the ending belongs in the project file. Delete a row only if this skill wrote it and it was wrong — a duplicate, a mistyped key — and note the date in `## Platform Facts`. Never touch a row this skill did not write.
- **An address is working data; a login is not.** Email and handle belong in the row; a client portal password, an App Store Connect invitation or a demo account goes in as a pointer (`1password:Work/Acme/portal`).
- **Projects**: one file per engagement from the first, holding goal, status, milestones, and the one-line summary of any decision whose full artifact lives in `~/Clawic/data/ios/artifacts/`. A finished engagement gets `status: done — <date>` inside its file; the file is never deleted, because it is the record of what shipped.

## artifacts/

One file per thing, at `~/Clawic/data/ios/artifacts/<kebab-name>.md`, created the first time it exists. Canonical types here: **an entitlements + Info.plist set that passes review**, **App Review notes and demo instructions**, **a runbook for a failure that recurred**, **a persistence or monetization decision**, **a launch-time teardown**, **a release checklist**. Every artifact opens with when to read it, and gets its `## Boxes` line in the same turn. Every secret inside is already a pointer.

```markdown
# Entitlements + Info.plist — Acme
*Read before adding any capability or purpose string. Passing review as of 2026-07-26.*

Why it is shaped this way: the App Group is on app, widget and notification-service targets because
all three read the shared snapshot; associated domains lists both the apex and www because the
marketing site redirects; the location string names the feature, which is what cleared the 5.1.1 note.

...the keys, with every secret replaced by its pointer...
```

```markdown
# Review notes — Acme
*Read before every submission. Updated 2026-07-26.*

Demo account: demo@acme.example / <1password:Work/Acme/review-demo>
What the reviewer needs to reach the paid feature, in four steps, plus the note that explains
why the app asks for location. Two rejections came from a reviewer who never found the feature.
```

```markdown
# Decision — SwiftData, not Core Data, for the notes store
*Read before any change to persistence or a migration. 2026-07-26.*

Decision: ...one sentence...
Rejected: Core Data — the migration control it buys is not worth the model boilerplate at this size.
Cost: heavy predicates are hand-tuned; the store is capped at ~50k rows before this is revisited.
Revisit when: the store passes 50k rows, or a lightweight migration fails once.
```

If the user tracks the app as a project, the one-line decision summary also belongs in the shared `~/Clawic/data/projects/<project>.md`, with the full artifact staying here and referenced by name.

## releases/

The record that makes the next release safe (SKILL.md Rule 9). Append-only, one file per year, never rewritten.

```markdown
# Releases — 2026

| Date | App | Version | Build | Min iOS | Submitted | Outcome | Rollout | Crash-free at 7d |
|------|-----|---------|-------|---------|-----------|---------|---------|------------------|
| 2026-05-02 | Acme | 3.1.0 | 401 | 17.0 | 2026-05-02 | rejected 3.1.1, approved 2026-05-04 | phased, completed | 99.6% |
| 2026-07-24 | Acme | 3.2.0 | 412 | 17.0 | 2026-07-23 | approved in 14 h | phased, paused at day 2 | 99.1% |

## Notes
2026-07-24: paused the phased release at 20% — crash-free dropped below the 99.5% gate; fixed in 413.
```

- The build number is the point of the row: it is the only durable link between a crash report, a dSYM and a version the user can reason about.
- `Outcome` records rejections too. A release log that only records approvals cannot answer "how often does this app get rejected, and for what".
- A paused or halted phased release is recorded the day it happens, with the number that triggered it.

## Split-out files

Created only by the split procedure above, never on day one. Each keeps the exact headings it had inside `memory.md`.

`apps.md` — `## Apps`, one `## <app>` heading per app once there is more than one, with its extension targets underneath. This is the file that answers "what are the identifiers" without opening Xcode or the developer portal.

`baselines.md` — `## Baselines`, plus `## Budgets` (the launch, size and crash-free numbers the team holds itself to). The budgets are why the file exists: a measurement with nothing to compare it against is a number, not a signal.

`sdks.md` — `## SDKs`, one `## <app>` heading per app when more than one exists. This is the file that answers "what is inside this binary" at submission time and when a customer asks.

`rejections.md` — `## Rejections`, grouped by guideline once the same one appears twice. A guideline that appears twice is a class of problem, and it earns a line in the release checklist artifact.
