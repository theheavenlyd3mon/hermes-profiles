# Extracting Pure Functions from MM node_helper.js for Unit Tests

MagicMirror's `node_helper.js` files mix framework code (`NodeHelper.create()` with socket listeners) and pure business logic (diffing, mapping, calculations). This makes them hard to unit test because `Module` and `Log` aren't available in Node.js outside MM.

## The Pattern

### 1. Create `board-utils.js` (or similar)

Extract all pure functions that don't depend on MM framework:

```javascript
// board-utils.js — no MagicMirror imports
function diffBoardState(previous, current) { /* ... */ }
function statusToEvent(status) { /* ... */ }
function clamp(val, min, max) { /* ... */ }

module.exports = { diffBoardState, statusToEvent, clamp };
```

### 2. Import in `node_helper.js`

```javascript
const { diffBoardState, statusToEvent, clamp } = require("./board-utils");
```

### 3. Remove local copies

**CRITICAL**: Delete the original function definitions from `node_helper.js`. Having both `const { X } = require(...)` and `function X(...)` in the same scope throws:
```
Error: Identifier 'X' has already been declared
```

### 4. Test directly (import from board-utils, not node_helper)

Import the pure functions directly from `board-utils.js` — no need to go through `node_helper.js`:

```javascript
const { diffBoardState, statusToEvent, clamp } = require("../../../../modules/hermes-bridge/board-utils");

describe("board-utils", () => {
  it("diff detects new task", () => {
    const prev = { tasks: [] };
    const curr = { tasks: [{ task_id: "1", status: "ready" }] };
    const events = diffBoardState(prev, curr);
    expect(events).toHaveLength(1);
    expect(events[0].type).toBe("HERMES_KANBAN_TASK_CREATED");
  });
});
```

**Why this is better than re-exporting through node_helper:** `board-utils.js` has zero MagicMirror dependencies, so the test never triggers `require("node_helper")` or `require("logger")`. No mocking needed for pure function tests.
