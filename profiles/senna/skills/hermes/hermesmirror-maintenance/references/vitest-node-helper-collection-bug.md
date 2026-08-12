# Vitest node_helper silent-collection bug (HermesMirror)

Pre-existing since commit `2c624c44`. Two specs —
`tests/unit/modules/hermes-chat/node_helper_spec.js` and
`tests/unit/modules/hermes-bridge/node_helper_spec.js` — **failed to load** and
reported **0 tests** instead of failing loudly.

**FIXED 2026-07-20** (commit `05d511b4`). Both suites now collect and pass
(55 tests total: 19 hermes-chat + 36 hermes-bridge). Full unit suite: 539/540
(1 pre-existing macOS systeminfo failure).

## Symptom
`--reporter=json` shows the suite with `status: "failed"`, `numTotalTests: 0`,
`assertionResults: []`, and `message: "Cannot find module 'node_helper'"`.
Because the count is 0 (not a red test), a pass/fail summary that only looks at
`numFailedTests` reads it as green. The earlier "~126/127 pass" figure was
actually `board-utils_spec.js` alone — both node_helper specs were dead.

## Root cause
The specs do `vi.mock("node_helper", () => NodeHelper)` then
`require("../../../../modules/<mod>/node_helper")`. The module itself does
`require("node_helper")` (bare). `tests/utils/vitest-setup.js` overrides
`Module.prototype.require` to alias `logger` → `js/logger.js`, but has **no
alias for `node_helper`**, so the bare require throws at load. `vi.mock()`
never gets a chance to intercept because the require never reaches vitest's
mock layer.

## The trap (tried 2026-07-20, REVERTED)
Adding a `node_helper` alias to the `Module.prototype.require` shim **globally
in `vitest-setup.js`** fixes collection but **breaks `vi.mock()` interception**:
the shim's `originalRequire` returns the REAL base class, not the mock.
Result: `helper` is a function, not the mocked object, and
`vi.spyOn(helper, "fetchMessages")` throws
`The property "fetchMessages" is not defined on the function` — 55 hard
failures, worse than the silent 0. Reverted.

## Correct fix (APPLIED 2026-07-20, commit 05d511b4)
Patch `Module.prototype.require` **in each spec file** (not globally in
`vitest-setup.js`), returning a mock directly for the bare id. This is the
same pattern the weather spec (`tests/unit/modules/default/weather/node_helper_spec.js`)
uses. The key difference from the global-shim trap: the local patch returns a
mock object, not the real base class, so `vi.spyOn` works.

```js
const Module = require("node:module");
const Log = { log: vi.fn(), warn: vi.fn(), error: vi.fn() };

const originalRequire = Module.prototype.require;
Module.prototype.require = function (id) {
  if (id === "node_helper") {
    return { create: vi.fn((obj) => Object.assign({ name: "hermes-chat" }, obj)) };
  }
  if (id === "logger") {
    return Log;
  }
  return originalRequire.apply(this, arguments);
};
const helper = require("../../../../modules/hermes-chat/node_helper");
Module.prototype.require = originalRequire;
```

Do NOT use `resolve.alias` in `vitest.config.mjs` — it was proposed but never
verified; the in-spec patch is simpler and proven.

## Bonus bug uncovered
Once the suite actually collected, a self-contradictory test surfaced:
"should reset backoff after successful fetch" mocked `fetchAndDiff` to a no-op
(`vi.spyOn(helper, "fetchAndDiff").mockResolvedValue(undefined)`) yet expected
the real success-path side effect (`retryDelay = null`). A mocked no-op never
runs that code. Fix: remove the mock, let the real `fetchAndDiff` run (the
`global.fetch` mock already provides the successful response).

## Detection one-liner
When reading vitest JSON, flag dead suites:
```js
(r.testResults||[]).filter(f => f.status === "failed" && (f.assertionResults||[]).length === 0)
  .forEach(f => console.log("DEAD SUITE:", f.name, "|", (f.message||"").split("\n")[0]));
```
