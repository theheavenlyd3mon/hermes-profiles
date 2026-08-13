---
name: hermes-desktop-pane-placement
description: Place or reorder Hermes desktop plugin panes (tabs, docks).
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, panes, layout, placement, plugins]
    category: hermes
    related_skills: [hermes-desktop-plugins, inspecting-hermes-desktop-dom]
---

# Hermes Desktop Pane Placement

How the desktop app decides WHERE a plugin pane lands, and how to control it.
Complements `hermes-desktop-plugins` (the SDK surface) with the layout-engine
internals. Verified against the fork reference 2026-08-13 while placing the
Hermes-Bot-Mode Bots pane.

## When to Use

- User asks to put a plugin pane at a specific place ("under New session, above Capabilities").
- A pane adopted into the wrong column/tab and you must explain or fix it.
- Need to know whether a position is even ACHIEVABLE via the plugin API before promising it.

## The layout model (what maps where)

- `sessions` pane (`placement: 'left'`, core) IS the whole left column: nav
  rail + session list. `workspace` pane (`placement: 'main'`) is the chat and
  its title is `'New session'` — don't confuse the title with a nav row.
- A plugin pane with `placement: 'left'` joins the SAME group as `sessions`
  → it becomes a TAB in the left column's tab strip: `[sessions] [plugin]`.
- The nav rail rows (New session / Capabilities / Messaging / Artifacts) are
  CORE CHROME inside the sessions pane. Plugin panes CANNOT be placed between
  those rows. `SIDEBAR_NAV_AREA` rows always render BELOW Artifacts.
  The closest achievable "top of left workspace" is a left-column tab ordered
  with `dock.before` — say so honestly instead of promising an inline slot.

## Controlling tab order

`pos: 'center'` joins the group as a tab; add `before: '<pane-id>'` to insert
before that tab. Bots-style roster first in the left column:

```js
data: {
  placement: 'left',
  width: '260px',
  dock: { pane: 'sessions', pos: 'center', before: 'sessions' }
}
```

## Pitfalls

- **Dock hints are ONE-TIME.** Adoption runs once per pane lifetime and the
  committed layout tree remembers user drags. Editing a hint into an
  already-adopted plugin does NOT re-position it — the user must drag the
  tab or reset the layout.
- **Adoption is silent** — it never fronts the zone's active tab, so a new
  pane can land in a stack the user doesn't notice.
- **Packaged builds have no CDP port** (no live DOM). Dev-server runs open
  `127.0.0.1:9222`. On a packaged app, reason from the fork reference source
  (`~/hermes-agent-fork-reference/apps/desktop/src`) instead of DOM inspection.
- **Syntax-check before shipping:** `node --input-type=module --check < plugin.js`
  — the app loads the file uncompiled; a parse error surfaces only as a toast.
- Plugin panes are never dismissed anymore: Close on a plugin pane DISABLES
  the plugin (contributed-pane dismissal entries are dropped on adoption).

## Verification

- After registering a dock hint, confirm tab order on the NEXT adoption (fresh
  profile or layout reset) — existing trees keep their committed order.
- Read the pane tree's committed layout in the fork reference tests or reason
  from `adoptContributedPanes` (see reference) when no CDP is available.

## References

- `references/pane-placement.md` — source map: adoption code paths,
  `insertAtGroup` semantics, `PaneDockHint`, file:line anchors.
