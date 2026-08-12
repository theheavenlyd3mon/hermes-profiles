# Data — Where It Goes, How It Is Protected, How It Migrates

**Before choosing a store or changing a model**, read `## Apps` in `~/Clawic/data/ios/memory.md` and open `artifacts/` entries the `## Boxes` index names for persistence — the previous decision, and what it rejected, is the input to this one.

**Contents:** [Choosing the Store](#choosing-the-store) · [Directories and Backup](#directories-and-backup) · [Data Protection Classes](#data-protection-classes) · [Keychain](#keychain) · [Core Data and SwiftData](#core-data-and-swiftdata) · [Migrations](#migrations) · [Sharing With Extensions](#sharing-with-extensions) · [Encryption Compliance](#encryption-compliance) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## Choosing the Store

| Need | Store | Escape hatch |
|---|---|---|
| A handful of user preferences | `UserDefaults` | Past a few dozen keys or any structured data, use a real store |
| Anything that authenticates or identifies | Keychain | Never UserDefaults, never a file, never a plist |
| Documents the user created and owns | Files in `Documents/` | Nothing — this is what that directory is for |
| Structured app data, queries, relationships | SwiftData, Core Data, or SQLite/GRDB | Below ~100 rows of flat data, a Codable file is simpler and faster |
| Regenerable derived data, thumbnails, downloads | `Library/Caches/` | If losing it breaks the app, it was not a cache |
| Preferences synced across the user's devices | `NSUbiquitousKeyValueStore` (1 MB, 1,024 keys) | Larger or structured → CloudKit (`capabilities.md`) |
| Data shared with a widget or extension | A snapshot file in the App Group container | Never the app's live database (`widgets.md`) |
| Anything else | A file in `Application Support/`, named after what it holds | — |

`UserDefaults` is a plist in the container: it is readable in an unencrypted backup, it is not encrypted at rest beyond the file's protection class, and it is loaded whole into memory. It is a preferences store, and treating it as a cache or a token vault is the most common data mistake in the platform.

## Directories and Backup

| Directory | Backed up | Purged by the system | Use for |
|---|---|---|---|
| `Documents/` | Yes | No | User-visible, user-created content only |
| `Library/Application Support/` | Yes | No | App data the user does not browse: databases, models |
| `Library/Caches/` | No | Yes, under disk pressure | Anything re-downloadable |
| `tmp/` | No | Yes, aggressively | Work in progress within a single operation |

- Large re-downloadable files in `Documents/` bloat the user's iCloud backup, and Apple's data-storage guidance makes it a review issue. Move them, or set `isExcludedFromBackup` on the URL.
- A file in `Caches/` can vanish between launches, including mid-session. Code that assumes it is still there is a crash on a full device.
- Enabling file sharing (`UIFileSharingEnabled`, `LSSupportsOpeningDocumentsInPlace`) exposes `Documents/` in the Files app. Anything in there becomes user-editable and user-deletable — including your database, if you put it in the wrong directory.

## Data Protection Classes

Files inherit `NSFileProtectionCompleteUntilFirstUserAuthentication` by default: readable after the first unlock following a boot, including while the device is locked afterwards.

| Class | Readable when | Choose it for |
|---|---|---|
| `Complete` | Device unlocked only | Sensitive documents, health, finance |
| `CompleteUnlessOpen` | Can be written while locked if opened while unlocked | Background downloads to a sensitive location |
| `CompleteUntilFirstUserAuthentication` (default) | After first unlock since boot | Almost everything, including databases background code touches |
| `None` | Always | Nothing that identifies a user |

The practical consequence: a background push handler running on a locked device can read a `CompleteUntilFirstUserAuthentication` database and **cannot** read a keychain token stored as `WhenUnlocked`. That mismatch produces uploads that fail only overnight (SKILL.md Rule 7, `background.md`).

## Keychain

- Accessibility classes mirror the file ones: `WhenUnlocked` (default), `AfterFirstUnlock`, `WhenPasscodeSetThisDeviceOnly`, and the `ThisDeviceOnly` variants that never leave the device in a backup or a device transfer.
- **Keychain items survive app deletion.** A reinstall sees the previous token, so "delete the app and try again" does not reset auth state. Either delete items explicitly on first launch after a fresh install (detected via a UserDefaults flag, which *is* cleared), or accept the behavior deliberately.
- `kSecAttrSynchronizable` puts the item in iCloud Keychain — convenient for credentials the user expects on every device, wrong for device-bound tokens.
- Sharing between your apps and extensions requires a keychain access group and one team (`capabilities.md`).
- The keychain is small-value storage. Encrypt a large blob with a key held in the keychain instead of storing the blob there.

## Core Data and SwiftData

- One `NSPersistentContainer`. The view context is main-thread only; every import or batch operation goes on a background context with `performBackgroundTask`. Touching a managed object from the wrong queue produces corruption that surfaces hours later — turn on the concurrency debug argument during development (`commands.md`).
- Set `automaticallyMergesChangesFromParent` on the view context, or the UI shows stale data after a background import and everyone blames SwiftUI.
- SQLite stores are three files: `.sqlite`, `.sqlite-wal`, `.sqlite-shm`. Copying, backing up or moving only the first one loses every uncommitted transaction — move all three, or checkpoint first.
- Batch operations (`NSBatchInsertRequest`, `NSBatchDeleteRequest`) bypass the context entirely: they are the only sane way to touch tens of thousands of rows, and they require merging the result IDs back manually.
- SwiftData is the smaller surface and the harder debug: predicate expressiveness, migration control and large-store performance still favour Core Data (SKILL.md, Where Experts Disagree). Both share the same store format, so the decision is reversible at a cost.

## Migrations

- **Lightweight migration** handles added attributes with defaults, new entities, and renames declared with a renaming identifier. It runs at store load, inside the launch budget.
- Anything else — splitting an entity, transforming values, merging stores — needs a mapping model or a staged custom migration, and it needs a progress UI: it can take tens of seconds on the oldest supported device with a real dataset.
- **Test the chain, not the step.** The App Store keeps serving the last compatible build to old devices, so a user can arrive from three versions back. Keep a fixture store from each shipped model version and run every path (`releases.md`).
- A migration that fails must not delete the store. Copy aside, migrate the copy, swap on success; the alternative is a support thread that starts "the update erased my data".
- Measure the migration on the floor device with a realistic store and record the number as a `## Baselines` row in `~/Clawic/data/ios/memory.md` — it is the input to whether the next model change is safe (`performance.md`).

## Sharing With Extensions

- The App Group container is the only shared filesystem. Write a **small purpose-built snapshot** for the extension rather than opening the app's database from it: it removes both the locking problem and the extension memory ceiling.
- Never hold an open SQLite or Core Data handle in a shared container across suspension — that is `0xdead10cc` (`capabilities.md`).
- Use `NSFileCoordinator` for anything both sides may touch. They genuinely run concurrently.
- `UserDefaults(suiteName:)` is fine for a few small values, and is the usual way a widget learns which account is signed in.

## Encryption Compliance

- Add `ITSAppUsesNonExemptEncryption` to Info.plist. Set to `NO` when the app only uses HTTPS and platform-provided cryptography — that skips the export-compliance question on every single upload.
- Setting it to `NO` when the app ships its own or non-exempt cryptography is a false declaration, not a shortcut. Custom crypto, proprietary protocols, or shipping an encryption library means the answer is `YES` plus the documentation Apple asks for.
- This is a legal declaration about the app, not a build setting to copy between projects without reading.

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| Token still present after deleting the app | Keychain survives deletion | Explicit delete on first run after a fresh install |
| Upload works when unlocked, fails overnight | Keychain `WhenUnlocked` vs a file the background code could read | Accessibility class of the credential |
| Data disappears at random | Stored in `Caches/` or `tmp/` | Move to `Application Support/` |
| UI shows stale data after an import | View context not merging parent changes | `automaticallyMergesChangesFromParent` |
| Corruption or "object accessed on wrong thread" crashes | Managed object crossed a queue | Concurrency debug argument, then pass IDs, not objects |
| Update wipes user content | Migration failure handled by recreating the store | Copy-migrate-swap, and never destroy on failure |
| Backup is enormous | Downloads in `Documents/` | `isExcludedFromBackup`, or move to `Caches/` |
| Widget shows nothing | Reading the app container instead of the group container | `capabilities.md` |

## Write It Down

- **The persistence decision** — which store, what was rejected, the size at which it should be revisited — is `artifacts/decision-persistence-<app>.md`, with its `## Boxes` line in the same turn (`memory-template.md`). It is re-argued every time the model changes, and the rejected option is the valuable half.
- **A measured migration duration** on a named device with a realistic store is a `## Baselines` row. Without it, "the migration is fast" is a claim about a developer's phone.
- **A data-loss incident or a near miss** is a `## Pain Points` line, immediately; the second occurrence earns a runbook in `artifacts/`.
