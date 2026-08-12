# Deep Links — Universal Links, Schemes, and Why It Opened Safari

**Before touching the AASA file**, read `## Platform Facts` in `~/Clawic/data/ios/memory.md`: whether this domain's file has been validated before, and how long propagation took last time, decides whether the next twenty minutes are useful or wasted.

**Contents:** [The AASA Contract](#the-aasa-contract) · [Path Matching](#path-matching) · [Receiving the Link](#receiving-the-link) · [Why It Opened Safari](#why-it-opened-safari) · [Diagnostics](#diagnostics) · [Custom URL Schemes](#custom-url-schemes) · [Links From Widgets, Notifications and Shortcuts](#links-from-widgets-notifications-and-shortcuts) · [Attribution After Install](#attribution-after-install) · [Write It Down](#write-it-down)

## The AASA Contract

Served at `https://<domain>/.well-known/apple-app-site-association`. Every one of these is a hard requirement:

- Valid HTTPS with a certificate that chains to a public root. No self-signed, no expired.
- `Content-Type: application/json`, **no `.json` extension** on the path.
- **No redirects.** A 301 to `www.` fails the fetch, and a redirect is the single most common cause of an AASA that "looks fine in the browser".
- Reachable with no authentication, no cookies, no geo-blocking, no bot filter. A WAF that challenges Apple's fetcher breaks universal links for everyone.
- The `appID` is `<TeamID>.<bundle id>`, and the domain must be listed in the app's Associated Domains entitlement as `applinks:<domain>` (`capabilities.md`).

Since iOS 14 the file is fetched **through Apple's CDN**, not from the device. Consequences: the file must be publicly reachable from the internet even for an intranet app, changes take hours to reach devices, and editing the file repeatedly during debugging tests nothing.

## Path Matching

```json
{ "applinks": { "details": [{
  "appIDs": ["ABCDE12345.com.acme.app"],
  "components": [
    { "/": "/orders/*", "comment": "order detail" },
    { "/": "/admin/*", "exclude": true, "comment": "stays in Safari" },
    { "/": "/search", "?": { "q": "?*" }, "comment": "only with a query" }
  ]}]}}
```

- Components are evaluated **in order**; the first match wins, so exclusions go above the wildcard that would otherwise catch them.
- `*` matches any characters including `/`; `?` matches a single character. Query and fragment matching use the `?` and `#` keys, not the path string.
- `caseSensitive: false` is worth setting explicitly — marketing links arrive capitalized.
- Keep the app's route table and the AASA components in one artifact, `~/Clawic/data/ios/artifacts/deep-links-<app>.md`. They drift, and the drift is invisible until a campaign link lands in Safari.

## Receiving the Link

- Universal links arrive as an `NSUserActivity` of type `NSUserActivityTypeBrowsingWeb`: `scene(_:continue:)` in UIKit, `onContinueUserActivity` or `onOpenURL` in SwiftUI.
- The link can arrive **during a cold launch**, before any UI exists. Buffer the destination, consume it when the root scene is active, and make every destination reachable from the root — deep links must not assume a navigation stack (`lifecycle.md`).
- Always ship a fallback: if the URL does not map to a screen (an old campaign link, a newer route from a newer build), open the closest parent screen, never a blank state.
- Universal links opened from inside your own app do not leave the app; handle them internally rather than round-tripping through the system.

## Why It Opened Safari

Ordered by how often it is the answer:

1. **The user chose Safari once.** Tapping "Open in Safari" from the smart banner, or the breadcrumb at the top right, makes that domain sticky in Safari. Recovery is a long-press → "Open in Acme", not a code change. This wastes more engineering hours than every other cause combined.
2. **The link was typed or pasted into the address bar.** Universal links never open the app that way, by design. Test by tapping a link in Notes or Messages.
3. **The link came from the same domain.** Navigating within `acme.com` in Safari does not bounce you into the app.
4. **The AASA has not been fetched yet** — the association is established at install and refreshed periodically; a just-installed app on a flaky network may not have it.
5. **The path does not match** any component, or matches an `exclude` rule.
6. **The link is a redirect**: the target of a `t.co` or a marketing redirector is checked, but some redirect chains break the association. Publish the final URL.
7. **It was opened inside another app's web view.** `SFSafariViewController` and `WKWebView` do not honor universal links to other apps.

## Diagnostics

- Check what Apple's CDN actually holds for the domain by fetching the CDN copy of the association file for that hostname — if the CDN has yesterday's file, the device has yesterday's file, and no amount of on-device debugging changes that.
- On device: Settings → Developer → **Associated Domains Development** lets a development build fetch the AASA directly from the server, bypassing the CDN. Pair it with the `?mode=developer` entitlement variant during development only.
- Watch the association subsystem in the device log while installing (`commands.md`); the failure reason (bad content type, redirect, unmatched appID) is printed there in plain language.
- Reinstalling the app forces a fresh association attempt — the fastest reliable reset while iterating.

## Custom URL Schemes

- Any app can claim any scheme; iOS resolves collisions unpredictably. Use schemes for internal navigation (widgets, your own extensions) and legacy integrations, never as the public entry point.
- Declare schemes you want to *open* in `LSApplicationQueriesSchemes` — maximum **50 entries**, and `canOpenURL` returns false for anything unlisted, which reads exactly like "the other app is not installed".
- A scheme URL cannot be validated: anything on the device can invoke it. Treat every parameter as untrusted input, and never let a scheme URL perform a destructive or authenticated action without an in-app confirmation.
- Universal links are the secure equivalent because the domain proves ownership. Where both exist, prefer the universal link and keep the scheme as a fallback.

## Links From Widgets, Notifications and Shortcuts

- Widgets: `widgetURL(_:)` for the whole widget, `Link` for tappable regions inside it. Both accept a custom scheme or a universal link; the app receives it through `onOpenURL` (`widgets.md`).
- Notifications: the destination travels in the payload, and the tap handler may fire before the UI exists — same buffering rule as above (`notifications.md`).
- App Intents and Shortcuts open the app with a parameterized intent rather than a URL; the routing table should be one shared function so all four entry points cannot disagree (`extensions.md`).
- Spotlight and Handoff use `NSUserActivity` with your own activity types; register them in Info.plist or they are ignored.

## Attribution After Install

iOS gives no install referrer. The honest options, and their costs:

- **App Clips**: the invocation URL survives into the full app if the user upgrades, which is the only genuinely seamless path. The clip has a hard uncompressed size ceiling in the tens of megabytes — verify the current number before designing around it.
- **Apple Ads attribution (AdServices)**: a token exchanged for campaign-level attribution, no ATT prompt required.
- **Fingerprinting** — matching IP and device characteristics — is prohibited and enforced. It is also what several attribution SDKs do by default; check what the SDK sends before shipping it (`privacy.md`).
- Clipboard-based deferred links now show a system paste banner, so the "invisible" version of this technique no longer exists.

## Write It Down

- **The route table and its AASA components** — which paths open which screens, which are excluded, and why — is `artifacts/deep-links-<app>.md`, with its `## Boxes` line in the same turn (`memory-template.md`). It is the file that stops the app and the website from drifting apart.
- **Propagation and infrastructure facts** — that this domain sits behind a WAF that had to allow the fetch, that the last change took a day to appear, that the marketing redirector must publish final URLs — go in `## Platform Facts`, one line each.
- **A deep-link failure that took real time to diagnose** is a `## Pain Points` line; the second occurrence earns `artifacts/runbook-deep-links.md` with the ordered checks.
