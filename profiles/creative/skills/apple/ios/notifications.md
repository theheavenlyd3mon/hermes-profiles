# Notifications — Push and Local

**Before debugging push**, read `## Apps` in `~/Clawic/data/ios/memory.md` for the bundle id, team and push capability, and `## Platform Facts` for the environment quirk this app already hit. Check `## Due` for the APNs key or push certificate expiry — an expired credential looks exactly like a broken integration.

**Contents:** [The Token Path](#the-token-path) · [Environments](#environments) · [Credentials](#credentials) · [APNs Headers](#apns-headers) · [Payload](#payload) · [Authorization](#authorization) · [Foreground and Actions](#foreground-and-actions) · [Notification Extensions](#notification-extensions) · [Local Notifications](#local-notifications) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## The Token Path

1. Ask for authorization (or use provisional), then call `registerForRemoteNotifications()` — registration is independent of authorization, and both are needed for alerts.
2. `didRegisterForRemoteNotificationsWithDeviceToken` returns `Data`; hex-encode it. Never `description` the `Data` — that formatting changed years ago and the resulting strings are silently wrong.
3. **Upload the token on every launch.** Tokens change on restore-from-backup, on some OS updates, and on reinstall. A server holding a stale token gets `410 Unregistered` and must delete it.
4. `didFailToRegisterForRemoteNotifications` fires on the simulator without a push-capable configuration and on a build with no `aps-environment` entitlement — read its error rather than assuming APNs is down.

## Environments

The single most common "push is broken":

| Build | APNs environment | Token valid against |
|---|---|---|
| Xcode debug build, development profile | sandbox | `api.sandbox.push.apple.com` |
| Ad-hoc / TestFlight / App Store | production | `api.push.apple.com` |

A sandbox token sent to production returns `400 BadDeviceToken` — a clear error that most stacks swallow. Store the environment alongside every token, and never mix builds in one device's token table. The `aps-environment` entitlement in the built app is the source of truth: dump it from the binary rather than trusting the project setting (`commands.md`).

## Credentials

- **Auth key (`.p8`)**: one key for the whole team, works for every app and both environments, does not expire. Preferred. You get the file exactly once, and the `.p8` body is a secret — the Key ID and Team ID are not (`memory-template.md`).
- **Push certificate (`.p12`)**: per-app, expires in a year, and its expiry is a scheduled outage. If one is in use, its date belongs in `## Due` today.
- Provider JWTs signed with the auth key must be **refreshed at least hourly and no more often than every 20 minutes** — regenerating on every request gets the provider throttled with `TooManyProviderTokenUpdates`.

## APNs Headers

| Header | Value | Consequence of getting it wrong |
|---|---|---|
| `apns-topic` | the bundle id (`.voip`, `.push-type.liveactivity` suffixes for those) | `TopicDisallowed` or `DeviceTokenNotForTopic` |
| `apns-push-type` | `alert`, `background`, `voip`, `liveactivity`, `complication` | Required; the wrong one is rejected or throttled |
| `apns-priority` | `10` for alerts, `5` for background and power-considerate delivery | Priority 10 on a background push is rejected |
| `apns-expiration` | epoch seconds; `0` = deliver now or discard | Default retains and delivers late — often worse than not delivering |
| `apns-collapse-id` | your key, ≤64 bytes | Without it, ten updates are ten banners |

Common responses: `400 BadDeviceToken` (wrong environment), `400 DeviceTokenNotForTopic` (token from another bundle id), `403 ExpiredProviderToken` (JWT older than an hour), `410 Unregistered` (delete the token, the app is gone), `429 TooManyRequests` (per-device throttle, usually background pushes).

## Payload

4 KB maximum (5 KB for VoIP). Anything larger is a fetch the push triggers, not a push.

```json
{
  "aps": {
    "alert": { "title": "Order shipped", "body": "Arriving Tuesday" },
    "sound": "default",
    "thread-id": "order-8891",
    "interruption-level": "time-sensitive",
    "relevance-score": 0.8,
    "mutable-content": 1
  },
  "order_id": "8891"
}
```

- `mutable-content: 1` is what invokes the notification service extension; without it the extension never runs.
- `content-available: 1` with no alert is a silent push, with its own rules and throttles (`background.md`).
- `interruption-level: time-sensitive` breaks through Focus and requires the time-sensitive entitlement; `critical` requires a separate Apple approval. Both are audited at review.
- Badge is not automatic: send `badge` explicitly, or set it locally with `setBadgeCount`. A badge that never clears is the most common complaint about a notification integration.

## Authorization

- `.provisional` delivers quietly with **no prompt at all**: notifications land in Notification Center, and the user is offered "keep" or "turn off" when they engage. It converts far better than a cold prompt and cannot be denied up front.
- Options are requested once; adding `.criticalAlert` or `.provisional` later does not re-prompt.
- `.providesAppNotificationSettings` puts a link to your own notification settings inside the system settings page — the place users actually look before uninstalling.
- Check `notificationSettings` rather than caching the request result: the user can disable categories, sounds, banners or Lock Screen delivery independently, and each one changes what "delivered" means.

## Foreground and Actions

- With the app foreground, nothing is shown unless `userNotificationCenter(_:willPresent:)` returns presentation options. Half of "push doesn't work" is testing with the app open.
- Register categories and actions in `didFinishLaunching`, before any notification can arrive — a notification whose category is unknown loses its buttons.
- The tap handler `didReceive response` may fire during a cold launch, before the UI exists. Buffer the destination and consume it when the scene is active (`lifecycle.md`).
- Notification actions can run without opening the app (`.foreground` omitted); that handler gets seconds, so it hands off to a background mechanism rather than doing the work.

## Notification Extensions

- **Service extension** (`mutable-content: 1`): roughly 30 seconds to decrypt, localize or attach media. It must call `contentHandler` — the `serviceExtensionTimeWillExpire` fallback delivers whatever you have, and if you supply nothing the original payload is shown. Its memory ceiling is well below the app's; download modest media only.
- **Content extension**: custom UI for a notification, no networking of consequence, and it cannot present alerts.
- Both are separate targets with separate entitlements: an App Group added only to the app leaves the extension unable to read anything (`capabilities.md`).

## Local Notifications

- Three triggers: time interval, calendar, and location (region entry/exit). Calendar triggers repeat by matching components — a `DateComponents` with only `hour` and `minute` repeats daily.
- **iOS keeps only the 64 soonest pending local notifications per app.** Scheduling a year of daily reminders silently drops everything past the 64th; reschedule a rolling window each launch instead.
- Cancelling is by identifier: use stable identifiers derived from the entity, not UUIDs, or you cannot cancel what you scheduled.
- Time zone changes: a calendar trigger with `DateComponents` follows the device's current time zone unless the trigger's calendar says otherwise. Travel is a bug report waiting to happen (`localization.md`).

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| No token, `didFailToRegister` fires | No push capability/entitlement, or an unsupported simulator setup | Dump `aps-environment` from the built binary |
| `400 BadDeviceToken` | Sandbox token sent to production, or the reverse | Environments table above |
| Push works in debug, not in TestFlight | Same as above — TestFlight is production | Store the environment with each token |
| `403 ExpiredProviderToken` | Provider JWT older than an hour | Refresh hourly, cache for at least 20 minutes |
| Delivered but nothing appears | App is foreground, or Focus/Scheduled Summary is filtering it | `willPresent` options; check `interruption-level` |
| Service extension never runs | `mutable-content: 1` missing, or the extension's deployment target is above the device | Both, in that order |
| Silent pushes stop after a burst | Per-app throttling, or Low Power Mode | `background.md` |
| Only some devices receive it | Stale tokens the server never deleted on `410` | Delete on `410 Unregistered`, always |
| Notifications vanish after a reinstall | New token, old one unregistered | Upload the token on every launch |

## Write It Down

- **The push identifiers** — Key ID, topic, which environments are wired, which extension targets exist — belong in `## Apps` in `~/Clawic/data/ios/memory.md`. The `.p8` body never does; it is a `file:` or `1password:` pointer (`memory-template.md`).
- **A push certificate or auth-key rotation date** is a `## Due` row the day it is discovered. This is the outage that arrives on a calendar.
- **An environment or delivery quirk** — that TestFlight builds need production tokens here, that this app's silent pushes are throttled after three — is one line in `## Platform Facts`.
- **A working payload and header set**, once it took an afternoon to get right, is `artifacts/push-payload-<app>.md` with its `## Boxes` line in the same turn.
