# Adaptive Layout — Safe Areas, Size Classes, Dynamic Type

**Before designing for a device**, read `platform.oldest_supported_device` in `~/Clawic/data/ios/config.yaml` and `## Platform Facts` in `~/Clawic/data/ios/memory.md` — the floor device and any recorded device-specific layout bug are the constraints, not the newest phone on the desk.

**Contents:** [Two Axes of Failure](#two-axes-of-failure) · [Safe Areas](#safe-areas) · [Size Classes, Not Devices](#size-classes-not-devices) · [Dynamic Type](#dynamic-type) · [The Keyboard](#the-keyboard) · [Orientation and Multitasking](#orientation-and-multitasking) · [Dark Mode and Semantic Colors](#dark-mode-and-semantic-colors) · [Testing the Matrix](#testing-the-matrix) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## Two Axes of Failure

Almost every layout bug is one of two things: **the smallest screen** (a 4.7" phone at the deployment-target floor) or **the largest text** (an accessibility Dynamic Type size). Designs are made on a large phone at the default size, which is the one combination that always works.

Fix the two extremes and the middle takes care of itself. Test them together — small screen *and* largest text — because that is where fixed heights, two-line buttons and clipped labels all appear at once.

## Safe Areas

- Lay out against the safe area, never against the screen. The insets encode the status bar, the Dynamic Island or notch, the home indicator, and — in an iPad window — the space the system needs.
- Background colors and images extend past it (`ignoresSafeArea()`); content and controls do not. A tap target under the home indicator loses to the system gesture.
- The keyboard is a safe area inset on modern iOS. `ignoresSafeArea(.keyboard)` is how you opt a background out without dragging the content with it.
- `additionalSafeAreaInsets` is the sanctioned way to reserve room for a custom bar. Hardcoding 44 or 34 points is how a layout breaks on the next device shape.
- Read insets from the window or the environment at layout time. Cached values are wrong after rotation, after a window resize, and during multitasking.

## Size Classes, Not Devices

- Branch on horizontal and vertical **size class**, never on `UIDevice.current.userInterfaceIdiom`. An iPad in Split View is compact-width; a phone in landscape is compact-height. Idiom-based layout is the reason iPad multitasking looks broken.
- Size classes change **at runtime** as the user resizes a window. Layout must recompute, not read once at load.
- `NavigationSplitView` / `UISplitViewController` collapse to a stack in compact width automatically. Fighting that collapse is nearly always the wrong direction.
- Never read `UIScreen.main.bounds` for layout: in a resizable window it is the screen, not your view. Use the view's own size or a geometry reader.
- `target_devices` in config decides how much of this applies — an iPhone-only app still meets compact-height in landscape.

## Dynamic Type

- Use text styles (`.body`, `.headline`) or scaled custom fonts. A fixed point size does not scale, and an app whose text never grows is failing the most used accessibility feature on the platform.
- Support the accessibility sizes, not just the standard ones. The largest accessibility size is roughly triple the default body size; a layout that assumes one line will show one word.
- Avoid fixed heights on anything containing text. Constrain by content, and let containers grow.
- Switch layout at large sizes rather than shrinking: a horizontal row of label and value becomes a vertical stack past a size threshold. In SwiftUI, `@Environment(\.dynamicTypeSize)` and `ViewThatFits` express this without a custom breakpoint.
- Clamping with `.dynamicTypeSize(...upTo:)` is a last resort for a genuinely fixed-geometry component (a chart axis), never a global policy.
- Images and glyphs beside text should scale with it — `ScaledMetric`, or SF Symbols configured with the same text style.

## The Keyboard

- SwiftUI moves focused content out of the way automatically; the failure mode is a custom container that also does it, producing double movement.
- In UIKit, read the frame from the notification's user info and convert it into the view's coordinate space. Assuming a height is wrong for floating keyboards, external keyboards with a shortcut bar, and split keyboards on iPad.
- A hardware keyboard means the software one never appears, and the accessory bar still occupies space. Test with one attached at least once.
- Scroll the focused field into view, and inset the scroll view rather than moving the whole screen — moving the screen breaks navigation bars and large titles.
- Dismissal must be reachable: interactive dismissal on scroll, or a Done button. A form with no way to dismiss the keyboard on a small screen is a rejection under basic quality rules.

## Orientation and Multitasking

- Declare the orientations the app supports in Info.plist, and per-scene overrides where a single screen differs (a video player). Every declared orientation must actually work.
- `UIRequiresFullScreen` opts an iPad app out of Split View and Slide Over. It is a legitimate choice for a few app types and a bad default: it removes the app from the multitasking flows iPad users expect, and it interacts badly with Stage Manager.
- Rotation is a size change, not an event: implement it as "lay out for this size", and the same code handles resizing, Slide Over and Stage Manager for free.
- Do not cache view dimensions across a transition. `viewWillTransition(to:with:)` gives the new size; a geometry reader gives it continuously.
- Support pointer interactions and hardware keyboard shortcuts on iPad when the app is a productivity tool — reviewers of iPad apps notice their absence, and users of Magic Keyboards notice more.

## Dark Mode and Semantic Colors

- Use semantic system colors (`.label`, `.secondarySystemBackground`) and asset-catalog colors with light and dark variants. A hardcoded hex is a dark-mode bug with a delay.
- Elevation matters: on dark backgrounds, layered surfaces differ by system-provided elevated colors, not by opacity guesses.
- Test with Increase Contrast and Reduce Transparency enabled — both change the effective palette (`accessibility.md`).
- Forcing `preferredColorScheme` app-wide overrides the user's choice; if the app offers a theme setting, it must still respect "System" as the default.
- Images that carry meaning need a dark variant in the asset catalog; a screenshot pasted into the app is a light-mode artifact forever.

## Testing the Matrix

The minimum matrix, and it is small:

| Case | Why |
|---|---|
| Floor device, default text | The performance and space floor (`devices.md`) |
| Floor device, largest accessibility text | Where clipping and truncation appear |
| Newest large phone, landscape | Compact height and the safe-area extremes |
| iPad in Split View, if `target_devices` includes iPad | Compact width at runtime, resizing |
| Dark mode, Increase Contrast | Palette assumptions |

SwiftUI previews cover this cheaply — one preview per row, kept in the file. The Accessibility Inspector's Dynamic Type slider does the same for UIKit without rebuilding.

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| Content under the notch or home indicator | Laid out against the screen, not the safe area | Safe-area insets, read live |
| Button text truncated to one word | Fixed width plus Dynamic Type | Switch layout at large sizes |
| Broken layout only on iPad multitasking | Branching on idiom instead of size class | Size classes, recomputed |
| Layout wrong after rotation | Cached bounds | Read the size at layout time |
| Keyboard covers the field | Custom avoidance fighting the system, or the wrong coordinate space | Convert the notification frame |
| Everything shifts when the keyboard appears | Screen moved instead of scroll inset | Inset the scroll view |
| Fine in light mode, unreadable in dark | Hardcoded colors | Semantic or asset-catalog colors |
| Text unreadable at default size for some users | Fixed font sizes | Text styles or scaled fonts |

## Write It Down

- **The floor device and the matrix the app is actually tested against** belong in `platform` in `config.yaml` (a declared preference) and the physical devices in the shared `~/Clawic/data/devices/devices.md` (`memory-template.md`).
- **A device-specific or OS-specific layout bug** — a model where the safe area behaves differently, an OS version that changed keyboard behavior — is a `## Platform Facts` line, one per fact.
- **A layout decision with consequences** (iPad opted out of multitasking, landscape unsupported, a custom Dynamic Type breakpoint) is `artifacts/decision-layout-<app>.md` with its `## Boxes` line — reviewers and future features both ask why.
