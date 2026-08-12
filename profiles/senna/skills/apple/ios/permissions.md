# Permissions — One Prompt, One Chance

The purpose-string table lives in SKILL.md (Permission Map). This is the flow around it: when to ask, what needs no permission at all, and what to do after a denial.

**Before designing a permission flow**, read `## Apps` and `## Platform Facts` in `~/Clawic/data/ios/memory.md` — a reviewer's past objection to a purpose string, or a measured grant rate, decides the design more than any principle here.

**Contents:** [The Ask Sequence](#the-ask-sequence) · [What Needs No Permission](#what-needs-no-permission) · [Partial Grants](#partial-grants) · [After a Denial](#after-a-denial) · [Purpose Strings That Pass Review](#purpose-strings-that-pass-review) · [Testing](#testing) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## The Ask Sequence

Four steps, in this order, for every permission:

1. **Reach the moment.** The user taps the button whose feature needs the capability. Never during onboarding, never at launch.
2. **Prime in your own UI.** One screen, one sentence about what the app does with it, and two buttons: continue, and a way to proceed without it. This screen costs nothing if the user declines — the system prompt is still unspent.
3. **Trigger the system prompt** from the continue action. The prompt only appears the first time; every later call returns the stored answer silently.
4. **Handle the answer both ways in the same commit.** The denied path is a feature, not an error state, and review checks it.

Never fire two system prompts in a row. The second is answered reflexively — that is how notification permission gets denied by a user who was dismissing the location alert.

Prompts fire from the framework call, not from a permission API: reading `CLLocationManager.authorizationStatus` does not prompt, `requestWhenInUseAuthorization()` does. Know which call is the trigger before wiring a button to it.

## What Needs No Permission

The most valuable distinction in this whole area, because half of all permission requests are unnecessary. These run out of process and hand back only what the user picked:

| Instead of asking for | Use | What the app sees |
|---|---|---|
| Photo library access | `PHPickerViewController` | Only the images the user selected, no prompt at all |
| Camera roll write for a one-off save | Share sheet, or ask only when saving is the feature | — |
| Contacts | `CNContactPickerViewController` | Only the contact the user tapped |
| Files access | `UIDocumentPickerViewController` | Only the chosen file, in a security-scoped URL |
| Location for a one-time address | A map/place picker, or let the user type it | The place, not a stream |
| Notifications, on day one | Provisional authorization (`.provisional`) | Delivered quietly to Notification Center; the prompt is earned later, when the user taps one (`notifications.md`) |

An app that ships pickers instead of prompts has no permission funnel to optimize, and one fewer purpose string a reviewer can object to.

## Partial Grants

Modern iOS grants sideways, not just yes/no. Code that treats the status as boolean breaks on the middle case:

- **Photos — limited access.** The user picks specific photos; your fetches return that subset with no error and no indication that anything is missing. Handle `.limited` explicitly, and offer the "select more photos" flow rather than pretending the library is empty.
- **Location — reduced accuracy.** The user can grant "approximate" (kilometers, not meters). Ask for temporary full accuracy with `requestTemporaryFullAccuracyAuthorization(withPurposeKey:)` and a matching `NSLocationTemporaryUsageDescriptionDictionary` entry, at the moment precision is needed.
- **Location — when-in-use, then always.** Ask for when-in-use first. The escalation to Always is a second prompt, and the system re-asks the user afterwards; a user who never sees a reason downgrades it silently.
- **Contacts and Calendar — write-only or limited variants.** Newer OSes offer narrower grants that users accept far more readily. Prefer the narrow one; ask for full access only when the feature genuinely reads everything.
- **Notifications — provisional.** Quiet delivery with no prompt, upgraded when the user chooses to keep them.

## After a Denial

- The system prompt cannot be shown again. The only recovery path is `UIApplication.shared.open(URL(string: UIApplication.openSettingsURLString)!)`, which opens *your* app's Settings page.
- Show that path only in response to the user trying the feature again — a banner nagging about a denied permission is a support ticket and, for tracking, a guideline problem.
- Detect the change on return: authorization can flip while the app is backgrounded, so re-read status on `active`, never cache it for the session.
- Some statuses are not the user's decision: `.restricted` means parental controls or an MDM profile, and no amount of UI will change it. Say so plainly instead of routing to Settings.

## Purpose Strings That Pass Review

- Name the feature and the benefit: "Acme uses your location to show delivery time from the nearest store." Not "This app needs location."
- The string must match what the app actually does. A camera string that mentions scanning documents, in an app with no scanner, is a 5.1.1 rejection with the string quoted back.
- Localize every purpose string. An untranslated string shows the English one in a Spanish system prompt — reviewers in that locale notice.
- A missing string is not a denial: the app **crashes** on first access to the API. That is why the crash message names the exact key (`crashes.md`).
- Adding an SDK can add a permission requirement you never wrote. Check the SDK's own Info.plist requirements at integration time, together with its privacy manifest (`privacy.md`).

## Testing

- Reset a simulator's grants for one app rather than reinstalling: `xcrun simctl privacy booted reset all com.acme.app` (also `grant`/`revoke` per service — `commands.md`).
- On a device, Settings → General → Transfer or Reset → Reset → Reset Location & Privacy resets every app's prompts. Deleting the app resets its own, but not the keychain (`data.md`).
- Run the whole app once with every permission denied. This is the state review tests, and it is the state most apps have never seen.
- The simulator has no camera and no real location; a camera feature "works" there by doing nothing. Verify on hardware (`devices.md`).

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| App crashes instantly on first camera/mic/photo use | Missing purpose string | The console names the key; add it to the target's Info.plist, not the workspace's |
| Prompt never appears, feature just fails | Already answered on a previous install run, or `.restricted` | Read the status; reset privacy to re-test |
| Photos returns an empty library | `.limited` grant with nothing selected | Handle `.limited` and offer the picker |
| Location returns city-level coordinates | Reduced accuracy granted | Request temporary full accuracy with a purpose key |
| Always-location silently becomes when-in-use | The system re-asked the user in the background | Design for when-in-use; treat Always as a bonus |
| ATT prompt never shows | Asked before the app was active, or the device-level toggle is off | ATT requires the app to be foreground-active; check `tracking_policy` first (`privacy.md`) |
| Local network discovery finds nothing | Missing `NSLocalNetworkUsageDescription` or Bonjour service list | Both are required, and failure is silent |

## Write It Down

- **The permission flow the app settled on** — which prompts, in what order, primed by which screen, with which fallback — is `artifacts/permission-flow-<app>.md`, with its `## Boxes` line in the same turn (`memory-template.md`). It is re-litigated at every feature that touches a capability.
- **A reviewer's objection to a purpose string, and the wording that passed**, is a `## Rejections` row (guideline 5.1.1) plus one line in `## Platform Facts` — the wording is the reusable part.
- **An observed grant behavior** (this user's device denies tracking system-wide; limited photos is the common case in this audience) goes in `## Platform Facts`, one line.
