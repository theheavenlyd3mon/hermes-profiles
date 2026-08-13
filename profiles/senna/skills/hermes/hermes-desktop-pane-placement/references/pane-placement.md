# Pane placement internals (desktop app)

Source map from the fork reference (`~/hermes-agent-fork-reference/apps/desktop/src/`),
verified 2026-08-13 while positioning the Hermes-Bot-Mode Bots pane. Use this
when a user asks to place a plugin pane at a specific spot in the left workspace.

## The layout model

- `src/app/contrib/controller.tsx` registers the core panes:
  - `sessions` — `placement: 'left'`, title `'sessions'`. This IS the whole
    left column (sidebar: nav rail + session list).
  - `workspace` — `placement: 'main'`, title `'New session'` (the chat area).
  - `terminal` (bottom), `files` / `preview` / `review` (right).
- A plugin pane with `placement: 'left'` joins the SAME group as `sessions` →
  it becomes a TAB in the left column's tab strip: `[sessions] [plugin]`.
- The nav rail rows (New session / Capabilities / Messaging / Artifacts) are
  core chrome INSIDE the sessions pane — plugin panes cannot be placed between
  them. `SIDEBAR_NAV_AREA` rows always render BELOW Artifacts. The only
  achievable "top of left workspace" is a left-column tab ordered via
  `dock.before`.

## Adoption (one-time!)

- `src/components/pane-shell/tree/store.ts::adoptContributedPanes` (line 766)
  runs on every registry change (`watchContributedPanes`, line 831).
- For each missing pane: anchor = `dock.pane` if it exists in the tree, else
  the first same-placement pane, else `mainId` → then
  `insertAtGroup(target, pane.id, dock?.pos ?? 'center', dock?.before, false)`.
- `src/components/pane-shell/tree/model.ts::insertAtGroup` (line 216):
  `pos: 'center'` joins the group as a tab; `before` inserts at
  `indexOf(before)` — so `before: 'sessions'` puts the new tab FIRST.
- `PaneDockHint` (store.ts:759): `{ pane, pos, before?: null | string }`.
- Comment at store.ts:755: adoption "Happens once per pane lifetime (the
  committed tree remembers it across boots), so user rearrangement wins from
  then on". A dock hint edited into plugin.js AFTER first adoption does NOT
  re-order — the user drags the tab, or the layout resets.

## Positioning recipe

Bots-style roster first in the left column:

```js
data: {
  placement: 'left',
  width: '260px',
  dock: { pane: 'sessions', pos: 'center', before: 'sessions' }
}
```

## Verification notes for a packaged app

- Packaged desktop builds never open the CDP port (no live DOM). Dev-server
  runs do (`127.0.0.1:9222`). On a packaged app, reason from the fork
  reference source instead of DOM inspection.
- Syntax-check a plugin file with `node --input-type=module --check < plugin.js`
  — the app loads it uncompiled, so a parse error surfaces only as a toast.
