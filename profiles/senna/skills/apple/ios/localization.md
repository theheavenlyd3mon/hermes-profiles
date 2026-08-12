# Localization — Languages, Regions, and the Bugs Between Them

**Before adding a locale**, read `localization.locales` in `~/Clawic/data/ios/config.yaml` and `## Apps` in `~/Clawic/data/ios/memory.md` — which locales already ship, and which store metadata exists for them, decides the work.

**Contents:** [Language Is Not Region](#language-is-not-region) · [String Catalogs](#string-catalogs) · [Plurals and Grammar](#plurals-and-grammar) · [Never Concatenate, Never Format by Hand](#never-concatenate-never-format-by-hand) · [Right to Left](#right-to-left) · [Dates, Calendars and Time Zones](#dates-calendars-and-time-zones) · [Prices](#prices) · [What Else Is Localized](#what-else-is-localized) · [Testing Without Translations](#testing-without-translations) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## Language Is Not Region

Two independent settings, and conflating them is the root of most localization bugs:

- **Language** decides which strings load. A user can set a per-app language different from the system one, so the app's language is not the device's.
- **Region** decides formatting: number separators, currency display, measurement units, first day of the week, calendar, 12- vs 24-hour time, paper size, phone-number shape.

An English speaker in Germany reads English strings with `1.234,56`, metric units, a Monday-first calendar and 24-hour time. Code that derives formatting from the language is wrong for that user, and there are a lot of that user.

Read the current locale rather than caching it: language and region both change at runtime, and the app is expected to update.

## String Catalogs

- `.xcstrings` String Catalogs are the current format: strings are extracted from source automatically, with state tracking for what is new, translated or stale. They replace `.strings` and `.stringsdict` and hold plural variations in the same file.
- Use `String(localized:)` / `LocalizedStringKey` and let extraction do the work. A string built at runtime from fragments is never extracted and never translated.
- **The comment is the deliverable.** "Button label; verb, imperative" versus "Noun, a saved file" is the difference between "Save" translating correctly and a translator guessing. A catalog with no comments produces confident, wrong translations.
- Keys: either the English text (simple, and it churns when copy changes) or symbolic keys (stable, and untranslated builds show `settings.header`). Pick one convention per app and record it in `~/Clawic/data/ios/artifacts/localization-<app>.md`; mixing them is what produces the missing-translation-in-production bug.
- Localize `InfoPlist.xcstrings` separately — permission purpose strings and the app's display name live there, and an untranslated purpose string is visible in the system prompt (`permissions.md`).

## Plurals and Grammar

- Never build "1 item" / "2 items" with a conditional. Languages have up to six plural categories (Arabic has six, Russian and Polish three); English has two, which is why English-only code looks correct forever.
- Plural variations live in the String Catalog, keyed by the format argument. The rule for zero is a category in some languages and not others — let the catalog decide.
- Gender and grammatical agreement: newer OSes support grammatical inflection for supported languages; where they do not, the fix is to rewrite the string so agreement is unnecessary rather than to build it in code.
- Ordinals, ranges and lists have their own formatters — `ListFormatter` produces "A, B and C" per locale; string joining does not.

## Never Concatenate, Never Format by Hand

- Use positional specifiers (`%1$@`, `%2$lld`) so translators can reorder. Word order is not universal, and a non-positional format string cannot be reordered.
- Numbers, currencies, percentages, distances, weights, byte counts, durations and relative dates all have formatters. `"\(count) km"` is wrong in an imperial region, and `String(format: "%.2f")` is wrong wherever the decimal separator is a comma.
- Measurement conversion belongs to `Measurement` and its formatter, driven by the locale — or by `units` in `~/Clawic/profile.yaml` when the user has declared a preference that overrides the region.
- Formatters are expensive to create. Build them once and reuse; creating one per table cell is a measurable scroll hitch (`performance.md`).
- Sorting and searching use locale-aware comparison — `localizedStandardCompare`, not `<`. Otherwise accented names sort into a separate section.

## Right to Left

- Use leading/trailing, never left/right, everywhere: constraints, padding, alignment, text alignment. The system mirrors correctly only if the layout is expressed in relative terms.
- Directional asymmetric icons (back arrows, indentation, progress) mirror; **media playback controls, clock faces and physical-world imagery do not**. Mark image assets accordingly in the asset catalog rather than flipping the whole view.
- Numbers stay left-to-right inside RTL text, which makes mixed strings (a price, a phone number) the place where naive mirroring breaks.
- Test with the RTL pseudolanguage before any Arabic or Hebrew translation exists — it finds the layout bugs, which are the expensive ones.

## Dates, Calendars and Time Zones

- Store instants in UTC; display in the user's current time zone; never store a formatted string.
- The Gregorian calendar is an assumption. `Calendar.current` may be Buddhist, Japanese or Hebrew, and the year is then not what your arithmetic expects. Do date math with `Calendar` components, never by adding seconds.
- First day of the week, week numbering and weekend days are regional. A hand-built calendar grid is wrong outside the developer's country.
- 12- versus 24-hour is a region setting the user can override; `DateFormatter` with a template (`setLocalizedDateFormatFromTemplate`) respects it, a hardcoded `HH:mm` does not.
- Local notifications with calendar triggers follow the device's current time zone unless told otherwise — travel changes when they fire (`notifications.md`).

## Prices

- Display StoreKit's own formatted price string. It is already localized to the storefront, including currency, symbol placement and separators — formatting the raw decimal yourself produces prices that look foreign to the user (`storekit.md`).
- The storefront is not the language: a user in Japan with an English device sees yen. Never infer currency from the language, or from the device region either.
- Prices are set per storefront from Apple's matrix; there is no "convert my USD price" step to reimplement.

## What Else Is Localized

- The app name and permission purpose strings (`InfoPlist.xcstrings`).
- App Store metadata: name, subtitle, description, keywords, screenshots and the What's New text, per locale, in App Store Connect. A localized app with English screenshots converts like an English app (`releases.md`).
- Push notification payloads: send `loc-key`/`loc-args` so the device localizes with the app's strings, rather than sending pre-translated text the server guessed (`notifications.md`).
- Siri and Shortcuts phrases, per language (`extensions.md`).
- Number and date content inside notifications and widgets, which render outside your view code.

## Testing Without Translations

- Xcode's pseudolanguages: **double-length** (catches truncation), **accented** (catches unlocalized strings — anything still plain ASCII was never extracted), **right-to-left**, and **bounded** (shows the layout limits).
- Run the scheme with an explicit language and region override, and separately with a language the app does not ship — the fallback chain is a real code path.
- Per-app language: set it in Settings for the installed build and verify the app updates without a relaunch.
- Test the longest language you ship in the smallest device: German and Finnish strings are routinely 30% longer than English, and that lands on the floor device (`layout.md`).

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| Some strings never translate | Built at runtime from fragments, so never extracted | Search for string interpolation inside user-facing text |
| Numbers show as `1234.56` in Europe | Manual formatting | `NumberFormatter` or `formatted()` |
| "1 items" in another language | Conditional plurals instead of catalog variations | Plural variations per key |
| Sentence word order wrong | Non-positional format specifiers | `%1$@`, `%2$@` |
| Layout breaks only in German | 30% longer strings meeting a fixed width | Pseudolanguage double-length |
| Back arrow points the wrong way in Arabic | Absolute left/right, or a non-mirroring asset | Leading/trailing plus asset direction |
| Reminder fires an hour off after a flight | Calendar trigger and time zone | Store UTC, trigger with an explicit zone |
| Price shows as `$9.99` in Japan | Formatting the price locally | StoreKit's `displayPrice` |

## Write It Down

- **Which locales ship** and which have store metadata is part of the app's row notes in `## Apps` (`memory-template.md`). It is the checklist at every release, and the answer to "did we ever translate the screenshots".
- **A translation or convention decision** — key style, who translates, what is deliberately not localized, how the glossary is maintained — is `artifacts/localization-<app>.md` with its `## Boxes` line in the same turn.
- **A locale-specific bug that reached users** is a `## Pain Points` line; a locale-specific platform behavior (a calendar, a formatter, a store quirk) is a `## Platform Facts` line.
