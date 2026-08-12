# Widgets and Live Activities

**Before changing a widget's data path**, read `## Apps` in `~/Clawic/data/ios/memory.md` for the App Group and the widget's own target row, and `## Platform Facts` for what this app has already learned about reload behavior.

**Contents:** [The Model](#the-model) · [Timelines and the Reload Budget](#timelines-and-the-reload-budget) · [Feeding the Widget](#feeding-the-widget) · [Memory](#memory) · [Interactivity](#interactivity) · [Live Activities](#live-activities) · [Placement and Redaction](#placement-and-redaction) · [Testing](#testing) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## The Model

A widget is not a small app. It is an extension that is asked, occasionally, to produce a **timeline**: a list of dated entries plus a policy for when to ask again. Between those moments nothing of yours is running.

Three callbacks: `placeholder` (instant, no data, used for redacted previews), `snapshot` (single entry, must return fast — the widget gallery calls it), and `timeline` (the real one). All three run in the extension process, under its memory ceiling, with seconds to work.

## Timelines and the Reload Budget

- Apple's documented budget is on the order of **40-70 refreshes per day** for a widget the user actually looks at, distributed by the system. A widget that "stopped updating" has usually spent its budget by reloading on every app event.
- Return **several future entries** in one timeline instead of asking to be woken every few minutes. A countdown, a schedule, or anything time-derived should be computed as entries, not fetched repeatedly.
- Reload policies: `.after(date)` (ask again then), `.atEnd` (after the last entry), `.never` (only when the app says so). Choose deliberately; `.atEnd` on a one-entry timeline is a request per refresh.
- `WidgetCenter.shared.reloadTimelines(ofKind:)` from the app is a request, not a command, and it draws from the same budget. Call it when the data actually changed, never on every foreground.
- A push can drive an update: the app receives it and reloads the timeline. The widget itself has no push token except for Live Activities.
- Network calls inside `getTimeline` are allowed and are the usual reason a widget is slow, expensive and blank. Prefer reading a snapshot the app already wrote.

## Feeding the Widget

- The app writes a small, purpose-built snapshot into the App Group container; the widget reads it and renders. This is the design that survives contact with the memory ceiling, the locking rules, and the budget.
- Both targets need the App Group entitlement. An App Group on the app alone is the single most common cause of a permanently empty widget (`capabilities.md`).
- Do not open the app's live Core Data or SQLite store from the widget: a handle held in a shared container across suspension is `0xdead10cc`, and the fetch itself can exceed the extension's memory.
- Cache images as already-downsampled files in the group container. The widget should never decode a full-resolution photo.

## Memory

Widget extensions are killed at a small fraction of the app's footprint — Apple does not publish the number, so the working rule is: keep peak usage in the low tens of megabytes and measure with the memory graph on the floor device. A widget that exceeds it does not crash visibly; it renders the placeholder, or nothing, which is why "the widget is blank" is nearly always a memory or entitlement problem rather than a layout one.

Consequences for the code: downsample images with ImageIO before they reach the widget, keep the snapshot file small and flat, avoid pulling in heavy SDKs through a shared framework, and never do the app's JSON parsing here.

## Interactivity

- Buttons and toggles inside a widget run **App Intents** in the extension process with a short budget. They are for one small mutation — toggling a task, starting a timer — and they must complete quickly and reload the timeline.
- An intent that needs the app open must say so; there is no way to run app code from a widget.
- Everything else is a link: `widgetURL(_:)` for the whole widget, `Link` for individual regions. The URL routes through the app's normal deep-link handling (`deep-links.md`).

## Live Activities

- Started from the app while it is in the foreground, with ActivityKit. They cannot be started from a push or from the background.
- **Duration ceilings: active for up to 8 hours, removed from the Lock Screen by 12 hours.** Anything longer is a notification, not an activity. Set `staleDate` so a stalled activity renders as stale rather than as wrong.
- Updates arrive by app code or by push with `apns-push-type: liveactivity` and the per-activity push token, which is separate from the device token (`notifications.md`).
- Every Dynamic Island presentation must be supplied: compact leading, compact trailing, minimal, and expanded. A missing minimal layout is what makes an activity look broken when a second app is also active.
- Content is limited in size and the update rate is budgeted like everything else here. Frequent updates need the frequent-updates Info.plist flag, and still get throttled.
- End the activity explicitly with a dismissal policy when the underlying event finishes. Activities left running are the most visible possible bug — they sit on the Lock Screen.

## Placement and Redaction

- The same widget code renders on the Home Screen, the Lock Screen (accessory families), StandBy and, on newer systems, in Control Center as a control widget. Each family needs a design, not a resize.
- On the Lock Screen, sensitive values are redacted by the system in some states; mark anything private with the privacy-sensitive modifier rather than assuming the Lock Screen is private.
- Widgets have no scrolling, no video, no continuous animation, and limited transitions. A design that needs any of those is an app screen.

## Testing

- Run the widget scheme with the containing app selected as the host; breakpoints work, but the reload budget does not apply in the debugger, which is exactly why widgets behave differently once installed.
- Verify the empty and error states: a widget's first render on a fresh install has no snapshot file.
- Force refresh from the app during development, then remove those calls before shipping — leftover debug reloads are a budget leak.
- The gallery preview uses `snapshot`; if it is slow or hits the network, adding the widget feels broken.

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| Widget permanently blank or placeholder | App Group missing on the widget target, or the extension is being killed on memory | Both, in that order |
| Updates stop after a while | Reload budget spent | Fewer reloads, more future entries |
| Data lags the app by hours | The app never writes the snapshot, or never requests a reload after writing it | Write then reload, in the same operation |
| Crash with no crash log after adding images | Extension memory ceiling | Downsample before writing to the group container |
| Live Activity frozen with old data | Push updates not arriving, or no `staleDate` set | Per-activity token and stale rendering |
| Live Activity never appears | Started from the background | Start it while the app is foreground |
| Tap opens the app at the root | The widget URL is not routed | `deep-links.md` |
| Works in Xcode, not once installed | Debugger exempts you from the budget | Test installed, over a day |

## Write It Down

- **The widget's data contract** — which snapshot file, written when, read how, and what the reload triggers are — is `artifacts/widget-data-<app>.md`, with its `## Boxes` line in the same turn (`memory-template.md`). It is the file that prevents the next feature from wiring the widget straight to the database.
- **Every widget or Live Activity target** gets its own row in `## Apps`, with its App Group in the `Capabilities` column. That row is the answer to half of all widget bugs.
- **Observed reload behavior** — how often this widget actually refreshes on a real device, what exhausted the budget — is a `## Platform Facts` line. It takes a day to observe and a second to record.
