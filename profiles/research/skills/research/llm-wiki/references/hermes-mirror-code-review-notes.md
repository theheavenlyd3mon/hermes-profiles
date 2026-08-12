# HermesMirror Code Review Notes

## Module Architecture (MagicMirror²)

Each module has:
- `module-name.js` — client-side module code (runs in Electron renderer)
- `module-name.css` — module styles
- `node_helper.js` — server-side module code (runs in Node.js)
- `README.md` — documentation

The client communicates with `node_helper` via `socketNotification` (Socket.IO under the hood).

## Common Bugs Found (2026-05-13 Review)

### 1. Backoff conflation (hermes-bridge)

**Bug:** Used `currentInterval` (meant for poll interval) as both the base interval AND the exponential backoff accumulator. With `refreshInterval: 30s`, the first backoff retry was 30s — not the intended 1s ramp.

**Fix:** Introduce a separate `retryDelay` property. Start at 1000ms on first failure, double each time, cap at 30000ms. Reset to `null` on success.

### 2. Shallow mutation on input (hermes-bridge diffBoardState)

**Bug:** Mutated the task object from `prevMap`, which was a reference into the function's `previous` parameter.

**Fix:** Spread copy before mutation.

### 3. Missing `animationSpeed` default (hermes-dashboard)

**Bug:** `this.config.animationSpeed || 0` referenced a key with no default, silently falling back to 0 (no animation).

**Fix:** Add to module `defaults`.

### 4. Stylelint BEM selector conflict

**Bug:** BEM class selectors (`block__element--modifier`) fail the default `selector-class-pattern` kebab-case rule in stylelint-config-standard.

**Fix:** Add BEM-compatible regex to `stylelint.config.mjs`:
```js
"selector-class-pattern": [
    "^[a-z][a-z0-9-]*(__[a-z][a-z0-9-]*)?(--[a-z][a-z0-9-]*)?$",
    { message: "Expected class selector to be kebab-case (BEM pattern allowed)" },
],
```

## HermesMirror-Specific Rules

- Never `npm start` (launches full-screen Electron) — use `npm run server` (headless HTTP) or `npm test` (vitest suite)
- Tab indentation for JS, 2-space tabs for CSS
- `.editorconfig` is authoritative
- `npm run config:check` validates config.js before deploying
