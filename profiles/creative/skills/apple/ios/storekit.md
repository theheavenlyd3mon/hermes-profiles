# StoreKit — Purchases, Subscriptions, and the Guidelines Around Them

**Before touching purchase code**, read `## Apps` in `~/Clawic/data/ios/memory.md` for the product identifiers, `## Rejections` for any 3.1.x history on this app, and `artifacts/` entries `## Boxes` names for the paywall or monetization decision.

**Contents:** [The StoreKit 2 Shape](#the-storekit-2-shape) · [Entitlement Is Derived, Never Stored](#entitlement-is-derived-never-stored) · [Server Side](#server-side) · [Subscriptions](#subscriptions) · [Offers and Price Changes](#offers-and-price-changes) · [Testing](#testing) · [What the Paywall Must Show](#what-the-paywall-must-show) · [Guideline 3.1](#guideline-31) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## The StoreKit 2 Shape

Four things, in this order, and the first one is the one that gets forgotten:

1. **Start `Transaction.updates` at launch**, before any UI. It delivers purchases that completed outside the app, Ask-to-Buy approvals, renewals, and anything interrupted. An app without this listener loses purchases and produces the "I paid and got nothing" support ticket.
2. **Load products** with `Product.products(for:)`. An empty result is a configuration problem, not a network one — see Symptoms.
3. **Purchase** with `product.purchase()`, and handle all four outcomes: success, user cancelled, pending (Ask to Buy, SCA), and unknown.
4. **Verify, grant, then finish.** A transaction that is finished before the content is granted is gone; a transaction never finished is re-delivered on every launch forever.

`VerificationResult` is real cryptographic verification of Apple's signed JWS on device — `.unverified` means do not grant, and log the reason.

## Entitlement Is Derived, Never Stored

- At launch, and on every `Transaction.updates` event, recompute what the user owns from `Transaction.currentEntitlements`. That is the source of truth.
- A local boolean flag "isPro" is trivially flipped, lost on reinstall, and wrong after a refund. If a local cache is needed for launch speed, it is a cache of the derived value, refreshed as soon as the recompute finishes.
- Because entitlements are derived automatically, **restore is rarely needed** — but a visible Restore button is still required for apps with non-consumables or subscriptions, and it calls `AppStore.sync()`. Never call `sync()` at launch: it prompts for the App Store password.
- Consumables are the exception: they are not in `currentEntitlements`, so the grant must be recorded by you (server-side if it matters) at the moment the transaction is finished.

## Server Side

- **App Store Server Notifications V2** is the only way to learn about renewals, cancellations, refunds, billing retries and grace periods while the app is not running. Subscribe to it, or the backend's idea of who is subscribed decays daily.
- Handle `REFUND` by revoking access. An app that keeps serving content after a refund is a fraud vector and a support cost.
- The **App Store Server API** lets the backend fetch transaction history and subscription status by transaction id, signed and verifiable. It replaces the old receipt-verification endpoint for new work.
- Where the entitlement lives decides the architecture: on-device verification is enough when the app is the only consumer; a backend that gates an API needs server-side truth (SKILL.md, Where Experts Disagree).
- The App Store shared secret used by legacy receipt validation is a credential — pointer only, never in `~/Clawic/data/` (`memory-template.md`).

## Subscriptions

- Products live in a **subscription group**; a user has at most one active subscription per group, and upgrades, downgrades and crossgrades are moves within it. Two groups means two parallel subscriptions and a support nightmare — use one unless the product genuinely has two independent axes.
- Upgrade is immediate with proration; downgrade takes effect at the next renewal. The UI must say which.
- **Billing retry and grace period**: when a renewal fails, Apple retries for a period; with grace period enabled the user keeps access while it retries. Enabling it is the single highest-return switch in subscription churn, and it costs nothing.
- Family Sharing is per product and can be enabled after launch — but not disabled without affecting existing purchasers.
- Auto-renew status, expiration and the reason for cancellation come from the signed transaction and the server notifications, never from your own timer.

## Offers and Price Changes

- **Introductory offer**: one per subscription group per Apple ID, eligibility determined by Apple. Check eligibility before showing "7 days free" to someone who already used it — a mismatch is a guideline problem and a trust problem.
- **Promotional offers** need a signature generated with a key you hold server-side; **offer codes** are redeemed outside the app or via a redemption sheet; **win-back offers** target lapsed subscribers through the store itself.
- **Price increases**: Apple permits one increase per year without user opt-in, within its published percentage and absolute caps; beyond that, every existing subscriber must actively consent or the subscription lapses. Verify the current caps before planning the increase, and plan the communication either way (`releases.md`).
- Prices are set per storefront from a matrix; the number a user sees is not your USD price converted (`localization.md`).

## Testing

Three environments, and they answer different questions:

| Environment | What it proves | What it cannot prove |
|---|---|---|
| Xcode StoreKit configuration file | Purchase flow, UI, edge cases, offline | Nothing about App Store Connect, review or real receipts |
| Sandbox (sandbox Apple ID on device) | The real store path, renewals, offers | Production pricing and real billing |
| TestFlight | Production-like purchase flow, free of charge to testers | Nothing about real money either |

Sandbox subscription durations are accelerated so a year can be observed in an hour: one week renews in minutes, one month in a few minutes, a year in about an hour — and a sandbox subscription **auto-renews a limited number of times (six) and then stops**, which is not a bug in your renewal handling.

Sandbox accounts are managed in Settings on the device, not by signing out of the real App Store account. Signing out of the real account to test is how people lock themselves out of their own purchases.

## What the Paywall Must Show

For auto-renewable subscriptions, on the screen where the purchase happens — not behind a link to a website:

- Title of the subscription and the content or service it unlocks
- Duration of a single period and the price for that period
- Price per unit where the product is priced by a unit (per month on an annual plan, if you show it)
- That it renews automatically until cancelled, and how to cancel
- Functional links to the Terms of Use (EULA) and the Privacy Policy
- A Restore button

Missing links and missing renewal disclosure are the most common paywall rejections, and they are found in seconds by a reviewer.

## Guideline 3.1

- **3.1.1**: digital content and features used inside the app go through StoreKit. No external payment link, no "contact us to upgrade", no crypto workaround. This includes unlocking content bought elsewhere unless the app qualifies for an exception.
- **3.1.3 reader apps** and the other exceptions are narrow and specific; qualifying requires no in-app purchase of the content at all, plus an entitlement application for the external link where one applies.
- **External purchase link entitlements** exist in some regions with their own disclosure sheets, commissions and reporting duties. Regional, changing, and never worth assuming — check the current rules for the storefront in question before designing around them.
- Physical goods and services consumed outside the app must **not** use StoreKit — that is the mirror-image rejection.
- Consumables that function as a currency for real-world value, and anything resembling gambling or loot boxes, carry extra disclosure duties (odds disclosure) and age rating consequences (`review.md`).

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| `products(for:)` returns empty | Product not Ready to Submit, bundle id mismatch, agreements not signed, or the product was created minutes ago | Paid Applications agreement first — it silently blocks everything |
| Purchase succeeds, nothing unlocks | Transaction finished before granting, or entitlement read from a stale local flag | Derive from `currentEntitlements` |
| The same purchase re-appears every launch | Transaction never finished | `finish()` after granting, always |
| Purchases made on another device do not appear | No `Transaction.updates` listener | Start it at launch |
| Works in the sandbox, fails in production | Product not approved with the build, or the app has no active agreement | The product must be submitted with a version |
| Subscription "cancels itself" in testing | Sandbox renews six times and stops | Expected behavior |
| Refunded users keep access | No server notification handling | Subscribe to V2 notifications, handle `REFUND` |
| Intro offer shown to an ineligible user | Eligibility not checked | Check before rendering the price |

## Write It Down

- **Product identifiers, subscription groups and what each unlocks** go in `## Apps` in `~/Clawic/data/ios/memory.md` — or in the app's row's notes when there are few (`memory-template.md`). Product ids are not secret and are needed constantly.
- **The monetization decision** — StoreKit 2 versus 1, on-device versus server-side entitlement, why the paywall is shaped this way, what was rejected — is `artifacts/decision-monetization-<app>.md`, with its `## Boxes` line in the same turn.
- **Every 3.1.x rejection and the exact change that cleared it** is a `## Rejections` row. Purchase rejections repeat by guideline across apps, and this table is the checklist for the next paywall.
- **A price change, an offer campaign or a grace-period switch** is a release-level fact: note it in the `## Notes` of `releases/<year>.md` alongside the build it shipped with.
