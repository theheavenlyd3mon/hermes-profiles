# Accessibility — VoiceOver, Dynamic Type, and the Audit

**Before an audit or a fix**, read `accessibility.commitment` in `~/Clawic/data/ios/config.yaml` (the level the team holds itself to) and open `artifacts/accessibility-audit-*.md` if `## Boxes` names one — an audit is only useful against the previous one.

**Contents:** [What VoiceOver Needs](#what-voiceover-needs) · [Traits, Values and Actions](#traits-values-and-actions) · [Focus and Announcements](#focus-and-announcements) · [The Settings Users Actually Have On](#the-settings-users-actually-have-on) · [Numbers That Are Requirements](#numbers-that-are-requirements) · [Beyond VoiceOver](#beyond-voiceover) · [Auditing](#auditing) · [Store and Legal Surface](#store-and-legal-surface) · [Symptoms](#symptoms) · [Write It Down](#write-it-down)

## What VoiceOver Needs

Four properties, and most bugs are a missing first one:

- **Label** — what it is, in words a person would say: "Play", not "play_button", not "button". No control type in the label; VoiceOver says "button" itself.
- **Value** — the current state where it varies: a slider's number, a toggle's on/off, a field's contents.
- **Traits** — what kind of thing it is: button, header, link, selected, disabled, image. Traits are how users navigate by type; a custom control with no button trait is invisible to a rotor.
- **Hint** — how to interact, only when it is not obvious. Optional, and usually noise.

Images that carry information need labels; decorative images are hidden from accessibility entirely. An unlabeled image reads as its filename, which is how internal naming reaches users.

Group compound cells into one element (`accessibilityElement(children: .combine)` or a container in UIKit) so a list row is one swipe, not five. Then override the combined label if the concatenation reads badly.

## Traits, Values and Actions

- Custom controls built from taps on a view are invisible until they declare `isAccessibilityElement`, a label and the button trait.
- Header traits on section titles enable heading navigation — the fastest way for a VoiceOver user to move through a long screen, and a two-line change.
- **Custom actions** replace a row full of small buttons: one element, with swipe-selectable actions. This is the single largest usability improvement available in most list-based apps.
- Adjustable elements (`accessibilityAdjustableAction` / the adjustable trait) let a swipe up and down change a value — correct for steppers, ratings and custom sliders.
- Anything that opens a link gets the link trait; anything disabled gets the disabled trait, or users are told to tap something that does nothing.

## Focus and Announcements

- After a modal appears, move focus to it. After it dismisses, return focus to what opened it. Without this, VoiceOver focus stays behind the sheet and the app feels broken.
- Announce asynchronous outcomes — "Saved", "3 results" — with a screen-change or announcement notification. A silent success is indistinguishable from a silent failure.
- Order matters: fix reading order with explicit accessibility elements or sort priority rather than reordering the visual layout.
- Loading states need an announcement or a busy trait; a spinner is invisible.

## The Settings Users Actually Have On

Dynamic Type is the most used, and it is a layout problem (`layout.md`). The rest change rendering, and each one is a one-line check:

| Setting | What the app must do |
|---|---|
| Reduce Motion | Replace slides, zooms and parallax with cross-fades. Respect it globally, not per animation |
| Reduce Transparency | Do not depend on blur for legibility |
| Increase Contrast | Semantic colors handle it; hardcoded palettes do not |
| Bold Text | System fonts adapt; custom fonts need a bold variant selected |
| Differentiate Without Color | Any state shown only by color needs a shape, icon or text too — status dots are the usual offender |
| Button Shapes | Text-only buttons get a visible affordance |
| Larger Text (accessibility sizes) | See Dynamic Type |

## Numbers That Are Requirements

- **44 × 44 points** minimum hit target (Apple's HIG). A 20-point icon needs an expanded touch area, not a bigger icon.
- **4.5:1** contrast for normal text, **3:1** for large text (18 pt, or 14 pt bold) — the WCAG AA thresholds Apple's own guidance mirrors. Measure with the Accessibility Inspector's color contrast calculator rather than guessing.
- Text must scale to the largest accessibility size without loss of function: content may reflow, nothing may become unreachable.
- Focus order must match reading order; there is no numeric threshold, but a screen where they disagree fails every audit.

## Beyond VoiceOver

- **Voice Control** users speak the labels: "tap Play". A control whose accessibility label does not match its visible text is unspeakable. Turn on "Show Names" once and the mismatches are visible instantly.
- **Switch Control** and **Full Keyboard Access** navigate by focus order and need every interactive element to be focusable — including custom gesture-only surfaces, which need an accessible equivalent.
- **Gesture-only features** (swipe to delete, long-press menus) must have a non-gesture path: a custom action, a button, or a menu item.
- **Captions and audio descriptions** for video; **haptics** as reinforcement, never as the only signal.
- Time limits and auto-advancing carousels need a way to pause or extend.

## Auditing

- Xcode's Accessibility Inspector runs an automated audit per screen: missing labels, contrast failures, element sizes, clipped text at large sizes. Run it on every screen; it takes minutes and catches the mechanical half.
- The other half needs VoiceOver on a device with the screen curtain on: navigate the main flow start to finish without looking. Nothing else finds focus-order and announcement problems.
- Test the two extremes together: largest accessibility text with VoiceOver on.
- Add the audit to the release checklist rather than to a quarterly intention — accessibility regresses feature by feature (`releases.md`).

## Store and Legal Surface

- App Store product pages can declare accessibility features; the declaration is a claim like any other and must be true for the version that ships.
- Accessibility is rarely a direct rejection reason, but an app that cannot be used with the system's own features draws support complaints, one-star reviews, and — for public-sector, banking, retail and other consumer services in several jurisdictions, including the European Accessibility Act regime — legal exposure. Check the obligations that apply to the app's market before treating this as optional polish.
- `audience: kids` and regulated audiences raise the bar further: those apps are reviewed and used with more assistive technology, not less.

## Symptoms

| Symptom | Cause | Check |
|---|---|---|
| VoiceOver reads "button" with no name | Missing label | Add a label; never put the type in it |
| VoiceOver reads a filename | Unlabeled image | Label it, or hide it if decorative |
| Swiping through a list takes forever | Cells not combined into one element | Combine children, then fix the combined label |
| Focus stays behind a modal | No focus move on present | Move focus in, and back out on dismiss |
| Voice Control cannot activate a button | Label differs from visible text | Match the label to the visible words |
| Toggle state never announced | Value or trait missing | Value plus the correct trait |
| Animations still play with Reduce Motion on | Setting not checked | One global check, applied at the animation layer |
| Status only shown as a colored dot | Color-only signal | Add shape or text (Differentiate Without Color) |

## Write It Down

- **An audit result** — date, screens covered, what failed, what was fixed — is `artifacts/accessibility-audit-<app>.md`, with its `## Boxes` line in the same turn (`memory-template.md`). The next audit compares against it; without a previous one, an audit only measures today's mood.
- **The commitment level** (VoiceOver-complete, Dynamic Type to the largest size, captions) is a declared preference and belongs in `accessibility` in `config.yaml`, where the Output Gates can enforce it.
- **A platform quirk found while testing** — a control that behaves differently under Switch Control, an OS version where an announcement stopped working — is a `## Platform Facts` line.
