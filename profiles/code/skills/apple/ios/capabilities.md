# Capabilities and Entitlements — What the App Is Allowed to Be

**Before adding any capability**, read `## Apps` in `~/Clawic/data/ios/memory.md` — the `Capabilities` column records what is actually enabled per target — and open `artifacts/entitlements-*.md` if `## Boxes` names one for this app.

**Contents:** [The Triangle](#the-triangle) · [The Capability Catalogue](#the-capability-catalogue) · [App Groups](#app-groups) · [Keychain Sharing](#keychain-sharing) · [Associated Domains](#associated-domains) · [Sign in with Apple](#sign-in-with-apple) · [iCloud and CloudKit](#icloud-and-cloudkit) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## The Triangle

A capability exists in three places, and it works only when all three agree (SKILL.md Rule 3):

1. **The App ID** in the developer portal — the capability switched on for that identifier.
2. **The entitlements file** of the target that uses it — and every extension is a separate target with its own file.
3. **A provisioning profile regenerated after both.** Automatic signing does this for you; manual signing does not, which is why the same project builds on one machine and fails on CI (`xcode` owns the signing side).

A build with the entitlement missing from the profile installs happily and fails at the first call, typically with a "missing entitlement" error or a silent no-op. When something that should work does nothing at all, dump the entitlements from the built binary rather than reading the project settings (`commands.md`) — the binary is the only honest source.

## The Capability Catalogue

| Capability | Entitlement / key | The part that trips people |
|---|---|---|
| Push Notifications | `aps-environment` | Value is `development` or `production` and decides which APNs host accepts your token (`notifications.md`) |
| App Groups | `com.apple.security.application-groups` | Must be on **every** target that reads the container, id must start with `group.` |
| Keychain Sharing | `keychain-access-groups` | The first group in the list is the default for writes — order matters |
| Associated Domains | `com.apple.developer.associated-domains` | `applinks:`, `webcredentials:`, `appclips:` are separate prefixes for the same domain |
| Background Modes | `UIBackgroundModes` (Info.plist, not entitlements) | Declaring a mode the app does not use is a review rejection (`background.md`) |
| In-App Purchase | portal capability, no entitlement file entry | Enabled on the App ID; the paid-apps agreement is what actually blocks sales (`storekit.md`) |
| Sign in with Apple | `com.apple.developer.applesignin` | Required by guideline 4.8 once another social login exists |
| HealthKit / HomeKit | `com.apple.developer.healthkit`, `homekit` | Entitlement **and** purpose strings; HealthKit apps cannot run on iPad-only configurations historically — verify the current device support before promising it |
| Time-Sensitive Notifications | `com.apple.developer.usernotifications.time-sensitive` | Without it, `interruption-level: time-sensitive` is downgraded silently |
| Communication Notifications | `com.apple.developer.usernotifications.communication` | What makes a message notification show an avatar and respect Focus |
| App Attest / DeviceCheck | `com.apple.developer.devicecheck.appattest-environment` | Attestation fails on the simulator by design — test on hardware |
| Network Extensions, Family Controls, NFC, Wallet | various | Several require an approval request to Apple that takes days — start before the sprint, not during it |
| Increased Memory Limit | `com.apple.developer.kernel.increased-memory-limit` | Raises the jetsam ceiling on supported devices; it is a request, not a guarantee, and never a substitute for fixing footprint (`performance.md`) |

## App Groups

The only shared surface between an app and its extensions. Everything a widget, share sheet or notification service extension sees, it sees through here.

```swift
let url = FileManager.default.containerURL(
    forSecurityApplicationGroupIdentifier: "group.com.acme.shared")
let defaults = UserDefaults(suiteName: "group.com.acme.shared")
```

- **Add the group to every target.** The single most common iOS data bug is a widget reading an empty container because the App Group was enabled on the app only. It fails silently: `containerURL` returns nil, `UserDefaults(suiteName:)` returns a store that works and persists nothing shared.
- **Never hold a file lock or an open SQLite/Core Data handle in the shared container across suspension.** That is `0xdead10cc`, and it reads as a random crash. Close on the way to background (`lifecycle.md`).
- Coordinate concurrent access with `NSFileCoordinator`/`NSFilePresenter` — the app and an extension genuinely run at the same time.
- Prefer writing a small, purpose-built snapshot for the extension over sharing the app's live database. It removes the locking problem and the extension's memory ceiling problem in one move (`widgets.md`).
- Group containers are backed up. Exclude regenerable caches with `isExcludedFromBackup` (`data.md`).

## Keychain Sharing

- The access group is `$(AppIdentifierPrefix)com.acme.shared`; the prefix is the Team ID, and hardcoding it breaks when the app changes teams.
- Sharing works only within one team. Two apps of different teams cannot share keychain items, whatever the group string says.
- Items written without an explicit `kSecAttrAccessGroup` land in the **first** group listed in the entitlement. Reordering that list silently orphans existing items.
- Keychain contents survive app deletion (`data.md`), which is a feature for credentials and a trap for debugging.

## Associated Domains

- Entitlement value per domain and per service: `applinks:acme.com`, `webcredentials:acme.com`, `appclips:acme.com`. Subdomains are not implied — list each one, or use a wildcard entry where the service supports it.
- `webcredentials` is what lets Password AutoFill and passkeys associate your app with the site. Adding it costs nothing and removes an entire class of login friction.
- The domain side of the contract (the AASA file, its caching, and why a link opens Safari) is in `deep-links.md`.

## Sign in with Apple

- Guideline 4.8: if the app offers a third-party or social login, it must also offer an equivalent option that limits data to name and email, allows hiding the email, and does not track. Sign in with Apple satisfies it; so do other services that meet the same criteria.
- The user identifier is stable **per team**, not per app: two apps of the same team see the same id, and moving an app to another team invalidates every account mapping.
- Email relay addresses forward until the user disables them; your transactional mail must come from a domain registered with Apple for relaying, or it bounces silently.
- Call `getCredentialState(forUserID:)` at launch. A revoked credential must sign the user out — leaving them signed in is both a bug and a review finding.

## iCloud and CloudKit

- Three separate services under one capability: CloudKit (records), iCloud Documents (files), and key-value store. Enabling the capability does not enable the container the code uses; check the container id in the entitlement.
- **CloudKit has a development and a production schema, and the production one is deployed manually.** Shipping an app whose records use a field that was never deployed is the classic first CloudKit outage. Deploy the schema before the build goes to review, and never rely on the automatic schema creation that only exists in development.
- `NSUbiquitousKeyValueStore` is capped at 1 MB total and 1,024 keys — a preferences sync, not a database.
- The production container serves TestFlight builds. A TestFlight tester writing bad records writes them into production.

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| Feature does nothing, no error | Entitlement missing from the profile the build was signed with | Dump entitlements from the binary (`commands.md`) |
| Widget shows placeholder data forever | App Group not on the widget target | Add it to every target, then rebuild both |
| `containerURL(...)` returns nil | Same cause, or a typo in the group id | The id must match the entitlement exactly, `group.` prefix included |
| Random crash after backgrounding | Shared-container handle held across suspension (`0xdead10cc`) | Close handles at `didEnterBackground` |
| Keychain item disappears after an update | Access-group order changed, or the item was written with a device-only accessibility class | `data.md` |
| CloudKit works in debug, fails in TestFlight | Schema not deployed to production | Deploy from the CloudKit dashboard, then verify with a production build |
| Time-sensitive notifications behave as normal ones | Entitlement missing | It is a separate capability, not part of push |
| Signing fails only on CI | Manual profile not regenerated after the capability change | Regenerate, commit the profile the CI uses (`xcode`) |

## Write It Down

- **Every capability change** — which capability, on which targets, with which identifiers (App Group, iCloud container, keychain group) — updates the `Capabilities` column of that app's row in `## Apps` (`memory-template.md`). This is the table that answers "why does the extension not see this".
- **The entitlements and Info.plist set that finally passed review** is `artifacts/entitlements-<app>.md`, with the reason each entry exists and its `## Boxes` line in the same turn. Capabilities get copied to the next app; the reasons do not survive in memory.
- **A capability that required an Apple approval request** goes in `## Platform Facts` with the date it was granted — the lead time is the planning input next time.
