# Networking on Device — ATS, Sessions, and Failures That Only Happen Off Wi-Fi

**Before debugging a request that works elsewhere**, read `## Platform Facts` in `~/Clawic/data/ios/memory.md`: a recorded ATS exception, a corporate proxy, a pinned certificate or a captive-portal quirk explains most "only on iOS" network bugs.

**Contents:** [App Transport Security](#app-transport-security) · [Choosing a Session](#choosing-a-session) · [Connectivity Is Not a Precondition](#connectivity-is-not-a-precondition) · [Constrained and Expensive Networks](#constrained-and-expensive-networks) · [Retries and Idempotency](#retries-and-idempotency) · [Caching](#caching) · [Certificate Pinning](#certificate-pinning) · [Web Views](#web-views) · [Error Codes](#error-codes) · [Write It Down](#write-it-down)

## App Transport Security

HTTPS with TLS 1.2 or better and forward secrecy, enforced by the OS, not by your code.

- `NSAllowsArbitraryLoads: true` disables it globally and **requires a justification at review**. "Our backend is HTTP" is not one; a documented third-party dependency might be.
- Prefer a narrow `NSExceptionDomains` entry with only the relaxation needed — `NSExceptionAllowsInsecureHTTPLoads` for one host beats disabling ATS everywhere, and reviewers read the difference.
- `NSAllowsLocalNetworking: true` covers `.local` and link-local addresses without weakening anything public. Local network access also needs its own permission and Bonjour declarations (`permissions.md`).
- ATS applies to `WKWebView` too, and to every SDK inside the app. An SDK talking HTTP is your ATS exception, filed under your justification.
- A blocked load logs a precise reason to the console naming the host and the failed requirement — read it before changing keys.

## Choosing a Session

| Configuration | Runs when | Use for |
|---|---|---|
| `default` | App is running | Everything ordinary; disk cache and cookies included |
| `ephemeral` | App is running | Private-mode behavior: no persistent cache, cookies or credentials |
| `background(withIdentifier:)` | The system transfers, app may be dead | Uploads and downloads that must survive backgrounding (`background.md`) |

- `timeoutIntervalForRequest` is the gap between packets, not the total. `timeoutIntervalForResource` is the ceiling for the whole transfer — set both deliberately; the defaults (60 s and 7 days) are almost never what an app wants.
- One session per purpose, created once. Creating a `URLSession` per request leaks connections and defeats connection reuse; not invalidating a delegate-based session leaks the delegate forever.
- HTTP/2 and HTTP/3 multiplex over one connection: parallel requests to the same host are cheap, and your own request queue usually makes things slower, not faster.

## Connectivity Is Not a Precondition

- `NWPathMonitor` reports the path, not reachability of your server. Captive portals, VPN gaps and asymmetric routes all present as "satisfied" while nothing works.
- **Attempt the request and handle failure**; never gate a request on a reachability check. Reachability is a diagnostic for the error message you show, not a permission to proceed.
- `waitsForConnectivity = true` (default and ephemeral sessions only) parks the request until a path appears instead of failing instantly, with `timeoutIntervalForResource` as the ceiling. It is the right default for user-initiated work that is not time-critical, and it changes the UX: show "waiting for network", not an error.
- Offline behaviour is a feature review checks: an app that shows a blank screen with no explanation when offline is rejected under 2.1 quality rules (`review.md`).

## Constrained and Expensive Networks

- Low Data Mode surfaces as a **constrained** path; cellular and Personal Hotspot as **expensive**. Set `allowsConstrainedNetworkAccess = false` on prefetches, video autoplay and analytics uploads, and leave it true for what the user asked for.
- The failure is explicit: a request refused for that reason returns an error whose `networkUnavailableReason` names constrained or expensive, so the app can degrade instead of retrying blindly.
- The user can disable cellular data per app in Settings; requests then fail with "data not allowed" (`-1020`), which is not an outage and must not be retried in a loop.
- Test on a real device with Low Data Mode on and cellular only. The simulator has neither.

## Retries and Idempotency

- Exponential backoff with jitter: delay ≈ `base × 2^attempt`, plus a random 0-100% of that delay, capped. Without jitter, every device that lost connectivity at the same moment retries at the same moment.
- Retry only idempotent requests automatically. A POST that creates something gets retried **only** with an idempotency key the server honours; otherwise a lost response duplicates the order.
- Respect `Retry-After` on 429 and 503 over your own schedule, and stop retrying on 4xx other than 408 and 429 — a 401 retried ten times is how an account gets locked.
- Cap total attempts and surface the failure. An infinite retry loop in the background drains the battery and earns `EXC_RESOURCE (WAKEUPS)`.

## Caching

- `URLCache.shared` respects `Cache-Control`, `ETag` and `Last-Modified` automatically. Most apps that "implemented caching" reimplemented what the server was already telling the session to do — fix the headers first.
- `cachePolicy` on the request overrides it. `.reloadIgnoringLocalCacheData` everywhere is a common cargo-cult that turns a 304 into a full download on every launch.
- Size the cache explicitly if it matters, and remember disk cache lives in `Caches/` and can be purged at any time (`data.md`).
- Images need their own decode-aware cache; a URL cache stores bytes, not decoded bitmaps, and decoded bitmaps are what exhaust memory (`performance.md`).

## Certificate Pinning

- Implement in `urlSession(_:didReceive challenge:)` by evaluating the server trust yourself; returning `.performDefaultHandling` for everything else.
- **Pin the SPKI hash, not the certificate**, and always ship at least one backup pin for a key you have not deployed yet. Pinning a leaf certificate guarantees an outage on the day it rotates — and it will rotate on a 90-day schedule.
- Ship a remote kill switch or a short pin expiry. A pinning failure is an app-wide outage that only a new release through review can fix (`releases.md`).
- Pinning breaks corporate MITM proxies, which is usually the point and occasionally the bug report.
- Background sessions cannot answer interactive challenges — pinning logic must be non-interactive there.

## Web Views

- `WKWebView` has its own cookie store (`WKHTTPCookieStore`) and does not share cookies with `URLSession`. A login done natively is not a login inside the web view unless the cookies are copied deliberately.
- `SFSafariViewController` shares Safari's cookies and cannot be inspected or scripted by the app — that is why it is the sanctioned OAuth surface, along with `ASWebAuthenticationSession`.
- Content in a web view does not trigger universal links to other apps (`deep-links.md`).
- A web view is a separate process with its own memory footprint that counts toward the app's jetsam budget indirectly; a leaking web view is a common source of background kills.

## Error Codes

| Code | Meaning | What it actually is, usually |
|---|---|---|
| `-1009` | Not connected to the internet | Airplane mode, no path, or a captive portal |
| `-1001` | Timed out | Server slow, or `timeoutIntervalForRequest` too tight for a cellular first byte |
| `-1005` | Network connection lost | Server or intermediary closed mid-response; retry once, then investigate the backend |
| `-1020` | Data not allowed | Cellular disabled for this app in Settings |
| `-1022` | ATS blocked the load | The console names the exact requirement that failed |
| `-1200` / `-9807` | TLS handshake failure | Wrong chain, missing intermediate, expired cert, or an over-eager pin |
| `-999` | Cancelled | Your own code cancelled the task, or the view was dismissed — not a network problem |
| `-1017` | Cannot parse response | Server returned HTML (an error page or a captive portal) where JSON was expected |

## Write It Down

- **Every ATS exception and its justification** goes in `artifacts/ats-exceptions-<app>.md`, with its `## Boxes` line in the same turn (`memory-template.md`) — review asks for the reasoning, and the reasoning is what nobody can reconstruct a year later.
- **Pinning configuration** — which SPKI hashes, which backup pin, the expiry, the kill switch — is its own artifact. A pin whose rationale lives in a pull request is an outage waiting for a rotation.
- **Infrastructure facts** — a corporate proxy, a CDN that strips a header, a backend whose first byte on cellular routinely takes seconds — are `## Platform Facts` lines, one each.
