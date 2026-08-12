# App Extensions — Separate Processes With Their Own Rules

Widgets and Live Activities have their own file (`widgets.md`); this covers every other extension point and what they all share.

**Before adding an extension target**, read `## Apps` in `~/Clawic/data/ios/memory.md` — extension targets get their own rows, and their `Capabilities` column is where App Group and entitlement mismatches become visible.

**Contents:** [What Every Extension Shares](#what-every-extension-shares) · [The Catalogue](#the-catalogue) · [Talking to the Containing App](#talking-to-the-containing-app) · [Share and Action Extensions](#share-and-action-extensions) · [Keyboards](#keyboards) · [App Intents and Shortcuts](#app-intents-and-shortcuts) · [Credential Provider and AutoFill](#credential-provider-and-autofill) · [Call Directory and Message Filter](#call-directory-and-message-filter) · [Debugging](#debugging) · [Write It Down](#write-it-down)

## What Every Extension Shares

- **A separate process, a separate target, a separate Info.plist and a separate entitlements file.** Nothing is inherited from the app. An App Group, a keychain group or a push capability added to the app alone does not exist here (`capabilities.md`).
- **A memory ceiling far below the app's**, undocumented and different per extension point. The rule is to keep peak footprint small and measure; if an extension "crashes with no crash log", assume memory first.
- **A short, host-controlled lifetime.** The host app can dismiss the extension at any moment. Work that must finish moves to a background `URLSession` owned by the shared container, not to a longer spinner (`background.md`).
- **No `UIApplication.shared`.** The API is unavailable in extensions, which rules out opening URLs, reading application state, or taking background task assertions the app way.
- **Its own bundle id, under the app's**: `com.acme.app.share`. Its own version and build numbers must match the app's at submission or the upload is rejected (`releases.md`).
- Shared code goes in a framework or a local package used by both. Duplicated code between app and extension drifts in exactly the places that matter.

## The Catalogue

| Extension | What it does | The part that trips people |
|---|---|---|
| Share | Receives content from the share sheet | The activation rule decides where it appears; a permissive rule shows it everywhere and reads as spam |
| Action | Transforms content in place | Rarely the right choice today; App Intents cover most of it |
| Notification service | Mutates a push before display | Needs `mutable-content: 1`, must call the handler, ~30 s (`notifications.md`) |
| Notification content | Custom UI for a delivered notification | Cannot present alerts or do meaningful networking |
| Keyboard | System-wide input | Must work with no network and no full access |
| Safari web extension | Content and background scripts in Safari | Ships inside the app; permissions are requested per site |
| File provider | Exposes a cloud filesystem in Files | The heaviest extension to build; enumeration and working-set semantics dominate |
| Photo editing | Round-trips an edit in Photos | Must handle adjustment data so the edit is reversible |
| Credential provider | Passwords and passkeys in AutoFill | Needs associated domains `webcredentials` |
| Call directory | Blocks and labels numbers | Entries must be supplied in ascending numeric order or the extension fails to load |
| Message filter | Classifies unknown-sender SMS | No network access unless the deferred-query entitlement is used |
| Intents / App Intents | Siri, Shortcuts, Spotlight, Action button, interactive widgets | Modern work goes to App Intents, not the legacy SiriKit intents |
| iMessage / stickers | Content inside Messages | A separate app target in practice, with its own review surface |
| Audio Unit | Plugins for audio hosts | Real-time thread rules: no allocation, no locks, no logging |

## Talking to the Containing App

- **Shared data**: the App Group container, ideally a small purpose-built file the app writes and the extension reads (`data.md`).
- **Shared credentials**: keychain access group, same team only.
- **Opening the app**: `NSExtensionContext.open(_:completionHandler:)` where the extension point supports it; otherwise a URL the host opens on your behalf. Reaching for `UIApplication.shared` through the responder chain is a workaround that has broken repeatedly across OS versions.
- **Handing back a result**: `extensionContext?.completeRequest(returningItems:)`, once. Calling it twice, or never, hangs or crashes the host.
- **Notifying the app**: there is no reliable IPC. Write to the group container, and have the app reconcile on next foreground. Darwin notifications exist but do not wake a suspended app.

## Share and Action Extensions

- `NSExtensionActivationRule` is a predicate over the item types the sheet is offering. Write a real rule — the maximum-counts form (`NSExtensionActivationSupportsWebURLWithMaxCount` and friends) covers most cases; `TRUEPREDICATE` makes the extension appear for everything, which reviewers and users both punish.
- Input arrives as `NSItemProvider` attachments. Load by **type identifier**, and expect the type you did not plan for: a "URL" share from one app is a URL, from another a plain string, from a third a web page with a title.
- Large media (a video share) is where the memory ceiling bites. Copy the file into the group container by URL rather than loading `Data`, and let the app process it later.
- The extension's UI is presented over another app: it must be usable in a sheet, at Dynamic Type sizes, with no assumption about orientation (`layout.md`).

## Keyboards

- Without **full access** (`RequestsOpenAccess`), a keyboard has no network, no shared container, and no keychain. Design the core experience for that state — most users never grant it.
- With full access, the app is handling everything the user types. The privacy label, the privacy manifest and the review notes all have to say exactly what is done with it (`privacy.md`).
- Keyboards must implement the next-keyboard switch, and must not become the only way to reach app functionality.

## App Intents and Shortcuts

- One intent definition powers Siri, the Shortcuts app, Spotlight, the Action button and interactive widgets. Model the *action* and its *entities*, not the UI.
- `AppShortcutsProvider` phrases must include the app name in every phrase, and phrase variations are the difference between "it never works with Siri" and it working.
- Intents run in your extension or app process with a short budget. Long work returns a result and continues elsewhere.
- Entity queries back Spotlight results and parameter pickers; a slow query makes the whole system UI feel slow, and it is measured against the same hang thresholds (`performance.md`).

## Credential Provider and AutoFill

- Requires the `webcredentials` associated domain for the sites the app fills, and the domain association must be live before AutoFill offers anything (`deep-links.md`).
- Passkey support is a distinct provider protocol from passwords; supporting one does not imply the other.
- The extension runs on the Lock Screen in some flows. Nothing here can assume the app has been launched since boot, which makes the keychain accessibility class decisive (`data.md`).

## Call Directory and Message Filter

- Call directory data is loaded in bulk and **must be sorted ascending by number**; an unsorted array fails silently and the extension appears not to work.
- Reloading is requested from the app (`CXCallDirectoryManager`), and errors are reported asynchronously — surface them, or the user sees stale blocking rules with no explanation.
- Message filters see the sender and the message for classification and, by default, have no network. The deferred-query entitlement adds a network round trip with strict rules about what may be sent.

## Debugging

- Run the extension's own scheme and pick the host app; Xcode attaches to the extension process. Breakpoints in the app target will not fire — it is a different process.
- Console logs from an extension appear under the extension's own process name, not the app's (`commands.md`).
- The simulator is adequate for UI and plumbing here, but memory ceilings and host behavior are only real on hardware (`devices.md`).
- Version and build mismatch between app and extension is caught at upload, hours after you thought you were done. Automate it in the release step (`releases.md`).

## Write It Down

- **Every extension target gets a row in `## Apps`** — bundle id, extension point, App Group, entitlements — in `~/Clawic/data/ios/memory.md` (`memory-template.md`). The row is what explains why a capability change did not take effect.
- **A working `NSExtension` configuration** (activation rule, type identifiers handled, memory-safe file handling) is `artifacts/extension-<point>-<app>.md`, with its `## Boxes` line in the same turn. Activation rules are copied between projects and never re-derived.
- **An extension killed for memory, or a host behavior that surprised you**, is a `## Pain Points` line; the second occurrence earns a runbook.
